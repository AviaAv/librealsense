# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2023 Intel Corporation. All Rights Reserved.

# test:device each(D400*)
# test:timeout 600
# timeout - on the worst case, we're testing with 8 streams, so:
# timeout = (8 choose 2) * (TIME_FOR_STEADY_STATE + TIME_TO_COUNT_FRAMES)
# 8 choose 2 tests to do (one for each pair)

from rspy import test, log
import pyrealsense2 as rs
import fps_helper
import itertools

def get_sensors_and_profiles(device):
    """
    Returns an array of pairs of a (sensor, profile) for each of its profiles
    """
    sensor_profiles_arr = []
    for sensor in device.query_sensors():
        if sensor.is_depth_sensor() and sensor.supports(rs.option.enable_auto_exposure):
            sensor.set_option(rs.option.enable_auto_exposure, 1)
        if sensor.is_color_sensor():
            if sensor.supports(rs.option.enable_auto_exposure):
                sensor.set_option(rs.option.enable_auto_exposure, 1)
            if sensor.supports(rs.option.auto_exposure_priority):
                sensor.set_option(rs.option.auto_exposure_priority, 0)  # AE priority should be 0 for constant FPS

        streams = []
        resolutions = []
        for profile in sensor.get_stream_profiles():
            if profile.stream_type() not in streams:
                streams.append(profile.stream_type())

            if fps_helper.get_resolution(profile) not in resolutions:
                resolutions.append(fps_helper.get_resolution(profile))

        resolutions.sort(reverse=True)
        profiles = []

        for resolution in resolutions:
            for stream in streams:
                profile = fps_helper.get_profile(sensor,stream,resolution)
                if profile is None:
                    break
                profiles.append(profile)
            if len(profiles) == len(streams):
                break
            profiles = []


        # if not enough... break ?

        for profile in profiles:
            sensor_profiles_arr.append((sensor, profile))

    return sensor_profiles_arr


#####################################################################################################

dev = test.find_first_device_or_exit()
sensor_profiles_array = get_sensors_and_profiles(dev)

stream_names = [profiles.stream_name() for _, profiles in sensor_profiles_array]  # all stream names
permutations_to_run = list(itertools.combinations(stream_names, 2))  # every pair from the array above

fps_helper.perform_fps_test(sensor_profiles_array, permutations_to_run)
