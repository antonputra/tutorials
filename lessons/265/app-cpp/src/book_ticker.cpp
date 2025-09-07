#include "book_ticker.hpp"

#include <boost/json.hpp>

#include "spdlog/spdlog.h"

void tag_invoke(const boost::json::value_from_tag&, boost::json::value& jv, const BookTicker& bt) {
    jv = {
            {"symbol", bt.symbol},
            {"bidPrice", bt.bidPrice},
            {"bidQty", bt.bidQty},
            {"askPrice", bt.askPrice},
            {"askQty", bt.askQty}};
}

std::string serialize_book_tickers(const std::vector<BookTicker>& tickers) {
    return boost::json::serialize(boost::json::value_from(tickers));
}
