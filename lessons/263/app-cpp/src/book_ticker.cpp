#include "book_ticker.hpp"

#include "spdlog/spdlog.h"

void fail(const beast::error_code& ec, char const* what) {
    spdlog::error("error: {}, {}", what, ec.message());
}

void tag_invoke(const json::value_from_tag&, json::value& jv, const BookTicker& bt) {
    jv = {
            {"symbol", bt.symbol},
            {"bidPrice", bt.bidPrice},
            {"bidQty", bt.bidQty},
            {"askPrice", bt.askPrice},
            {"askQty", bt.askQty}};
}

std::string serialize_book_tickers(const std::vector<BookTicker>& tickers) {
    return boost::json::serialize(json::value_from(tickers));
}
