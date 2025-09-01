#include <algorithm>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <thread>
#include <vector>

#include "listener.hpp"
#include "spdlog/spdlog.h"


namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = asio::ip::tcp;


int main() {
    auto const address = net::ip::make_address("0.0.0.0");
    constexpr auto port = static_cast<unsigned short>(8080);
    // 2 Threads, same as Rust
    constexpr auto threads = 2;

    // The io_context is required for all I/O
    net::io_context ioc{threads};

    // Create and launch a listening port
    std::make_shared<listener>(ioc, tcp::endpoint{address, port})->run();

    // Run the I/O service on the requested number of threads
    std::vector<std::thread> v;
    v.reserve(threads - 1);
    for (auto i = threads - 1; i > 0; --i)
        v.emplace_back([&ioc] { ioc.run(); });

    spdlog::info("Starting a server on port: {}", port);
    ioc.run();

    return EXIT_SUCCESS;
}
