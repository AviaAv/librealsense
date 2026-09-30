# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

import json
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import logging
import pytest
from rspy import repo

log = logging.getLogger(__name__)

# Browser + server + real camera. The Playwright half lives in the viewer's own suite;
# this wrapper owns the camera, the server process and the readiness handshake.
pytestmark = [
    pytest.mark.device("D455"),
    pytest.mark.skipif(
        sys.platform != "linux" or platform.machine() == "aarch64",
        reason="rest-api wrapper supports x86_64 Linux only",
    ),
]

_SERVER_DIR = os.path.join(repo.root, "wrappers", "rest-api")
_VIEWER_DIR = os.path.join(_SERVER_DIR, "tools", "react-viewer")
_API_PORT = 8000
_API = f"http://127.0.0.1:{_API_PORT}"

# Nested innermost-first so Playwright is the one that gives up and still writes its
# summary. The marker must never fire: conftest's thread method kills the whole run.
_PW_GLOBAL_MS = 600_000
_SUBPROCESS_TIMEOUT = 700
_MARKER_TIMEOUT = 1200

_SERVER_READY_TIMEOUT = 90
_DEVICE_READY_TIMEOUT = 60


def _get_json(url):
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.load(response)


def _port_in_use(port):
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _fail_if_not_ready_to_run():
    # jammy's apt node is 12, which breaks vite in ways that read as test failures
    node = shutil.which("node") and subprocess.run(
        ["node", "-p", "process.versions.node.split('.')[0]"],
        stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
    if not node or int(node) < 18:
        pytest.fail(f"react-viewer e2e: need Node 18+, found {node or 'none'}. LibCI installs it "
                    "in 'Install Requirements'; locally use deb.nodesource.com/setup_20.x")

    if _port_in_use(_API_PORT):
        pytest.fail(f"react-viewer e2e: port {_API_PORT} is already in use -- a leftover "
                    "uvicorn from a crashed run would serve a stale SDK")


def _wait_for_server(server, server_log_path):
    deadline = time.time() + _SERVER_READY_TIMEOUT
    while time.time() < deadline:
        if server.poll() is not None:
            pytest.fail(f"rest-api server exited with {server.returncode} before becoming ready:\n"
                        f"{_tail(server_log_path)}")
        try:
            return _get_json(f"{_API}/api/v1/health")
        except (urllib.error.URLError, OSError, ValueError):
            time.sleep(0.5)
    pytest.fail(f"rest-api server was not ready within {_SERVER_READY_TIMEOUT}s:\n{_tail(server_log_path)}")


def _wait_for_device(serial_number):
    deadline = time.time() + _DEVICE_READY_TIMEOUT
    seen = []
    while time.time() < deadline:
        try:
            seen = [d.get("serial_number") for d in _get_json(f"{_API}/api/v1/devices/")]
        except (urllib.error.URLError, OSError, ValueError):
            seen = []
        if serial_number in seen:
            return
        time.sleep(1)
    pytest.fail(f"camera {serial_number} was never enumerated by the rest-api server "
                f"within {_DEVICE_READY_TIMEOUT}s; it reported {seen}")


def _killpg(server, sig):
    try:
        os.killpg(os.getpgid(server.pid), sig)
    except ProcessLookupError:
        pass


def _tail(path, lines=40):
    try:
        with open(path) as f:
            return "".join(f.readlines()[-lines:])
    except OSError:
        return "<no server log>"


@pytest.mark.timeout(_MARKER_TIMEOUT)
def test_react_viewer_e2e(module_device_setup, request):
    _fail_if_not_ready_to_run()
    serial_number = module_device_setup

    logdir = request.config._test_logdir
    server_log_path = os.path.join(logdir, f"rest-api-server_{serial_number}.log")
    playwright_log_path = os.path.join(logdir, f"react-viewer-e2e_{serial_number}.log")

    env = os.environ.copy()
    pyrs_dir = repo.find_pyrs_dir()
    if pyrs_dir:
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = pyrs_dir + os.pathsep + existing if existing else pyrs_dir

    with open(server_log_path, "w") as server_log:
        server = subprocess.Popen(
            [sys.executable, "-u", "-m", "uvicorn", "main:combined_app",
             "--host", "127.0.0.1", "--port", str(_API_PORT)],
            cwd=_SERVER_DIR, env=env, stdout=server_log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            health = _wait_for_server(server, server_log_path)
            # Records which SDK actually served the run - main.py only finds <root>/build,
            # which does not exist on LibCI, so PYTHONPATH above is what picks it.
            log.info("rest-api server ready, SDK %s", health.get("sdk_version"))
            _wait_for_device(serial_number)

            env.update(REAL_DEVICE="true", API_URL=_API, DEVICE_SERIAL=serial_number, CI="true")
            # list replaces the config's html reporter, which blocks serving a report.
            # CI=true buys reuseExistingServer=false but also retries=3; LibCI reruns already.
            command = ["npm", "run", "test:e2e", "--",
                       "--project=real-device",
                       "--retries=1",
                       "--reporter=list",
                       f"--global-timeout={_PW_GLOBAL_MS}",
                       "--trace=retain-on-failure",
                       f"--output={os.path.join(logdir, 'react-viewer-e2e')}"]
            with open(playwright_log_path, "w") as playwright_log:
                try:
                    # To a file, not PIPE: a timeout discards captured output, and this
                    # run takes minutes.
                    completed = subprocess.run(command, cwd=_VIEWER_DIR, env=env,
                                               stdout=playwright_log, stderr=subprocess.STDOUT,
                                               timeout=_SUBPROCESS_TIMEOUT, check=False)
                except subprocess.TimeoutExpired:
                    log.error("playwright timed out after %ss:\n%s",
                              _SUBPROCESS_TIMEOUT, _tail(playwright_log_path, 80))
                    raise
            output = _tail(playwright_log_path, 80)
            if completed.returncode:
                log.error("playwright failed (rc=%s):\n%s", completed.returncode, output)
            else:
                log.info(output)
            assert completed.returncode == 0
        finally:
            # aiortc worker threads hold the camera, so the whole group must go before the
            # hub powers the port off - and never raise here, it would bury the real failure.
            _killpg(server, signal.SIGTERM)
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                _killpg(server, signal.SIGKILL)
                server.wait(timeout=15)
            log.info("rest-api server log:\n%s", _tail(server_log_path))
