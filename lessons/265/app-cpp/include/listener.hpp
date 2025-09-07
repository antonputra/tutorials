#ifndef LISTENER_HPP
#define LISTENER_HPP

#include <boost/asio.hpp>
#include <boost/asio/spawn.hpp>
#include <boost/beast.hpp>

void do_listen(boost::asio::io_context& ioc, const boost::asio::ip::tcp::endpoint& endpoint, const boost::asio::yield_context& yield);

#endif  // LISTENER_HPP
