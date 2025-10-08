cmake_minimum_required(VERSION 3.5)
project(rosbag2_storage_default_plugins)

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
find_package(rosbag2_storage QUIET)
find_package(sqlite3_vendor QUIET)
find_package(SQLite3 QUIET)
find_package(yaml_cpp_vendor QUIET)

add_library(${PROJECT_NAME} SHARED
  src/rosbag2_storage_default_plugins/sqlite/sqlite_wrapper.cpp
  src/rosbag2_storage_default_plugins/sqlite/sqlite_storage.cpp
  src/rosbag2_storage_default_plugins/sqlite/sqlite_statement_wrapper.cpp)

set(_deps pluginlib rosbag2_storage rcpputils rcutils SQLite3::SQLite3 yaml_cpp_vendor sqlite3_vendor)
foreach(d IN LISTS _deps)
  if(TARGET ${d})
    list(APPEND _resolved ${d})
  endif()
endforeach()
if(_resolved)
  target_link_libraries(${PROJECT_NAME} PUBLIC ${_resolved})
endif()

target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>)

target_compile_definitions(${PROJECT_NAME} PRIVATE ROSBAG2_STORAGE_DEFAULT_PLUGINS_BUILDING_DLL)

install(DIRECTORY include/ DESTINATION include/${PROJECT_NAME})
install(FILES plugin_description.xml DESTINATION share/${PROJECT_NAME})
install(TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)
install(EXPORT export_${PROJECT_NAME}
  FILE ${PROJECT_NAME}Targets.cmake
  NAMESPACE ${PROJECT_NAME}::
  DESTINATION lib/cmake/${PROJECT_NAME})
