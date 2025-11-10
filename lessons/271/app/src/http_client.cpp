#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <iostream>
#include <simdjson.h>
#include <string>
#include <thread>
#include <nlohmann/json.hpp>
#include <spdlog/spdlog.h>
#include "prometheus/exposer.h"
#include "prometheus/histogram.h"
#include "prometheus/registry.h"

#include "utils.hpp"

namespace beast = boost::beast;
namespace http = beast::http;
namespace net = boost::asio;
using tcp = net::ip::tcp;
using namespace prometheus;
using namespace simdjson;

ondemand::parser parser;

// Send a request with an adjustable rate limiter.
void send_request(http::request<http::string_body> &req, beast::tcp_stream &stream, beast::flat_buffer &buffer,
                  Histogram &hist, const int rate) {
    static auto window_start = std::chrono::steady_clock::now();
    static int count = 0;

    auto now = std::chrono::steady_clock::now();
    const auto elapsed = now - window_start;

    if (elapsed >= std::chrono::seconds(1)) {
        window_start = now;
        count = 0;
    }

    if (count >= rate) {
        auto time_to_next = std::chrono::seconds(1) - elapsed;
        if (time_to_next > std::chrono::nanoseconds(0)) {
            std::this_thread::sleep_for(time_to_next);
        }
        now = std::chrono::steady_clock::now();
        window_start = now;
        count = 0;
    }

    count++;

    const nlohmann::json response = {{"ts", get_timestamp_ns()}};

    req.body() = response.dump();
    req.prepare_payload();

    // Send the HTTP request to the remote host
    http::write(stream, req);

    // Declare a container to hold the response
    http::response<http::dynamic_body> res;

    // Receive the HTTP response
    http::read(stream, buffer, res);

    // Extract the body as a string
    std::string body = beast::buffers_to_string(res.body().data());

    // Parse the JSON using simdjson ondemand parser
    padded_string json = padded_string(body);
    ondemand::document payload = parser.iterate(json);

    auto ts = payload["ts"].get_int64().value();
    hist.Observe(get_timestamp_ns() - ts);

    // Add a slight delay after each request (e.g., 10us)
    std::this_thread::sleep_for(std::chrono::microseconds(10));
}

int main(int argc, char **argv) {
    // Prometheus setup
    Exposer exposer{"0.0.0.0:8082"};
    const auto registry = std::make_shared<Registry>();
    auto &hist_fam = BuildHistogram().Name("app_duration_nanoseconds").Register(*registry);
    exposer.RegisterCollectable(registry);

    auto &hist = hist_fam.Add({{"server", "http"}}, get_hist_buckets());

    try {
        int port = 8080;
        if (argc != 3) {
            spdlog::error("Usage: ./websocket_client <url> <sleep>");
            return 1;
        }
        auto const host = argv[1];
        int rate = std::stoi(argv[2]);

        int version = 11;

        // The io_context is required for all I/O
        net::io_context ioc;

        // These objects perform our I/O
        tcp::resolver resolver(ioc);
        beast::tcp_stream stream(ioc);

        // Look up the domain name
        auto const results = resolver.resolve(host, std::to_string(port));

        // Make the connection on the IP address we get from a lookup
        stream.connect(results);

        // Set up an HTTP POST request message
        http::request<http::string_body> req{http::verb::post, "/api/order", version};
        req.set(http::field::host, host);
        req.set(http::field::user_agent, BOOST_BEAST_VERSION_STRING);
        req.set(http::field::content_type, "application/json");

        // This buffer is used for reading and must be persisted
        beast::flat_buffer buffer;

        while (true) {
            send_request(req, stream, buffer, hist, rate);
        }

        // Gracefully close the socket
        beast::error_code ec;
        stream.socket().shutdown(tcp::socket::shutdown_both, ec);
    } catch (std::exception const &e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    return 1;
}
