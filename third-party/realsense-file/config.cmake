set(ROSBAG_DIR ${CMAKE_CURRENT_LIST_DIR}/rosbag)
set(LZ4_DIR ${CMAKE_CURRENT_LIST_DIR}/lz4)

set(LZ4_INCLUDE_PATH ${LZ4_DIR}/lib/)
include(${ROSBAG_DIR}/config.cmake)
add_subdirectory(${CMAKE_CURRENT_LIST_DIR}/rosbag2
                 ${CMAKE_CURRENT_BINARY_DIR}/rosbag2_build)
