#pragma once

#include <drogon/HttpController.h>

using namespace drogon;

namespace demo
{
  namespace v1
  {
    class Device : public drogon::HttpController<Device>
    {
    public:
      METHOD_LIST_BEGIN

      ADD_METHOD_TO(Device::get, "/api/devices", Get);

      METHOD_LIST_END

      void get(const HttpRequestPtr &req, std::function<void(const HttpResponsePtr &)> &&callback);
    };
  }
}
