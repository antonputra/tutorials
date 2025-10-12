cmake_minimum_required(VERSION 3.28)

if (APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif (UNIX)
    set(VCPKG_TARGET_TRIPLET "x64-linux")
endif ()

project(App VERSION 0.1.0)

# Set C++ standard to C++20 for all targets
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(udp_server src/udp_server.cpp)
add_executable(udp_client src/udp_client.cpp)

# Add libraries
add_library(utils STATIC src/utils/utils.hpp src/utils/utils.cpp)

find_package(prometheus-cpp CONFIG REQUIRED)

# Link libraries
target_link_libraries(utils
        PRIVATE
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
)

target_link_libraries(udp_client
        PRIVATE
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
        utils
)

target_link_libraries(udp_server
        PRIVATE
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
        utils
)
