cmake_minimum_required(VERSION 3.5)
project(rcpputils LANGUAGES C CXX)

# # Default to C11
# if(NOT CMAKE_C_STANDARD)
#   set(CMAKE_C_STANDARD 11)
# endif()
# # Default to C++14
# if(NOT CMAKE_CXX_STANDARD)
#   set(CMAKE_CXX_STANDARD 14)
# endif()
# 
# if(NOT WIN32)
#   add_compile_options(-Wall -Wextra -Wpedantic)
# endif()

# Remove ament_* usage; rely on plain CMake + in-tree rcutils
# find_package(rcutils REQUIRED) # provided locally # <----!

add_library(${PROJECT_NAME}
  src/asserts.cpp
  src/find_library.cpp
  src/shared_library.cpp)

# Public include dirs
set(_public_inc
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

target_include_directories(${PROJECT_NAME} PUBLIC ${_public_inc})

if(WIN32)
  target_compile_definitions(${PROJECT_NAME} PRIVATE RCPPUTILS_BUILDING_LIBRARY)
endif()

# Link rcutils if it's a target or via its libs variables
if(TARGET rcutils)
  target_link_libraries(${PROJECT_NAME} PUBLIC rcutils)
elseif(rcutils_LIBRARIES)
  target_link_libraries(${PROJECT_NAME} PUBLIC ${rcutils_LIBRARIES})
endif()
if(rcutils_INCLUDE_DIRS)
  target_include_directories(${PROJECT_NAME} PUBLIC ${rcutils_INCLUDE_DIRS})
endif()

# # Installation & export
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
# # Minimal Config file so find_package(rcpputils) works post-install
# file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake "include(\"\${CMAKE_CURRENT_LIST_DIR}/${PROJECT_NAME}Targets.cmake\")")
# install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake
#   DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME})

include(config.cmake)
