#include "event.capnp.h"
#include <capnp/serialize-packed.h>
#include <sw/redis++/redis++.h>
#include <sw/redis++/async_redis++.h>
#include "atomic_queue/atomic_queue.h"
#include "simdjson.h"
#include <iostream>
#include "config.hpp"
#include "monitoring.hpp"
#include "market.hpp"
#include <prometheus/exposer.h>
#include <prometheus/registry.h>
#include <prometheus/histogram.h>

using namespace prometheus;

using Attrs = std::unordered_map<std::string, std::string>;
using Item = std::pair<std::string, sw::redis::Optional<Attrs>>;
using ItemStream = std::vector<Item>;

void consume(config::Config *cfg, prometheus::Histogram *msg_duration, const char* topic)
{
    // Create a result to host Redis data.
    std::unordered_map<std::string, ItemStream> result;

    auto client = sw::redis::Redis(cfg->redis_streams_uri);

    // Consumer group parameters
    const std::string group_name = "my-group";
    const std::string consumer_name = "consumer1";

    try {
        // Create consumer group if it doesn't exist
        // '0' means start from the beginning of the stream
        client.xgroup_create(topic, group_name, "0", true);
    }     catch (const sw::redis::Error& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
    
    while (true)
    {
        // Subscribe to Redis stream.
        client.xreadgroup(group_name, consumer_name, topic, ">", 1, true, std::inserter(result, result.end()));

        if (!result.empty())
        {
            for (const auto &[id, entries] : result[topic])
            {
                auto msg = entries->at("data");
                
                // Deserialize the Cap’n Proto message
                kj::ArrayPtr<const uint8_t> bytes(reinterpret_cast<const uint8_t*>(msg.data()), msg.size());
                kj::ArrayInputStream input(bytes);
                ::capnp::PackedMessageReader reader(input);
                Quote::Reader quote = reader.getRoot<Quote>();

                auto end = monitoring::get_time();
                auto duration = end - quote.getTb();
                msg_duration->Observe(duration);
            }
            result.clear();
        }
    }
}

void produce(atomic_queue::AtomicQueue2<market::RawEvent *, 1024> *queue, config::Config *cfg, const char* topic)
{
    // Create an asynchronous client to publish messages to Redis.
    auto client = sw::redis::AsyncRedis(cfg->redis_streams_uri);

    // Initialize JSON parser.
    simdjson::ondemand::parser parser;

    // Continuously publish messages to Redis.
    while (true)
    {
        // Get the raw JSON event from the queue.
        market::RawEvent *event = queue->pop();

        // Convert the raw event to a padded string.
        simdjson::padded_string padded_json(event->data);

        // Parse the JSON object received from the market data provider.
        simdjson::ondemand::document data = parser.iterate(padded_json);

        // Since the object is an array of events, we need to iterate over each of them.
        for (auto doc : data)
        {
            // Serialize JSON to Cap’n Proto data format.
            auto serialized_data = market::serialize_event(doc);

            // Publish the serialized data to a channel named "quotes"
            client.command<std::string>("XADD", topic, "MAXLEN", "~", "100000", "*", "data", std::string(serialized_data.begin(), serialized_data.end()));
        }
    }
}

int main()
{
    // Load config from the file.
    config::Config cfg = config::load("config.yaml");

    Exposer exposer{"0.0.0.0:" + std::to_string(cfg.metrics_port)};
    auto registry = std::make_shared<Registry>();
    auto buckets = Histogram::BucketBoundaries{monitoring::get_buckets()};
    auto &duration = BuildHistogram().Name("myapp_duration_nanoseconds").Help("Duration of the processing.").Register(*registry);
    auto &msg_duration = duration.Add({{"db", "streams"}}, buckets);
    exposer.RegisterCollectable(registry);

    const char* topic = std::getenv("TOPIC");
    if (topic != nullptr) {
        std::cout << "Value: " << topic << std::endl;
    } else {
        std::cout << "TOPIC environment variable not found" << std::endl;
    }

    // Create multiple-producer-multiple-consumer lock-free queue based on ring buffer.
    atomic_queue::AtomicQueue2<market::RawEvent *, 1024> queue;

    // Create a vector which will hold producer and consumer threads.
    std::vector<std::thread> threads;

    // Start the consumer in its own thread.
    threads.emplace_back([&cfg, &msg_duration, &topic]{ consume(&cfg, &msg_duration, topic); });

    // Start the producer in its own thread and share the queue with it.
    threads.emplace_back([&queue, &cfg, &topic]{ produce(&queue, &cfg, topic); });

    // A sample of an event that you may receive from the exchange or the market data provider.
    std::string event_string = R"([{"ev": "Q","sym": "TSLA","bx": 4,"bp": 114.125,"bs": 100,"ax": 7,"ap": 114.128,"as": 160,"c": 0,"i": [604],"t": 1536036818784,"q": 50385480,"z": 3}])";

    // Create an event struct and push it to the queue.
    market::RawEvent event = market::RawEvent(event_string);

    while (true)
    {
        queue.push(&event);
        std::this_thread::sleep_for(std::chrono::microseconds(cfg.delay_us));
    }
}
