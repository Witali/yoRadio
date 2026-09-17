#pragma once
#include <stdint.h>
#include <stdbool.h>

/* 160 MHz / (8 * 13 * 32) = 48000 * 625/624.  The I2S clock is
 * not nominal48k. Keep one previous sample and interpolate at that exact
 * rational rate; no input/PCM allocation and no floating point. */
typedef struct { uint16_t phase; int16_t previous; bool primed; } pdm_clock_resampler_t;
static inline unsigned pdm_clock_resample(pdm_clock_resampler_t *s,
                                         int16_t sample, int16_t out[2]) {
    if (!s->primed) { s->previous = sample; s->primed = true; }
    unsigned phase = s->phase + 625U, count = 0;
    while (phase >= 624U) {
        phase -= 624U;
        /* |delta * phase| <= 65535*624, safely inside int32_t.
         * Division by the compile-time constant uses GCC's reciprocal. */
        int32_t correction = ((int32_t)sample - s->previous) * (int32_t)phase;
        out[count++] = (int16_t)((int32_t)sample - correction / 625);
    }
    s->phase = (uint16_t)phase;
    s->previous = sample;
    return count;
}
