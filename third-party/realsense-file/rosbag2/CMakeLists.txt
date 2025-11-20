cmake_minimum_required(VERSION 3.10)
project(rosbag2_independent)

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
    GIT_TAG a83cd31548b19d50f3f983b069dceb4f4d50756d  # need any commit/tag after tag 0.8.0 - we need YAML_CPP_DISABLE_UNINSTALL flag
)
# Disable yaml-cpp's uninstall target
set(YAML_CPP_DISABLE_UNINSTALL ON CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(yaml-cpp)

# Force SQLite to export all symbols on Windows so the .lib is generated
# There's probably a better way to do it but it works for now - either have the folder on the repo, or pass the flag
# if there's no better way, we can and should restore the old flag
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

FetchContent_Declare(
    sqlite3
    GIT_REPOSITORY https://github.com/sjinks/sqlite3-cmake
    GIT_TAG v3.49.1
)
FetchContent_MakeAvailable(sqlite3)

# Reset it so it doesn't affect other libraries
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS OFF)

# -- zstd --
file(GLOB_RECURSE ZSTD_SOURCES
    "${CMAKE_CURRENT_LIST_DIR}/zstd/zstd.c"
)

file(GLOB_RECURSE ZSTD_HEADERS
    "${CMAKE_CURRENT_LIST_DIR}/zstd/*.h"
)


include(tinyxml2/config.cmake)

#add_library(tinyxml2 STATIC tinyxml2/tinyxml2.cpp)
#target_include_directories(tinyxml2 PUBLIC tinyxml2)

set(CLASS_LOADER_IGNORE_AMENT TRUE CACHE BOOL "Do not use ament" FORCE) # for class_loader

# Add subdirectories (adjust pluginlib path to nested folder)
include(rcutils/config.cmake)
include(pluginlib/config.cmake)
include(rcpputils/config.cmake)
include(rosbag2_storage/config.cmake)
include(rosbag2_storage_default_plugins/config.cmake)
include(rosbag2_cpp/config.cmake)
include(rosbag2_compression/config.cmake)
include(console_bridge/config.cmake)
include(class_loader/config.cmake)
include(ament_index_cpp/config.cmake)

include(config.cmake) # sets variables with values for header/source files and dirs

message(STATUS "ROSBAG2_COMPILE_FLAGS (INTERNAL): ${ROSBAG2_COMPILE_FLAGS}")
set(ROSBAG2_COMPILE_FLAGS "${ROSBAG2_COMPILE_FLAGS}" PARENT_SCOPE) # PARENT_SCOPE to propagate to parent cmake files