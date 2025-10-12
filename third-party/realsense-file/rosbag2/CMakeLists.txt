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

# ---- FetchContent for direct library dependencies ----
include(FetchContent)

# yaml-cpp
FetchContent_Declare(
    yaml-cpp
    GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
    GIT_TAG master  # using master for latest version, we can also pick a specific commit but we need one after version 0.8.0 - we need YAML_CPP_DISABLE_UNINSTALL flag
)
# Disable yaml-cpp's uninstall target
set(YAML_CPP_DISABLE_UNINSTALL ON CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(yaml-cpp)

# sqlite3 with CMake support
FetchContent_Declare(
    sqlite3
    GIT_REPOSITORY https://github.com/sjinks/sqlite3-cmake
    GIT_TAG v3.49.1  # latest stable version
)
FetchContent_MakeAvailable(sqlite3)

add_library(tinyxml2 STATIC tinyxml2/tinyxml2.cpp)
target_include_directories(tinyxml2 PUBLIC tinyxml2)


# Add subdirectories (adjust pluginlib path to nested folder)
add_subdirectory(rcutils)
add_subdirectory(pluginlib)
add_subdirectory(rcpputils)
add_subdirectory(rosbag2_storage)
add_subdirectory(rosbag2_storage_default_plugins)

# ---- Create a single umbrella target ----
add_library(rosbag2_independent INTERFACE)

# Link everything under it
target_link_libraries(rosbag2_independent INTERFACE
    rcutils
    yaml-cpp::yaml-cpp        # Direct yaml-cpp target
    SQLite::SQLite3           # Direct sqlite3 target
    pluginlib
    tinyxml2
    rcpputils
    rosbag2_storage
    rosbag2_storage_default_plugins
)
