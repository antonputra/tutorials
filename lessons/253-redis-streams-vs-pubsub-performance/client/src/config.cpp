#include "yaml-cpp/yaml.h"
#include "config.hpp"

template <>
struct YAML::convert<config::Config>
{
    static Node encode(const config::Config &rhs)
    {
        Node node;
        node["redis_pubsub_uri"] = rhs.redis_pubsub_uri;
        node["redis_streams_uri"] = rhs.redis_streams_uri;
        node["delay_us"] = rhs.delay_us;
        node["metrics_port"] = rhs.metrics_port;
        return node;
    }

    static bool decode(const Node &node, config::Config &rhs)
    {
        if (!node.IsMap() || node.size() != 4)
        {
            return false;
        }
        rhs.redis_pubsub_uri = node["redis_pubsub_uri"].as<std::string>();
        rhs.redis_streams_uri = node["redis_streams_uri"].as<std::string>();
        rhs.delay_us = node["delay_us"].as<int>();
        rhs.metrics_port = node["metrics_port"].as<int>();
        return true;
    }
};

config::Config config::load(std::string path)
{
    return YAML::LoadFile(path).as<config::Config>();
}