# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

"""Opt-in parallel test execution across devices, via pytest-xdist.

Design: docs/superpowers/specs/2026-06-09-parallel-device-tests-design.md

Default behavior is unchanged. Everything runs under a SINGLE pytest call:

    pytest -n <N> --dist loadgroup

``serial_param`` stamps each device test with an ``xdist_group`` so loadgroup
decides placement:

  - ``parallel_safe`` test → group keyed on its device serial. All of one camera's
    tests stay on a single worker (per-device serial order preserved), while
    different cameras run on different workers → parallel across devices.
  - every other (exclusive) test → one shared ``SERIAL_GROUP``. loadgroup pins the
    whole group to a single worker, so exclusive tests run one-at-a-time, never
    concurrently with each other.

No ``-m`` filter and no second invocation: parallel and serial tests run together
in one pass.

pytest-xdist is treated as OPTIONAL, not a required plugin: when it is absent or
the run is not using workers (no ``-n``), every hook here degrades to a no-op
and the suite runs serially. This is a deliberate graceful-degrade, not a silent
option no-op, so it is intentionally NOT listed in REQUIRED_PYTEST_PLUGINS.
"""

import logging

log = logging.getLogger(__name__)

PARALLEL_SAFE_MARKER = "parallel_safe"

# Shared loadgroup for every non-parallel_safe test. loadgroup keeps a whole group
# on one worker, so all exclusive tests are serialized onto a single worker (never
# run concurrently with each other) while parallel_safe tests spread per-device.
# Prefixed with "__" so it can never collide with a real device serial.
SERIAL_GROUP = "__serial__"


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
    # Worker (workerinput dict) or controller (-n/numprocesses set). is_xdist_worker
    # also guards against a MagicMock config (unit tests) false-positiving.
    return is_xdist_worker(config) or bool(config.getoption("numprocesses", 0))


def serial_param(config, serial, parallel_safe):
    """Wrap a device-serial parametrize value with the loadgroup it belongs to.

    Attaches ``@pytest.mark.xdist_group(...)`` when xdist is active and the value is a
    real serial (not a __SKIP__/__MISSING__ sentinel or a multi-device list):

      - parallel_safe test → group = the device serial → loadgroup keeps one camera's
        tests on a single worker, different cameras on different workers (parallel).
      - other test        → group = SERIAL_GROUP → all exclusive tests share one
        worker and run one-at-a-time (serial).

    Returns the bare value otherwise (no xdist → plain serial run, unchanged shape).

    Must be applied at parametrize time (pytest_generate_tests), NOT in a later
    pytest_collection_modifyitems hook: xdist derives the loadgroup ``@<group>``
    nodeid suffix in its own worker-side collection hook, which runs before conftest's
    — a marker added there arrives too late and xdist falls back to round-robin
    (splitting one camera's tests across workers → concurrent hub access).
    """
    if (xdist_active(config) and isinstance(serial, str)
            and serial and not serial.startswith("__")):
        import pytest
        group = serial if parallel_safe else SERIAL_GROUP
        return pytest.param(serial, marks=pytest.mark.xdist_group(group))
    return serial
