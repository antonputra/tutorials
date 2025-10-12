#include <cstring>
#include <iostream>
#include <netdb.h>
#include <thread>
#include <unistd.h>

#include "../include/sbe/Bbo.h"
#include "utils/utils.hpp"

using std::string;
using std::chrono::system_clock;

// 1432 is usually a safe size over WAN, but certain networks may have lower limits and others may have higher limits.
// If doing the test on localhost, this number can be increased to 63k (63 * 1024) which should greatly improve throughput.
#define UDP_BUFSIZE 1432
#define PORT "8080"

using namespace std::literals;

int main(int argc, char *argv[]) {
    const std::string delay_us(argv[1]);
    const std::string target(argv[2]);

    std::cout << "delay between requests: " << delay_us << "μs" << std::endl;
    std::cout << "target host is: " << target << std::endl;

    // This variable hold file descriptor. We use them to read and write data.
    int client_fd, bytes_sent;

    // addrinfo is used to prepare the socket address structures.
    struct addrinfo hints, *servinfo;

    // Make sure the struct is empty.
    memset(&hints, 0, sizeof hints);

    // We don't care whether it is IPv4 or IPv6 to use for the server.
    hints.ai_family = AF_UNSPEC;

    // Create UDP socket to listen for incoming connections.
    hints.ai_socktype = SOCK_DGRAM;

    // Bind the server to the host IP address and listen on all interfaces (0.0.0.0).
    hints.ai_flags = AI_PASSIVE;

    // Fill out the struct. Assign the address of the server to the socket structure, etc.
    int err;
    if ((err = getaddrinfo(target.c_str(), PORT, &hints, &servinfo)) != 0) {
        std::cerr << "getaddrinfo failed: " << gai_strerror(err) << std::endl;
        return 1;
    }

    // Create a socket for the client and return a file descriptor that we can use to send data.
    client_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    constexpr std::size_t buffer_length = 256;
    alignas(16) std::uint8_t buffer_data[buffer_length];

    // Pre-compute constant values
    constexpr std::size_t header_length = sbe::MessageHeader::encodedLength();
    constexpr std::size_t block_length = sbe::Bbo::sbeBlockLength();
    constexpr std::uint16_t template_id = sbe::Bbo::sbeTemplateId();
    constexpr std::uint16_t schema_id = sbe::Bbo::sbeSchemaId();
    constexpr std::uint16_t schema_version = sbe::Bbo::sbeSchemaVersion();

    // Reuse header and BBO objects
    sbe::MessageHeader header;
    sbe::Bbo bbo;

    while (true) {
        // Reset buffer position
        header.wrap(reinterpret_cast<char *>(buffer_data), 0, 0, buffer_length).blockLength(block_length).templateId(template_id).schemaId(schema_id).version(schema_version);
        bbo.wrapForEncode(reinterpret_cast<char *>(buffer_data), header_length, buffer_length);

        // Generate random values
        bbo.putSymbol("BTCUSDT");
        bbo.ask_price(101'000'000);
        bbo.bid_price(100'000'000);
        bbo.bid_qty(500'000);
        bbo.bid_qty(600'000);
        bbo.price_exponent(3);
        bbo.qty_exponent(8);
        bbo.ts_event(utils::get_timestamp_ns());

        const std::size_t total_length = header_length + bbo.encodedLength();

        // Send data to UDP server. Returns -1 on error.
        bytes_sent = sendto(client_fd, buffer_data, total_length, 0, servinfo->ai_addr, servinfo->ai_addrlen);

        // Check if we successfully send data ro server.
        if (bytes_sent == -1) {
            perror("failed to send a message to the server: ");
        }

        std::this_thread::sleep_for(std::chrono::microseconds(std::stoi(delay_us)));
    }

    // Close the socket.
    close(client_fd);

    return 0;
}
