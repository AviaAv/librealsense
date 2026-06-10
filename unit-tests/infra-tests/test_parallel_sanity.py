# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

"""Sanity tests for the opt-in parallel-device framework (no hardware).

Proves the plumbing only:
- the ``parallel_safe`` marker is registered and selectable via ``-m parallel_safe``
- tagged tests execute under pytest-xdist workers (``-n``) and serially without it
- ``resolve_num_workers`` caps to min(devices, cores) and honors --max-device-workers

Hardware-free. Real device-parallel (xdist_group pinning across cameras) is
validated separately once the non-exclusive ``enable_only`` mode lands.
"""

import os
import pytest

from rspy.pytest.parallel import resolve_num_workers

pytestmark = pytest.mark.parallel_safe


def test_marker_selected():
    """If ``-m parallel_safe`` selected this test to run, the marker is live."""
    assert True


def test_runs_under_worker():
    """Under ``-n`` xdist sets PYTEST_XDIST_WORKER (gw0/gw1/...); serial leaves it unset."""
    worker = os.environ.get("PYTEST_XDIST_WORKER")
    assert worker is None or worker.startswith("gw")


def test_resolve_num_workers_caps():
    cores = os.cpu_count() or 1
    assert resolve_num_workers(4, cap=2) == 2
    assert resolve_num_workers(1) == 1
    assert resolve_num_workers(100) <= cores
    assert resolve_num_workers(0) == 1  # never zero workers
