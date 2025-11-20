cmake_minimum_required(VERSION 3.5)
project(ament_index_cpp)

# # Default to C++14
# if(NOT CMAKE_CXX_STANDARD)
#   set(CMAKE_CXX_STANDARD 14)
# endif()
# 
# if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
#   add_compile_options(-std=c++14 -Wall -Wextra -Wpedantic)
# endif()
include(config.cmake)
return()
add_library(${PROJECT_NAME}
  src/get_package_prefix.cpp
  src/get_package_share_directory.cpp
  src/get_packages_with_prefixes.cpp
  src/get_resource.cpp
  src/get_resources.cpp
  src/get_search_paths.cpp
  src/has_resource.cpp
)

target_compile_definitions(${PROJECT_NAME} PRIVATE "AMENT_INDEX_CPP_BUILDING_DLL")

target_include_directories(${PROJECT_NAME} PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>")

install(DIRECTORY include/
  DESTINATION include)

install(TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)

install(EXPORT export_${PROJECT_NAME}
  DESTINATION lib/cmake/${PROJECT_NAME}
  NAMESPACE ${PROJECT_NAME}::
  FILE ${PROJECT_NAME}Targets.cmake)
