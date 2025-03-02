#include <boost/beast/core.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <cstdlib>
#include <iostream>
#include <string>
#include <prometheus/exposer.h>
#include <prometheus/registry.h>
#include <prometheus/histogram.h>

using namespace prometheus;

namespace beast = boost::beast;
namespace http = beast::http;
namespace websocket = beast::websocket;
namespace net = boost::asio;
using tcp = boost::asio::ip::tcp;

// Sends a WebSocket message and prints the response
int main()
{
    // std::string host = "websocket-server.antonputra.pvt";
    std::string host = "localhost";
    // std::string host = "host.docker.internal";
    auto const port = "9001";
    auto const text = "hi";

    try
    {
        // Expose Prometheus metrics on port 9081.
        Exposer exposer{"0.0.0.0:9080"};

        // Create a Prometheus registry to store metrics.
        auto registry = std::make_shared<Registry>();

        // Create histogram metrics to measure duration.
        auto &packet_counter = BuildCounter().Name("app_messages_total").Help("Number of observed messages.").Register(*registry);

        // Add a label to the histogram to indicate which protocol is used.
        auto &tcp_counter = packet_counter.Add({{"protocol", "websocket"}});

        // Register the histogram metric with the Prometheus exporter.
        exposer.RegisterCollectable(registry);

        // The io_context is required for all I/O
        net::io_context ioc;

        // These objects perform our I/O
        tcp::resolver resolver{ioc};
        websocket::stream<tcp::socket> ws{ioc};

        // Look up the domain names
        auto const results = resolver.resolve(host, port);

        // Make the connection on the IP address we get from a lookup
        auto ep = net::connect(ws.next_layer(), results);

        // Create Host header for the WebSocket handshake.
        host += ':' + std::to_string(ep.port());

        // Set a decorator to change the User-Agent of the handshake
        ws.set_option(websocket::stream_base::decorator(
            [](websocket::request_type &req)
            {
                req.set(http::field::user_agent, std::string(BOOST_BEAST_VERSION_STRING) + " websocket-client-coro");
            }));

        // Perform the websocket handshake
        ws.handshake(host, "/devices");

        // Send the message
        ws.write(net::buffer(std::string(text)));

        // This buffer will hold the incoming message
        beast::flat_buffer buffer;

        // Read a message into our buffer
        while (true)
        {
            ws.read(buffer);
            // std::cout << beast::make_printable(buffer.data()) << std::endl;
            buffer.consume(buffer.size());
            tcp_counter.Increment();
        }

        // Close the WebSocket connection
        ws.close(websocket::close_code::normal);
    }
    catch (std::exception const &e)
    {
        std::cerr << "Error: " << e.what() << std::endl;
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}