cmake_minimum_required(VERSION 3.28.3)

project(Benchmark)

add_executable(pubsub_client src/pubsub_client.cpp)
add_executable(streams_client src/streams_client.cpp)

add_library(config STATIC src/config.hpp src/config.cpp)
add_library(market STATIC src/market.hpp src/market.cpp)
add_library(monitoring STATIC src/monitoring.hpp src/monitoring.cpp)

target_compile_features(pubsub_client PUBLIC cxx_std_23)
target_compile_features(config PUBLIC cxx_std_23)
target_compile_features(market PUBLIC cxx_std_23)
target_compile_features(monitoring PUBLIC cxx_std_23)

if(APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif(UNIX)
    set(VCPKG_TARGET_TRIPLET "x64-linux")
endif()

set(VCPKG_ROOT_DIR ${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET})

find_package(libuv CONFIG REQUIRED)
find_package(prometheus-cpp CONFIG REQUIRED)
find_package(spdlog REQUIRED)
find_package(simdjson CONFIG REQUIRED)
find_package(CapnProto CONFIG REQUIRED)
find_package(hiredis CONFIG REQUIRED)
find_package(yaml-cpp CONFIG REQUIRED)
find_package(redis++ CONFIG REQUIRED)

target_link_libraries(config PRIVATE yaml-cpp::yaml-cpp)
target_link_libraries(market PRIVATE simdjson::simdjson)

target_link_libraries(pubsub_client PRIVATE
    prometheus-cpp::core
    prometheus-cpp::pull
    prometheus-cpp::util
    simdjson::simdjson
    CapnProto::kj
    CapnProto::capnp
    CapnProto::capnpc
    CapnProto::kj-gzip
    libuv::uv_a
    spdlog::spdlog
    hiredis::hiredis
    redis++::redis++_static
    monitoring
    config
    market
)

target_link_libraries(streams_client PRIVATE
    prometheus-cpp::core
    prometheus-cpp::pull
    prometheus-cpp::util
    simdjson::simdjson
    CapnProto::kj
    CapnProto::capnp
    CapnProto::capnpc
    CapnProto::kj-gzip
    libuv::uv_a
    spdlog::spdlog
    hiredis::hiredis
    redis++::redis++_static
    monitoring
    config
    market
)
