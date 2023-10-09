# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2022 Intel Corporation. All Rights Reserved.

# test:device D400*

import pyrealsense2 as rs
from rspy.stopwatch import Stopwatch
from rspy import test, log
import time
import sys
import numpy as np
import cv2
from scipy.ndimage import zoom


# Start depth + color streams and go through the frame to make sure it is showing a depth image
# Color stream is only used to display the way the camera is facing
# Verify that the frame does indeed have variance - therefore it is showing a depth image

dev = test.find_first_device_or_exit()

cfg = rs.config()
cfg.enable_stream(rs.stream.depth, rs.format.z16, 30)
cfg.enable_stream(rs.stream.color, rs.format.bgr8, 30)


def display_image(windowTitle, img):
    """
    Display a given image and exits when the x button or esc key are pressed
    """
    cv2.imshow(windowTitle, img)
    while cv2.getWindowProperty(windowTitle, cv2.WND_PROP_VISIBLE) > 0:
        k = cv2.waitKey(33)
        if k == 27:  # Esc key to stop
            cv2.destroyAllWindows()
            break
        elif k == -1:  # normally -1 returned,so don't print it
            pass


def save_image(depth, color, filename, showImage):
    colorizer = rs.colorizer()
    depth_image = np.asanyarray(colorizer.colorize(depth).get_data())
    color_image = np.asanyarray(color.get_data())

    depth_rows, _, _ = depth_image.shape
    color_rows, _, _ = color_image.shape

    # resize the image with the higher resolution to look like the smaller one
    if depth_rows < color_rows:
        color_image = zoom(color_image, (depth_rows/color_rows, depth_rows/color_rows, 1))
    elif color_rows < depth_rows:
        depth_image = zoom(depth_image, (color_rows/depth_rows, color_rows/depth_rows, 1))

    img = np.concatenate((depth_image, color_image), axis=1)

    if filename != "":
        cv2.imwrite(filename, img)
        cv2.imwrite("test.png",depth_image)
        cv2.imwrite("test2.png",color_image)

    if showImage:
        display_image("Depth Stream", img)


def setup(config, laserOn):
    pipeline = rs.pipeline()
    pipeline_profile = pipeline.start(config)

    if laserOn is False:
        sensor = pipeline_profile.get_device().first_depth_sensor()
        sensor.set_option(rs.option.laser_power, 0)
        sensor.set_option(rs.option.emitter_enabled, 0)

    frames = pipeline.wait_for_frames()
    for i in range(30):
        frames = pipeline.wait_for_frames()
    depth = frames.get_depth_frame()
    color = frames.get_color_frame()
    return pipeline, depth, color


def get_distances(depth):
    MAX_METERS = 10  # max distance that can be detected, in meters
    dists = {}
    total = 0
    for y in range(480):
        for x in range(640):
            dist = depth.get_distance(x, y)
            if dist >= MAX_METERS:  # out of bounds, assuming it is a junk value
                continue
            # we only distinguish between two pixels if they are different more than 10cm apart
            # we can get a more accurate measure if we round it less, say round(dist,2)*100 to get 1cm difference noted
            dist = int(round(dist, 1) * 10)
            if dists.get(dist) is not None:
                dists[dist] += 1
            else:
                dists[dist] = 1
            total += 1
    # print(dists)
    return dists, total


def check_depth(config, laserOn=True, filename="", showImage: bool = False):
    """
    Checks if the camera is showing a frame with a meaningful depth
    the higher the detail level is, the more it is sensitive to distance
    eg: 1 for a difference of 1 meter, 100 for a diff of 1cm

    returns true iff is it does
    """

    pipeline, depth, color = setup(config, laserOn)

    if not depth or not color:
        print("Error getting depth / color frames")
        return False
    else:
        pass

    dists, total = get_distances(depth)
    save_image(depth, color, filename, showImage)

    is_depth = True
    for key in dists:
        if dists[key] > total*0.9:
            is_depth = False
            break
    pipeline.stop()
    return is_depth


################################################################################################
test.start("Testing depth frame - laser ON -", dev.get_info(rs.camera_info.name))
res = check_depth(cfg, True, "1.png", True)
test.check(res is True)
test.finish()

################################################################################################

test.start("Testing depth frame - laser OFF -", dev.get_info(rs.camera_info.name))
res = check_depth(cfg, False, "2.png", True)
test.check(res is True)
test.finish()

################################################################################################

test.print_results_and_exit()
