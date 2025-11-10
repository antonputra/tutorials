# Specify the minimum required CMake version
cmake_minimum_required(VERSION 3.28)

# Define the project
project(app
        VERSION 0.1.0
        DESCRIPTION "App for the bench."
        LANGUAGES CXX
)

# Set C++ standard to C++20 for all targets
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add executable
add_executable(http_server src/http_server.cpp)
add_executable(http_client src/http_client.cpp)
add_executable(websocket_server src/websocket_server.cpp)
add_executable(websocket_client src/websocket_client.cpp)

# Find libraries
find_package(spdlog CONFIG REQUIRED)
find_package(simdjson CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)
find_package(boost_beast CONFIG REQUIRED)
find_package(unofficial-uwebsockets CONFIG REQUIRED)
find_package(prometheus-cpp CONFIG REQUIRED)

# Include directories
include_directories("include")

if (APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif (UNIX)
    set(VCPKG_TARGET_TRIPLET "x64-linux")
endif ()

# Dependencies
target_link_libraries(http_server
        PRIVATE
        spdlog::spdlog
        simdjson::simdjson
        nlohmann_json::nlohmann_json
        unofficial::uwebsockets::uwebsockets
)

target_link_libraries(http_client
        PRIVATE
        Boost::beast
        spdlog::spdlog
        simdjson::simdjson
        nlohmann_json::nlohmann_json
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
)

target_link_libraries(websocket_server
        PRIVATE
        spdlog::spdlog
        simdjson::simdjson
        nlohmann_json::nlohmann_json
        unofficial::uwebsockets::uwebsockets
)

target_link_libraries(websocket_client
        PRIVATE
        Boost::beast
        spdlog::spdlog
        simdjson::simdjson
        nlohmann_json::nlohmann_json
        prometheus-cpp::core
        prometheus-cpp::pull
        prometheus-cpp::util
)
