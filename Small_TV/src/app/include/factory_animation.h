#pragma once
#include <stdint.h>

typedef struct
{
    uint8_t next_frame;
} factory_animation_t;

int factory_animation_next(factory_animation_t *state, unsigned frame_count);
