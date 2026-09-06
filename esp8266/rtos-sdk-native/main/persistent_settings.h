#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

#define SETTINGS_HOST_CAPACITY 24
#define SETTINGS_SNTP_CAPACITY 36

typedef struct {
    uint8_t volume;
    int8_t balance;
    uint16_t last_station;
    uint8_t smart_start;
    uint8_t brightness;
    bool station_uppercase;
    bool numbered_playlist;
    bool screensaver_enabled;
    bool screensaver_blank;
    uint16_t screensaver_timeout_s;
    bool normalization_enabled;
    int8_t normalization_target_db;
    uint8_t normalization_max_gain_db;
    uint16_t normalization_time_ms;
    int8_t timezone_hour;
    uint8_t timezone_minute;
    uint16_t time_sync_interval_min;
    uint8_t volume_steps;
    uint16_t encoder_acceleration;
    char mdns_name[SETTINGS_HOST_CAPACITY];
    char sntp1[SETTINGS_SNTP_CAPACITY];
    char sntp2[SETTINGS_SNTP_CAPACITY];
} persistent_settings_t;

/* Extra keys keep the original version-1 blob ABI readable by older builds. */
typedef struct {
    bool audio_info;
    uint8_t softap_delay_min;
} persistent_web_settings_t;
void persistent_settings_get_web(persistent_web_settings_t *output);
esp_err_t persistent_settings_update_web(const persistent_web_settings_t *settings);

esp_err_t persistent_settings_init(void);
void persistent_settings_get(persistent_settings_t *output);
esp_err_t persistent_settings_save(const persistent_settings_t *settings);
esp_err_t persistent_settings_update_runtime(
    const persistent_settings_t *settings);
esp_err_t persistent_settings_commit(void);
esp_err_t persistent_settings_reset_group(const char *group);
void persistent_settings_set_volume_runtime(uint8_t volume);
void persistent_settings_set_last_station_runtime(uint16_t station);
void persistent_settings_set_smart_start_runtime(uint8_t state);
