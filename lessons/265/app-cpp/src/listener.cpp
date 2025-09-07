#include "listener.hpp"

#include "http_session.hpp"
#include "utils.hpp"


void do_listen(boost::asio::io_context& ioc, const boost::asio::ip::tcp::endpoint& endpoint, const boost::asio::yield_context& yield) {
    boost::beast::error_code ec;

    // Open the acceptor
    boost::asio::ip::tcp::acceptor acceptor(ioc);
    acceptor.open(endpoint.protocol(), ec);
    if (ec)
        return fail(ec, "open");

    // Allow address reuse
    acceptor.set_option(boost::asio::socket_base::reuse_address(true), ec);
    if (ec)
        return fail(ec, "set_option");

    // Bind to the server address
    acceptor.bind(endpoint, ec);
    if (ec)
        return fail(ec, "bind");

    // Start listening for connections
    acceptor.listen(boost::asio::socket_base::max_listen_connections, ec);
    if (ec)
        return fail(ec, "listen");

    for (;;) {
        boost::asio::ip::tcp::socket socket(ioc);
        acceptor.async_accept(socket, yield[ec]);
        if (ec)
            fail(ec, "accept");
        else
            boost::asio::spawn(acceptor.get_executor(), std::bind(&do_session, boost::beast::tcp_stream(std::move(socket)), std::placeholders::_1), boost::asio::detached);
    }
}
