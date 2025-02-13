#include <drogon/drogon.h>

int main()
{
    drogon::app().addListener("0.0.0.0", 8080);

    // Match Rust number of threads which is equal number of CPU cores
    drogon::app().setThreadNum(2);
    drogon::app().run();

    return 0;
}
