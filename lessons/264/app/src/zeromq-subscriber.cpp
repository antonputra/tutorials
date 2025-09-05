#include <iostream>
#include <prometheus/exposer.h>
#include <prometheus/histogram.h>
#include <prometheus/registry.h>
#include <spdlog/spdlog.h>
#include <string>
#include <zmq.hpp>

#include "../include/sbe/Bbo.h"
#include "utils/utils.hpp"

using namespace prometheus;

int main() {
    std::string channel;
    zmq::context_t ctx;
    zmq::socket_t sub(ctx, zmq::socket_type::sub);
    sub.set(zmq::sockopt::subscribe, "");

    const auto registry = std::make_shared<Registry>();
    auto &hist = BuildHistogram().Name("zeromq_duration_nanoseconds").Help("Duration of the processing.").Register(*registry);
    auto &duration = hist.Add({{"side", "sub"}}, utils::get_hist_buckets());

    Exposer exposer{"0.0.0.0:" + std::to_string(9070)};
    exposer.RegisterCollectable(registry);

    try {
        channel = utils::get_env("CHANNEL");
        spdlog::info("ZeroMQ channel: {}", channel);
    } catch (const std::exception &e) {
        spdlog::error(e.what());
        return 1;
    }

    sub.connect(channel);

    sbe::Bbo bbo;

    while (true) {
        // Receive via ZeroMQ
        zmq::message_t zmq_msg;
        const auto res = sub.recv(zmq_msg, zmq::recv_flags::none);
        if (!res) {
            continue;
        }

        bbo.wrapForDecode(static_cast<char *>(zmq_msg.data()), sbe::MessageHeader::encodedLength(), sbe::Bbo::sbeBlockLength(), sbe::Bbo::sbeSchemaVersion(), zmq_msg.size());

        // Record how long it takes to process the message.
        duration.Observe(utils::get_timestamp_ns() - bbo.ts_event());
    }

    return 0;
}
