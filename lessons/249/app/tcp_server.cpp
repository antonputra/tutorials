#include <unistd.h>
#include <netdb.h>
#include <iostream>
#include <thread>
#include <cstring>
#include "monitoring.hpp"

using std::string;
using std::to_string;
using std::chrono::duration;
using std::chrono::microseconds;
using std::chrono::system_clock;

// Port on the server to listen for incoming connections.
#define PORT "8080"

// Declare some variables for the test.
int stage_count = 1;
int stage_interval_s = 1000;
int sleep_us = 100000000;

// Number of pending connections the server will hold (queue size).
#define BACKLOG 10

int main(void)
{
    const char *enable_monitoring_env = std::getenv("ENABLE_MONITORING");

    std::string enable_monitoring(enable_monitoring_env);

    // These variables hold server and client file descriptors. We use them to read and write data.
    int server_fd, client_fd, bytes_sent;

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

    // Fill out the struct. Assign the address of my localhost to the socket structure, etc.
    getaddrinfo(NULL, PORT, &hints, &servinfo);

    // Create a socket for the server and return a file descriptor that we can use to listen for new connections.
    server_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    std::cout << "server's socket file descriptor is " + to_string(server_fd) << std::endl;

    // Associate socket with a port on your local machine. Returns -1 on error.
    int bind_result = bind(server_fd, servinfo->ai_addr, servinfo->ai_addrlen);

    // Check if we successfully bound to the port 8080.
    if (bind_result != 0)
    {
        perror("bind failed");
        exit(1);
    }

    // Start listening for incoming connections. Returns -1 on error.
    int listen_result = listen(server_fd, BACKLOG);

    // Check if we successfully started to listen on port 8080.
    if (listen_result != 0)
    {
        perror("listen failed");
        exit(1);
    }

    // Get the size of the client IP address, IPv4 or IPv6.
    socklen_t sin_size = sizeof client_addr;

    // Get the local file descriptor that was created for the client. We can use it directly to write data to it.
    client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &sin_size);

    if (client_fd == -1)
    {
        perror("accept failed");
        exit(1);
    }

    std::cout << "client's socket file descriptor is " + to_string(client_fd) << std::endl;

    string msg = "{\"id\":66009,\"mac\":\"81-6E-79-DA-5A-B2\",\"firmware\":\"4.0.2\",\"create_at\": 170341283583666}";

    for (int stage = 0; stage < stage_count; stage++)
    {
        // Get the start time of the stage.
        auto start_time = system_clock::now();

        // When the client establishes a connection, continuously send the same message over and over.
        while (true)
        {
            if (enable_monitoring == "true")
            {
                // Generate a payload message with a timestamp to measure the duration.
                msg = monitoring::generate_payload();
            }

            // Send data to the client.
            bytes_sent = send(client_fd, msg.c_str(), msg.length(), 0);

            // Check if we successfully sent data to the client.
            if (bytes_sent == -1)
            {
                std::cout << "failed to send a message to the client" << std::endl;
                exit(1);
            }

            // Get the current time.
            duration<double> elapsed_seconds = system_clock::now() - start_time;

            // Finish the state based on the time elapsed.
            if (elapsed_seconds.count() > stage_interval_s)
            {
                sleep_us -= 1;
                std::cout << to_string(stage) + " stage is finished, sleeping now for: " + to_string(sleep_us) + " microseconds" << std::endl;
                break;
            }

            // Sleep to add a delay between sending messages to the client.
            std::this_thread::sleep_for(microseconds(sleep_us));
        }
    }

    while (true)
    {
        if (enable_monitoring == "true")
        {
            // Generate a payload message with a timestamp to measure the duration.
            msg = monitoring::generate_payload();
        }

        // Send data to the client.
        bytes_sent = send(client_fd, msg.c_str(), msg.length(), 0);

        // Check if we successfully sent data to the client.
        if (bytes_sent == -1)
        {
            perror("send failed");
            exit(1);
        }
    }

    // Close the connection on your socket descriptor.
    close(server_fd);

    return 0;
}