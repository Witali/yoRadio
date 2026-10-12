#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "board.h"
typedef struct
{
    uint32_t version;
    char ssid[33], password[65], city[65], country[3], ntp[65], weather_key[65];
    uint16_t day_level, night_level, colors[3]; /* per-mille duty, RGB565 */
    uint8_t theme, animation, date_format, night_start, night_stop, photo_seconds;
    uint8_t fahrenheit, hour12, miles, browser_time, night_mode, click_count, photo_mask;
    /* Reuses the old padding byte; the persisted NVS blob remains 344 bytes. */
    uint8_t wifi_mode; /* factory values: 0/2 = setup, 1 = station */
    uint32_t photo_size[PHOTO_COUNT];
} tv_settings_t;
esp_err_t settings_init(void);
void settings_snapshot(tv_settings_t *out);
esp_err_t settings_replace(const tv_settings_t *settings);
esp_err_t settings_photo_size(unsigned slot, uint32_t bytes);
esp_err_t settings_flush(void);
uint32_t settings_generation(void);
bool settings_valid(const tv_settings_t *s);
uint16_t rgb565_from_rgb888(uint32_t rgb);
uint32_t rgb888_from_rgb565(uint16_t rgb);
