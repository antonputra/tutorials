cmake_minimum_required(VERSION 3.28)

project(Benchmark)

add_executable(websocket_server websocket_server.cpp)
add_executable(websocket_client websocket_client.cpp)

target_compile_features(websocket_server PUBLIC cxx_std_20)
target_compile_features(websocket_client PUBLIC cxx_std_20)

if(APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif(UNIX)
    # set(VCPKG_TARGET_TRIPLET "arm64-linux") # to build docker on apple
    set(VCPKG_TARGET_TRIPLET "x64-linux") # to build docker on apple
    # set(VCPKG_TARGET_TRIPLET "x64-linux")
endif()

set(VCPKG_ROOT_DIR ${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET})
set(USOCKETS_LIB ${VCPKG_ROOT_DIR}/lib/libuSockets.a)

find_package(ZLIB REQUIRED)
find_package(libuv CONFIG REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(Boost REQUIRED COMPONENTS context)
find_package(prometheus-cpp CONFIG REQUIRED)

target_link_libraries(websocket_server PRIVATE 
    ${USOCKETS_LIB}
    ZLIB::ZLIB
    libuv::uv_a
    OpenSSL::SSL
)

target_link_libraries(websocket_client PRIVATE 
    Boost::boost
    Boost::context
    prometheus-cpp::core
    prometheus-cpp::pull
    prometheus-cpp::util
    ZLIB::ZLIB
    libuv::uv_a
    OpenSSL::SSL
)
