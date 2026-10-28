#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "board.h"
#include "color_convert.h"
/* The factory raw sector reserves 20 bytes, including NUL, for regional keys. */
#define TV_COUNTRY_BYTES 20
#define TV_SETTINGS_VERSION 2
#define TV_JPEG_WRITE_LIMIT_DEFAULT_KIB 200u
typedef struct
{
    uint32_t version;
    char ssid[33], password[65], city[65], country[TV_COUNTRY_BYTES], ntp[65], weather_key[65];
    uint16_t day_level, night_level, colors[3]; /* per-mille duty, RGB565 */
    uint8_t theme, animation, date_format, night_start, night_stop, photo_seconds;
    uint8_t fahrenheit, hour12, miles, browser_time, night_mode, click_count, photo_mask;
    uint8_t wifi_mode; /* factory values: 0/2 = setup, 1 = station */
    uint32_t photo_size[PHOTO_COUNT];
} tv_settings_t;
esp_err_t settings_init(void);
void settings_snapshot(tv_settings_t *out);
void settings_snapshot_with_revisions(tv_settings_t *out, uint32_t *configuration_revision,
                                      uint32_t *theme_selection_revision);
esp_err_t settings_replace(const tv_settings_t *settings);
esp_err_t settings_select_theme(unsigned theme);
esp_err_t settings_update_city(const char *city, const char *country);
esp_err_t settings_photo_size(unsigned slot, uint32_t bytes);
esp_err_t settings_flush(void);
uint32_t settings_generation(void);
bool settings_valid(const tv_settings_t *s);
bool settings_country_valid(const char country[TV_COUNTRY_BYTES]);
/* REQUESTED_CHANGE: independent NVS preference; factory and native blob ABIs
 * remain compatible. Zero forbids codec program/erase; source upload is separate. */
uint32_t settings_jpeg_write_limit_kib(void);
esp_err_t settings_set_jpeg_write_limit_kib(uint32_t kib);
