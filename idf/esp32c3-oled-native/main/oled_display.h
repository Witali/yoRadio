#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

#define OLED_DISPLAY_WIDTH 72
#define OLED_DISPLAY_HEIGHT 40
#define OLED_DISPLAY_TEXT_COLUMNS 12

typedef struct {
    void *bus;
    void *device;
    uint8_t framebuffer[OLED_DISPLAY_WIDTH * OLED_DISPLAY_HEIGHT / 8];
} oled_display_t;

esp_err_t oled_display_init(oled_display_t *display);
void oled_display_clear(oled_display_t *display);
void oled_display_draw_text(oled_display_t *display, int x, int y,
                            const char *text);
void oled_display_draw_compact_text(oled_display_t *display, int x, int y,
                                    const char *text);
size_t oled_display_large_text_length(const char *text);
void oled_display_draw_large_text(oled_display_t *display, int x, int y,
                                  const char *text, size_t first_glyph);
esp_err_t oled_display_present(oled_display_t *display);

