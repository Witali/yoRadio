#pragma once

#include <stdbool.h>
#include "native_state.h"
#include "oled_display.h"

// Activity guards prevent sleep in the middle of a command or flash write.
bool deep_sleep_clock_begin_activity(void);
void deep_sleep_clock_end_activity(void);
void deep_sleep_clock_set_ready(void);
void deep_sleep_clock_try_enter(native_state_t *state, oled_display_t *display);
// Called before any GPIO/peripheral initialization after a full wake.
bool deep_sleep_clock_boot(void);
void deep_sleep_clock_wait_for_release(int pin);
