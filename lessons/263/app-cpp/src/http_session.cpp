#include "http_session.hpp"

#include <boost/bind.hpp>
#include <ctime>  // For time functions
#include <iomanip>  // For std::put_time
#include <sstream>  // For std::ostringstream

#include "book_ticker.hpp"

http_session::http_session(tcp::socket&& socket) :
    stream_(std::move(socket)) {}

void http_session::run() {
    do_read();
}

void http_session::do_read() {
    req_ = {};
    http::async_read(stream_, buffer_, req_, boost::bind(&http_session::on_read, shared_from_this(), std::placeholders::_1));
}

void http_session::on_read(const beast::error_code& ec) {
    if (ec == http::error::end_of_stream) {
        return do_close();
    }
    if (ec) {
        return fail(ec, "read");
    }

    const auto res = std::make_shared<http::response<http::string_body>>();
    res->version(req_.version());
    res->keep_alive(req_.keep_alive());

    auto const target = req_.target();
    // Simulate Binance API
    if (target == "/api/v3/ticker/bookTicker") {
        // Preallocate capacity for 2 elements same as Rust
        std::vector<BookTicker> data_array;
        data_array.reserve(2);
        data_array.emplace_back("LTCBTC", "4.00000000", "431.00000000", "4.00000200", "9.00000000");
        data_array.emplace_back("ETHBTC", "0.07946700", "49.00000000", "100000.00000000", "1000.00000000");

        res->result(http::status::ok);
        res->set(http::field::content_type, "application/json");
        res->body() = serialize_book_tickers(data_array);
    } else {
        res->result(http::status::not_found);
        res->set(http::field::content_type, "text/plain");
        res->body() = "Not Found";
    }

    res->prepare_payload();

    http::async_write(stream_, *res, boost::bind(&http_session::on_write, shared_from_this(), std::placeholders::_1, res));
}

void http_session::on_write(const beast::error_code& ec, const std::shared_ptr<http::response<http::string_body>>& res) {
    if (ec) {
        return fail(ec, "write");
    }

    if (res->keep_alive()) {
        do_read();
    } else {
        do_close();
    }
}

void http_session::do_close() {
    beast::error_code ec;
    stream_.socket().shutdown(tcp::socket::shutdown_send, ec);
}
