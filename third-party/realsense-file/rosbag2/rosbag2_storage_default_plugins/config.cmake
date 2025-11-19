cmake_minimum_required(VERSION 3.10)

set(HEADER_FILES_ROSBAG2_STORAGE_DEFAULT_PLUGINS
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage_default_plugins/visibility_control.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage_default_plugins/sqlite/sqlite_exception.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage_default_plugins/sqlite/sqlite_statement_wrapper.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage_default_plugins/sqlite/sqlite_storage.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage_default_plugins/sqlite/sqlite_wrapper.hpp
)

set(SOURCE_FILES_ROSBAG2_STORAGE_DEFAULT_PLUGINS
    ${CMAKE_CURRENT_LIST_DIR}/src/rosbag2_storage_default_plugins/sqlite/sqlite_statement_wrapper.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/rosbag2_storage_default_plugins/sqlite/sqlite_storage.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/rosbag2_storage_default_plugins/sqlite/sqlite_wrapper.cpp
)

