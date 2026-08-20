#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

#define OLED_DISPLAY_WIDTH 72
#define OLED_DISPLAY_HEIGHT 40
#define OLED_DISPLAY_TEXT_COLUMNS 12
#define OLED_LARGE_GLYPH_WIDTH 8
#define OLED_LARGE_GLYPH_HEIGHT 15
#define OLED_HARDWARE_SCROLL_MAX_GLYPHS 15

typedef struct {
    void *bus;
    void *device;
    uint8_t framebuffer[OLED_DISPLAY_WIDTH * OLED_DISPLAY_HEIGHT / 8];
} oled_display_t;

esp_err_t oled_display_init(oled_display_t *display);
esp_err_t oled_display_set_brightness(oled_display_t *display,
                                      uint8_t brightness);
esp_err_t oled_display_show_boot_logo(oled_display_t *display);
void oled_display_clear(oled_display_t *display);
void oled_display_draw_text(oled_display_t *display, int x, int y,
                            const char *text);
void oled_display_draw_compact_text(oled_display_t *display, int x, int y,
                                    const char *text);
size_t oled_display_large_text_length(const char *text);
void oled_display_draw_large_text(oled_display_t *display, int x, int y,
                                  const char *text, size_t pixel_offset,
                                  bool wrap, bool inverted, bool uppercase);
esp_err_t oled_display_start_text_scroll(oled_display_t *display,
                                         uint8_t first_page,
                                         const char *text, bool inverted,
                                         bool uppercase);
esp_err_t oled_display_stop_scroll(oled_display_t *display);
esp_err_t oled_display_present(oled_display_t *display);

