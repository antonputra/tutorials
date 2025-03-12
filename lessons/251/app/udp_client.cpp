#include <unistd.h>
#include <iostream>
#include <netdb.h>
#include <thread>
#include <cstring>

using std::string;
using std::chrono::system_clock;

// 1432 is usually a safe size over WAN, but certain networks may have lower limits and others may have higher limits.
// If doing the test on localhost, this number can be increased to 63k (63 * 1024) which should greatly improve throughput.
#define UDP_BUFSIZE 1432
#define PORT "8080"
// #define ADDRESS "localhost"
#define ADDRESS "udp-server.antonputra.pvt"

using namespace std::literals;

int main()
{
    const char *optimize_env = std::getenv("OPTIMIZE");
    bool optimize = optimize_env && std::strcmp(optimize_env, "true") == 0;

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

    // Fill out the struct. Assign the address of of the server to the socket structure, etc.
    int err;
    if ((err = getaddrinfo(ADDRESS, PORT, &hints, &servinfo)) != 0)
    {
        std::cerr << "getaddrinfo failed: " << gai_strerror(err) << std::endl;
        return 1;
    }

    // Create a socket for the client and return a file descriptor that we can use to send data.
    client_fd = socket(servinfo->ai_family, servinfo->ai_socktype, servinfo->ai_protocol);

    string msg = "{\"id\":66009,\"mac\":\"81-6E-79-DA-5A-B2\",\"firmware\":\"4.0.2\",\"create_at\":170341283583666}";

    // Batch messages together. This helps UDP more than TCP as the kernel will do this automatically
    // for TCP unless TCP_NODELAY is set. TCP will still be helped by the reduced number
    // of syscalls and context switches.
    if (optimize)
    {
        msg.reserve(UDP_BUFSIZE);

        intptr_t batch_count = UDP_BUFSIZE / msg.length() - 1;
        for (; batch_count > 0; --batch_count)
        {
            msg += "{\"id\":66009,\"mac\":\"81-6E-79-DA-5A-B2\",\"firmware\":\"4.0.2\",\"create_at\":170341283583666}";
        }
    }

    while (true)
    {
        // Send data to UDP server. Returns -1 on error.
        bytes_sent = sendto(client_fd, msg.c_str(), msg.length(), 0, servinfo->ai_addr, servinfo->ai_addrlen);

        // Check if we successfully send data ro server.
        if (bytes_sent == -1)
        {
            perror("failed to send a message to the server: ");
            // return 1;
        }
    }

    // Close the socket.
    close(client_fd);

    return 0;
}
