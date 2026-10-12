#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
typedef struct {
    bool valid;
    float temperature_c, wind_mps;
    int humidity, timezone_seconds;
    char icon[4], description[65], city[65], country[3];
    uint32_t generation;
} weather_snapshot_t;
void services_start(void);
void weather_start(void);
void weather_request_update(void);
void weather_snapshot(weather_snapshot_t *out);
