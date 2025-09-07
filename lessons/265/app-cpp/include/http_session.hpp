#ifndef HTTP_SESSION_HPP
#define HTTP_SESSION_HPP

#include <boost/asio/spawn.hpp>
#include <boost/beast.hpp>

void do_session(boost::beast::tcp_stream& stream, boost::asio::yield_context yield);

#endif  // HTTP_SESSION_HPP
