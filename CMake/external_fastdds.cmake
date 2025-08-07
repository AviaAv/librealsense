cmake_minimum_required(VERSION 3.16.3)  # same as in FastDDS (U20)
include(FetchContent)

# We use a function to enforce a scoped variables creation only for FastDDS build (i.e turn off BUILD_SHARED_LIBS which is used on LRS build as well)
function(get_fastdds)

    # Mark new options from FetchContent as advanced options
    mark_as_advanced(FETCHCONTENT_QUIET)
    mark_as_advanced(FETCHCONTENT_BASE_DIR)
    mark_as_advanced(FETCHCONTENT_FULLY_DISCONNECTED)
    mark_as_advanced(FETCHCONTENT_UPDATES_DISCONNECTED)

    message(CHECK_START  "Fetching fastdds... WE HAVE STARTED TO FETCH FAST DDS")
    list(APPEND CMAKE_MESSAGE_INDENT "  ")  # Indent outputs

    FetchContent_Declare(
      fastdds
      GIT_REPOSITORY https://github.com/eProsima/Fast-DDS.git
      # 2.10.x is eProsima's last LTS version that still supports U20
      # 2.10.4 has specific modifications based on support provided, but it has some incompatibility
      # with the way we clone (which works with v2.11+), so they made a fix and tagged it for us:
      # Once they have 2.10.5 we should move to it
      GIT_TAG        v2.10.4-realsense
      GIT_SUBMODULES ""     # Submodules will be cloned as part of the FastDDS cmake configure stage
      GIT_SHALLOW ON        # No history needed
      SOURCE_DIR ${CMAKE_BINARY_DIR}/third-party/fastdds
      EXCLUDE_FROM_ALL 
    )

    # Set FastDDS internal variables
    # We use cached variables so the default parameter inside the sub directory will not override the required values
    # We add "FORCE" so that is a previous cached value is set our assignment will override it.
    set(THIRDPARTY_Asio FORCE CACHE INTERNAL "" FORCE)
    set(THIRDPARTY_fastcdr FORCE CACHE INTERNAL "" FORCE)
    set(THIRDPARTY_TinyXML2 FORCE CACHE INTERNAL "" FORCE)
    set(COMPILE_TOOLS OFF CACHE INTERNAL "" FORCE)
    set(BUILD_TESTING OFF CACHE INTERNAL "" FORCE)
    set(SQLITE3_SUPPORT OFF CACHE INTERNAL "" FORCE)
    #set(ENABLE_OLD_LOG_MACROS OFF CACHE INTERNAL "" FORCE)  doesn't work
    set(FASTDDS_STATISTICS OFF CACHE INTERNAL "" FORCE)
    # Enforce NO_TLS to disable SSL: if OpenSSL is found, it will be linked to, and we don't want it!
    set(NO_TLS ON CACHE INTERNAL "" FORCE)

    # Set special values for FastDDS sub directory
    set(BUILD_SHARED_LIBS OFF)
    set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/fastdds/fastdds_install) 
    set(CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR}/fastdds/fastdds_install)  

    # Get fastdds
    FetchContent_MakeAvailable(fastdds)
    
    # point these at wherever your .a files actually live:
set_target_properties(fastcdr PROPERTIES
  IMPORTED_LOCATION
    "${CMAKE_BINARY_DIR}/third-party/fastdds/fastcdr/libfastcdr.a"
)

set_target_properties(fastrtps PROPERTIES
  IMPORTED_LOCATION
    "${CMAKE_BINARY_DIR}/third-party/fastdds/fastrtps/libfastrtps.a"
)
    
    message(INFO  "Fetching fastdds... WE HAVE STARTED TO FETCH FAST DDS")
    # Mark new options from FetchContent as advanced options
    mark_as_advanced(FETCHCONTENT_SOURCE_DIR_FASTDDS)
    mark_as_advanced(FETCHCONTENT_UPDATES_DISCONNECTED_FASTDDS)

    # place FastDDS project with other 3rd-party projects
    set_target_properties(fastcdr fastrtps foonathan_memory PROPERTIES
                          FOLDER "3rd Party/fastdds")

    list(POP_BACK CMAKE_MESSAGE_INDENT) # Unindent outputs

    # Create an interface target that will contain everything needed
    add_library(dds INTERFACE)
    add_dependencies(dds fastcdr fastrtps)

    # Include paths from FastDDS targets
    target_include_directories(dds INTERFACE 
        $<TARGET_PROPERTY:fastcdr,INTERFACE_INCLUDE_DIRECTORIES>
        $<TARGET_PROPERTY:fastrtps,INTERFACE_INCLUDE_DIRECTORIES>
    )
    
    # Link against the static libraries directly using their paths
    if (CMAKE_BUILD_TYPE)
        message(STATUS "CMAKE_BUILD_TYPE is set to ${CMAKE_BUILD_TYPE}")
        if (WIN32)
            target_link_libraries(dds INTERFACE 
                "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/fastcdr.lib"
                "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/fastrtps.lib"
            )
        else()
            target_link_libraries(dds INTERFACE 
                "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/libfastcdr.a"
                "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/libfastrtps.a"
            )
        endif()
    else()
        target_link_libraries(dds INTERFACE fastcdr fastrtps)
    endif()

    message(INFO "libs are at ${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/libfastcdr.lib 
    and ${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/libfastrtps.lib")
    
    # Add any compile definitions needed
    target_compile_definitions(dds INTERFACE BUILD_WITH_DDS)
    
    disable_third_party_warnings(fastcdr)  
    disable_third_party_warnings(fastrtps)  

    add_definitions(-DBUILD_WITH_DDS)
#install(TARGETS fastrtps EXPORT realsense2Targets) # this breaks, but gives a different error when copied anyway!
    # Only export our interface target, not the underlying FastDDS targets

    install(TARGETS dds EXPORT realsense2Targets)
    message(CHECK_PASS "Done")
endfunction()


pop_security_flags()

# Trigger the FastDDS build
get_fastdds()

push_security_flags()
