cmake_minimum_required(VERSION 3.10)
project(rosbag2_standalone)

# Allow consumers to opt-in explicitly; default OFF to avoid configuration failures
option(BUILD_ROSBAG2 "Build rosbag2 third-party components" OFF)
if(NOT BUILD_ROSBAG2)
    message(STATUS "rosbag2: BUILD_ROSBAG2=OFF - skipping build of rosbag2 third-party components")
    return()
endif()

# Prevent duplicate processing if this directory is added more than once
if(TARGET rcutils OR TARGET rosbag2_independent)
    message(STATUS "rosbag2: targets already defined - skipping duplicate inclusion")
    return()
endif()

set(CMAKE_CXX_STANDARD 14)

# Add subdirectories (adjust pluginlib path to nested folder)
add_subdirectory(rcutils)
add_subdirectory(yaml_cpp_vendor)
add_subdirectory(sqlite3_vendor)
add_subdirectory(pluginlib/pluginlib)
add_subdirectory(rcpputils)
add_subdirectory(rosbag2_storage)
add_subdirectory(rosbag2_storage_default_plugins)
add_subdirectory(rosbag2_cpp)

# ---- Create a single umbrella target ----
add_library(rosbag2_independent INTERFACE)

# Link everything under it
target_link_libraries(rosbag2_independent INTERFACE
    rcutils
    yaml_cpp_vendor
    sqlite3_vendor
    pluginlib
    rcpputils
    rosbag2_storage
    rosbag2_storage_default_plugins
    rosbag2_cpp
)
