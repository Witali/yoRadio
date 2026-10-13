#pragma once
#include <stdbool.h>
#include <stdint.h>

enum
{
    TV_TIMER_SECOND = 1u << 0,
    TV_TIMER_DESCRIPTION = 1u << 1,
    TV_TIMER_PHOTO = 1u << 2,
    TV_TIMER_MINUTE = 1u << 3,
    TV_TIMER_NETWORK = 1u << 4,
    TV_TIMER_SLOW = 1u << 5,
    TV_TIMER_WEATHER = 1u << 6,
    TV_TIMER_STARTUP_DRAW = 1u << 7
};

typedef struct
{
    uint32_t weather_seconds, pending;
    uint8_t subsecond_ticks, description_seconds, photo_seconds, minute_seconds;
    uint8_t slow_seconds, startup_progress;
    bool startup_active;
} factory_timer_t;

void factory_timer_init(factory_timer_t *state, bool startup);
bool factory_timer_tick(factory_timer_t *state, uint32_t photo_interval);
uint32_t factory_timer_take(factory_timer_t *state, uint32_t mask);
