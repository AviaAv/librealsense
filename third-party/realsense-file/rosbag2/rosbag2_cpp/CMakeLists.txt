cmake_minimum_required(VERSION 3.5)
project(rosbag2_cpp)

add_definitions(-D_SRC_REINDEX_DIR_PATH="${CMAKE_CURRENT_SOURCE_DIR}/test/rosbag2_cpp/reindex_test_bags")

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
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wthread-safety)
endif()

# Windows supplies macros for min and max by default. We should only use min and max from stl
if(WIN32)
  add_definitions(-DNOMINMAX)
endif()

option(DISABLE_SANITIZERS "disables the use of gcc sanitizers" ON)
if(NOT DISABLE_SANITIZERS AND CMAKE_COMPILER_IS_GNUCXX)
  include(CheckCXXSourceRuns)
  set(OLD_CMAKE_REQUIRED_FLAGS ${CMAKE_REQUIRED_FLAGS})
  set(CMAKE_REQUIRED_FLAGS "${OLD_CMAKE_REQUIRED_FLAGS} -fsanitize=address,leak,undefined")
  check_cxx_source_runs("int main() {}" HAVE_SANITIZERS)
  set(CMAKE_REQUIRED_FLAGS ${OLD_CMAKE_REQUIRED_FLAGS})
  if(NOT HAVE_SANITIZERS)
    set(DISABLE_SANITIZERS ON)
    message(WARNING "Sanitizers aren't supported by the compiler or environment - disabling")
  endif()
endif()

# Optional (quiet) discovery of ROS-related dependencies; build can continue without them
find_package(ament_index_cpp QUIET)
find_package(pluginlib QUIET)
find_package(rclcpp QUIET)
find_package(rcpputils QUIET)
find_package(rcutils QUIET)
find_package(rmw QUIET)
find_package(rmw_implementation QUIET)
find_package(rosbag2_storage QUIET)
find_package(rosidl_runtime_c QUIET)
find_package(rosidl_runtime_cpp QUIET)
find_package(rosidl_typesupport_cpp QUIET)
find_package(rosidl_typesupport_introspection_cpp QUIET)

add_library(${PROJECT_NAME} SHARED
  src/rosbag2_cpp/cache/cache_consumer.cpp
  src/rosbag2_cpp/cache/message_cache_buffer.cpp
  src/rosbag2_cpp/cache/message_cache_circular_buffer.cpp
  src/rosbag2_cpp/cache/message_cache.cpp
  src/rosbag2_cpp/cache/circular_message_cache.cpp
  src/rosbag2_cpp/clocks/time_controller_clock.cpp
  src/rosbag2_cpp/converter.cpp
  src/rosbag2_cpp/info.cpp
  src/rosbag2_cpp/reader.cpp
  src/rosbag2_cpp/readers/sequential_reader.cpp
  src/rosbag2_cpp/rmw_implemented_serialization_format_converter.cpp
  src/rosbag2_cpp/serialization_format_converter_factory.cpp
  src/rosbag2_cpp/types/introspection_message.cpp
  src/rosbag2_cpp/typesupport_helpers.cpp
  src/rosbag2_cpp/types/introspection_message.cpp
  src/rosbag2_cpp/writer.cpp
  src/rosbag2_cpp/writers/sequential_writer.cpp
  src/rosbag2_cpp/reindexer.cpp)

# Collect targets discovered above for linking
set(_maybe_deps
  ament_index_cpp::ament_index_cpp
  pluginlib
  rclcpp::rclcpp
  rcpputils
  rcutils
  rmw::rmw
  rosbag2_storage
  rosidl_runtime_c::rosidl_runtime_c
  rosidl_runtime_cpp::rosidl_runtime_cpp
  rosidl_typesupport_cpp::rosidl_typesupport_cpp
  rosidl_typesupport_introspection_cpp::rosidl_typesupport_introspection_cpp
)
foreach(d IN LISTS _maybe_deps)
  if(TARGET ${d})
    list(APPEND _resolved_deps ${d})
  endif()
endforeach()
if(_resolved_deps)
  target_link_libraries(${PROJECT_NAME} PUBLIC ${_resolved_deps})
endif()

target_include_directories(${PROJECT_NAME}
  PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
)

# Causes the visibility macros to use dllexport rather than dllimport,
# which is appropriate when building the dll but not consuming it.
target_compile_definitions(${PROJECT_NAME} PRIVATE "ROSBAG2_CPP_BUILDING_DLL")

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

# Tests removed (ament based)
