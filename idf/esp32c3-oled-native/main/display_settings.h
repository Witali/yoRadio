#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"
#include "oled_display.h"

esp_err_t display_settings_init(oled_display_t *display);
uint8_t display_settings_get_brightness(void);
esp_err_t display_settings_set_brightness(uint8_t brightness, bool persist);
bool display_settings_get_station_uppercase(void);
esp_err_t display_settings_set_station_uppercase(bool enabled, bool persist);
bool display_settings_get_screen_on(void);
esp_err_t display_settings_set_screen_on(bool enabled, bool persist);
bool display_settings_get_numbered_playlist(void);
esp_err_t display_settings_set_numbered_playlist(bool enabled, bool persist);
bool display_settings_get_screensaver_enabled(void);
esp_err_t display_settings_set_screensaver_enabled(bool enabled);
uint16_t display_settings_get_screensaver_timeout(void);
esp_err_t display_settings_set_screensaver_timeout(uint16_t seconds);
bool display_settings_get_screensaver_blank(void);
esp_err_t display_settings_set_screensaver_blank(bool blank);
bool display_settings_get_screensaver_playing_enabled(void);
esp_err_t display_settings_set_screensaver_playing_enabled(bool enabled);
uint16_t display_settings_get_screensaver_playing_timeout(void);
esp_err_t display_settings_set_screensaver_playing_timeout(uint16_t minutes);
bool display_settings_get_screensaver_playing_blank(void);
esp_err_t display_settings_set_screensaver_playing_blank(bool blank);
void display_settings_note_activity(void);
bool display_settings_screensaver_active(bool playing, uint32_t now_ms,
                                         bool *power_off);
