cmake_minimum_required(VERSION 3.5)
project(pluginlib)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(NOT WIN32)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(class_loader REQUIRED)
find_package(rcutils REQUIRED)
find_package(rcpputils REQUIRED)
find_package(tinyxml2_vendor REQUIRED)
find_package(TinyXML2 REQUIRED)  # provided by tinyxml2 upstream, or tinyxml2_vendor

add_library(${PROJECT_NAME} INTERFACE)
target_include_directories(${PROJECT_NAME} INTERFACE
  "$<INSTALL_INTERFACE:include>")
ament_target_dependencies(${PROJECT_NAME} INTERFACE
  ament_index_cpp class_loader rcutils rcpputils TinyXML2)
ament_export_dependencies(ament_index_cpp class_loader rcutils rcpputils tinyxml2_vendor TinyXML2)
ament_export_include_directories(include)
ament_export_targets(${PROJECT_NAME})

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND CMAKE_CXX_FLAGS MATCHES "-stdlib=libc\\+\\+")
  if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 7.0)
    # Before LLVM 7.0, filesystem is part of experimental
    set(FILESYSTEM_LIB c++experimental)
  elseif(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9.0)
    # Before LLVM 9.0 you have to manually link the fs library
    set(FILESYSTEM_LIB c++fs)
  else()
    # Starting at LLVM 9.0 filesystem is built in
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
  # this is needed to use the experimental/filesystem on Linux, but cannot be passed with
  # ament_export_libraries() because it is not absolute and cannot be found with find_library
  target_link_libraries(${PROJECT_NAME}
    INTERFACE ${FILESYSTEM_LIB})
endif()

install(
  TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}
)

install(
  DIRECTORY cmake
  DESTINATION share/${PROJECT_NAME}
)

install(
  DIRECTORY include/
  DESTINATION include
)

ament_package(
  CONFIG_EXTRAS "pluginlib-extras.cmake"
)
