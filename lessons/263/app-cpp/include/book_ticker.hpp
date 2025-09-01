#ifndef BOOK_TICKER_HPP
#define BOOK_TICKER_HPP

#include <boost/beast.hpp>
#include <boost/json.hpp>
#include <string>
#include <vector>

namespace beast = boost::beast;
namespace json = boost::json;

struct BookTicker {
    std::string symbol;
    std::string bidPrice;
    std::string bidQty;
    std::string askPrice;
    std::string askQty;
};

std::string serialize_book_tickers(const std::vector<BookTicker>& tickers);

void fail(const beast::error_code& ec, char const* what);

#endif  // BOOK_TICKER_HPP
