cmake_minimum_required(VERSION 3.5)
project(rosbag2_storage)

if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()
if(WIN32)
  add_definitions(-DNOMINMAX)
endif()

find_package(pluginlib QUIET)
find_package(rcpputils QUIET)
find_package(rcutils QUIET)
find_package(yaml_cpp_vendor QUIET)

add_library(${PROJECT_NAME} SHARED
  src/rosbag2_storage/default_storage_id.cpp
  src/rosbag2_storage/metadata_io.cpp
  src/rosbag2_storage/ros_helper.cpp
  src/rosbag2_storage/storage_factory.cpp
  src/rosbag2_storage/storage_options.cpp
  src/rosbag2_storage/base_io_interface.cpp)

target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>)

set(_deps pluginlib rcpputils rcutils yaml_cpp_vendor)
foreach(d IN LISTS _deps)
  if(TARGET ${d})
    list(APPEND _resolved ${d})
  endif()
endforeach()
if(_resolved)
  target_link_libraries(${PROJECT_NAME} PUBLIC ${_resolved})
endif()

target_compile_definitions(${PROJECT_NAME} PRIVATE "ROSBAG2_STORAGE_BUILDING_DLL")

install(DIRECTORY include/ DESTINATION include/${PROJECT_NAME})
install(TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)
install(EXPORT export_${PROJECT_NAME}
  FILE ${PROJECT_NAME}Targets.cmake
  NAMESPACE ${PROJECT_NAME}::
  DESTINATION lib/cmake/${PROJECT_NAME})

# Tests removed
