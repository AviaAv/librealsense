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

find_package(pluginlib QUIET)
find_package(rcpputils QUIET)
find_package(rcutils QUIET)
find_package(rosbag2_storage QUIET)
# find_package(rosidl_runtime_c QUIET)
# find_package(rosidl_runtime_cpp QUIET)
# find_package(rosidl_typesupport_cpp QUIET)
# find_package(rosidl_typesupport_introspection_cpp QUIET)

add_library(${PROJECT_NAME} SHARED
  src/rosbag2_cpp/converter.cpp
  src/rosbag2_cpp/info.cpp
  src/rosbag2_cpp/reader.cpp
  src/rosbag2_cpp/readers/sequential_reader.cpp
  src/rosbag2_cpp/serialization_format_converter_factory.cpp
  src/rosbag2_cpp/types/introspection_message.cpp
  src/rosbag2_cpp/typesupport_helpers.cpp
  src/rosbag2_cpp/writer.cpp
  src/rosbag2_cpp/writers/sequential_writer.cpp
)

# Link dependencies manually instead of ament_target_dependencies
target_link_libraries(${PROJECT_NAME}
  PUBLIC
    pluginlib
    rosbag2_storage
#   rosidl_runtime_c
#   rosidl_runtime_cpp
#   rosidl_typesupport_cpp
#   rosidl_typesupport_introspection_cpp
  PRIVATE
    rcpputils
    rcutils
)

target_include_directories(${PROJECT_NAME}
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Visibility and pluginlib defines
target_compile_definitions(${PROJECT_NAME}
  PRIVATE ROSBAG2_CPP_BUILDING_DLL
  PUBLIC PLUGINLIB__DISABLE_BOOST_FUNCTIONS
)

#target_include_directories(${PROJECT_NAME} PUBLIC
#    ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_runtime_c/include
#    ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_runtime_cpp/include
#    ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_cpp/include
#    ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_introspection_cpp/include
#    ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_introspection_c/include
#    ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_interface/include
#)

target_include_directories(${PROJECT_NAME} PUBLIC
   $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
   $<INSTALL_INTERFACE:include>

   $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_runtime_c/include>
   $<INSTALL_INTERFACE:include/rosidl_runtime_c>

   $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_runtime_cpp/include>
   $<INSTALL_INTERFACE:include/rosidl_runtime_cpp>

   $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_cpp/include>
   $<INSTALL_INTERFACE:include/rosidl_typesupport_cpp>

   $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_introspection_cpp/include>
   $<INSTALL_INTERFACE:include/rosidl_typesupport_introspection_cpp>

   $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_introspection_c/include>
   $<INSTALL_INTERFACE:include/rosidl_typesupport_introspection_c>

   $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_interface/include>
   $<INSTALL_INTERFACE:include/rosidl_typesupport_interface>
)

# Main install for your own headers
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/
        DESTINATION include)

# Vendored ROSIDL header install rules:
install(DIRECTORY ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_runtime_c/include/
        DESTINATION include/rosidl_runtime_c)

install(DIRECTORY ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_runtime_cpp/include/
        DESTINATION include/rosidl_runtime_cpp)

install(DIRECTORY ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_cpp/include/
        DESTINATION include/rosidl_typesupport_cpp)

install(DIRECTORY ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_introspection_cpp/include/
        DESTINATION include/rosidl_typesupport_introspection_cpp)

install(DIRECTORY ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_introspection_c/include/
        DESTINATION include/rosidl_typesupport_introspection_c)

install(DIRECTORY ${CMAKE_SOURCE_DIR}/third-party/realsense-file/rosbag2/rosidl_typesupport_interface/include/
        DESTINATION include/rosidl_typesupport_interface)



# # Installation rules
# install(
#   DIRECTORY include/
#   DESTINATION include
# )
# 
# install(
#   TARGETS ${PROJECT_NAME}
#   EXPORT ${PROJECT_NAME}Targets
#   ARCHIVE DESTINATION lib
#   LIBRARY DESTINATION lib
#   RUNTIME DESTINATION bin
# )
# 
# # Generate and install CMake config files for find_package()
# include(CMakePackageConfigHelpers)
# write_basic_package_version_file(
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
#   VERSION 1.0.0
#   COMPATIBILITY AnyNewerVersion
# )
# 
# configure_package_config_file(
#   ${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   INSTALL_DESTINATION lib/cmake/${PROJECT_NAME}
# )
# 
# install(FILES
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake
#   DESTINATION lib/cmake/${PROJECT_NAME}
# )
# 
# install(EXPORT ${PROJECT_NAME}Targets
#   NAMESPACE ${PROJECT_NAME}::
#   DESTINATION lib/cmake/${PROJECT_NAME}
# )
