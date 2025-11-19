cmake_minimum_required(VERSION 3.10)

set(HEADER_FILES_ROSBAG2_STORAGE
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/bag_metadata.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/logging.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/metadata_io.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/ros_helper.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/serialized_bag_message.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_factory.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_factory_interface.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_filter.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_traits.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/topic_metadata.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/visibility_control.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_options.hpp
 #   ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/yaml.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_interfaces/base_info_interface.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_interfaces/base_io_interface.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_interfaces/base_read_interface.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_interfaces/base_write_interface.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_interfaces/read_only_interface.hpp
    ${CMAKE_CURRENT_LIST_DIR}/include/rosbag2_storage/storage_interfaces/read_write_interface.hpp
)

set(SOURCE_FILES_ROSBAG2_STORAGE
    ${CMAKE_CURRENT_LIST_DIR}/src/rosbag2_storage/base_io_interface.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/rosbag2_storage/metadata_io.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/rosbag2_storage/ros_helper.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/rosbag2_storage/storage_factory.cpp
)

