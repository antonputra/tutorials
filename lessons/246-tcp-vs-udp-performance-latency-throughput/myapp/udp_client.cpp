#include <unistd.h>
#include <iostream>
#include <netdb.h>
#include <thread>
#include <cstring>
#include "monitoring.hpp"

using std::string;
using std::to_string;
using std::chrono::duration;
using std::chrono::microseconds;
using std::chrono::system_clock;

#define PORT "8080"
// #define ADDRESS "udp-server.antonputra.pvt"
#define ADDRESS "localhost"

// Declare some variables for the test.
int stage_count = 1;
int stage_interval_s = 300;
int sleep_us = 1;

int main()
{
    // This variable hold file descriptor. We use them to read and write data.
    int client_fd, bytes_send;

    // addrinfo is used to prepare the socket address structures.
    struct addrinfo hints, *servinfo;

    // This variable is used to hold the client IP address.
    struct sockaddr_storage client_addr;

    // Make sure the struct is empty.
    memset(&hints, 0, sizeof hints);

    // We don't care whether it is IPv4 or IPv6 to use for the server.
    hints.ai_family = AF_UNSPEC;

    // Create UDP socket to listen for incoming connections.
    hints.ai_socktype = SOCK_DGRAM;

    // Bind the server to the host IP address and listen on all interfaces (0.0.0.0).
    hints.ai_flags = AI_PASSIVE;

    // Fill out the struct. Assign the address of of the server to the socket structure, etc.
    getaddrinfo(ADDRESS, PORT, &hints, &servinfo);

    // Create a socket for the client and return a file descriptor that we can use to send data.
    client_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    for (int stage = 0; stage < stage_count; stage++)
    {
        // Get the start time of the stage.
        auto start_time = system_clock::now();

        // When the client establishes a connection, continuously send the same message over and over.
        while (true)
        {
            // Sleep to add a delay between sending messages to the client.
            std::this_thread::sleep_for(microseconds(sleep_us));

            // Generate a payload message with a timestamp to measure the duration.
            string msg = monitoring::generate_payload();

            // Send data to UDP server. Returns -1 on error.
            bytes_send = sendto(client_fd, msg.c_str(), msg.length(), 0, servinfo->ai_addr, servinfo->ai_addrlen);

            // Check if we successfully send data ro server.
            if (bytes_send == -1)
            {
                std::cout << "failed to send a message to the server." << std::endl;
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
        }
    }

    // Run the final stage in its own loop to eliminate all other function calls and comparisons.
    std::cout << "Starting the final stage." << std::endl;
    while (true)
    {
        // Generate a payload message with a timestamp to measure the duration.
        string msg = monitoring::generate_payload();

        // Send data to UDP server. Returns -1 on error.
        bytes_send = sendto(client_fd, msg.c_str(), msg.length(), 0, servinfo->ai_addr, servinfo->ai_addrlen);

        // Check if we successfully send data ro server.
        if (bytes_send == -1)
        {
            std::cout << "failed to send a message to the server." << std::endl;
            exit(1);
        }
    }

    // Close the socket.
    close(client_fd);

    return 0;
}