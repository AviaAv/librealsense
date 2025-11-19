cmake_minimum_required(VERSION 3.5)
project(rosbag2_compression)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(rcpputils QUIET)
find_package(rcutils QUIET)
find_package(rosbag2_storage QUIET)

# Build zstd compression library
add_library(${PROJECT_NAME}_zstd
  SHARED
  src/rosbag2_compression/zstd_compressor.cpp
  src/rosbag2_compression/zstd_decompressor.cpp)

target_include_directories(${PROJECT_NAME}_zstd
  PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

target_link_libraries(${PROJECT_NAME}_zstd
  PUBLIC
    rosbag2_storage
    rosbag2_cpp
  PRIVATE
    rcpputils
    rcutils
    libzstd_shared)

target_compile_definitions(${PROJECT_NAME}_zstd
  PRIVATE
    ROSBAG2_COMPRESSION_BUILDING_DLL)

# Build main compression library
add_library(${PROJECT_NAME}
  SHARED
  src/rosbag2_compression/compression_factory.cpp
  src/rosbag2_compression/compression_options.cpp
  src/rosbag2_compression/sequential_compression_reader.cpp
  src/rosbag2_compression/sequential_compression_writer.cpp)

target_include_directories(${PROJECT_NAME}
  PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

target_link_libraries(${PROJECT_NAME}
  PUBLIC
    ${PROJECT_NAME}_zstd
    rosbag2_storage
  PRIVATE
    rcpputils
    rcutils
    libzstd_shared
    )

target_compile_definitions(${PROJECT_NAME}
  PRIVATE
    ROSBAG2_COMPRESSION_BUILDING_DLL)

# # Installation
# install(
#   DIRECTORY include/
#   DESTINATION include)
# 
# install(
#   TARGETS ${PROJECT_NAME} ${PROJECT_NAME}_zstd
#   EXPORT ${PROJECT_NAME}Targets
#   ARCHIVE DESTINATION lib
#   LIBRARY DESTINATION lib
#   RUNTIME DESTINATION bin)
# 
# # Export targets for find_package
# install(EXPORT ${PROJECT_NAME}Targets
#   FILE ${PROJECT_NAME}Targets.cmake
#   NAMESPACE ${PROJECT_NAME}::
#   DESTINATION lib/cmake/${PROJECT_NAME})
# 
# # Create package config file
# include(CMakePackageConfigHelpers)
# configure_package_config_file(
#   ${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   INSTALL_DESTINATION lib/cmake/${PROJECT_NAME})
# 
# install(FILES
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   DESTINATION lib/cmake/${PROJECT_NAME})
# 