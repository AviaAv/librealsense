cmake_minimum_required(VERSION 3.5)
project(pluginlib)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(NOT WIN32)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
endif()

# Find required packages
#find_package(class_loader REQUIRED)
#find_package(TinyXML2 REQUIRED)

# Create interface library
add_library(${PROJECT_NAME} INTERFACE)

target_include_directories(${PROJECT_NAME} INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

#target_link_libraries(${PROJECT_NAME} INTERFACE
#  class_loader::class_loader
#  tinyxml2::tinyxml2
#)

target_link_libraries(${PROJECT_NAME} INTERFACE tinyxml2)

# Filesystem library handling
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND CMAKE_CXX_FLAGS MATCHES "-stdlib=libc\\+\\+")
  if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 7.0)
    set(FILESYSTEM_LIB c++experimental)
  elseif(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9.0)
    set(FILESYSTEM_LIB c++fs)
  else()
    set(FILESYSTEM_LIB)
  endif()
elseif(CMAKE_CXX_COMPILER_ID MATCHES "QCC")
  if(CMAKE_CXX_FLAGS MATCHES "-stdlib=libstdc\\+\\+")
    set(FILESYSTEM_LIB stdc++fs)
  else()
    set(FILESYSTEM_LIB c++fs)
  endif()
else()
  set(FILESYSTEM_LIB stdc++fs)
endif()

if(UNIX AND NOT APPLE)
  target_link_libraries(${PROJECT_NAME} INTERFACE ${FILESYSTEM_LIB})
endif()

# # Installation
# install(TARGETS ${PROJECT_NAME}
#   EXPORT ${PROJECT_NAME}Targets
#   LIBRARY DESTINATION lib
#   ARCHIVE DESTINATION lib
#   RUNTIME DESTINATION bin
#   INCLUDES DESTINATION include
# )
# 
# install(DIRECTORY include/
#   DESTINATION include
# )
# 
# install(DIRECTORY cmake/
#   DESTINATION share/${PROJECT_NAME}/cmake
# )
# 
# # Export targets
# install(EXPORT ${PROJECT_NAME}Targets
#   FILE ${PROJECT_NAME}Targets.cmake
#   NAMESPACE ${PROJECT_NAME}::
#   DESTINATION lib/cmake/${PROJECT_NAME}
# )
# 
# Create config file
# include(CMakePackageConfigHelpers)
# configure_package_config_file(
#   ${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   INSTALL_DESTINATION lib/cmake/${PROJECT_NAME}
# )
# 
# install(FILES
#   ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   DESTINATION lib/cmake/${PROJECT_NAME}
# )