#include "listener.hpp"

#include <boost/bind.hpp>

#include "book_ticker.hpp"
#include "http_session.hpp"

listener::listener(asio::io_context& ioc, const tcp::endpoint& endpoint) :
    ioc_(ioc), acceptor_(ioc), socket_(ioc) {
    beast::error_code ec;

    acceptor_.open(endpoint.protocol(), ec);
    if (ec) {
        fail(ec, "open");
        return;
    }

    acceptor_.set_option(tcp::acceptor::reuse_address(true), ec);
    if (ec) {
        fail(ec, "set_option");
        return;
    }

    acceptor_.bind(endpoint, ec);
    if (ec) {
        fail(ec, "bind");
        return;
    }

    acceptor_.listen(tcp::acceptor::max_listen_connections, ec);
    if (ec) {
        fail(ec, "listen");
        return;
    }
}

void listener::run() {
    do_accept();
}

void listener::do_accept() {
    acceptor_.async_accept(socket_, boost::bind(&listener::on_accept, shared_from_this(), std::placeholders::_1));
}

void listener::on_accept(const beast::error_code& ec) {
    if (ec) {
        return fail(ec, "accept");
    }

    std::make_shared<http_session>(std::move(socket_))->run();
    do_accept();
}
