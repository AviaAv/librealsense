cmake_minimum_required(VERSION 3.5)
project(rosbag2_storage_default_plugins)

# # Default to C99
# if(NOT CMAKE_C_STANDARD)
#   set(CMAKE_C_STANDARD 99)
# endif()
# 
# # Default to C++14
# if(NOT CMAKE_CXX_STANDARD)
#   set(CMAKE_CXX_STANDARD 14)
# endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

if(WIN32)
  add_definitions(-DNOMINMAX)
endif()

# find_package(rosbag2_storage QUIET)
# find_package(rcpputils QUIET)
# find_package(pluginlib QUIET)


add_library(${PROJECT_NAME} SHARED
  src/rosbag2_storage_default_plugins/sqlite/sqlite_wrapper.cpp
  src/rosbag2_storage_default_plugins/sqlite/sqlite_storage.cpp
  src/rosbag2_storage_default_plugins/sqlite/sqlite_statement_wrapper.cpp)

target_link_libraries(${PROJECT_NAME} PUBLIC SQLite::SQLite3)

set(_deps rosbag2_storage rcpputils rcutils pluginlib)
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

target_include_directories(${PROJECT_NAME}
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Causes the visibility macros to use dllexport rather than dllimport
 target_compile_definitions(${PROJECT_NAME} PRIVATE ROSBAG2_STORAGE_DEFAULT_PLUGINS_BUILDING_DLL)

# # Install plugin description (replacement for pluginlib export macro)
# install(FILES plugin_description.xml DESTINATION share/${PROJECT_NAME})
# 
# include(GNUInstallDirs)
# install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
# install(TARGETS ${PROJECT_NAME}
#   EXPORT ${PROJECT_NAME}Targets
#   ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
#   LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
#   RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
# 
# install(EXPORT ${PROJECT_NAME}Targets
#   FILE ${PROJECT_NAME}Targets.cmake
#   NAMESPACE ${PROJECT_NAME}::
#   DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME})
# 
# file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake "include(\"\${CMAKE_CURRENT_LIST_DIR}/${PROJECT_NAME}Targets.cmake\")")
# install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME})


include(config.cmake)
