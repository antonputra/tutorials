cmake_minimum_required(VERSION 3.28)

if(APPLE)
    set(VCPKG_TARGET_TRIPLET "arm64-osx")
elseif(UNIX)
    set(VCPKG_TARGET_TRIPLET "x64-linux")
endif()

project(App VERSION 0.1.0)

add_executable(tcp_server tcp_server.cpp)
add_executable(tcp_client tcp_client.cpp)
add_executable(udp_server udp_server.cpp)
add_executable(udp_client udp_client.cpp)

find_package(prometheus-cpp CONFIG REQUIRED)

target_compile_features(tcp_server PUBLIC cxx_std_20)
target_compile_features(tcp_client PUBLIC cxx_std_20)
target_compile_features(udp_server PUBLIC cxx_std_20)
target_compile_features(udp_client PUBLIC cxx_std_20)

target_link_libraries(tcp_client PRIVATE prometheus-cpp::core prometheus-cpp::pull prometheus-cpp::util)
target_link_libraries(udp_server PRIVATE prometheus-cpp::core prometheus-cpp::pull prometheus-cpp::util)
