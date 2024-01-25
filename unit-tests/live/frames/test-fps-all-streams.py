# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2023 Intel Corporation. All Rights Reserved.

# test:device each(D400*)
# test:timeout 600
# timeout - on the worst case, we're testing on D585S, which have 8 streams, so:
# timeout = ((8 choose 2)+1) * (TIME_FOR_STEADY_STATE + TIME_TO_COUNT_FRAMES)
# 8 choose 2 tests to do (one for each pair), plus one for all streams on

from rspy import test, log
import pyrealsense2 as rs
import fps_helper


def get_mutual_resolution(sensor):
    stream_resolutions_dict = {}  # a map between a stream type and all of its possible resolutions
    possible_combinations = []
    for profile in sensor.get_stream_profiles():
        stream_type = profile.stream_type()
        resolution = fps_helper.get_resolution(profile)
        fps = profile.fps()

        # d[key] = d.get(key, []) + [value] -> adds to the dictionary or appends if it exists
        stream_resolutions_dict[stream_type] = stream_resolutions_dict.get(stream_type, []) + [resolution]

        if (resolution, fps) not in possible_combinations:
            possible_combinations.append((resolution, fps))

    possible_combinations.sort(reverse=True)  # sort by resolution first, then by fps, so the best res and fps are first

    # first, try to find a resolution and fps that all profiles have
    for option in possible_combinations:
        profiles = get_profiles_by_resolution(sensor, option[0], option[1])
        if len(profiles) == len(stream_resolutions_dict):
            return profiles

    # if none found, try to find a resolution that all profiles have, on any fps
    for option in possible_combinations:
        profiles = get_profiles_by_resolution(sensor, option[0], None)
        if len(profiles) == len(stream_resolutions_dict):
            return profiles
    # if reached here, then we couldn't find a resolution that all profiles have, so we can't test them together :(
    log.f("Can't run test, sensor", sensor.name, "doesn't have a resolution for all profiles")
    return []


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
        print(sensor, resolutions)
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

fps_helper.perform_fps_test(sensor_profiles_array,[fps_helper.Modes.ALL_STREAMS])

