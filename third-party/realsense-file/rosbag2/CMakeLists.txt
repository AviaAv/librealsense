cmake_minimum_required(VERSION 3.10)
project(rosbag2_standalone)

set(CMAKE_CXX_STANDARD 14)

# Don't use find_package(ament_cmake)
# Instead, manually configure dependencies

# Build rcutils first
add_subdirectory(rcutils)

# Build yaml_cpp_vendor
add_subdirectory(yaml_cpp_vendor)

# Build sqlite3_vendor
add_subdirectory(sqlite3_vendor)

# Build pluginlib (may need modification)
add_subdirectory(pluginlib)

# Build rcpputils
add_subdirectory(rcpputils)

# Build rosbag2_storage
add_subdirectory(rosbag2_storage)

# Build storage plugins
add_subdirectory(rosbag2_storage_default_plugins)

# Build rosbag2_cpp (modified version)
add_subdirectory(rosbag2_cpp)
