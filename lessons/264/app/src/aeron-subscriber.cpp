#include <Aeron.h>
#include <prometheus/exposer.h>
#include <prometheus/histogram.h>
#include <prometheus/registry.h>
#include <spdlog/spdlog.h>

#include "../include/sbe/Bbo.h"
#include "FragmentAssembler.h"
#include "concurrent/BusySpinIdleStrategy.h"
#include "utils/utils.hpp"

using namespace prometheus;
using namespace aeron;

fragment_handler_t process_bbo(Histogram &duration) {
    return [&duration](const AtomicBuffer &buffer, const index_t offset, const index_t length, const Header &hdr) {
        // Precompute base pointer to minimize casts and arithmetic
        const auto base = reinterpret_cast<const char *>(buffer.buffer());
        const auto msg_ptr = base + offset;

        sbe::Bbo bbo;
        bbo.wrapForDecode(const_cast<char *>(msg_ptr), sbe::MessageHeader::encodedLength(), sbe::Bbo::sbeBlockLength(), sbe::Bbo::sbeSchemaVersion(), length);

        // Record how long it takes to process the message.
        duration.Observe(utils::get_timestamp_ns() - bbo.ts_event());
    };
}

int main() {
    std::string channel;
    int32_t stream_id = 1001;

    // Initialize pointers as nullptr for clarity
    std::shared_ptr<Aeron> client = nullptr;
    std::shared_ptr<Subscription> subscription = nullptr;

    try {
        channel = utils::get_env("CHANNEL");
        spdlog::info("Aeron channel: {}", channel);
    } catch (const std::exception &e) {
        spdlog::error(e.what());
        return 1;
    }

    const auto registry = std::make_shared<Registry>();
    auto &hist = BuildHistogram().Name("aeron_duration_nanoseconds").Help("Duration of the processing.").Register(*registry);
    auto &duration = hist.Add({{"side", "sub"}}, utils::get_hist_buckets());

    Exposer exposer{"0.0.0.0:" + std::to_string(9070)};
    exposer.RegisterCollectable(registry);

    try {
        Context context;

        // Connect to Aeron
        client = Aeron::connect(context);
        const std::int64_t sub_id = client->addSubscription(channel, stream_id);
        subscription = client->findSubscription(sub_id);

        // Wait until subscription is available
        while (!subscription) {
            std::this_thread::yield();
            subscription = client->findSubscription(sub_id);
        }

        // Validate subscription
        if (subscription->isClosed()) {
            throw std::runtime_error("Subscription is closed or invalid");
        }

        spdlog::info("The subscription has been successfully connected");

        // Fragment assembler for handling fragments
        FragmentAssembler fragment_assembler(process_bbo(duration));
        fragment_handler_t handler = fragment_assembler.handler();
        BusySpinIdleStrategy busy_strategy;

        // Poll loop
        while (true) {
            const int fragmentsRead = subscription->poll(handler, 10);
            busy_strategy.idle(fragmentsRead);
        }

    } catch (const std::exception &e) {
        throw std::runtime_error(fmt::format("Aeron connection failed: {}", e.what()));
    }

    return 0;
}
