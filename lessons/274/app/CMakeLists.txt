# Specify the minimum required CMake version
cmake_minimum_required(VERSION 3.28)

# Define the project
project(app
        VERSION 0.1.0
        DESCRIPTION "App for the bench."
        LANGUAGES CXX
)

# Set C++ standard to C++23 for all targets
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find libraries
find_package(spdlog CONFIG REQUIRED)
find_package(prometheus-cpp CONFIG REQUIRED)
find_package(glaze CONFIG REQUIRED)

include(FetchContent)
FetchContent_Declare(
        protobuf
        GIT_REPOSITORY https://github.com/protocolbuffers/protobuf
        GIT_TAG v33.2
)

# Disable tests and examples to speed up the build
set(protobuf_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(protobuf)

include(${protobuf_SOURCE_DIR}/cmake/protobuf-generate.cmake)

protobuf_generate(
        OUT_VAR PROTO_GENERATED_FILES
        PROTOS proto/small.proto proto/medium.proto proto/large.proto
        PROTOC_OUT_DIR ${CMAKE_CURRENT_BINARY_DIR}
)

if (APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif (UNIX)
    set(VCPKG_TARGET_TRIPLET "x64-linux")
endif ()

# Include directories
include_directories("include")

# Add executable
add_executable(protobuf src/protobuf.cpp ${PROTO_GENERATED_FILES})
add_executable(json src/json.cpp)

# Dependencies
target_link_libraries(protobuf
        PRIVATE
        spdlog::spdlog
        protobuf::libprotobuf
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
)

target_include_directories(protobuf
        PRIVATE
        ${CMAKE_CURRENT_BINARY_DIR}
)

target_link_libraries(json
        PRIVATE
        spdlog::spdlog
        glaze::glaze
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
)
