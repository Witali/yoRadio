#pragma once
#include <stdint.h>
#include <stdbool.h>

/* 160 MHz / (8 * 13 * 32) = 48000 * 625/624.  The I2S clock is
 * not nominal48k. Keep one previous sample and interpolate at that exact
 * rational rate; no input/PCM allocation and no floating point. */
typedef struct { uint16_t phase; int16_t previous; bool primed; } pdm_clock_resampler_t;
static inline uint32_t pdm_clock_div625(uint32_t magnitude) {
    /* Domain0..65535*624. ceil(2^26/625)=107375; its error gives
     * at most one excess quotient. Split at15 bits to keep both products
     * and their sum in uint32, then correct that excess exactly. LX106
     * has MULL but no cheap high32 product, so avoid uint64 and __divsi3. */
    uint32_t low = (magnitude & 32767U) * 107375U;
    uint32_t high = (magnitude >> 15) * 107375U + (low >> 15);
    uint32_t q = high >> 11;
    return q - (q * 625U > magnitude);
}
static inline unsigned pdm_clock_resample(pdm_clock_resampler_t *s,
                                         int16_t sample, int16_t out[2]) {
    if (!s->primed) { s->previous = sample; s->primed = true; }
    unsigned phase = s->phase + 625U, count = 0;
    while (phase >= 624U) {
        phase -= 624U;
        /* |delta * phase| <= 65535*624, safely inside int32_t.
         * The bounded reciprocal helper is exact for this whole domain. */
        int32_t correction = ((int32_t)sample - s->previous) * (int32_t)phase;
        uint32_t magnitude = (uint32_t)(correction < 0 ? -correction : correction);
        int32_t divided = (int32_t)pdm_clock_div625(magnitude);
        out[count++] = (int16_t)((int32_t)sample - (correction < 0 ? -divided : divided));
    }
    s->phase = (uint16_t)phase;
    s->previous = sample;
    return count;
}
