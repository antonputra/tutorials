# Specify the minimum required CMake version
cmake_minimum_required(VERSION 3.28)

# Define the project
project(app
        VERSION 0.1.0
        DESCRIPTION "App to test Aeron and ZeroMQ."
        LANGUAGES CXX
)

# Set C++ standard to C++20 for all targets
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# For Aeron
add_definitions(-DAERON_COMPILER_MSVC=1)

# Add executable
add_executable(aeron-publisher src/aeron-publisher.cpp)
add_executable(aeron-subscriber src/aeron-subscriber.cpp)
add_executable(zeromq-publisher src/zeromq-publisher.cpp)
add_executable(zeromq-subscriber src/zeromq-subscriber.cpp)

# Add libraries
add_library(utils STATIC src/utils/utils.hpp src/utils/utils.cpp)

# Include directories for external dependencies
include_directories("/usr/local/include")

# Set VCPKG triplet based on platform
if (APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif (UNIX AND NOT APPLE)
    set(VCPKG_TARGET_TRIPLET "x64-linux")
endif ()

# Find external dependencies
find_package(spdlog CONFIG REQUIRED)
find_package(cppzmq CONFIG REQUIRED)
find_package(prometheus-cpp CONFIG REQUIRED)

# Link libraries
target_link_libraries(utils
        PRIVATE
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
)

target_link_libraries(aeron-publisher
        PRIVATE
        utils
        spdlog::spdlog
        /usr/local/lib/libaeron_client.a
)

target_link_libraries(aeron-subscriber
        PRIVATE
        utils
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
        spdlog::spdlog
        /usr/local/lib/libaeron_client.a
)

target_link_libraries(zeromq-publisher
        PRIVATE
        utils
        spdlog::spdlog
        cppzmq-static
)

target_link_libraries(zeromq-subscriber
        PRIVATE
        utils
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
        spdlog::spdlog
        cppzmq-static
)
