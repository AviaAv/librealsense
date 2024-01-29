# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2023 Intel Corporation. All Rights Reserved.

# test:device each(D400*)
# test:timeout 300
# timeout - on the worst case, we're testing on D585S, which have 8 streams, so:
# timeout = ((8 choose 2)+1) * (TIME_FOR_STEADY_STATE + TIME_TO_COUNT_FRAMES)
# 8 choose 2 tests to do (one for each pair), plus one for all streams on

from rspy import test, log
import pyrealsense2 as rs
import time
import itertools
import math
import threading


# To add a new test mode (ex. all singles or triplets) only add it below and on should_test
# add it in get_time_est_string for an initial time calculation
# run perform_fps_test(sensor_profiles_array, [mode])
ALL_PERMUTATIONS = 1
ALL_PAIRS = 2
ALL_SENSORS = 3

# global variable used to count on all the sensors simultaneously
count_frames = False

# tests parameters
TEST_ALL_COMBINATIONS = False
TIME_FOR_STEADY_STATE = 3
TIME_TO_COUNT_FRAMES = 5


##########################################
# ---------- Helper Functions ---------- #
##########################################
def get_resolution(profile):
    return profile.as_video_stream_profile().width(), profile.as_video_stream_profile().height()


def check_fps_pair(measured_fps, expected_fps):
    delta_Hz = expected_fps * 0.05  # Validation KPI is 5%
    return (measured_fps <= (expected_fps + delta_Hz) and measured_fps >= (expected_fps - delta_Hz))


def get_expected_fps(sensor_profiles_dict):
    """
    For every sensor, find the expected fps according to its profiles
    Return a dictionary between the sensor and its expected fps
    """
    expected_fps_dict = {}
    # log.d(sensor_profiles_dict)
    for key in sensor_profiles_dict:
        avg = 0
        for profile in sensor_profiles_dict[key]:
            avg += profile.fps()

        avg /= len(sensor_profiles_dict[key])
        expected_fps_dict[key] = avg
    return expected_fps_dict


def should_test(mode, permutation):
    """
    Returns true if the given permutation should be tested:
    If the mode is ALL_PERMUTATIONS returns true (every permutation should be tested)
    If the mode is ALL_SENSORS return true only if all streams are to be tested
    If the mode is ALL_PAIRS return true only if there are exactly two streams to be tested
    """
    return ((mode == ALL_PERMUTATIONS) or
            (mode == ALL_SENSORS and all(v == 1 for v in permutation)) or
            (mode == ALL_PAIRS and permutation.count(1) == 2))


def get_dict_for_permutation(sensor_profiles_arr, permutation):
    """
    Given an array of pairs (sensor, profile) and a permutation of the same length,
    return a sensor-profiles dictionary containing the relevant profiles
     - profile will be added only if there's 1 in the corresponding element in the permutation
    """
    partial_dict = {}
    for i, j in enumerate(permutation):
        if j == 1:
            sensor = sensor_profiles_arr[i][0]
            partial_dict[sensor] = partial_dict.get(sensor, []) + [sensor_profiles_arr[i][1]]
    return partial_dict


def get_time_est_string(num_profiles, modes):
    s = "Estimated time for test:"
    details_str = ""
    total_time = 0
    global TIME_TO_COUNT_FRAMES
    global TIME_FOR_STEADY_STATE
    time_per_test = TIME_TO_COUNT_FRAMES + TIME_FOR_STEADY_STATE
    for mode in modes:
        test_time = 0
        if mode == ALL_PERMUTATIONS:
            test_time = math.factorial(num_profiles) * time_per_test
            details_str += f"{math.factorial(num_profiles)} tests for all permutations"
        elif mode == ALL_PAIRS:
            test_time = math.comb(num_profiles, 2) * time_per_test
            details_str += f"{math.comb(num_profiles,2)} tests for all pairs"
        elif mode == ALL_SENSORS:
            test_time = time_per_test
            details_str += f"1 test for all sensors on"

        details_str += " + "
        total_time += test_time

    # Remove the last " + " for aesthetics
    details_str = details_str[:-3]
    details_str = f"({details_str})"
    details_str += f" * {time_per_test} secs per test"
    s = f"{s} {total_time} secs ({details_str})"
    return s


def get_tested_profiles_string(sensor_profiles_dict):
    s = ""
    for sensor in sensor_profiles_dict:
        for profile in sensor_profiles_dict[sensor]:
            s += sensor.name + " / " + profile.stream_name() + " + "

    # Remove the last " + " for aesthetics
    s = s[:-3]
    return s


#############################################
# ---------- Core Test Functions ---------- #
#############################################
def check_fps_dict(measured_fps, expected_fps):
    all_fps_ok = True
    for key in expected_fps:
        res = check_fps_pair(measured_fps[key], expected_fps[key])
        if not res:
            all_fps_ok = False
        log.e(f"Expected {expected_fps[key]} fps, received {measured_fps[key]} fps in sensor {key.name}"
              f" { '(Pass)' if res else '(Fail)' }")
    return all_fps_ok


def generate_functions(sensor_profiles_dict):
    """
    Creates callable functions for each sensor to be triggered when a new frame arrives
    Used to count frames received for measuring fps
    """
    locks = {}
    sensor_function_dict = {}
    for sensor_key in sensor_profiles_dict:
        new_lock = threading.Lock()
        locks[sensor_key] = new_lock

        def on_frame_received(frame, key=sensor_key):
            global count_frames
            if count_frames:
                with locks[key]:
                    sensor_profiles_dict[key] += 1

        sensor_function_dict[sensor_key] = on_frame_received
    return sensor_function_dict


def measure_fps(sensor_profiles_dict):
    """
    Given a dictionary of sensors and profiles to test, activate all sensors on the given profiles
    and measure fps
    Return a dictionary of sensors and the fps measured for them
    """
    global TIME_FOR_STEADY_STATE
    global TIME_TO_COUNT_FRAMES

    global count_frames
    count_frames = False

    # initialize fps dict
    sensor_fps_dict = {}
    for key in sensor_profiles_dict:
        sensor_fps_dict[key] = 0

    # generate sensor-callable dictionary
    funcs_dict = generate_functions(sensor_fps_dict)

    for sensor, profiles in sensor_profiles_dict.items():
        sensor.open(profiles)
        sensor.start(funcs_dict[sensor])

    # the core of the test - frames are counted during sleep when count_frames is on
    time.sleep(TIME_FOR_STEADY_STATE)
    count_frames = True  # Start counting frames
    time.sleep(TIME_TO_COUNT_FRAMES)
    count_frames = False  # Stop counting

    for sensor, profiles in sensor_profiles_dict.items():
        sensor_fps_dict[sensor] /= len(profiles)  # number of profiles on the sensor
        sensor_fps_dict[sensor] /= TIME_TO_COUNT_FRAMES
        # now for each sensor we have the average fps received

        sensor.stop()
        sensor.close()

    return sensor_fps_dict


def get_test_details_str(sensor_profile_dict, expected_fps_dict):
    s = ""
    for sensor_key in sensor_profile_dict:
        if len(sensor_profile_dict[sensor_key]) > 1:
            s += f"Expected average fps for {sensor_key.name} is {expected_fps_dict[sensor_key]}:\n"
            for profile in sensor_profile_dict[sensor_key]:
                s += f"Profile {profile.stream_name()} expects {profile.fps()} fps on {get_resolution(profile)}\n"
        else:
            s += (f"Expected fps for sensor {sensor_key.name} on profile "
                  f"{sensor_profile_dict[sensor_key][0].stream_name()} is {expected_fps_dict[sensor_key]}"
                  f" on {get_resolution(sensor_profile_dict[sensor_key][0])}\n")
    s = s.replace("on (0, 0)", "")  # remove no resolution for Motion Module profiles
    return s


def perform_fps_test(sensor_profiles_arr, modes):

    log.d(get_time_est_string(len(sensor_profiles_arr), modes))

    for mode in modes:
        # Generate a list of all possible combinations of 1s and 0s (permutations) in the length of the array
        perms = list(itertools.product([0, 1], repeat=len(sensor_profiles_arr)))

        # Go over every possible permutation and check if we should test it
        # Each index in a permutation represents a profile, which will be tested only if the value in that index is 1
        for perm in perms:
            # log.d(perm)
            if all(v == 0 for v in perm):
                continue
            if should_test(mode, perm):
                partial_dict = get_dict_for_permutation(sensor_profiles_arr, perm)
                test.start("Testing", get_tested_profiles_string(partial_dict))
                expected_fps = get_expected_fps(partial_dict)
                log.d(get_test_details_str(partial_dict, expected_fps))
                fps_dict = measure_fps(partial_dict)
                test.check(check_fps_dict(fps_dict, expected_fps))
                test.finish()


####################################################
# ---------- Test Preparation Functions ---------- #
####################################################
def get_profiles_by_resolution(sensor, resolution, fps=None):
    # resolution is a required parameter because on a sensor all active profiles must have the same resolution
    profiles = []
    stream_types_added = []
    for p in sensor.get_stream_profiles():
        if get_resolution(p) == resolution:
            if fps is None or p.fps() == fps:
                # to avoid having a long run time, we don't choose the same stream more than once
                if p.stream_type() not in stream_types_added:
                    profiles.append(p)
                    stream_types_added.append(p.stream_type())
    return profiles


def get_mutual_resolution(sensor):
    stream_resolutions_dict = {}  # a map between a stream type and all of its possible resolutions
    possible_combinations = []
    for profile in sensor.get_stream_profiles():
        stream_type = profile.stream_type()
        resolution = get_resolution(profile)
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

    # if none found, try to find a resolution that all profiles have, on any fps (fps will be taken as an average later)
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

        profiles = get_mutual_resolution(sensor)
        for profile in profiles:
            sensor_profiles_arr.append((sensor, profile))

    return sensor_profiles_arr


#####################################################################################################

dev = test.find_first_device_or_exit()
sensor_profiles_array = get_sensors_and_profiles(dev)

if TEST_ALL_COMBINATIONS:
    test_modes = [ALL_PERMUTATIONS]
else:
    test_modes = [ALL_SENSORS]

perform_fps_test(sensor_profiles_array, test_modes)

#####################################################################################################

test.print_results_and_exit()
