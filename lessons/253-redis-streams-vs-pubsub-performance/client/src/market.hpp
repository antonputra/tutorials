#ifndef MARKET_HPP_INCLUDED
#define MARKET_HPP_INCLUDED

#include <iostream>

namespace market
{
    // A struct to hold market data events.
    struct RawEvent
    {
        // Data field which holds raw JSON payload.
        std::string data;

        // Custom constructor to initialize the event.
        RawEvent(const std::string &n) : data(n) {};
    };

    struct Event
    {
        std::string ev;
        std::string sym;
        int64_t bx;
        double bp;
        int64_t bs;
        int64_t ax;
        double ap;
        int64_t as;
        int64_t c;
        std::vector<int64_t> i;
        int64_t t;
        int64_t q;
        int64_t z;
    };

    std::vector<uint8_t> serialize_event(simdjson::simdjson_result<simdjson::ondemand::value> doc);
}

#endif