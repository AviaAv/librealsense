# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

"""Live smoke test for parallel-device execution.

`device_each` produces one instance per connected camera; each is tagged
`parallel_safe`, so under `pytest -n <N> --dist loadgroup -m parallel_safe` the
per-camera instances are pinned to separate xdist workers (by serial) and run
concurrently. Bodies are content/arrival-only (no rate or timing assertion), so
they are unaffected by USB contention.

Multiple distinct test functions share one module-scoped device setup (a single
hw_reset/enable per camera) — this is what amortizes the fixed per-camera setup
cost across the parallel run.
"""

import os
import pytest
import pyrealsense2 as rs
import logging
log = logging.getLogger(__name__)

pytestmark = [
    pytest.mark.device_each("D400*"),
    pytest.mark.parallel_safe,
]

FRAMES_TO_GRAB = 10


def _worker():
    return os.environ.get("PYTEST_XDIST_WORKER", "serial")


def test_reads_identity(test_device):
    dev, _ = test_device
    name = dev.get_info(rs.camera_info.name)
    serial = dev.get_info(rs.camera_info.serial_number)
    log.info("worker=%s device=%s serial=%s", _worker(), name, serial)
    assert name and serial


def test_depth_sensor_present(test_device):
    dev, _ = test_device
    assert dev.first_depth_sensor() is not None


def _stream_depth(test_device):
    dev, ctx = test_device
    serial = dev.get_info(rs.camera_info.serial_number)
    pipe = rs.pipeline(ctx)
    cfg = rs.config()
    cfg.enable_device(serial)
    cfg.enable_stream(rs.stream.depth)
    pipe.start(cfg)
    try:
        for _ in range(FRAMES_TO_GRAB):
            frames = pipe.wait_for_frames()
            assert frames.get_depth_frame(), f"{serial}: no depth frame"
    finally:
        pipe.stop()


def test_depth_stream_a(test_device):
    _stream_depth(test_device)


def test_depth_stream_b(test_device):
    _stream_depth(test_device)


def test_depth_stream_c(test_device):
    _stream_depth(test_device)
