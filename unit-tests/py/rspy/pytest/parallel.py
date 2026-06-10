# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

"""Opt-in parallel test execution across devices, via pytest-xdist.

Design: docs/superpowers/specs/2026-06-09-parallel-device-tests-design.md

Default behavior is unchanged. A test runs in parallel only when explicitly
tagged ``@pytest.mark.parallel_safe``; untagged tests run serially exactly as
before. Two phases (sequenced as two pytest invocations):

    serial   :  pytest -p no:xdist -m "not parallel_safe"
    parallel :  pytest -n <N> --dist loadgroup -m parallel_safe

In the parallel phase, ``assign_xdist_groups`` stamps each parallel_safe device
test with an ``xdist_group`` keyed on its device serial, so loadgroup keeps all
of one camera's tests on a single worker (preserving per-device serial order)
while different cameras run on different workers.

pytest-xdist is treated as OPTIONAL, not a required plugin: when it is absent or
the run is not using workers (no ``-n``), every hook here degrades to a no-op
and the suite runs serially. This is a deliberate graceful-degrade, not a silent
option no-op, so it is intentionally NOT listed in REQUIRED_PYTEST_PLUGINS.
"""

import logging

log = logging.getLogger(__name__)

PARALLEL_SAFE_MARKER = "parallel_safe"


def register_marker(config):
    """Register the parallel_safe marker to avoid PytestUnknownMarkWarning."""
    config.addinivalue_line(
        "markers",
        "parallel_safe: test is safe to run concurrently with a different "
        "device's tests (no rate/drop/TTFF/sync assertion, no hub/reset/enumerate). "
        "Selected for the parallel phase via -m parallel_safe."
    )


def is_xdist_worker(config):
    """True only in an xdist *worker* process (controller/serial run → False).

    xdist injects ``workerinput`` (a dict) into the worker's config. The hub
    (Acroname BrainStem) accepts only one process connection, so workers must NOT
    init/connect the hub — the controller owns it and powers the ports.
    """
    return isinstance(getattr(config, "workerinput", None), dict)


def xdist_active(config):
    """True when this process is part of an xdist distributed run.

    Works in BOTH roles, which matters because pytest_generate_tests runs on the
    worker, not the controller:
      - worker:     xdist injects ``config.workerinput``;
      - controller: ``-n``/``--numprocesses`` is set.
    False in plain/serial runs, under ``-p no:xdist``, and in unit tests that call
    resolve directly — so the parametrize value shape is unchanged outside a real
    parallel run.
    """
    # Real xdist injects workerinput as a dict on the worker; check the type so a
    # MagicMock config (unit tests) doesn't false-positive via auto-created attributes.
    if isinstance(getattr(config, "workerinput", None), dict):
        return True
    return bool(config.getoption("numprocesses", 0))


def resolve_num_workers(num_devices, cap=None):
    """Workers for the parallel phase: min(devices, physical cores), capped.

    Device count is normally well under core count, so this is effectively one
    worker per camera with a safety ceiling that protects low-core machines from
    oversubscription. ``cap`` is the optional --max-device-workers override.
    """
    import os
    cores = os.cpu_count() or 1
    n = min(num_devices, cores)
    if cap:
        n = min(n, cap)
    return max(1, n)


def serial_param(config, serial):
    """Wrap a device-serial parametrize value so loadgroup pins it to one worker.

    Attaches ``@pytest.mark.xdist_group(serial)`` when xdist is active and the value
    is a real serial (not a __SKIP__/__MISSING__ sentinel or a multi-device list).
    Returns the bare value otherwise.

    Must be applied at parametrize time (pytest_generate_tests), NOT in a later
    pytest_collection_modifyitems hook: xdist derives the loadgroup ``@<group>``
    nodeid suffix in its own worker-side collection hook, which runs before conftest's
    — a marker added there arrives too late and xdist falls back to round-robin
    (splitting one camera's tests across workers → concurrent hub access).
    """
    if (xdist_active(config) and isinstance(serial, str)
            and serial and not serial.startswith("__")):
        import pytest
        return pytest.param(serial, marks=pytest.mark.xdist_group(serial))
    return serial
