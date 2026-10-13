#include "factory_timer.h"
#include <string.h>
#ifdef ESP_PLATFORM
#include "esp_attr.h"
#else
#define IRAM_ATTR
#endif

void factory_timer_init(factory_timer_t *state, bool startup)
{
    /* Initialize the counters before enabling the original 100-ms timer. */
    memset(state, 0, sizeof(*state));
    state->startup_active = startup;
}

bool IRAM_ATTR factory_timer_tick(factory_timer_t *state, uint32_t photo_interval)
{
    /* Advance the byte counters/latched flags observed at 0x4200826a. */
    bool draw_startup = state->startup_active;
    if (draw_startup)
    {
        ++state->startup_progress;
        if (state->startup_progress > 180)
            state->startup_active = false;
        state->pending |= TV_TIMER_STARTUP_DRAW;
    }
    if (++state->subsecond_ticks <= 10)
        return draw_startup;
    state->subsecond_ticks = 0;
    state->pending |= TV_TIMER_SECOND;
    if (++state->description_seconds > 2)
    {
        state->description_seconds = 0;
        state->pending |= TV_TIMER_DESCRIPTION;
    }
    if (++state->photo_seconds >= photo_interval)
    {
        state->photo_seconds = 0;
        state->pending |= TV_TIMER_PHOTO;
    }
    if (++state->minute_seconds > 59)
    {
        state->minute_seconds = 0;
        state->pending |= TV_TIMER_MINUTE | TV_TIMER_NETWORK;
    }
    if (++state->slow_seconds > 180)
    {
        state->slow_seconds = 0;
        state->pending |= TV_TIMER_SLOW;
    }
    if (++state->weather_seconds > 1800)
    {
        state->weather_seconds = 0;
        state->pending |= TV_TIMER_WEATHER;
    }
    return draw_startup;
}

uint32_t factory_timer_take(factory_timer_t *state, uint32_t mask)
{
    /* Consume only the caller's flags; repeated events coalesce as in stock. */
    uint32_t events = state->pending & mask;
    state->pending &= ~mask;
    return events;
}
