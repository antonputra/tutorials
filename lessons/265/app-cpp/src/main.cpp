#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/spawn.hpp>
#include <boost/beast/core.hpp>
#include <cstdlib>
#include <thread>
#include <vector>

#include "listener.hpp"

int main() {
    boost::asio::ip::tcp::endpoint endpoint(boost::asio::ip::tcp::v4(), 8080);

    // The io_context is required for all I/O
    constexpr auto threads = 2;
    boost::asio::io_context ioc{threads};

    // Spawn a listening port
    boost::asio::spawn(ioc, std::bind(&do_listen, std::ref(ioc), endpoint, std::placeholders::_1), [](const std::exception_ptr& ex) {
        if (ex)
            std::rethrow_exception(ex);
    });

    // Run the I/O service on the requested number of threads
    std::vector<std::thread> v;
    v.reserve(threads - 1);
    for (auto i = threads - 1; i > 0; --i)
        v.emplace_back([&ioc] { ioc.run(); });
    ioc.run();

    return EXIT_SUCCESS;
}
