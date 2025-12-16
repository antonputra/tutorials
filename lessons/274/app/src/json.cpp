#include <glaze/glaze.hpp>

#include "large.hpp"
#include "medium.hpp"
#include "prometheus/exposer.h"
#include "prometheus/histogram.h"
#include "prometheus/registry.h"
#include "small.hpp"
#include "spdlog/spdlog.h"
#include "tscns.h"
#include "utils.hpp"

using namespace prometheus;

constexpr glz::opts write_opts{.minified = true};
constexpr glz::opts read_opts{.null_terminated = false, .error_on_unknown_keys = false, .minified = true};

void generate_quote(Quote& quote) {
    quote.symbol = random_string(4);
    quote.price = random_double(0.0, 500.0);
    quote.timestamp = get_timestamp_ns();
}

void generate_user(User& user) {
    user.user_id = random_int64(0, 10000);
    user.username = random_string(10);
    user.full_name = random_string(10);
    user.email = random_string(10);
    user.phone = random_string(10);
    user.bio = random_string(10);
    user.timezone = random_string(10);
    user.currency = random_string(10);
    user.age = random_int32(0, 10000);
    user.height_cm = random_double(0.0, 500.0);
    user.weight_kg = random_double(0.0, 500.0);
    user.balance = random_double(0.0, 500.0);
    user.score = random_double(0.0, 500.0);
    user.is_active = true;
    user.is_verified = false;
    user.is_premium = true;
    user.created_at = get_timestamp_ns();
    user.last_login = get_timestamp_ns();
}

void generate_user_profile(UserProfile& user_profile) {
    user_profile.userId = random_int64(0, 10000);
    user_profile.username = random_string(20);
    user_profile.firstName = random_string(20);
    user_profile.middleName = random_string(20);
    user_profile.lastName = random_string(20);
    user_profile.fullName = random_string(20);
    user_profile.displayName = random_string(20);
    user_profile.email = random_string(20);
    user_profile.backupEmail = random_string(20);
    user_profile.phone = random_string(20);
    user_profile.phoneCountryCode = random_string(20);
    user_profile.dateOfBirth = random_string(20);
    user_profile.age = random_int32(0, 10000);
    user_profile.gender = random_string(20);
    user_profile.gender = random_string(20);
    user_profile.pronouns = random_string(20);
    user_profile.bio = random_string(20);
    user_profile.website = random_string(20);
    user_profile.locationCity = random_string(20);
    user_profile.locationState = random_string(20);
    user_profile.locationCountry = random_string(20);
    user_profile.locationLat = random_double(0.0, 500.0);
    user_profile.locationLng = random_double(0.0, 500.0);
    user_profile.timezone = random_string(20);
    user_profile.languagePrimary = random_string(20);
    user_profile.currency = random_string(20);
    user_profile.isVerified = true;
    user_profile.isPrivate = true;
    user_profile.isActive = true;
    user_profile.isOnline = true;
    user_profile.isBanned = true;
    user_profile.isDeleted = true;
    user_profile.hasTwoFactor = true;
    user_profile.registrationDate = random_int64(0, 10000);
    user_profile.lastLoginDate = random_int64(0, 10000);
    user_profile.lastActiveDate = random_int64(0, 10000);
    user_profile.subscriptionExpiry = random_int64(0, 10000);
    user_profile.emailVerifiedAt = random_int64(0, 10000);
    user_profile.phoneVerifiedAt = random_int64(0, 10000);
    user_profile.lastPurchaseDate = random_int64(0, 10000);
    user_profile.nextBillingDate = random_int64(0, 10000);
    user_profile.createdAt = random_int64(0, 10000);
    user_profile.updatedAt = random_int64(0, 10000);
    user_profile.deletedAt = random_int64(0, 10000);
    user_profile.profileViewsCount = random_int64(0, 10000);
    user_profile.followersCount = random_int64(0, 10000);
    user_profile.followingCount = random_int64(0, 10000);
    user_profile.postsCount = random_int64(0, 10000);
    user_profile.likesGivenCount = random_int64(0, 10000);
    user_profile.likesReceivedCount = random_int64(0, 10000);
    user_profile.commentsCount = random_int64(0, 10000);
    user_profile.repostsCount = random_int64(0, 10000);
    user_profile.referralsCount = random_int64(0, 10000);
    user_profile.githubRepos = random_int64(0, 10000);
    user_profile.githubStars = random_int64(0, 10000);
    user_profile.githubFollowers = random_int64(0, 10000);
    user_profile.creditsAvailable = random_int64(0, 10000);
    user_profile.rewardPoints = random_int64(0, 10000);
    user_profile.experiencePoints = random_int64(0, 10000);
    user_profile.accountTier = random_string(20);
    user_profile.monthlySpendUSD = random_double(0.0, 500.0);
    user_profile.totalSpendUSD = random_double(0.0, 500.0);
    user_profile.balanceUSD = random_double(0.0, 500.0);
    user_profile.reputationScore = random_int32(0, 10000);
    user_profile.level = random_int32(0, 10000);
    user_profile.dailyStreak = random_int32(0, 10000);
    user_profile.longestStreak = random_int32(0, 10000);
    user_profile.heightCm = random_double(0.0, 500.0);
    user_profile.weightKg = random_double(0.0, 500.0);
    user_profile.bloodType = random_string(20);
    user_profile.dietPreference = random_string(20);
    user_profile.alcohol = random_string(20);
    user_profile.exerciseFrequency = random_string(20);
    user_profile.smoking = true;
    user_profile.sleepHoursAverage = random_double(0.0, 500.0);
    user_profile.favoriteColor = random_string(20);
    user_profile.favoriteFood = random_string(20);
    user_profile.favoriteMovie = random_string(20);
    user_profile.favoriteBook = random_string(20);
    user_profile.favoriteNumber = random_int32(0, 10000);
    user_profile.skillLevelJavaScript = random_double(0.0, 500.0);
    user_profile.skillLevelRust = random_double(0.0, 500.0);
    user_profile.jobTitle = random_string(20);
    user_profile.company = random_string(20);
    user_profile.companyIndustry = random_string(20);
    user_profile.salaryUSD = random_int64(0, 10000);
    user_profile.salaryCurrency = random_string(20);
    user_profile.employmentType = random_string(20);
    user_profile.workLocation = random_string(20);
    user_profile.yearsExperience = random_int32(0, 10000);
    user_profile.educationLevel = random_string(20);
    user_profile.educationField = random_string(20);
    user_profile.university = random_string(20);
    user_profile.graduationYear = random_int32(0, 10000);
    user_profile.gpa = random_double(0.0, 500.0);
    user_profile.githubUsername = random_string(20);
    user_profile.twitterHandle = random_string(20);
    user_profile.linkedinUrl = random_string(20);
    user_profile.portfolioUrl = random_string(20);
    user_profile.preferredContactMethod = random_string(20);
    user_profile.notificationEmail = true;
    user_profile.notificationPush = true;
    user_profile.notificationSMS = true;
    user_profile.darkMode = true;
    user_profile.reducedMotion = true;
    user_profile.highContrast = true;
    user_profile.fontSize = random_string(20);
    user_profile.emailSignature = random_string(20);
    user_profile.statusMessage = random_string(20);
    user_profile.currentMood = random_string(20);
    user_profile.relationshipStatus = random_string(20);
    user_profile.hasChildren = true;
    user_profile.childrenCount = random_int32(0, 10000);
    user_profile.petType = random_string(20);
    user_profile.petName = random_string(20);
    user_profile.carMake = random_string(20);
    user_profile.carModel = random_string(20);
    user_profile.carYear = random_int32(0, 10000);
    user_profile.carColor = random_string(20);
    user_profile.licensePlate = random_string(20);
    user_profile.bitcoinAddress = random_string(20);
    user_profile.ethereumAddress = random_string(20);
    user_profile.ipAddress = random_string(20);
    user_profile.userAgent = random_string(20);
    user_profile.deviceType = random_string(20);
    user_profile.os = random_string(20);
    user_profile.browser = random_string(20);
    user_profile.screenResolution = random_string(20);
    user_profile.timeSpentTodayMinutes = random_int64(0, 10000);
}

void generate_large(UserProfile& user_profile, std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    generate_user_profile(user_profile);

    const int64_t start_tsc = TSCNS::rdtsc();
    if (const auto error = glz::write<write_opts>(user_profile, buffer); !error) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void parse_large(UserProfile& user_profile, const std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    const int64_t start_tsc = TSCNS::rdtsc();
    if (const auto error = glz::read<read_opts>(user_profile, buffer); !error) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void generate_medium(User& user, std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    generate_user(user);

    const int64_t start_tsc = TSCNS::rdtsc();
    if (const auto error = glz::write<write_opts>(user, buffer); !error) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void parse_medium(User& user, const std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    const int64_t start_tsc = TSCNS::rdtsc();
    if (const auto error = glz::read<read_opts>(user, buffer); !error) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void generate_small(Quote& quote, std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    generate_quote(quote);

    const int64_t start_tsc = TSCNS::rdtsc();
    if (const auto error = glz::write<write_opts>(quote, buffer); !error) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void parse_small(Quote& quote, const std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    const int64_t start_tsc = TSCNS::rdtsc();
    if (const auto error = glz::read<read_opts>(quote, buffer); !error) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

int main(int argc, char* argv[]) {
    const std::string test = argv[1];

    TSCNS tscns;
    tscns.init();

    std::vector<std::thread> threads;
    threads.emplace_back([&tscns] { calibrate(tscns); });

    // Prometheus setup
    Exposer exposer{"0.0.0.0:8082"};
    const auto registry = std::make_shared<Registry>();
    auto& hist_fam = BuildHistogram().Name("app_duration_nanoseconds").Register(*registry);
    auto& gauge_fam = BuildGauge().Name("app_info").Register(*registry);
    exposer.RegisterCollectable(registry);

    auto& serialize_hist = hist_fam.Add({{"type", "json"}, {"op", "serialize"}}, get_hist_buckets());
    auto& deserialize_hist = hist_fam.Add({{"type", "json"}, {"op", "deserialize"}}, get_hist_buckets());
    auto& size_gauge = gauge_fam.Add({{"type", "json"}, {"op", "size"}});

    std::string buffer;

    if (test == "small") {
        // Only to measure size
        Quote quote;
        generate_quote(quote);
        if (const auto error = glz::write<write_opts>(quote, buffer); !error)
            size_gauge.Set(buffer.size());

        while (true) {
            generate_small(quote, buffer, tscns, serialize_hist);
            parse_small(quote, buffer, tscns, deserialize_hist);
        }
    }

    if (test == "medium") {
        User user;
        generate_user(user);
        if (const auto error = glz::write<write_opts>(user, buffer); !error)
            size_gauge.Set(buffer.size());

        while (true) {
            generate_medium(user, buffer, tscns, serialize_hist);
            parse_medium(user, buffer, tscns, deserialize_hist);
        }
    }

    if (test == "large") {
        UserProfile user_profile;
        if (const auto error = glz::write<write_opts>(user_profile, buffer); !error)
            size_gauge.Set(buffer.size());

        while (true) {
            generate_large(user_profile, buffer, tscns, serialize_hist);
            parse_large(user_profile, buffer, tscns, deserialize_hist);
        }
    }
}
