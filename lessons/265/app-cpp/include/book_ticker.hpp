#ifndef BOOK_TICKER_HPP
#define BOOK_TICKER_HPP

#include <string>
#include <vector>

struct BookTicker {
    std::string symbol;
    std::string bidPrice;
    std::string bidQty;
    std::string askPrice;
    std::string askQty;
};

std::string serialize_book_tickers(const std::vector<BookTicker>& tickers);

#endif  // BOOK_TICKER_HPP
