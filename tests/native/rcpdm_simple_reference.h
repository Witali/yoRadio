#pragma once
#include "rc_pdm.h"

/* Diagnostic-only literal model, independent of the constant-step shortcut.
 * Wide arithmetic makes range/rounding explicit; never used in timed output. */
static inline uint32_t rcpdm_simple_reference(rc_pdm_t *p, int16_t pcm) {
    const uint64_t target = (uint64_t)((int32_t)pcm + 32768) * 65536U;
    uint64_t state = p->rc;
    uint32_t word = 0;
    for (unsigned i = 0; i < 32; ++i) {
        unsigned high = target > state;
        if (high) state += (UINT32_MAX - state) / 16U;
        else state -= state / 16U;
        word = (word << 1) | high;
    }
    p->rc = (uint32_t)state;
    return word;
}
