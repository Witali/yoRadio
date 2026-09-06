#pragma once
#include "rc_pdm.h"

/* Experimental direct PCM/current-state comparison, no look-ahead.
 * count is 1..32; shift is 1..31 (benchmarks use 2 and 4). State and target
 * have the same unsigned fixed32 scale as production RCPDM. MSB first.
 * This changes the modulation algorithm, not just its implementation. */
static inline uint32_t rcpdm_simple_bits(rc_pdm_t *p, int16_t pcm,
                                        unsigned count, unsigned shift) {
    const uint32_t target = rc_pdm_target(pcm);
    uint32_t state = p->rc, word = 0;
    for (unsigned i = 0; i < count; ++i) {
        /* Decide BEFORE updating the RC state. Equal target selects zero. */
        word <<= 1;
        if (state < target) {
            state += (UINT32_MAX - state) >> shift;
            word |= 1U;
        } else {
            state -= state >> shift;
        }
    }
    p->rc = state;
    return word;
}

/* Charge towards the upper rail for bit 1, discharge towards zero for bit 0.
 * Each selected update uses only unsigned 32-bit arithmetic and a shift.
 * The state stays bounded by the rails; no saturation or wide multiply. */
static inline uint32_t rcpdm_simple_sample(rc_pdm_t *p, int16_t pcm) {
    return rcpdm_simple_bits(p, pcm, RC_PDM_BITS_PER_SAMPLE, RC_PDM_SHIFT);
}

/* Same DMA span contract as rc_pdm_fill, with no intermediate audio buffer. */
static inline void rcpdm_simple_fill(rc_pdm_t *p, uint32_t *words,
                                     const int16_t *pcm, size_t frames,
                                     unsigned channels) {
    rc_pdm_t current = *p;
    if (channels == 2) {
        for (size_t i = 0; i < frames; ++i) {
            int32_t mono = ((int32_t)pcm[i * 2] + pcm[i * 2 + 1]) / 2;
            words[i] = rcpdm_simple_sample(&current, (int16_t)mono);
        }
    } else {
        for (size_t i = 0; i < frames; ++i)
            words[i] = rcpdm_simple_sample(&current, pcm[i]);
    }
    *p = current;
}
