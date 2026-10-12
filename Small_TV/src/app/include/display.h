#pragma once
#include <stdint.h>
#include "esp_err.h"
#include "settings.h"
esp_err_t display_init(void);
void display_fill(int x, int y, int width, int height, uint16_t color);
void display_blit(int x, int y, int width, int height, const uint16_t *pixels);
void display_text(int x, int y, const char *text, unsigned scale, uint16_t color,
                  uint16_t background);
void display_line(int x0, int y0, int x1, int y1, uint16_t color);
esp_err_t backlight_init(void);
void backlight_set_level(unsigned per_mille);
void backlight_update(const tv_settings_t *s, int local_hour, int local_minute, bool clock_valid);
void clock_ui_start(void);
