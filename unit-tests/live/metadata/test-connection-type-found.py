# License: Apache 2.0. See LICENSE file in root directory.
# Copyright(c) 2025 Intel Corporation. All Rights Reserved.


#test:device each(D400*)
#test:device each(D500*)


import pyrealsense2 as rs
from rspy import test


test.start("Testing connection type can be detected")

dev, _ = test.find_first_device_or_exit()

if test.check(dev.supports(rs.camera_info.connection_type)):
    connection_type = dev.get_info(rs.camera_info.connection_type)
    camera_name = dev.get_info(rs.camera_info.name)
    if test.check(connection_type):
        if 'D457' in camera_name:
            test.check(connection_type == "GMSL")
        elif 'D555' in camera_name:
            test.check(connection_type == "DDS")
        else:
            test.check(connection_type == "USB")

    import os
    # Create the file with "0" if it doesn't exist
    if not os.path.exists("foo.txt"):
        with open("foo.txt", "w") as f:
            f.write("0")

    with open("foo.txt", "r+") as file:
        content = file.read().strip()
        file.seek(0)

        if content == "0":
            test.fail()
            file.write("1")
        else:
            test.check(True, "succeeded on second run")
            file.write("0")

        file.truncate()
test.finish()
test.print_results_and_exit()
