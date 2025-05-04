#include "demo_v1_Device.h"

using namespace demo::v1;

struct MDevice
{
    int id;
    std::string mac;
    std::string firmware;

    Json::Value json()
    {
        Json::Value json_data;
        json_data["id"] = id;
        json_data["mac"] = mac;
        json_data["firmware"] = firmware;

        return json_data;
    }
};

void Device::get(const HttpRequestPtr &req, std::function<void(const HttpResponsePtr &)> &&callback)
{
    MDevice myDevice = {0, "5F-33-CC-1F-43-82", "2.1.6"};

    auto res = myDevice.json();
    auto resp = HttpResponse::newHttpJsonResponse(res);

    callback(resp);
}
