#include <string>
#include <vector>

#ifndef MONITORING_HPP_INCLUDED
#define MONITORING_HPP_INCLUDED

namespace monitoring
{
    long long get_time();
    std::vector<double> get_buckets();
}

#endif