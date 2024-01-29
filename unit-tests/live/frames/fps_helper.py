# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2023 Intel Corporation. All Rights Reserved.

from rspy import test, log
import time
import itertools
import math
from enum import Enum
from rspy.stopwatch import Stopwatch


class Modes(Enum):
    # To add a new test mode (ex. all singles or triplets) only add it below and on should_test
    # add it in get_time_est_string for an initial time calculation
    # run perform_fps_test(sensor_profiles_array, [mode])
    ALL_PERMUTATIONS = 1
    ALL_PAIRS = 2
    ALL_STREAMS = 3


# global variable used to count on all the sensors simultaneously
count_frames = False
# tests parameters
TIME_FOR_STEADY_STATE = 3
TIME_TO_COUNT_FRAMES = 5


##########################################
# ---------- Helper Functions ---------- #
##########################################
def check_fps_pair(measured_fps, expected_fps):
    delta_Hz = expected_fps * 0.05  # Validation KPI is 5%
    return (measured_fps <= (expected_fps + delta_Hz) and measured_fps >= (expected_fps - delta_Hz))


def get_expected_fps_dict(sensor_profiles_dict):
    """
    Returns a dictionary between each stream name and its expected fps
    """
    expected_fps_dict = {}
    for sensor, profiles in sensor_profiles_dict.items():
        for profile in profiles:
            expected_fps_dict[profile.stream_name()] = profile.fps()
    return expected_fps_dict


def should_test(mode, permutation, custom_perm):
    """
    Returns true if the given permutation should be tested:
    If the mode is ALL_PERMUTATIONS returns true (every permutation should be tested)
    If the mode is ALL_SENSORS return true only if all streams are to be tested
    If the mode is ALL_PAIRS return true only if there are exactly two streams to be tested
    """
    if custom_perm is not None:
        return permutation in custom_perm
    return ((mode == Modes.ALL_PERMUTATIONS) or
            (mode == Modes.ALL_STREAMS and all(v == 1 for v in permutation)) or
            (mode == Modes.ALL_PAIRS and permutation.count(1) == 2))


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


# To reduce required python version, we implement choose instead of using math.comb
def choose(n, k):
    return math.factorial(n)/(math.factorial(k) * math.factorial(n - k))


def get_time_est_string(num_profiles, modes):
    time_est_string = "Estimated time for test:"
    details_str = ""
    total_time = 0
    global TIME_TO_COUNT_FRAMES, TIME_FOR_STEADY_STATE
    time_per_test = TIME_TO_COUNT_FRAMES + TIME_FOR_STEADY_STATE
    for mode in modes:
        test_time = 0
        if mode == Modes.ALL_PERMUTATIONS:
            test_time = math.factorial(num_profiles) * time_per_test
            details_str += f"{math.factorial(num_profiles)} tests for all permutations"
        elif mode == Modes.ALL_PAIRS:
            test_time = choose(num_profiles, 2) * time_per_test
            details_str += f"{choose(num_profiles, 2)} tests for all pairs"
        elif mode == Modes.ALL_STREAMS:
            test_time = time_per_test
            details_str += f"1 test for all streams on"

        details_str += " + "
        total_time += test_time

    # Remove the last " + " for aesthetics
    details_str = details_str[:-3]
    details_str = f"({details_str})"
    details_str += f" * {time_per_test} secs per test"
    time_est_string = f"{time_est_string} {total_time} secs ({details_str})"
    return time_est_string


def get_tested_profiles_string(sensor_profiles_dict):
    tested_profile_string = ""
    for sensor, profiles in sensor_profiles_dict.items():
        for profile in profiles:
            tested_profile_string += f"{sensor.name} / {profile.stream_name()} + "

    # Remove the last " + " for aesthetics
    tested_profile_string = tested_profile_string[:-3]
    return tested_profile_string


#############################################
# ---------- Core Test Functions ---------- #
#############################################
def _check_fps_dict(measured_fps, expected_fps):
    all_fps_ok = True
    for profile_name in expected_fps:
        res = check_fps_pair(measured_fps[profile_name], expected_fps[profile_name])
        if not res:
            all_fps_ok = False
        log.d(f"Expected {expected_fps[profile_name]} fps, received {measured_fps[profile_name]} fps in profile"
              f" {profile_name}"
              f" { '(Pass)' if res else '(Fail)' }")
    return all_fps_ok

start_call_stopwatch = None
def generate_callbacks(sensor_profiles_dict, profile_name_fps_dict):
    """
    Creates callable functions for each sensor to be triggered when a new frame arrives
    Used to count frames received for measuring fps
    """
    sensor_function_dict = {}
    for sensor_key in sensor_profiles_dict:
        def on_frame_received(frame):  # variables declared on generate_functions should not be used here
            global count_frames
            global start_call_stopwatch
            if count_frames:
                profile_name = frame.profile.stream_name()
                log.i("frame arrived after {} on profile {}".format(start_call_stopwatch.get_elapsed(), profile_name))
                profile_name = frame.profile.stream_name()
                profile_name_fps_dict[profile_name] += 1

        sensor_function_dict[sensor_key] = on_frame_received
    return sensor_function_dict


def measure_fps(sensor_profiles_dict):
    """
    Given a dictionary of sensors and profiles to test, activate all streams on the given profiles
    and measure fps
    Return a dictionary of profiles and the fps measured for them
    """
    global TIME_FOR_STEADY_STATE, TIME_TO_COUNT_FRAMES

    global count_frames
    count_frames = False

    # initialize fps dict
    profile_name_fps_dict = {}
    for sensor, profiles in sensor_profiles_dict.items():
        for profile in profiles:
            profile_name_fps_dict[profile.stream_name()] = 0

    # generate sensor-callable dictionary
    funcs_dict = generate_callbacks(sensor_profiles_dict, profile_name_fps_dict)

    for sensor, profiles in sensor_profiles_dict.items():
        sensor.open(profiles)
        sensor.start(funcs_dict[sensor])

    # the core of the test - frames are counted during sleep when count_frames is on
    time.sleep(TIME_FOR_STEADY_STATE)
    global start_call_stopwatch
    start_call_stopwatch = Stopwatch()
    count_frames = True  # Start counting frames
    time.sleep(TIME_TO_COUNT_FRAMES)
    count_frames = False  # Stop counting

    for sensor, profiles in sensor_profiles_dict.items():
        for profile in profiles:
            profile_name_fps_dict[profile.stream_name()] /= TIME_TO_COUNT_FRAMES

        sensor.stop()
        sensor.close()

    return profile_name_fps_dict


def get_test_details_str(sensor_profile_dict):
    test_details_str = ""
    for sensor, profiles in sensor_profile_dict.items():
        for profile in profiles:
            test_details_str += (f"Expected fps for profile {profile.stream_name()} on sensor "
                                 f"{sensor.name} is {profile.fps()} "
                                 f"on {get_resolution(profile)}\n")

    test_details_str = test_details_str.replace("on (0, 0)", "")  # remove no resolution for Motion Module profiles
    return test_details_str


def run_test(sensor_profiles_arr, mode=None, custom_perm=None):
    # Generate a list of all possible combinations of 1s and 0s (permutations) in the length of the array
    perms = list(itertools.product([0, 1], repeat=len(sensor_profiles_arr)))

    # Go over every possible permutation and check if we should test it
    # Each index in a permutation represents a profile, which will be tested only if the value in that index is 1
    for perm in perms:
        if all(v == 0 for v in perm):
            continue
        if should_test(mode, perm, custom_perm):
            partial_dict = get_dict_for_permutation(sensor_profiles_arr, perm)
            with test.closure("Testing", get_tested_profiles_string(partial_dict)):
                expected_fps_dict = get_expected_fps_dict(partial_dict)
                log.d(get_test_details_str(partial_dict))
                fps_dict = measure_fps(partial_dict)
                test.check(_check_fps_dict(fps_dict, expected_fps_dict))
    test.print_results_and_exit()


############################################
# ----------- Public Functions ----------- #
############################################
def get_resolution(profile):
    return profile.as_video_stream_profile().width(), profile.as_video_stream_profile().height()


def perform_custom_fps_test(sensor_profiles_arr, custom_perm):
    """
    :param sensor_profiles_arr: an array of length N of tuples (sensor, profile) to test on
    :param custom_perm: an array of tuples of length N each with 1s and 0s, where each tuple represent an fps test to
    run - the i-th profile will run in that test only if there is 1 in the i-th cell in that tuple
    """
    run_test(sensor_profiles_arr, None, custom_perm)


def perform_fps_test(sensor_profiles_arr, modes):
    """
    :param sensor_profiles_arr: an array of length N of tuples (sensor, profile) to test on
    :param modes: one of the modes mentioned at the beginning of the file, used to indicate what combinations to run
    """
    log.d(get_time_est_string(len(sensor_profiles_arr), modes))
    for mode in modes:
        run_test(sensor_profiles_arr, mode, None)


def get_profile(sensor, stream, resolution=None, fps=None):
    return next((profile for profile in sensor.profiles if profile.stream_type() == stream
                and (resolution is None or get_resolution(profile) == resolution)
                and (fps is None or profile.fps() == fps)),
                None)  # return None if no profile found
