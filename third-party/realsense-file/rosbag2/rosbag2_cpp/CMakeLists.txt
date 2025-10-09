cmake_minimum_required(VERSION 3.5)
project(rosbag2_cpp)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

# Windows supplies macros for min and max by default. We should only use min and max from stl
if(WIN32)
  add_definitions(-DNOMINMAX)
endif()

option(DISABLE_SANITIZERS "disables the use of gcc sanitizers")
if(NOT DISABLE_SANITIZERS AND CMAKE_COMPILER_IS_GNUCXX)
  include(CheckCXXSourceRuns)
  set(OLD_CMAKE_REQUIRED_FLAGS ${CMAKE_REQUIRED_FLAGS})
  set(CMAKE_REQUIRED_FLAGS "${OLD_CMAKE_REQUIRED_FLAGS} -fsanitize=leak")
  check_cxx_source_runs("int main() {}" HAVE_SANITIZERS)
  set(CMAKE_REQUIRED_FLAGS ${OLD_CMAKE_REQUIRED_FLAGS})
  if(NOT HAVE_SANITIZERS)
    set(DISABLE_SANITIZERS ON)
    message(WARNING "Sanitizers aren't supported by the compiler or environment - disabling")
  endif()
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rcpputils REQUIRED)
find_package(rcutils REQUIRED)
find_package(rosbag2_storage REQUIRED)
find_package(rosidl_runtime_c REQUIRED)
find_package(rosidl_runtime_cpp REQUIRED)
find_package(rosidl_typesupport_cpp REQUIRED)
find_package(rosidl_typesupport_introspection_cpp REQUIRED)

add_library(${PROJECT_NAME} SHARED
  src/rosbag2_cpp/converter.cpp
  src/rosbag2_cpp/info.cpp
  src/rosbag2_cpp/reader.cpp
  src/rosbag2_cpp/readers/sequential_reader.cpp
  src/rosbag2_cpp/serialization_format_converter_factory.cpp
  src/rosbag2_cpp/types/introspection_message.cpp
  src/rosbag2_cpp/typesupport_helpers.cpp
  src/rosbag2_cpp/types/introspection_message.cpp
  src/rosbag2_cpp/writer.cpp
  src/rosbag2_cpp/writers/sequential_writer.cpp)

ament_target_dependencies(${PROJECT_NAME}
  ament_index_cpp
  pluginlib
  rcpputils
  rcutils
  rosbag2_storage
  rosidl_runtime_c
  rosidl_runtime_cpp
  rosidl_typesupport_cpp
  rosidl_typesupport_introspection_cpp
)

target_include_directories(${PROJECT_NAME}
  PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# Causes the visibility macros to use dllexport rather than dllimport,
# which is appropriate when building the dll but not consuming it.
target_compile_definitions(${PROJECT_NAME} PRIVATE "ROSBAG2_CPP_BUILDING_DLL")

# prevent pluginlib from using boost
target_compile_definitions(${PROJECT_NAME} PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")

install(
  DIRECTORY include/
  DESTINATION include)

install(
  TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)

ament_export_include_directories(include)
ament_export_libraries(${PROJECT_NAME})
ament_export_targets(export_${PROJECT_NAME})
ament_export_dependencies(pluginlib
  rosbag2_storage
  rosidl_runtime_c
  rosidl_runtime_cpp
  rosidl_typesupport_cpp
  rosidl_typesupport_introspection_cpp
)

ament_package()
