#include <cstring>
#include <stdio.h>
#include <cstdlib>
#include <unistd.h>
#include <cerrno>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <iostream>
#include <cstring>
#include <prometheus/exposer.h>
#include <prometheus/registry.h>
#include <prometheus/histogram.h>

// 1432 is usually a safe size over WAN, but certain networks may have lower limits and others may have higher limits.
// If doing the test on localhost, this number can be increased to 63k (63 * 1024) which should greatly improve throughput.
#define UDP_BUFSIZE 1432
#define MSG_BUFSIZE 86
#define PORT "8080"

using std::chrono::high_resolution_clock;
using namespace prometheus;

int main(void)
{
    const char *optimize_env = std::getenv("OPTIMIZE");
    bool optimize = optimize_env && std::strcmp(optimize_env, "true") == 0;

    // Expose Prometheus metrics on port 9080.
    Exposer exposer{"0.0.0.0:9080"};

    // Create a Prometheus registry to store metrics.
    auto registry = std::make_shared<Registry>();

    // Create histogram metrics to measure duration.
    auto &packet_counter = BuildCounter().Name("app_messages_total").Help("Number of observed messages").Register(*registry);

    // Add a label to the histogram to indicate which protocol is used.
    auto &udp_counter = packet_counter.Add({{"protocol", "udp"}});

    // Register the histogram metric with the Prometheus exporter.
    exposer.RegisterCollectable(registry);

    // These variables hold server and client file descriptors. We use them to read and write data.
    int server_fd, bytes_recv;

    // addrinfo is used to prepare the socket address structures.
    struct addrinfo hints, *servinfo;

    // This variable is used to hold the client IP address.
    struct sockaddr_storage client_addr;

    char buf[UDP_BUFSIZE + 1];

    // Make sure the struct is empty.
    memset(&hints, 0, sizeof hints);

    // We don't care whether it is IPv4 or IPv6 to use for the server.
    hints.ai_family = AF_UNSPEC;

    // Create UDP socket to listen for incoming connections.
    hints.ai_socktype = SOCK_DGRAM;

    // Bind the server to the host IP address and listen on all interfaces (0.0.0.0).
    hints.ai_flags = AI_PASSIVE;

    // Fill out the struct. Assign the address of my localhost to the socket structure, etc.
    int err;
    if ((err = getaddrinfo(NULL, PORT, &hints, &servinfo)) != 0)
    {
        std::cerr << "getaddrinfo failed: " << gai_strerror(err) << std::endl;
        return 1;
    }

    // Create a socket for the server and return a file descriptor that we can use to listen for new connections.
    server_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    std::cout << "server's socket file descriptor is " << server_fd << std::endl;

    // Associate socket with a port on your local machine. Returns -1 on error.
    int bind_result = bind(server_fd, servinfo->ai_addr, servinfo->ai_addrlen);

    // Check if we successfully bound to the port 8080.
    if (bind_result != 0)
    {
        std::cout << "failed to bind to port " PORT << std::endl;
        return 1;
    }

    // Get the size of the client IP address, IPv4 or IPv6.
    socklen_t addr_len = sizeof client_addr;

    if (optimize)
    {
        while (true)
        {
            // Use a buffer size equal to the MTU.
            bytes_recv = recvfrom(server_fd, buf, UDP_BUFSIZE, 0, (struct sockaddr *)&client_addr, &addr_len);

            // Check if we successfully received data from the client.
            if (bytes_recv == -1)
            {
                std::cout << "failed to receive a message from the client" << std::endl;
                return 1;
            }

            buf[bytes_recv] = '\0';

            for (char *pos = buf; pos != NULL; pos = std::strchr(pos, '{'))
            {
                udp_counter.Increment();

                // increment past the {
                pos++;
            }
        }
    }
    else
    {
        while (true)
        {
            // Use a small buffer to fit a single message.
            bytes_recv = recvfrom(server_fd, buf, MSG_BUFSIZE, 0, (struct sockaddr *)&client_addr, &addr_len);

            // Check if we successfully received data from the client.
            if (bytes_recv == -1)
            {
                std::cout << "failed to receive a message from the client" << std::endl;
                return 1;
            }

            buf[bytes_recv] = '\0';

            udp_counter.Increment();
        }
    }

    // Close the socket.
    close(server_fd);

    return 0;
}
