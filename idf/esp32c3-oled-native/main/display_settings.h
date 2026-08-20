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
