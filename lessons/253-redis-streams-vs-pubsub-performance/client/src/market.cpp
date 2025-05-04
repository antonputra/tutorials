#include "simdjson.h"
#include "market.hpp"
#include "event.capnp.h"
#include <capnp/message.h>
#include "monitoring.hpp"
#include <capnp/serialize-packed.h>

template <>
simdjson_inline simdjson::simdjson_result<market::Event> simdjson::ondemand::value::get() noexcept
{
    ondemand::object obj;

    auto error = get_object().get(obj);
    if (error)
    {
        return error;
    }

    market::Event event;
    if ((error = obj["ev"].get_string(event.ev)))
    {
        return error;
    }
    if ((error = obj["sym"].get_string(event.sym)))
    {
        return error;
    }
    if ((error = obj["bx"].get_int64().get(event.bx)))
    {
        return error;
    }
    if ((error = obj["bp"].get_double().get(event.bp)))
    {
        return error;
    }
    if ((error = obj["bs"].get_int64().get(event.bs)))
    {
        return error;
    }
    if ((error = obj["ax"].get_int64().get(event.ax)))
    {
        return error;
    }
    if ((error = obj["ap"].get_double().get(event.ap)))
    {
        return error;
    }
    if ((error = obj["as"].get_int64().get(event.as)))
    {
        return error;
    }
    if ((error = obj["c"].get_int64().get(event.c)))
    {
        return error;
    }
    if ((error = obj["i"].get<std::vector<int64_t>>().get(event.i)))
    {
        return error;
    }
    if ((error = obj["t"].get_int64().get(event.t)))
    {
        return error;
    }
    if ((error = obj["q"].get_int64().get(event.q)))
    {
        return error;
    }
    if ((error = obj["z"].get_int64().get(event.z)))
    {
        return error;
    }

    return event;
}

std::vector<uint8_t> market::serialize_event(simdjson::simdjson_result<simdjson::ondemand::value> doc)
{
    market::Event event(doc);
    
    // Create a message builder
    capnp::MallocMessageBuilder message;
    Quote::Builder quote = message.initRoot<Quote>();

    long long tb = monitoring::get_time();

    // Populate the message
    quote.setEv(event.ev);
    quote.setSym(event.sym);
    quote.setBx(event.bx);
    quote.setBp(event.bp);
    quote.setBs(event.bs);
    quote.setAx(event.ax);
    quote.setAp(event.ap);
    quote.setAs(event.as);
    quote.setC(event.c);
    quote.setT(event.t);
    quote.setQ(event.q);
    quote.setZ(event.z);
    quote.setTb(tb);

    // Serialize to packed format
    kj::VectorOutputStream output;
    capnp::writePackedMessage(output, message);

    // Get the packed bytes
    kj::ArrayPtr<const uint8_t> packed_bytes = output.getArray();
    std::vector<uint8_t> serialized_data(packed_bytes.begin(), packed_bytes.end());

    return serialized_data;
}