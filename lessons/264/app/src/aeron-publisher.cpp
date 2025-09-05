#include <Aeron.h>
#include <random>
#include <spdlog/spdlog.h>

#include "../include/sbe/Bbo.h"
#include "utils/utils.hpp"

using namespace aeron;


// Generate the BBO (Best Bid and Offer) and send it to the client using Aeron.
void produce_bbo(const std::shared_ptr<ExclusivePublication>& pub_, int64_t sleep_interval_us, const int64_t stage_interval_us, const int64_t decrement_interval_us) {
    // Static random number generation setup
    static std::minstd_rand gen(std::random_device{}());
    static std::uniform_int_distribution<> distr(1, 1000000);

    // Pre-allocate buffer and objects outside the loop
    constexpr std::size_t buffer_length = 256;
    alignas(16) std::uint8_t buffer_data[buffer_length];

    const AtomicBuffer msg_buffer(buffer_data, buffer_length);

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
        header.wrap(reinterpret_cast<char*>(buffer_data), 0, 0, buffer_length).blockLength(block_length).templateId(template_id).schemaId(schema_id).version(schema_version);
        bbo.wrapForEncode(reinterpret_cast<char*>(buffer_data), header_length, buffer_length);

        // Generate random values
        bbo.putSymbol("BTCUSDT");
        bbo.bid_price(distr(gen));
        bbo.bid_volume(distr(gen));
        bbo.ask_price(distr(gen));
        bbo.ask_volume(distr(gen));
        bbo.ts_event(utils::get_timestamp_ns());

        const std::size_t total_length = header_length + bbo.encodedLength();

        switch (pub_->offer(msg_buffer, 0, total_length)) {
            case BACK_PRESSURED:
                spdlog::warn("Back pressure detected");
                break;
            case NOT_CONNECTED:
                spdlog::warn("Publisher not connected to a subscriber");
                break;
            case ADMIN_ACTION:
                spdlog::warn("Admin action blocked publication");
                break;
            case PUBLICATION_CLOSED:
                spdlog::warn("Publication closed");
                break;
            default:
                // Success case - no logging needed
                break;
        }

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
    int32_t stream_id = 1001;

    // Initialize pointers as nullptr for clarity
    std::shared_ptr<Aeron> client = nullptr;
    std::shared_ptr<ExclusivePublication> publication = nullptr;

    try {
        channel = utils::get_env("CHANNEL");
        sleep_interval_us = std::stoll(utils::get_env("SLEEP_INTERVAL_US"));
        stage_interval_us = std::stoll(utils::get_env("STAGE_INTERVAL_US"));
        decrement_interval_us = std::stoll(utils::get_env("DECREMENT_INTERVAL_US"));

        spdlog::info("Aeron CHANNEL: {}", channel);
        spdlog::info("Aeron SLEEP_INTERVAL_US: {}", sleep_interval_us);
        spdlog::info("Aeron STAGE_INTERVAL_US: {}", stage_interval_us);
        spdlog::info("Aeron DECREMENT_INTERVAL_US: {}", decrement_interval_us);
    } catch (const std::exception& e) {
        spdlog::error(e.what());
        return 1;
    }

    try {
        // Configure context with minimal allocations
        Context context;

        // Connect to Aeron
        client = Aeron::connect(context);

        // Add exclusive publication if you have a single producer and do not need thread safety.
        const std::int64_t id = client->addExclusivePublication(channel, stream_id);

        // Wait for the publication to be valid.
        while (!publication) {
            std::this_thread::yield();
            publication = client->findExclusivePublication(id);
        }
        spdlog::info("Aeron publisher is created");

    } catch (const std::exception& e) {
        spdlog::error("Aeron connection failed: {}", e.what());
        return 1;
    }

    // Generate and publish BBOs.
    produce_bbo(publication, sleep_interval_us, stage_interval_us, decrement_interval_us);

    return 0;
}
