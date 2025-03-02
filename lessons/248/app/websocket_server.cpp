#include <uwebsockets/App.h>

int main() {
  std::vector < std::thread * > threads(std::thread::hardware_concurrency());

  struct PerSocketData {};

  std::transform(threads.begin(), threads.end(), threads.begin(), [](std::thread * /*t*/ ) {
    return new std::thread([]() {
      // Create a sample message of 85 bytes to send to the client.
      std::string_view msg = "{\"id\":66009,\"mac\":\"81-6E-79-DA-5A-B2\",\"firmware\":\"4.0.2\",\"create_at\":\"1611082428813\"}";

      uWS::App().ws < PerSocketData > ("/devices", {
        .compression = uWS::SHARED_COMPRESSOR,
        .maxPayloadLength = 100 * 1024 * 1024,
        .idleTimeout = 16,
        .maxBackpressure = 100 * 1024 * 1024,
        .closeOnBackpressureLimit = false,
        .resetIdleTimeoutOnSend = false,
        .sendPingsAutomatically = true,

        /* Handlers */
        .upgrade = nullptr,
        .open = [](auto * ) {},
        .message = [msg](auto * ws, std::string_view message, uWS::OpCode opCode) {
          while (true) {
            ws -> send(msg, opCode, false);
          }
        },
        .dropped = [](auto * , std::string_view, uWS::OpCode) {},
        .drain = [](auto * ) {},
        .ping = [](auto * , std::string_view) {},
        .pong = [](auto * , std::string_view) {},
        .close = [](auto * , int, std::string_view) {}
      }).listen(9001, [](auto * listen_socket) {
        if (listen_socket) {
          std::cout << "Thread " << std::this_thread::get_id() << " listening on port " << 9001 << std::endl;
        } else {
          perror("listen failed");
          std::cout << "Thread " << std::this_thread::get_id() << " failed to listen on port 9001" << std::endl;
        }
      }).run();

    });
  });

  std::for_each(threads.begin(), threads.end(), [](std::thread * t) {
    t -> join();
  });
}