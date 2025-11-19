cmake_minimum_required(VERSION 3.10)
project(rosbag2_independent)

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

# Force SQLite and libzstd to export all symbols on Windows so the .lib is generated
# There's probably a better way to do it but it works for now - either have the folder on the repo, or pass the flag
# if there's no better way, we can and should restore the old flag
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

FetchContent_Declare(
    sqlite3
    GIT_REPOSITORY https://github.com/sjinks/sqlite3-cmake
    GIT_TAG v3.49.1
)
FetchContent_MakeAvailable(sqlite3)

add_library(libzstd_shared SHARED zstd/zstd.c)
target_include_directories(libzstd_shared PUBLIC 
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/zstd>
    $<INSTALL_INTERFACE:include/zstd>
)


# Reset it so it doesn't affect other libraries
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS OFF)

add_subdirectory(tinyxml2)

#add_library(tinyxml2 STATIC tinyxml2/tinyxml2.cpp)
#target_include_directories(tinyxml2 PUBLIC tinyxml2)

set(CLASS_LOADER_IGNORE_AMENT TRUE CACHE BOOL "Do not use ament" FORCE) # for class_loader

# Add subdirectories (adjust pluginlib path to nested folder)
add_subdirectory(rcutils)
add_subdirectory(pluginlib)
add_subdirectory(rcpputils)
add_subdirectory(rosbag2_storage)
add_subdirectory(rosbag2_storage_default_plugins)
add_subdirectory(rosbag2_cpp)
add_subdirectory(rosbag2_compression)
add_subdirectory(console_bridge)
add_subdirectory(class_loader)
add_subdirectory(ament_index_cpp)


# ---- Create a single umbrella target ----
add_library(rosbag2_independent INTERFACE)

# Link everything under it
target_link_libraries(rosbag2_independent INTERFACE
    rcutils
    yaml-cpp::yaml-cpp        # Direct yaml-cpp target
    SQLite::SQLite3           # Direct sqlite3 target
    pluginlib
    tinyxml2
    libzstd_shared
    rcpputils
    rosbag2_storage
    rosbag2_storage_default_plugins
    rosbag2_compression
    rosbag2_cpp
    class_loader
    ament_index_cpp
)

include(config.cmake) # sets variables with values for header/source files and dirs

install(TARGETS 
    rosbag2_independent
    rcutils
    rosbag2_storage
    rosbag2_storage_default_plugins
    rosbag2_cpp
    rosbag2_compression
    rosbag2_compression_zstd
    class_loader
    ament_index_cpp
    pluginlib
    rcpputils
    tinyxml2
    libzstd_shared
    yaml-cpp
    SQLite3
    EXPORT realsense2Targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
