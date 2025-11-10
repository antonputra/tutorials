#include <simdjson.h>

#include "nlohmann/json.hpp"
#include "spdlog/spdlog.h"
#include "uwebsockets/App.h"

using namespace simdjson;
using namespace uWS;

ondemand::parser parser;

void handle_orders(HttpResponse<false> *res, HttpRequest *) {
    std::string buffer;
    res->onData([res, buffer = std::move(buffer)](const std::string_view data, const bool last) mutable {
        buffer.append(data.data(), data.length());
        if (last) {
            try {
                // Parse the received body as JSON using simdjson
                ondemand::document payload = parser.iterate(buffer.data(), buffer.length(), buffer.length() + SIMDJSON_PADDING);

                // Create a response with a timestamp sent by the client to measure latency.
                const nlohmann::json response = {{"ts", payload["ts"].get_int64().value()}};

                res->end(response.dump());
            } catch (const simdjson_error &e) {
                const nlohmann::json response = {{"message", "failed to parse json"}};
                res->end(response.dump());
            }
        }
    });

    res->onAborted([] {
        spdlog::error("request aborted");
    });
}

void on_listen(const us_listen_socket_t *soc, int port) {
    if (soc) {
        spdlog::info("listening on port {}", port);
    } else {
        spdlog::error("failed to listen on port {}", port);
    }
}

int main() {
    int port = 8080;

    App().post("/api/order", handle_orders)
            .listen(port, [port](const us_listen_socket_t *soc) { on_listen(soc, port); })
            .run();

    return 0;
}
