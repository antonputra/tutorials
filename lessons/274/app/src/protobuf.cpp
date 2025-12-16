#include "prometheus/exposer.h"
#include "prometheus/histogram.h"
#include "prometheus/registry.h"
#include "proto/large.pb.h"
#include "proto/medium.pb.h"
#include "proto/small.pb.h"
#include "spdlog/spdlog.h"
#include "tscns.h"
#include "utils.hpp"

using namespace prometheus;

void generate_quote(market::Quote& quote) {
    quote.set_symbol(random_string(4));
    quote.set_price(random_double(0.0, 500.0));
    quote.set_timestamp(get_timestamp_ns());
}

void generate_user(market::User& user) {
    user.set_user_id(random_int64(0, 10000));
    user.set_username(random_string(10));
    user.set_full_name(random_string(10));
    user.set_email(random_string(10));
    user.set_phone(random_string(10));
    user.set_bio(random_string(10));
    user.set_timezone(random_string(10));
    user.set_currency(random_string(10));
    user.set_age(random_int32(0, 10000));
    user.set_height_cm(random_double(0.0, 500.0));
    user.set_weight_kg(random_double(0.0, 500.0));
    user.set_balance(random_double(0.0, 500.0));
    user.set_score(random_double(0.0, 500.0));
    user.set_is_active(true);
    user.set_is_verified(false);
    user.set_is_premium(true);
    user.set_created_at(get_timestamp_ns());
    user.set_last_login(get_timestamp_ns());
}

void generate_user_profile(market::UserProfile& user_profile) {
    user_profile.set_user_id(random_int64(0, 10000));
    user_profile.set_username(random_string(20));
    user_profile.set_first_name(random_string(20));
    user_profile.set_middle_name(random_string(20));
    user_profile.set_last_name(random_string(20));
    user_profile.set_full_name(random_string(20));
    user_profile.set_display_name(random_string(20));
    user_profile.set_email(random_string(20));
    user_profile.set_backup_email(random_string(20));
    user_profile.set_phone(random_string(20));
    user_profile.set_phone_country_code(random_string(20));
    user_profile.set_date_of_birth(random_string(20));
    user_profile.set_age(random_int32(0, 10000));
    user_profile.set_gender(random_string(20));
    user_profile.set_gender(random_string(20));
    user_profile.set_pronouns(random_string(20));
    user_profile.set_bio(random_string(20));
    user_profile.set_website(random_string(20));
    user_profile.set_location_city(random_string(20));
    user_profile.set_location_state(random_string(20));
    user_profile.set_location_country(random_string(20));
    user_profile.set_location_lat(random_double(0.0, 500.0));
    user_profile.set_location_lng(random_double(0.0, 500.0));
    user_profile.set_timezone(random_string(20));
    user_profile.set_language_primary(random_string(20));
    user_profile.set_currency(random_string(20));
    user_profile.set_is_verified(true);
    user_profile.set_is_private(true);
    user_profile.set_is_active(true);
    user_profile.set_is_online(true);
    user_profile.set_is_banned(true);
    user_profile.set_is_deleted(true);
    user_profile.set_has_two_factor(true);
    user_profile.set_registration_date(random_int64(0, 10000));
    user_profile.set_last_login_date(random_int64(0, 10000));
    user_profile.set_last_active_date(random_int64(0, 10000));
    user_profile.set_subscription_expiry(random_int64(0, 10000));
    user_profile.set_email_verified_at(random_int64(0, 10000));
    user_profile.set_phone_verified_at(random_int64(0, 10000));
    user_profile.set_last_purchase_date(random_int64(0, 10000));
    user_profile.set_next_billing_date(random_int64(0, 10000));
    user_profile.set_created_at(random_int64(0, 10000));
    user_profile.set_updated_at(random_int64(0, 10000));
    user_profile.set_deleted_at(random_int64(0, 10000));
    user_profile.set_profile_views_count(random_int64(0, 10000));
    user_profile.set_followers_count(random_int64(0, 10000));
    user_profile.set_following_count(random_int64(0, 10000));
    user_profile.set_posts_count(random_int64(0, 10000));
    user_profile.set_likes_given_count(random_int64(0, 10000));
    user_profile.set_likes_received_count(random_int64(0, 10000));
    user_profile.set_comments_count(random_int64(0, 10000));
    user_profile.set_reposts_count(random_int64(0, 10000));
    user_profile.set_referrals_count(random_int64(0, 10000));
    user_profile.set_github_repos(random_int64(0, 10000));
    user_profile.set_github_stars(random_int64(0, 10000));
    user_profile.set_github_followers(random_int64(0, 10000));
    user_profile.set_credits_available(random_int64(0, 10000));
    user_profile.set_reward_points(random_int64(0, 10000));
    user_profile.set_experience_points(random_int64(0, 10000));
    user_profile.set_account_tier(random_string(20));
    user_profile.set_monthly_spend_usd(random_double(0.0, 500.0));
    user_profile.set_total_spend_usd(random_double(0.0, 500.0));
    user_profile.set_balance_usd(random_double(0.0, 500.0));
    user_profile.set_reputation_score(random_int32(0, 10000));
    user_profile.set_level(random_int32(0, 10000));
    user_profile.set_daily_streak(random_int32(0, 10000));
    user_profile.set_longest_streak(random_int32(0, 10000));
    user_profile.set_height_cm(random_double(0.0, 500.0));
    user_profile.set_weight_kg(random_double(0.0, 500.0));
    user_profile.set_blood_type(random_string(20));
    user_profile.set_diet_preference(random_string(20));
    user_profile.set_alcohol(random_string(20));
    user_profile.set_exercise_frequency(random_string(20));
    user_profile.set_smoking(true);
    user_profile.set_sleep_hours_average(random_double(0.0, 500.0));
    user_profile.set_favorite_color(random_string(20));
    user_profile.set_favorite_food(random_string(20));
    user_profile.set_favorite_movie(random_string(20));
    user_profile.set_favorite_book(random_string(20));
    user_profile.set_favorite_number(random_int32(0, 10000));
    user_profile.set_skill_level_java_script(random_double(0.0, 500.0));
    user_profile.set_skill_level_rust(random_double(0.0, 500.0));
    user_profile.set_job_title(random_string(20));
    user_profile.set_company(random_string(20));
    user_profile.set_company_industry(random_string(20));
    user_profile.set_salary_usd(random_int64(0, 10000));
    user_profile.set_salary_currency(random_string(20));
    user_profile.set_employment_type(random_string(20));
    user_profile.set_work_location(random_string(20));
    user_profile.set_years_experience(random_int32(0, 10000));
    user_profile.set_education_level(random_string(20));
    user_profile.set_education_field(random_string(20));
    user_profile.set_university(random_string(20));
    user_profile.set_graduation_year(random_int32(0, 10000));
    user_profile.set_gpa(random_double(0.0, 500.0));
    user_profile.set_github_username(random_string(20));
    user_profile.set_twitter_handle(random_string(20));
    user_profile.set_linkedin_url(random_string(20));
    user_profile.set_portfolio_url(random_string(20));
    user_profile.set_preferred_contact_method(random_string(20));
    user_profile.set_notification_email(true);
    user_profile.set_notification_push(true);
    user_profile.set_notification_sms(true);
    user_profile.set_dark_mode(true);
    user_profile.set_reduced_motion(true);
    user_profile.set_high_contrast(true);
    user_profile.set_font_size(random_string(20));
    user_profile.set_email_signature(random_string(20));
    user_profile.set_status_message(random_string(20));
    user_profile.set_current_mood(random_string(20));
    user_profile.set_relationship_status(random_string(20));
    user_profile.set_has_children(true);
    user_profile.set_children_count(random_int32(0, 10000));
    user_profile.set_pet_type(random_string(20));
    user_profile.set_pet_name(random_string(20));
    user_profile.set_car_make(random_string(20));
    user_profile.set_car_model(random_string(20));
    user_profile.set_car_year(random_int32(0, 10000));
    user_profile.set_car_color(random_string(20));
    user_profile.set_license_plate(random_string(20));
    user_profile.set_bitcoin_address(random_string(20));
    user_profile.set_ethereum_address(random_string(20));
    user_profile.set_ip_address(random_string(20));
    user_profile.set_user_agent(random_string(20));
    user_profile.set_device_type(random_string(20));
    user_profile.set_os(random_string(20));
    user_profile.set_browser(random_string(20));
    user_profile.set_screen_resolution(random_string(20));
    user_profile.set_time_spent_today_minutes(random_int64(0, 10000));
}

void generate_large(market::UserProfile& user_profile, std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    generate_user_profile(user_profile);

    const size_t sz = user_profile.ByteSizeLong();
    buffer.resize(sz);

    const int64_t start_tsc = TSCNS::rdtsc();
    if (user_profile.SerializeToArray(buffer.data(), static_cast<int>(sz))) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void parse_large(market::UserProfile& user_profile, const std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    const int64_t start_tsc = TSCNS::rdtsc();
    if (user_profile.ParseFromArray(buffer.data(), static_cast<int>(buffer.size()))) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void generate_medium(market::User& user, std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    generate_user(user);

    const size_t sz = user.ByteSizeLong();
    buffer.resize(sz);

    const int64_t start_tsc = TSCNS::rdtsc();
    if (user.SerializeToArray(buffer.data(), static_cast<int>(sz))) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void parse_medium(market::User& user, const std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    const int64_t start_tsc = TSCNS::rdtsc();
    if (user.ParseFromArray(buffer.data(), static_cast<int>(buffer.size()))) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void generate_small(market::Quote& quote, std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    generate_quote(quote);

    const size_t sz = quote.ByteSizeLong();
    buffer.resize(sz);

    const int64_t start_tsc = TSCNS::rdtsc();
    if (quote.SerializeToArray(buffer.data(), static_cast<int>(sz))) {
        const int64_t end_tsc = TSCNS::rdtsc();
        hist.Observe(tscns.tsc2ns(end_tsc) - tscns.tsc2ns(start_tsc));
    }
}

void parse_small(market::Quote& quote, const std::string& buffer, const TSCNS& tscns, Histogram& hist) {
    const int64_t start_tsc = TSCNS::rdtsc();
    if (quote.ParseFromArray(buffer.data(), static_cast<int>(buffer.size()))) {
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

    auto& serialize_hist = hist_fam.Add({{"type", "protobuf"}, {"op", "serialize"}}, get_hist_buckets());
    auto& deserialize_hist = hist_fam.Add({{"type", "protobuf"}, {"op", "deserialize"}}, get_hist_buckets());
    auto& size_gauge = gauge_fam.Add({{"type", "protobuf"}, {"op", "size"}});

    std::string buffer;

    if (test == "small") {
        market::Quote quote;
        generate_quote(quote);
        size_gauge.Set(quote.ByteSizeLong());

        while (true) {
            generate_small(quote, buffer, tscns, serialize_hist);
            parse_small(quote, buffer, tscns, deserialize_hist);
        }
    }
    if (test == "medium") {
        market::User user;
        generate_user(user);
        size_gauge.Set(user.ByteSizeLong());

        while (true) {
            generate_medium(user, buffer, tscns, serialize_hist);
            parse_medium(user, buffer, tscns, deserialize_hist);
        }
    }

    if (test == "large") {
        market::UserProfile user_profile;
        generate_user_profile(user_profile);
        size_gauge.Set(user_profile.ByteSizeLong());

        while (true) {
            generate_large(user_profile, buffer, tscns, serialize_hist);
            parse_large(user_profile, buffer, tscns, deserialize_hist);
        }
    }
}
