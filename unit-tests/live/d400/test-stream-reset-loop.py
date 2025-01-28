# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2023 Intel Corporation. All Rights Reserved.

# test:device each(D400*) 
# test:timeout 6000

import pyrealsense2 as rs
from rspy.stopwatch import Stopwatch
from rspy import test, log
import time

import os
print("my pid is ", os.getpid())
rs.log_to_console(rs.log_severity.warn)
#rs.log_to_file(rs.log_severity.warn, "my_warn_log.log")

def cb(f):
    if f.is_frameset():
        #print(f)
        pass

import os
import ctypes

# Define constants for Windows API
PROCESS_ALL_ACCESS = 0x1F0FFF
SET_PROCESS_AFFINITY_MASK = 0x00000008

# Get the current process ID
pid = os.getpid()

# Open the current process
process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

# Set the CPU affinity to the first two cores (0 and 1)
# The mask 0b00000011 means use CPU 0 and CPU 1
ctypes.windll.kernel32.SetProcessAffinityMask(process_handle, 0b00000011)
# loop and hw reset loop test
################################################################################################
test.start("Testing stream and hw reset loop")
max_iteration = 500
for i in range(max_iteration):
    log.out("starting iteration #", i + 1, "/", max_iteration)
    pipe = rs.pipeline()
    #print("STARTING PIPE")
    pp = pipe.start(cb)
    dev = pp.get_device()
    time.sleep(3)
    #print("STOPPING PIPE")
    pipe.stop()

    if i % 10 == 0:
        print("perform HW reset")
        dev.hardware_reset()
        time.sleep(1) # sleep to make sure the device is removed
        # del dev
        # del pp
        # time.sleep(0.5)
        # del dev
        # del pipe
        # print("working after a HW reset")
    # time.sleep(1)

test.finish()

################################################################################################
test.print_results_and_exit()
