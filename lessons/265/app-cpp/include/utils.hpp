#ifndef UTILS_HPP
#define UTILS_HPP

#include <boost/beast/core/error.hpp>

void fail(const boost::beast::error_code& ec, char const* what);

#endif  // UTILS_HPP
