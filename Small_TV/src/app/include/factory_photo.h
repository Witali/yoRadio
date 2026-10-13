#pragma once
#include <stdbool.h>
#include <stdint.h>

typedef struct
{
    uint8_t fade, next_slot;
} factory_photo_t;

typedef struct
{
    uint16_t duty;
    int8_t photo; /* -2: no drawing; -1: clear; 0..4: selected photo. */
    bool set_duty, finished;
} factory_photo_action_t;

void factory_photo_step(factory_photo_t *state, uint32_t enabled, uint32_t present,
                        bool photo_event, bool blocked, factory_photo_action_t *action);
