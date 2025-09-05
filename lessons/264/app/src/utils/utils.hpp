#pragma once

#include <prometheus/histogram.h>
#include <string>

namespace utils {
    // Retrieves the current timestamp in nanoseconds since the Unix epoch.
    std::int64_t get_timestamp_ns();

    // Get environment variable.
    std::string get_env(const char* name);

    // Retrieves the bucket boundaries for a Prometheus histogram.
    prometheus::Histogram::BucketBoundaries get_hist_buckets();
}  // namespace utils
