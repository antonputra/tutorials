#include <boost/beast/core.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <cstdlib>
#include <iostream>
#include <string>
#include <simdjson.h>
#include <nlohmann/json.hpp>
#include <spdlog/spdlog.h>
#include "utils.hpp"
#include "prometheus/exposer.h"
#include "prometheus/histogram.h"
#include "prometheus/registry.h"

namespace beast = boost::beast;
namespace http = beast::http;
namespace websocket = beast::websocket;
namespace net = boost::asio;
using namespace prometheus;
using namespace simdjson;
using tcp = boost::asio::ip::tcp;

ondemand::parser parser;

// Send a request with an adjustable rate limiter.
void send_request(beast::flat_buffer &buffer, websocket::stream<tcp::socket> &ws, Histogram &hist, const int rate) {
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
    ws.write(net::buffer(response.dump()));

    // Read WebSocket message
    ws.read(buffer);

    // Extract the body as a string
    const std::string body = beast::buffers_to_string(buffer.data());

    // Parse the JSON using simdjson ondemand parser
    const padded_string json = padded_string(body);
    ondemand::document payload = parser.iterate(json);

    const auto ts = payload["ts"].get_int64().value();
    hist.Observe(get_timestamp_ns() - ts);

    buffer.consume(buffer.size());

    // Add a slight delay after each request (e.g., 10us)
    std::this_thread::sleep_for(std::chrono::microseconds(10));
}

int main(const int argc, char **argv) {
    // Prometheus setup
    Exposer exposer{"0.0.0.0:8082"};
    const auto registry = std::make_shared<Registry>();
    auto &hist_fam = BuildHistogram().Name("app_duration_nanoseconds").Register(*registry);
    exposer.RegisterCollectable(registry);

    auto &hist = hist_fam.Add({{"server", "websocket"}}, get_hist_buckets());

    try {
        int port = 8081;
        if (argc != 3) {
            spdlog::error("Usage: ./websocket_client <url> <rate>");
            return 1;
        }
        std::string host = argv[1];
        int rate = std::stoi(argv[2]);

        // The io_context is required for all I/O
        net::io_context ioc;

        // These objects perform our I/O
        tcp::resolver resolver{ioc};
        websocket::stream<tcp::socket> ws{ioc};

        // Look up the domain name
        auto const results = resolver.resolve(host, std::to_string(port));

        // Make the connection on the IP address we get from a lookup
        auto ep = net::connect(ws.next_layer(), results);

        // Update the host_ string. This will provide the value of the Host HTTP header during the WebSocket handshake.
        host += ':' + std::to_string(ep.port());

        // Set a decorator to change the User-Agent of the handshake
        ws.set_option(websocket::stream_base::decorator([](websocket::request_type &req) {
            req.set(http::field::user_agent, std::string(BOOST_BEAST_VERSION_STRING) + " websocket-client-coro");
        }));

        // Perform the websocket handshake
        ws.handshake(host, "/api/order");

        // This buffer will hold the incoming message
        beast::flat_buffer buffer;

        while (true) {
            send_request(buffer, ws, hist, rate);
        }

        // Close the WebSocket connection
        ws.close(websocket::close_code::normal);
    } catch (std::exception const &e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
