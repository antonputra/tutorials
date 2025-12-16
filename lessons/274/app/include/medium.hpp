#pragma once

#include <string>

struct User {
    uint64_t user_id;
    std::string username;
    std::string full_name;
    std::string email;
    std::string phone;
    std::string bio;
    std::string timezone;
    std::string currency;
    int32_t age;
    double height_cm;
    double weight_kg;
    double balance;
    double score;
    bool is_active;
    bool is_verified;
    bool is_premium;
    int64_t created_at;
    int64_t last_login;
};
