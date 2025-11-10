#include <simdjson.h>

#include "nlohmann/json.hpp"
#include "spdlog/spdlog.h"
#include "uwebsockets/App.h"

using namespace simdjson;
using namespace uWS;

ondemand::parser parser;

struct PerSocketData {
};

void on_listen(const us_listen_socket_t *soc, int port) {
    if (soc) {
        spdlog::info("listening on port {}", port);
    } else {
        spdlog::error("failed to listen on port {}", port);
    }
}

void on_open(WebSocket<false, true, PerSocketData> *) {
    spdlog::info("websocket connected");
}

void on_close(WebSocket<false, true, PerSocketData> *, int, std::string_view) {
    spdlog::warn("websocket closed");
}

void on_message(WebSocket<false, true, PerSocketData> *ws, const std::string_view data, const OpCode) {
    try {
        // We can parse directly from the string_view; we just need to add padding for the parser.
        ondemand::document payload = parser.iterate(data.data(), data.length(), data.length() + SIMDJSON_PADDING);

        // Create a response with a timestamp sent by the client to measure latency.
        const nlohmann::json response = {{"ts", payload["ts"].get_int64().value()}};

        // Send a response with a timestamp back to the client.
        ws->send(response.dump(), TEXT);
    } catch (const simdjson_error &) {
        const nlohmann::json response = {{"message", "failed to parse json"}};
        ws->send(response.dump(), TEXT);
    }
}

App::WebSocketBehavior<PerSocketData> bootstrap() {
    return {
        .open = on_open,
        .message = on_message,
        .close = on_close
    };
}

int main() {
    int port = 8081;

    App().ws<PerSocketData>("/api/order", bootstrap())
            .listen(port, [port](const us_listen_socket_t *soc) { on_listen(soc, port); })
            .run();

    return 0;
}
