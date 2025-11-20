cmake_minimum_required(VERSION 3.5)
project(rosbag2_storage)
message(STATUS "Configuring rosbag2_storage standalone build yo doug this is T-Bone speaking!")
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

# # Removed ament; use plain find_package for dependencies (they must be available or optional)
# find_package(pluginlib QUIET)
# find_package(rcpputils QUIET)
# #find_package(rcutils REQUIRED) # local project

add_library(
  ${PROJECT_NAME}
  SHARED
  src/rosbag2_storage/metadata_io.cpp
  src/rosbag2_storage/ros_helper.cpp
  src/rosbag2_storage/storage_factory.cpp
  src/rosbag2_storage/base_io_interface.cpp)

target_include_directories(${PROJECT_NAME}
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(${PROJECT_NAME} PUBLIC yaml-cpp::yaml-cpp)

# Link dependencies similarly to ament_target_dependencies
set(_deps pluginlib rcpputils rcutils)
foreach(dep IN LISTS _deps)
  if(${dep}_INCLUDE_DIRS)
    target_include_directories(${PROJECT_NAME} PUBLIC ${${dep}_INCLUDE_DIRS})
  endif()
  if(${dep}_LIBRARIES)
    target_link_libraries(${PROJECT_NAME} PUBLIC ${${dep}_LIBRARIES})
  elseif(TARGET ${dep})
    target_link_libraries(${PROJECT_NAME} PUBLIC ${dep})
  endif()
endforeach()

# Causes the visibility macros to use dllexport rather than dllimport,
# which is appropriate when building the dll but not consuming it.
target_compile_definitions(${PROJECT_NAME} PRIVATE "ROSBAG2_STORAGE_BUILDING_DLL")

# prevent pluginlib from using boost
target_compile_definitions(${PROJECT_NAME} PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")

# Installation
include(GNUInstallDirs)
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(TARGETS ${PROJECT_NAME}
  EXPORT ${PROJECT_NAME}Targets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(DIRECTORY cmake DESTINATION share/${PROJECT_NAME})

# # Export targets
# install(EXPORT ${PROJECT_NAME}Targets
#   FILE ${PROJECT_NAME}Targets.cmake
#   NAMESPACE ${PROJECT_NAME}::
#   DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME})

# # Basic Config file (any extra macros formerly in ament_package omitted)
# include(CMakePackageConfigHelpers)
# configure_package_config_file(${CMAKE_CURRENT_LIST_DIR}/cmake/rosbag2_storage-config.cmake.in
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}
#   NO_SET_AND_CHECK_MACRO
#   NO_CHECK_REQUIRED_COMPONENTS_MACRO)
# install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME})

include(config.cmake)
