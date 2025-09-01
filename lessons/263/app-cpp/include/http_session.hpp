#ifndef HTTP_SESSION_HPP
#define HTTP_SESSION_HPP

#include <boost/asio.hpp>
#include <boost/beast.hpp>
#include <iomanip>
#include <memory>

namespace beast = boost::beast;
namespace http = beast::http;
namespace asio = boost::asio;
using tcp = asio::ip::tcp;

class http_session : public std::enable_shared_from_this<http_session> {
    beast::tcp_stream stream_;
    beast::flat_buffer buffer_;
    http::request<http::string_body> req_;

public:
    explicit http_session(tcp::socket&& socket);
    void run();

private:
    void do_read();
    void on_read(const beast::error_code& ec);
    void on_write(const beast::error_code& ec, const std::shared_ptr<http::response<http::string_body>>& res);
    void do_close();
};

#endif  // HTTP_SESSION_HPP
