#include "utils.hpp"

#include <spdlog/spdlog.h>

void fail(const boost::beast::error_code& ec, char const* what) {
    spdlog::error("error: {}, {}", what, ec.message());
}
