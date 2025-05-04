#include <unistd.h>
#include <iostream>
#include <netdb.h>
#include <thread>
#include <cstring>
#include "monitoring.hpp"

using std::string;
using std::chrono::system_clock;

#define PORT "8080"
//#define ADDRESS "udp-server.antonputra.pvt"
#define ADDRESS "localhost"

using namespace std::literals;
// Declare some variables for the test.
int stage_count = 1;
auto stage_interval = 0s;
auto sleep_time = 1us;

int main()
{
    const char *enable_monitoring_env = std::getenv("ENABLE_MONITORING");
    bool enable_monitoring = enable_monitoring_env && std::strcmp(enable_monitoring_env, "true") == 0;

    // This variable hold file descriptor. We use them to read and write data.
    int client_fd, bytes_send;

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

    // Fill out the struct. Assign the address of of the server to the socket structure, etc.
    int err;
    if ((err = getaddrinfo(NULL, PORT, &hints, &servinfo)) != 0)
    {
        std::cerr << "getaddrinfo failed: " << gai_strerror(err) << std::endl;
        return 1;
    }

    // Create a socket for the client and return a file descriptor that we can use to send data.
    client_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    string msg = "{\"id\":66009,\"mac\":\"81-6E-79-DA-5A-B2\",\"firmware\":\"4.0.2\",\"create_at\": 170341283583666}";

    // Batch messages together. This helps UDP more than TCP as the kernel will do this automatically
    // for TCP unless TCP_NODELAY is set. TCP will still be helped by the reduced number
    // of syscalls and context switches.
    msg.reserve(UDP_BUFSIZE);
    if (!enable_monitoring)
    {
        intptr_t batch_count = UDP_BUFSIZE / msg.length() - 1;
        for(; batch_count > 0; --batch_count)
        {
            msg += "{\"id\":66009,\"mac\":\"81-6E-79-DA-5A-B2\",\"firmware\":\"4.0.2\",\"create_at\": 170341283583666}";
        }
    }

    for (int stage = 0; stage < stage_count; stage++)
    {
        // Get the start time of the stage.
        auto start_time = system_clock::now();

        // When the client establishes a connection, continuously send the same message over and over.
        while (true)
        {
            // Sleep to add a delay between sending messages to the client.
            std::this_thread::sleep_for(sleep_time);

            if (enable_monitoring)
            {
                // Generate a payload message with a timestamp to measure the duration.
                msg.clear();
                while(msg.length() + MAXDATASIZE < UDP_BUFSIZE)
                {
                    char buf[MAXDATASIZE];
                    monitoring::generate_payload(buf);
                    msg += buf;
                }
            }

            // Send data to UDP server. Returns -1 on error.
            bytes_send = sendto(client_fd, msg.data(), msg.length(), 0, servinfo->ai_addr, servinfo->ai_addrlen);

            // Check if we successfully send data ro server.
            if (bytes_send == -1)
            {
                perror("failed to send a message to the server: ");
                return 1;
            }

            // Get the current time.
            auto elapsed_time = system_clock::now() - start_time;

            // Finish the state based on the time elapsed.
            if (elapsed_time > stage_interval)
            {
                sleep_time -= 1us;
                std::cout << stage << " stage is finished, sleeping now for: " << sleep_time.count() << " microseconds" << std::endl;
                break;
            }
        }
    }

    // Run the final stage in its own loop to eliminate all other function calls and comparisons.
    std::cout << "Starting the final stage." << std::endl;
    while (true)
    {
        if (enable_monitoring)
        {
            // Generate a payload message with a timestamp to measure the duration.
            msg.clear();
            while(msg.length() + MAXDATASIZE < UDP_BUFSIZE)
            {
              char buf[MAXDATASIZE];
              monitoring::generate_payload(buf);
              msg += buf;
            }
        }

        // Send data to UDP server. Returns -1 on error.
        bytes_send = sendto(client_fd, msg.c_str(), msg.length(), 0, servinfo->ai_addr, servinfo->ai_addrlen);

        // Check if we successfully send data ro server.
        if (bytes_send == -1)
        {
            std::cout << "failed to send a message to the server." << std::endl;
            return 1;
        }
    }

    // Close the socket.
    close(client_fd);

    return 0;
}
