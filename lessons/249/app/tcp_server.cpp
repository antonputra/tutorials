#include <unistd.h>
#include <netdb.h>
#include <iostream>
#include <thread>
#include <cstring>
#include "monitoring.hpp"

using std::string;
using std::chrono::system_clock;

// Port on the server to listen for incoming connections.
#define PORT "8080"

using namespace std::literals;
// Declare some variables for the test.
int stage_count = 1;
//auto stage_interval = 1000s;
//auto sleep_time = 100000000us;
auto stage_interval = 0s;
auto sleep_time = 1us;

// Number of pending connections the server will hold (queue size).
#define BACKLOG 10

int main(void)
{
    const char *enable_monitoring_env = std::getenv("ENABLE_MONITORING");
    bool enable_monitoring = enable_monitoring_env && std::strcmp(enable_monitoring_env, "true") == 0;

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
        perror("bind failed");
        return 1;
    }

    // Start listening for incoming connections. Returns -1 on error.
    int listen_result = listen(server_fd, BACKLOG);

    // Check if we successfully started to listen on port 8080.
    if (listen_result != 0)
    {
        perror("listen failed");
        return 1;
    }

    // Get the size of the client IP address, IPv4 or IPv6.
    socklen_t sin_size = sizeof client_addr;

    // Get the local file descriptor that was created for the client. We can use it directly to write data to it.
    client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &sin_size);

    if (client_fd == -1)
    {
        perror("accept failed");
        return 1;
    }

    std::cout << "client's socket file descriptor is " << client_fd << std::endl;

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

            // Send data to the client.
            bytes_sent = send(client_fd, msg.data(), msg.length(), 0);

            // Check if we successfully sent data to the client.
            if (bytes_sent == -1)
            {
                std::cerr << "failed to send a message to the client" << std::endl;
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

            // Sleep to add a delay between sending messages to the client.
            std::this_thread::sleep_for(sleep_time);
        }
    }

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

        // Send data to the client.
        bytes_sent = send(client_fd, msg.data(), msg.length(), 0);

        // Check if we successfully sent data to the client.
        if (bytes_sent == -1)
        {
            perror("send failed");
            return 1;
        }
    }

    // graceful shutdown
    shutdown(client_fd, SHUT_RDWR);
    close(client_fd);

    return 0;
}
