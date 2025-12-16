/*
MIT License

Copyright (c) 2022 Meng Rao <raomeng1@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#pragma once
#include <chrono>
#include <atomic>
#include <thread>

#ifdef _MSC_VER
#include <intrin.h>
#endif

class TSCNS
{
public:
  static const int64_t NsPerSec = 1000000000;

  void init(int64_t init_calibrate_ns = 20000000, int64_t calibrate_interval_ns = 3 * NsPerSec) {
    calibate_interval_ns_ = calibrate_interval_ns;
    int64_t base_tsc, base_ns;
    syncTime(base_tsc, base_ns);
    int64_t expire_ns = base_ns + init_calibrate_ns;
    while (rdsysns() < expire_ns) std::this_thread::yield();
    int64_t delayed_tsc, delayed_ns;
    syncTime(delayed_tsc, delayed_ns);
    double init_ns_per_tsc = (double)(delayed_ns - base_ns) / (delayed_tsc - base_tsc);
    saveParam(base_tsc, base_ns, 0, init_ns_per_tsc);
  }

  void calibrate() {
    if (rdtsc() < next_calibrate_tsc_) return;
    int64_t tsc, ns;
    syncTime(tsc, ns);
    int64_t ns_err = tsc2ns(tsc) - ns;
    if (ns_err > 1000000) ns_err = 1000000;
    if (ns_err < -1000000) ns_err = -1000000;
    double new_ns_per_tsc =
      ns_per_tsc_ * (1.0 - (ns_err + ns_err - base_ns_err_) / ((tsc - base_tsc_) * ns_per_tsc_));
    saveParam(tsc, ns, ns_err, new_ns_per_tsc);
  }

  static inline int64_t rdtsc() {
#ifdef _MSC_VER
    return __rdtsc();
#elif defined(__i386__) || defined(__x86_64__) || defined(__amd64__)
    return __builtin_ia32_rdtsc();
#else
    return rdsysns();
#endif
  }

  inline int64_t tsc2ns(int64_t tsc) const {
    while (true) {
      uint32_t before_seq = param_seq_.load(std::memory_order_acquire) & ~1;
      std::atomic_signal_fence(std::memory_order_acq_rel);
      int64_t ns = base_ns_ + (int64_t)((tsc - base_tsc_) * ns_per_tsc_);
      std::atomic_signal_fence(std::memory_order_acq_rel);
      uint32_t after_seq = param_seq_.load(std::memory_order_acquire);
      if (before_seq == after_seq) return ns;
    }
  }

  inline int64_t rdns() const { return tsc2ns(rdtsc()); }

  static inline int64_t rdsysns() {
    using namespace std::chrono;
    return duration_cast<nanoseconds>(system_clock::now().time_since_epoch()).count();
  }

  double getTscGhz() const { return 1.0 / ns_per_tsc_; }

  // Linux kernel sync time by finding the first trial with tsc diff < 50000
  // We try several times and return the one with the mininum tsc diff.
  // Note that MSVC has a 100ns resolution clock, so we need to combine those ns with the same
  // value, and drop the first and the last value as they may not scan a full 100ns range
  static void syncTime(int64_t& tsc_out, int64_t& ns_out) {
#ifdef _MSC_VER
    const int N = 15;
#else
    const int N = 3;
#endif
    int64_t tsc[N + 1];
    int64_t ns[N + 1];

    tsc[0] = rdtsc();
    for (int i = 1; i <= N; i++) {
      ns[i] = rdsysns();
      tsc[i] = rdtsc();
    }

#ifdef _MSC_VER
    int j = 1;
    for (int i = 2; i <= N; i++) {
      if (ns[i] == ns[i - 1]) continue;
      tsc[j - 1] = tsc[i - 1];
      ns[j++] = ns[i];
    }
    j--;
#else
    int j = N + 1;
#endif

    int best = 1;
    for (int i = 2; i < j; i++) {
      if (tsc[i] - tsc[i - 1] < tsc[best] - tsc[best - 1]) best = i;
    }
    tsc_out = (tsc[best] + tsc[best - 1]) >> 1;
    ns_out = ns[best];
  }

  void saveParam(int64_t base_tsc, int64_t sys_ns, int64_t base_ns_err, double new_ns_per_tsc) {
    base_ns_err_ = base_ns_err;
    next_calibrate_tsc_ = base_tsc + (int64_t)((calibate_interval_ns_ - 1000) / new_ns_per_tsc);
    uint32_t seq = param_seq_.load(std::memory_order_relaxed);
    param_seq_.store(++seq, std::memory_order_release);
    std::atomic_signal_fence(std::memory_order_acq_rel);
    base_tsc_ = base_tsc;
    base_ns_ = sys_ns + base_ns_err;
    ns_per_tsc_ = new_ns_per_tsc;
    std::atomic_signal_fence(std::memory_order_acq_rel);
    param_seq_.store(++seq, std::memory_order_release);
  }

  alignas(64) std::atomic<uint32_t> param_seq_ = 0;
  double ns_per_tsc_;
  int64_t base_tsc_;
  int64_t base_ns_;
  int64_t calibate_interval_ns_;
  int64_t base_ns_err_;
  int64_t next_calibrate_tsc_;
};