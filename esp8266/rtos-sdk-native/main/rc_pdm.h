#pragma once

#include <stdint.h>

/* Predictive, unsigned full-scale RC model, alpha = 1/16. The peripheral
 * only transports these bits; this is not a hardware PDM modulator. */
#define RC_PDM_BITS_PER_SAMPLE 32U
#define RC_PDM_SHIFT 4U
#define RC_PDM_STEP (UINT32_MAX >> RC_PDM_SHIFT)

typedef struct {
    uint32_t rc;
} rc_pdm_t;

static inline void rc_pdm_init(rc_pdm_t *p) {
    p->rc = UINT32_C(0x80000000);
}

static inline uint32_t rc_pdm_target(int16_t pcm) {
    return (uint32_t)((int32_t)pcm + 32768) << 16;
}

/* One 32-bit word per output PCM sample, chronological bits MSB first.
 * up = s + ((~s) >> 4), down = s - (s >> 4).
 * Their distance is always UINT32_MAX >> 4, including integer rounding.
 * Thus the constant-step form is bit-exact with the two-candidate model;
 * down + STEP and the midpoint cannot exceed UINT32_MAX. */
static inline uint32_t rc_pdm_sample(rc_pdm_t *p, int16_t pcm) {
    const uint32_t target = rc_pdm_target(pcm);
    /* down + HALF never overflows. Clamp before unsigned subtraction:
     * target <= HALF cannot select the upper candidate for any state. */
    const uint32_t half = RC_PDM_STEP >> 1;
    const uint32_t limit = target > half ? target - half : 0;
    uint32_t word = 0;
    uint32_t state = p->rc;
    for (unsigned bit = 0; bit < RC_PDM_BITS_PER_SAMPLE; ++bit) {
        uint32_t down = state - (state >> RC_PDM_SHIFT);
        state = down;
        word <<= 1;
        if (down < limit) {
            state += RC_PDM_STEP;
            word |= 1U;
        }
    }
    p->rc = state;
    return word;
}
