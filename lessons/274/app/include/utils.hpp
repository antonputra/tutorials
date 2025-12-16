#pragma once

#include <chrono>
#include <prometheus/histogram.h>
#include <random>
#include <thread>

inline std::int64_t get_timestamp_ns() {
    // Get current time with nanosecond precision.
    const auto now = std::chrono::high_resolution_clock::now();

    // Convert to nanoseconds since epoch.
    return std::chrono::duration_cast<std::chrono::nanoseconds>(now.time_since_epoch()).count();
}

inline std::string random_string(size_t length, const std::string& chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") {
    thread_local std::mt19937 rg{std::random_device{}()};
    std::uniform_int_distribution<std::string::size_type> pick(0, chars.size() - 1);

    std::string s;
    s.reserve(length);

    while (length--)
        s += chars[pick(rg)];

    return s;
}

inline double random_double(const double min = 0.0, const double max = 1.0) {
    thread_local std::mt19937 rg{std::random_device{}()};
    std::uniform_real_distribution dist(min, max);

    return dist(rg);
}

inline std::int32_t random_int32(const std::int32_t min = 0, const std::int32_t max = 1) {
    thread_local std::mt19937 rg{std::random_device{}()};
    std::uniform_int_distribution dist(min, max);

    return dist(rg);
}

inline std::int64_t random_int64(const std::int64_t min = 0, const std::int64_t max = 1) {
    thread_local std::mt19937 rg{std::random_device{}()};
    std::uniform_int_distribution dist(min, max);

    return dist(rg);
}

inline void throttle(const int rate) {
    static auto window_start = std::chrono::steady_clock::now();
    static int count = 0;

    auto now = std::chrono::steady_clock::now();
    const auto elapsed = now - window_start;

    if (elapsed >= std::chrono::seconds(1)) {
        window_start = now;
        count = 0;
    }

    if (count > rate) {
        auto time_to_next = std::chrono::seconds(1) - elapsed;
        if (time_to_next > std::chrono::nanoseconds(0)) {
            std::this_thread::sleep_for(time_to_next);
        }
        now = std::chrono::steady_clock::now();
        window_start = now;
        count = 0;
    }

    count++;
}

inline void calibrate(TSCNS& tscns) {
    while (true) {
        tscns.calibrate();
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
}

inline prometheus::Histogram::BucketBoundaries get_hist_buckets() {
    // clang-format off
    static const std::vector<double> buckets = {
        1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51,
        53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101,
        103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, 125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, 147, 149, 151,
        153, 155, 157, 159, 161, 163, 165, 167, 169, 171, 173, 175, 177, 179, 181, 183, 185, 187, 189, 191, 193, 195, 197, 199, 201,
        203, 205, 207, 209, 211, 213, 215, 217, 219, 221, 223, 225, 227, 229, 231, 233, 235, 237, 239, 241, 243, 245, 247, 249, 251,
        253, 255, 257, 259, 261, 263, 265, 267, 269, 271, 273, 275, 277, 279, 281, 283, 285, 287, 289, 291, 293, 295, 297, 299, 301,
        303, 305, 307, 309, 311, 313, 315, 317, 319, 321, 323, 325, 327, 329, 331, 333, 335, 337, 339, 341, 343, 345, 347, 349, 351,
        353, 355, 357, 359, 361, 363, 365, 367, 369, 371, 373, 375, 377, 379, 381, 383, 385, 387, 389, 391, 393, 395, 397, 399, 401,
        403, 405, 407, 409, 411, 413, 415, 417, 419, 421, 423, 425, 427, 429, 431, 433, 435, 437, 439, 441, 443, 445, 447, 449, 451,
        453, 455, 457, 459, 461, 463, 465, 467, 469, 471, 473, 475, 477, 479, 481, 483, 485, 487, 489, 491, 493, 495, 497, 499, 501,
        503, 505, 507, 509, 511, 513, 515, 517, 519, 521, 523, 525, 527, 529, 531, 533, 535, 537, 539, 541, 543, 545, 547, 549, 551,
        553, 555, 557, 559, 561, 563, 565, 567, 569, 571, 573, 575, 577, 579, 581, 583, 585, 587, 589, 591, 593, 595, 597, 599, 601,
        603, 605, 607, 609, 611, 613, 615, 617, 619, 621, 623, 625, 627, 629, 631, 633, 635, 637, 639, 641, 643, 645, 647, 649, 651,
        653, 655, 657, 659, 661, 663, 665, 667, 669, 671, 673, 675, 677, 679, 681, 683, 685, 687, 689, 691, 693, 695, 697, 699, 701,
        703, 705, 707, 709, 711, 713, 715, 717, 719, 721, 723, 725, 727, 729, 731, 733, 735, 737, 739, 741, 743, 745, 747, 749, 751,
        753, 755, 757, 759, 761, 763, 765, 767, 769, 771, 773, 775, 777, 779, 781, 783, 785, 787, 789, 791, 793, 795, 797, 799, 801,
        803, 805, 807, 809, 811, 813, 815, 817, 819, 821, 823, 825, 827, 829, 831, 833, 835, 837, 839, 841, 843, 845, 847, 849, 851,
        853, 855, 857, 859, 861, 863, 865, 867, 869, 871, 873, 875, 877, 879, 881, 883, 885, 887, 889, 891, 893, 895, 897, 899, 901,
        903, 905, 907, 909, 911, 913, 915, 917, 919, 921, 923, 925, 927, 929, 931, 933, 935, 937, 939, 941, 943, 945, 947, 949, 951,
        953, 955, 957, 959, 961, 963, 965, 967, 969, 971, 973, 975, 977, 979, 981, 983, 985, 987, 989, 991, 993, 995, 997, 999, 1001,
        1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000,
        2050, 2100, 2150, 2200, 2250, 2300, 2350, 2400, 2450, 2500, 2550, 2600, 2650, 2700, 2750, 2800, 2850, 2900, 2950, 3000,
        3050, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000,
        4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4550, 4600, 4650, 4700, 4750, 4800, 4850, 4900, 4950, 5000,
        5050, 5100, 5150, 5200, 5250, 5300, 5350, 5400, 5450, 5500, 5550, 5600, 5650, 5700, 5750, 5800, 5850, 5900, 5950, 6000,
        6050, 6100, 6150, 6200, 6250, 6300, 6350, 6400, 6450, 6500, 6550, 6600, 6650, 6700, 6750, 6800, 6850, 6900, 6950, 7000
    };
    // clang-format on

    return prometheus::Histogram::BucketBoundaries{buckets};
}
