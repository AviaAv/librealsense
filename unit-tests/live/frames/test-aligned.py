# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2026 RealSense, Inc. All Rights Reserved.

# test:device each(D400*)

import pyrealsense2 as rs
from rspy import log, test
import numpy as np

# Simple test that validates that after aligning depth to color the depth frame
# contains valid (non-zero) data. Some platforms/drivers produce an aligned depth
# frame that exists but whose buffer is all zeros; this test fails in that case.

NUM_FRAMES = 60
SKIP_INITIAL = 30
DEBUG_MODE = False


dev, ctx = test.find_first_device_or_exit()

pipe = rs.pipeline(ctx)
cfg = rs.config()
cfg.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
cfg.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

profile = pipe.start(cfg)
align = rs.align(rs.stream.color)

# skip a few frames to stabilize
for _ in range(SKIP_INITIAL):
    pipe.wait_for_frames()

# Check aligned depth frames are not all zeros
for i in range(NUM_FRAMES):
    frames = pipe.wait_for_frames()
    aligned = align.process(frames)
    aligned_depth = aligned.get_depth_frame()

    test.check(aligned_depth, f"Frame {i}: aligned depth frame missing")

    data = np.asanyarray(aligned_depth.get_data())
    test.check(np.any(data), f"Frame {i}: aligned depth frame is all zeros")

pipe.stop()
test.print_results_and_exit()
