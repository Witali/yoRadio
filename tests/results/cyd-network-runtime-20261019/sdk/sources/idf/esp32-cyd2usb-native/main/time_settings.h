#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"
#include "native_time_sntp.h"

typedef struct {
    int16_t utc_offset_minutes;
    uint16_t sync_interval_minutes;
    uint8_t server_count;
    char servers[NATIVE_TIME_SNTP_SERVER_COUNT][NATIVE_TIME_SNTP_NAME_CAPACITY];
} time_settings_t;

void time_settings_defaults(time_settings_t *settings);
bool time_settings_valid(const time_settings_t *settings);
esp_err_t time_settings_init(void);
bool time_settings_snapshot(time_settings_t *settings, uint32_t *revision);
esp_err_t time_settings_save(const time_settings_t *settings);
