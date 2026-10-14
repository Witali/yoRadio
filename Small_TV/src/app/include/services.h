#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include "settings.h"
#include "esp_err.h"
typedef struct
{
    bool valid;
    double temperature_c, wind_mps, temperature_min_c, temperature_max_c;
    int humidity, timezone_seconds;
    char icon[4], description[65], city[65], country[3];
    char main[16], wind_direction[20];
    uint32_t generation;
} weather_snapshot_t;
void services_start(void);
bool services_time_synced(void);
bool services_local_time(const char *country, time_t utc, struct tm *local);
void weather_start(void);
void weather_request_update(void);
void weather_snapshot(weather_snapshot_t *out);
bool weather_parse_response(const char *body, size_t length, const tv_settings_t *settings,
                            weather_snapshot_t *out);
bool weather_request_active(void);
