cmake_minimum_required(VERSION 3.5)

project(rcpputils)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_ros REQUIRED)
find_package(rcutils REQUIRED)

# Default to C11
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 11)
endif()
# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(NOT WIN32)
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

include_directories(include)

ament_export_include_directories(include)

add_library(${PROJECT_NAME}
  src/asserts.cpp
  src/find_library.cpp
  src/shared_library.cpp)
target_include_directories(${PROJECT_NAME} PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>")
if(WIN32)
  target_compile_definitions(${PROJECT_NAME}
    PRIVATE "RCPPUTILS_BUILDING_LIBRARY")
endif()
ament_target_dependencies(${PROJECT_NAME} rcutils)
ament_export_libraries(${PROJECT_NAME})
ament_export_targets(${PROJECT_NAME})
ament_export_dependencies(rcutils)

ament_package()

install(
  DIRECTORY include/
  DESTINATION include)
install(
  TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
