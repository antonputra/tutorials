#include <iostream>
#include <unistd.h>
#include <netdb.h>
#include <cstring>
#include <prometheus/exposer.h>
#include <prometheus/registry.h>
#include <prometheus/histogram.h>

// 1432 is usually a safe size over WAN, but certain networks may have lower limits and others may have higher limits.
// If doing the test on localhost, this number can be increased to 63k (63 * 1024) which should greatly improve throughput.
#define UDP_BUFSIZE 1432
#define MSG_BUFSIZE 86
#define BACKLOG 20
#define PORT "8080"
#define ADDRESS "tcp-server.antonputra.pvt"
// #define ADDRESS "localhost"

using namespace prometheus;

int main()
{
    const char *optimize_env = std::getenv("OPTIMIZE");
    bool optimize = optimize_env && std::strcmp(optimize_env, "true") == 0;

    // Expose Prometheus metrics on port 9081.
    Exposer exposer{"0.0.0.0:9080"};

    // Create a Prometheus registry to store metrics.
    auto registry = std::make_shared<Registry>();

    // Create histogram metrics to measure duration.

    auto &packet_counter = BuildCounter().Name("app_messages_total").Help("Number of observed messages").Register(*registry);

    // Add a label to the histogram to indicate which protocol is used.
    auto &tcp_counter = packet_counter.Add({{"protocol", "tcp"}});

    // Register the histogram metric with the Prometheus exporter.
    exposer.RegisterCollectable(registry);

    // Buffer to store received data from the server.
    char buf[UDP_BUFSIZE + 1];

    // This variable hold file descriptor. We use them to read and write data.
    int client_fd, bytes_recv;

    // addrinfo is used to prepare the socket address structures.
    struct addrinfo hints, *servinfo;

    // Make sure the struct is empty.
    memset(&hints, 0, sizeof hints);

    // We don't care whether it is IPv4 or IPv6 to use for the server.
    hints.ai_family = AF_UNSPEC;

    // Create TCP socket to listen for incoming connections.
    hints.ai_socktype = SOCK_STREAM;

    // Bind the server to the host IP address and listen on all interfaces (0.0.0.0).
    hints.ai_flags = AI_PASSIVE;

    // Fill out the struct. Assign the address of of the server to the socket structure, etc.
    int err;
    if ((err = getaddrinfo(ADDRESS, PORT, &hints, &servinfo)) != 0)
    {
        std::cerr << "getaddrinfo failed: " << gai_strerror(err) << std::endl;
        return 1;
    }

    // Create a socket for the client and return a file descriptor that we can use to receive data.
    client_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    // Connect to the server. Return -1 on error.
    int connect_result = connect(client_fd, servinfo->ai_addr, servinfo->ai_addrlen);

    // Check if we successfully connected to the server.
    if (connect_result != 0)
    {
        perror("connect failed");
        return 1;
    }

    if (optimize)
    {
        while (true)
        {
            // Use a buffer size equal to the MTU.
            bytes_recv = recv(client_fd, buf, UDP_BUFSIZE, MSG_WAITALL);
            buf[bytes_recv] = '\0';

            for (char *pos = buf; pos != NULL; pos = std::strchr(pos, '{'))
            {
                tcp_counter.Increment();
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
            bytes_recv = recv(client_fd, buf, MSG_BUFSIZE, MSG_WAITALL);
            buf[bytes_recv] = '\0';

            tcp_counter.Increment();
        }
    }

    // graceful shutdown. disable sending and recieving, empty the kernel buffer, then close.
    shutdown(client_fd, SHUT_RDWR);
    while (read(client_fd, buf, UDP_BUFSIZE) > 0)
    {
    }
    close(client_fd);

    return 0;
}
