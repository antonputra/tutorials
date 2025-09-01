#ifndef LISTENER_HPP
#define LISTENER_HPP

#include <boost/asio.hpp>
#include <boost/beast.hpp>
#include <memory>

namespace beast = boost::beast;
namespace asio = boost::asio;
using tcp = asio::ip::tcp;

class listener : public std::enable_shared_from_this<listener> {
    asio::io_context& ioc_;
    tcp::acceptor acceptor_;
    tcp::socket socket_;

public:
    listener(asio::io_context& ioc, const tcp::endpoint& endpoint);
    void run();

private:
    void do_accept();
    void on_accept(const beast::error_code& ec);
};

#endif  // LISTENER_HPP
