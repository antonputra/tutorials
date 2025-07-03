#include <string>
#include <vector>

#ifndef MONITORING_HPP_INCLUDED
#define MONITORING_HPP_INCLUDED

// Just for simplicity, declare the constants.
#define MAXDATASIZE 90
#define TIMESTART 69
#define TIMESIZE 20
// 1432 is usually a safe size over WAN, but certain networks may have lower limits and others may have higher limits.
// If doing the test on localhost, this number can be increased to 63k (63 * 1024) which should greatly improve throughput.
#define UDP_BUFSIZE 1432
//#define UDP_BUFSIZE 63 * 1024

namespace monitoring
{
    long long get_time();
    long long parse_time(char buf[MAXDATASIZE]);
    size_t generate_payload(char buf[MAXDATASIZE]);
    std::vector<double> get_buckets();
}

#endif
