cmake_minimum_required(VERSION 3.5)
project(sqlite3_vendor)

message(STATUS "SQLite3 not found (or force build enabled) - building vendor SQLite3 3.24.0")
set(extra_cmake_args)
if(DEFINED CMAKE_TOOLCHAIN_FILE)
list(APPEND extra_cmake_args "-DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}")
endif()
include(ExternalProject)
ExternalProject_Add(sqlite3-3.24.0
PREFIX sqlite3-3.24.0
URL https://www.sqlite.org/2018/sqlite-amalgamation-3240000.zip
URL_MD5 4ea1e0c6e7e82cb0490d4753d6878698
CMAKE_ARGS
    -DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/sqlite3_install
    ${extra_cmake_args}
INSTALL_DIR "${CMAKE_CURRENT_BINARY_DIR}/sqlite3_install"
PATCH_COMMAND
    ${CMAKE_COMMAND} -E copy "${CMAKE_CURRENT_SOURCE_DIR}/sqlite3_cmakelists.txt" <SOURCE_DIR>/CMakeLists.txt
)
# Stage install content into main install tree
install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/sqlite3_install/include/ DESTINATION include)
install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/sqlite3_install/lib/ DESTINATION lib)

install(DIRECTORY cmake DESTINATION share/${PROJECT_NAME})

# ament_package removed; pure CMake vendor package now.
