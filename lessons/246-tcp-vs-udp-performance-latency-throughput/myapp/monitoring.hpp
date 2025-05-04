#include <string>
#include <vector>

#ifndef MONITORING_HPP_INCLUDED
#define MONITORING_HPP_INCLUDED

// Just for simplicity, declare the constants.
#define MAXDATASIZE 90
#define TIMESTART 69
#define TIMESIZE 20

namespace monitoring
{
    long long get_time();
    long long parse_time(char buf[MAXDATASIZE]);
    std::string generate_payload();
    std::vector<double> get_buckets();
}

#endif