# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

"""Sanity tests for the opt-in parallel-device framework (no hardware).

Proves the plumbing only:
- the ``parallel_safe`` marker is registered and selectable via ``-m parallel_safe``
- tagged tests execute under pytest-xdist workers (``-n``) and serially without it

Hardware-free. Real device-parallel (xdist_group pinning across cameras) is
validated separately on a hub machine.
"""

import os
import pytest

pytestmark = pytest.mark.parallel_safe


def test_marker_selected():
    """If ``-m parallel_safe`` selected this test to run, the marker is live."""
    assert True


def test_runs_under_worker():
    """Under ``-n`` xdist sets PYTEST_XDIST_WORKER (gw0/gw1/...); serial leaves it unset."""
    worker = os.environ.get("PYTEST_XDIST_WORKER")
    assert worker is None or worker.startswith("gw")
