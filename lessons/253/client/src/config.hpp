#ifndef CONFIG_HPP_INCLUDED
#define CONFIG_HPP_INCLUDED

namespace config
{
    struct Config
    {
        std::string redis_pubsub_uri;
        std::string redis_streams_uri;
        int delay_us;
        int metrics_port;
    };

    Config load(std::string path);
}

#endif