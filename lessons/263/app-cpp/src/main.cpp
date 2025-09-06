#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/asio/spawn.hpp> // need to link with boost_coroutine

#include <boost/json.hpp>
#include <boost/json/src.hpp>

#include <thread>

namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = net::ip::tcp;

namespace json = boost::json;

void fail(beast::error_code const &ec, const char* const what) {
    fprintf(stderr, "error: %s, %s\n", what, ec.message().c_str());
}

int main() {
    beast::error_code ec;
    net::io_context ioc;

    tcp::endpoint endpoint(tcp::v4(), 8080);

    tcp::acceptor acceptor(ioc);
    acceptor.open(endpoint.protocol(), ec);
    if (ec) {
        fail(ec, "open");
        return 1;
    }

    acceptor.set_option(net::socket_base::reuse_address(true), ec);
    if (ec) {
        fail(ec, "set_option");
        return 1;
    }

    acceptor.bind(endpoint, ec);
    if (ec) {
        fail(ec, "bind");
        return 1;
    }

    acceptor.listen(net::socket_base::max_listen_connections, ec);
    if (ec) {
        fail(ec, "listen");
        return 1;
    }

    net::spawn(acceptor.get_executor(), [&](net::yield_context const &yield) {
        while (acceptor.is_open()) {
            tcp::socket socket(ioc);
            acceptor.async_accept(socket, yield[ec]);
            if (ec) {
                fail(ec, "accept");
                break;
            }

            net::spawn(acceptor.get_executor(), [s = std::move(socket)](net::yield_context const &yield) mutable {
                beast::tcp_stream stream(std::move(s));

                beast::error_code ec;
                beast::flat_buffer buffer;
                while (true) { // TODO not sure how keep_alive should work
                    http::request_parser<http::string_body> requestParser;
                    http::async_read(stream, buffer, requestParser, yield[ec]);
                    if (ec) {
                        fail(ec, "read");
                        return;
                    }

                    auto const &request = requestParser.get();

                    http::response<http::dynamic_body> response;
                    response.version(request.version());
                    response.keep_alive(request.keep_alive());

                    if (request.method() == http::verb::get && request.target() == "/api/v3/ticker/bookTicker") {
                        response.result(http::status::ok);
                        response.set(http::field::content_type, "application/json");
                        // TODO without the vector for simplicity of that example
                        beast::ostream(response.body()) << json::serialize(json::array{
                                json::object{
                                        {"symbol",   "LTCBTC"},
                                        {"bidPrice", "4.00000000"},
                                        {"bidQty",   "431.00000000"},
                                        {"askPrice", "4.00000200"},
                                        {"askQty",   "9.00000000"}
                                },
                                json::object{
                                        {"symbol",   "ETHBTC"},
                                        {"bidPrice", "0.07946700"},
                                        {"bidQty",   "49.00000000"},
                                        {"askPrice", "100000.00000000"},
                                        {"askQty",   "1000.00000000"}
                                },
                        });
                    } else {
                        response.result(http::status::not_found);
                        response.set(http::field::content_type, "text/plain");
                        beast::ostream(response.body()) << "Not Found";
                    }

                    response.prepare_payload();

                    http::async_write(stream, response, yield[ec]);
                    if (ec) {
                        fail(ec, "write");
                        return;
                    }

                    // TODO not sure how keep_alive should work
//                    printf("%d\n", request.keep_alive()); // always return true (through curl)
                                                          // from docs: The value depends on the *version* in the message
                    auto const con_header = request.find("Connection");
                    if (con_header == request.end() || con_header->value() != "keep-alive")
                        break;
                }
            });
        }
    });

    constexpr auto threads = 2;

    std::vector<std::thread> v;
    v.reserve(threads - 1);
    for (auto i = threads - 1; i > 0; --i)
        v.emplace_back([&ioc] { ioc.run(); });

    ioc.run();

    return 0;
}
