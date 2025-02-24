cmake_minimum_required(VERSION 3.28)
project(MyApp VERSION 0.1.0)

add_executable(tcp_server tcp_server.cpp)
add_executable(tcp_client tcp_client.cpp)

add_executable(udp_server udp_server.cpp)
add_executable(udp_client udp_client.cpp)

target_include_directories(tcp_client PUBLIC /usr/local/include)

target_compile_features(tcp_server PUBLIC cxx_std_17)
target_compile_features(tcp_client PUBLIC cxx_std_17)

target_link_libraries(tcp_client 
    /usr/local/lib/libprometheus-cpp-pull.a
    /usr/local/lib/libprometheus-cpp-core.a 
    monitoring
)

target_include_directories(udp_client PUBLIC /usr/local/include)

target_compile_features(udp_client PUBLIC cxx_std_17)

target_link_libraries(udp_client 
    /usr/local/lib/libprometheus-cpp-pull.a
    /usr/local/lib/libprometheus-cpp-core.a 
    monitoring
)

target_include_directories(udp_server PUBLIC /usr/local/include)

target_compile_features(udp_server PUBLIC cxx_std_17)

target_link_libraries(udp_server 
    /usr/local/lib/libprometheus-cpp-pull.a
    /usr/local/lib/libprometheus-cpp-core.a 
    monitoring
)

add_library(monitoring STATIC monitoring.hpp monitoring.cpp)

target_compile_features(monitoring PUBLIC cxx_std_17)

target_link_libraries(tcp_server PRIVATE monitoring)