# Specify the minimum required CMake version
cmake_minimum_required(VERSION 3.28)

# Define the project
project(app-cpp
        VERSION 0.1.0
        DESCRIPTION "Simple HTTP server."
        LANGUAGES CXX
)

# Set C++ standard to C++20 for all targets
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add executable
add_executable(app
        src/main.cpp
        src/http_session.cpp
        src/listener.cpp
        src/book_ticker.cpp
)

find_package(boost_beast CONFIG REQUIRED)
find_package(boost_json CONFIG REQUIRED)
find_package(spdlog CONFIG REQUIRED)

include_directories(include)

# Set VCPKG triplet based on platform
if (APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif (UNIX AND NOT APPLE)
    set(VCPKG_TARGET_TRIPLET "x64-linux")
endif ()

# Link libraries
target_link_libraries(app
        PRIVATE
        Boost::beast
        Boost::json
        spdlog::spdlog
)
