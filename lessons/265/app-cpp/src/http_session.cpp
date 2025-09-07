#include "http_session.hpp"

#include <sstream>

#include "book_ticker.hpp"
#include "utils.hpp"

template<class Body, class Allocator>
boost::beast::http::message_generator handle_request(boost::beast::http::request<Body, boost::beast::http::basic_fields<Allocator>>&& req) {
    boost::beast::http::response<boost::beast::http::dynamic_body> res;
    res.version(req.version());
    res.keep_alive(req.keep_alive());

    auto const target = req.target();
    // Simulate Binance API
    if (target == "/api/v3/ticker/bookTicker") {
        // Preallocate capacity for 2 elements same as Rust
        std::vector<BookTicker> data_array;
        data_array.reserve(2);
        data_array.emplace_back("LTCBTC", "4.00000000", "431.00000000", "4.00000200", "9.00000000");
        data_array.emplace_back("ETHBTC", "0.07946700", "49.00000000", "100000.00000000", "1000.00000000");

        res.result(boost::beast::http::status::ok);
        res.set(boost::beast::http::field::content_type, "application/json");
        boost::beast::ostream(res.body()) << serialize_book_tickers(data_array);
    } else {
        res.result(boost::beast::http::status::not_found);
        res.set(boost::beast::http::field::content_type, "text/plain");
        boost::beast::ostream(res.body()) << "Not Found";
    }

    res.prepare_payload();

    return res;
}

void do_session(boost::beast::tcp_stream& stream, boost::asio::yield_context yield) {
    boost::beast::error_code ec;

    // This buffer is required to persist across reads
    boost::beast::flat_buffer buffer;

    // This lambda is used to send messages
    for (;;) {
        // Set the timeout.
        stream.expires_after(std::chrono::seconds(30));

        // Read a request
        boost::beast::http::request<boost::beast::http::string_body> req;
        boost::beast::http::async_read(stream, buffer, req, yield[ec]);
        if (ec == boost::beast::http::error::end_of_stream)
            break;
        if (ec)
            return fail(ec, "read");

        // Handle the request
        boost::beast::http::message_generator msg = handle_request(std::move(req));

        // Determine if we should close the connection
        const bool keep_alive = msg.keep_alive();

        // Send the response
        boost::beast::async_write(stream, std::move(msg), yield[ec]);

        if (ec)
            return fail(ec, "write");

        if (!keep_alive) {
            break;
        }
    }

    // Send a TCP shutdown
    stream.socket().shutdown(boost::asio::ip::tcp::socket::shutdown_send, ec);
}
