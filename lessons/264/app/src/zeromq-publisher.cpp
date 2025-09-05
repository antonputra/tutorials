#include <chrono>
#include <iostream>
#include <random>
#include <spdlog/spdlog.h>
#include <string>
#include <thread>
#include <zmq.hpp>

#include "../include/sbe/Bbo.h"
#include "utils/utils.hpp"

void produce_bbo(zmq::socket_t &pub, int64_t sleep_interval_us, const int64_t stage_interval_us, const int64_t decrement_interval_us) {
    // Static random number generation setup
    static std::minstd_rand gen(std::random_device{}());
    static std::uniform_int_distribution<> distr(1, 1000000);

    constexpr std::size_t buffer_length = 256;
    alignas(16) std::uint8_t buffer_data[buffer_length];

    // Pre-compute constant values
    constexpr std::size_t header_length = sbe::MessageHeader::encodedLength();
    constexpr std::size_t block_length = sbe::Bbo::sbeBlockLength();
    constexpr std::uint16_t template_id = sbe::Bbo::sbeTemplateId();
    constexpr std::uint16_t schema_id = sbe::Bbo::sbeSchemaId();
    constexpr std::uint16_t schema_version = sbe::Bbo::sbeSchemaVersion();

    // Reuse header and BBO objects
    sbe::MessageHeader header;
    sbe::Bbo bbo;

    int64_t now = utils::get_timestamp_ns();

    while (true) {
        // Reset buffer position
        header.wrap(reinterpret_cast<char *>(buffer_data), 0, 0, buffer_length).blockLength(block_length).templateId(template_id).schemaId(schema_id).version(schema_version);
        bbo.wrapForEncode(reinterpret_cast<char *>(buffer_data), header_length, buffer_length);

        // Generate random values
        bbo.putSymbol("BTCUSDT");
        bbo.bid_price(distr(gen));
        bbo.bid_volume(distr(gen));
        bbo.ask_price(distr(gen));
        bbo.ask_volume(distr(gen));
        bbo.ts_event(utils::get_timestamp_ns());

        const std::size_t total_length = header_length + bbo.encodedLength();

        zmq::message_t message(buffer_data, total_length);
        pub.send(message, zmq::send_flags::none);

        if (sleep_interval_us > 0) {
            const auto current_time_ns = utils::get_timestamp_ns();
            const auto elapsed_ns = current_time_ns - now;
            if (elapsed_ns >= stage_interval_us * 1'000) {
                sleep_interval_us -= decrement_interval_us;
                now = current_time_ns;
                spdlog::info("Sleep interval {}us", sleep_interval_us);
            }
            std::this_thread::sleep_for(std::chrono::microseconds(sleep_interval_us));
        }
    }
}


int main() {
    std::string channel;
    int64_t sleep_interval_us;
    int64_t stage_interval_us;
    int64_t decrement_interval_us;
    zmq::context_t ctx;
    zmq::socket_t pub(ctx, zmq::socket_type::pub);

    try {
        channel = utils::get_env("CHANNEL");
        sleep_interval_us = std::stoll(utils::get_env("SLEEP_INTERVAL_US"));
        stage_interval_us = std::stoll(utils::get_env("STAGE_INTERVAL_US"));
        decrement_interval_us = std::stoll(utils::get_env("DECREMENT_INTERVAL_US"));

        spdlog::info("ZeroMQ CHANNEL: {}", channel);
        spdlog::info("ZeroMQ SLEEP_INTERVAL_US: {}", sleep_interval_us);
        spdlog::info("ZeroMQ STAGE_INTERVAL_US: {}", stage_interval_us);
        spdlog::info("ZeroMQ DECREMENT_INTERVAL_US: {}", decrement_interval_us);
    } catch (const std::exception &e) {
        spdlog::error(e.what());
        return 1;
    }

    pub.bind(channel);
    produce_bbo(pub, sleep_interval_us, stage_interval_us, decrement_interval_us);

    return 0;
}
