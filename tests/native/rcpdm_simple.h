#pragma once
#include "rc_pdm.h"

/* Host experiment: direct PCM/current-state comparison, no look-ahead.
 * count is 1..32; shift is 1..31 (benchmarks use 2 and 4). State and target
 * have the same unsigned fixed32 scale as production RCPDM. MSB first.
 * This changes the modulation algorithm, not just its implementation. */
static inline uint32_t rcpdm_simple_bits(rc_pdm_t *p, int16_t pcm,
                                        unsigned count, unsigned shift) {
    const uint32_t target = rc_pdm_target(pcm);
    const uint32_t step = UINT32_MAX >> shift;
    uint32_t state = p->rc, word = 0;
    for (unsigned i = 0; i < count; ++i) {
        /* Decide BEFORE updating the RC state. Equal target selects zero. */
        const unsigned high = target > state;
        state -= state >> shift;
        if (high) state += step;
        word = (word << 1) | high;
    }
    p->rc = state;
    return word;
}

/* up == down + step for the UINT32_MAX rail. This uses one shift regardless
 * of the selected bit, and equals s + ((UINT32_MAX-s) >> shift) for bit 1.
 * The state is bounded by the rails; no saturation or wide multiply needed. */
static inline uint32_t rcpdm_simple_sample(rc_pdm_t *p, int16_t pcm) {
    return rcpdm_simple_bits(p, pcm, RC_PDM_BITS_PER_SAMPLE, RC_PDM_SHIFT);
}
