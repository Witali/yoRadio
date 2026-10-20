#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#include "time_settings.h"

typedef struct {
    bool available;
    bool network_ready;
    bool clock_valid;
    bool synchronized_this_boot;
    time_t utc_epoch;
    struct tm local_time;
    time_t last_sync_epoch;
    int64_t last_sync_age_ms;
    uint32_t desired_revision;
    uint32_t applied_revision;
    esp_err_t last_apply_error;
    time_settings_t settings;
} time_snapshot_t;

esp_err_t time_service_start(void);
esp_err_t time_service_get_settings(time_settings_t *settings);
// Success means persisted desired settings; snapshot reports application.
esp_err_t time_service_save_settings(const time_settings_t *settings);
void time_service_notify_network(bool has_station_ip);
bool time_service_snapshot(time_snapshot_t *snapshot);
