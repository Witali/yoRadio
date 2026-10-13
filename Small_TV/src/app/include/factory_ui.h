#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
#include "settings.h"
#include "services.h"

typedef struct
{
    const uint8_t *pixels;
    unsigned width, height, stride;
} tv_bitmap_t;

bool factory_glyph(unsigned character, unsigned height, tv_bitmap_t *bitmap);
bool factory_symbol(unsigned symbol, tv_bitmap_t *bitmap);
void display_bitmap(int x, int y, const tv_bitmap_t *bitmap, uint16_t color, uint16_t background,
                    bool transparent);
void display_factory_text(int x, int y, const char *text, unsigned height, uint16_t color,
                          uint16_t background, bool transparent);
void display_factory_symbol(int x, int y, unsigned symbol, uint16_t color, uint16_t background);

enum
{
    TV_SYMBOL_CELSIUS,
    TV_SYMBOL_FAHRENHEIT,
    TV_SYMBOL_STARTUP_BORDER,
    TV_SYMBOL_STARTUP_CAP,
    TV_SYMBOL_SIMPLE_PLATE,
    TV_SYMBOL_DIGIT_PLATE
};

void factory_draw_setup(void);
void factory_draw_startup(const char *address, unsigned progress);
void factory_draw_classic(const tv_settings_t *settings, const struct tm *local,
                          const weather_snapshot_t *weather, unsigned description_step,
                          unsigned animation_frame, bool reset, bool force_status);
void factory_draw_simple(const tv_settings_t *settings, const struct tm *local,
                         const char *address, bool reset, bool second_update, bool minute_update);
void factory_draw_dial(const struct tm *local, const char *address, bool reset);
void factory_draw_photo(unsigned slot, const char *address);
