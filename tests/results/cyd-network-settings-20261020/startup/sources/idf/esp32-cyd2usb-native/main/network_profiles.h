#pragma once

#include <stdint.h>

#include "esp_err.h"

#define NETWORK_PROFILES_MAX 5U

typedef struct {
    char ssid[32];
    char password[64];
} network_profile_t;

typedef struct {
    network_profile_t rows[NETWORK_PROFILES_MAX];
    uint8_t count;
} network_profiles_t;

// Read the boot snapshot from the existing recoverable Wi-Fi file. Keep the
// first five valid legacy rows in file order; an existing empty file succeeds
// with count zero. No profile is published on any open/read/close failure.
// NOT_FOUND identifies ENOENT; other I/O failures return ESP_FAIL. A NULL output
// returns INVALID_ARG. This tolerant reader does not validate desired edits.
esp_err_t network_profiles_load(network_profiles_t *out);
