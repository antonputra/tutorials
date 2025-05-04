#include <iostream>
#include <unistd.h>
#include <netdb.h>
#include <cstring>
#include <prometheus/exposer.h>
#include <prometheus/registry.h>
#include <prometheus/histogram.h>
#include "monitoring.hpp"

#define BACKLOG 20
#define MAXDATASIZE 90
#define PORT "8082"
// #define ADDRESS "server.antonputra.pvt"
#define ADDRESS "127.0.0.1"

using namespace prometheus;

int main()
{
    // Expose Prometheus metrics on port 9081.
    Exposer exposer{"0.0.0.0:9080"};

    // Create a Prometheus registry to store metrics.
    auto registry = std::make_shared<Registry>();

    // Create histogram buckets.
    auto buckets = Histogram::BucketBoundaries{monitoring::get_buckets()};

    // Create histogram metrics to measure duration.
    auto &duration = BuildHistogram().Name("myapp_duration_nanoseconds").Help("Duration to send and receive a message.").Register(*registry);
    auto &packet_counter = BuildCounter().Name("myapp_observed_packets_total").Help("Number of observed packets").Register(*registry);

    // Add a label to the histogram to indicate which protocol is used.
    auto &msg_duration = duration.Add({{"protocol", "tcp"}}, buckets);
    auto &tcp_counter = packet_counter.Add({{"protocol", "tcp"}});

    // Register the histogram metric with the Prometheus exporter.
    exposer.RegisterCollectable(registry);

    // Buffer to store received data from the server.
    char buf[MAXDATASIZE];

    // This variable hold file descriptor. We use them to read and write data.
    int client_fd, bytes_recv;

    // addrinfo is used to prepare the socket address structures.
    struct addrinfo hints, *servinfo;

    // This variable is used to hold the client IP address.
    struct sockaddr_storage client_addr;

    // Make sure the struct is empty.
    memset(&hints, 0, sizeof hints);

    // We don't care whether it is IPv4 or IPv6 to use for the server.
    hints.ai_family = AF_UNSPEC;

    // Create TCP socket to listen for incoming connections.
    hints.ai_socktype = SOCK_STREAM;

    // Bind the server to the host IP address and listen on all interfaces (0.0.0.0).
    hints.ai_flags = AI_PASSIVE;

    // Fill out the struct. Assign the address of of the server to the socket structure, etc.
    getaddrinfo(ADDRESS, PORT, &hints, &servinfo);

    // Create a socket for the client and return a file descriptor that we can use to receive data.
    client_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    // Connect to the server. Return -1 on error.
    int connect_result = connect(client_fd, servinfo->ai_addr, servinfo->ai_addrlen);

    // Check if we successfully connected to the server.
    if (connect_result != 0)
    {
        std::cout << "failed to connect to the server" << std::endl;
        exit(1);
    }

    // Start receiving data from the server.
    while (true)
    {
        // Get data from the server. Returns -1 on error.
        bytes_recv = recv(client_fd, buf, MAXDATASIZE - 1, 0);
        buf[bytes_recv] = '\0';

        // Check if we successfully get data from the server.
        if (bytes_recv == -1)
        {
            std::cout << "failed to receive a message from the server." << std::endl;
            exit(1);
        }
        // msg_duration.Observe(monitoring::get_time() - monitoring::parse_time(buf));

        tcp_counter.Increment();

        // // Measure the amount of time it takes to send and receive a message over the network.
        try
        {
            msg_duration.Observe(monitoring::get_time() - monitoring::parse_time(buf));
        }
        catch (...)
        {
            // std::cout << "failed to parse" << std::endl;
        }
    }

    // Close the socket.
    close(client_fd);

    return 0;
}