#pragma once
#include "rc_pdm.h"

// Desktop research only. Eight bits of RCPDM, NOT 8-bit PCM or delta-sigma.
// Shift=4 preserves the existing alpha=1/16; Shift=2 tests alpha=1/4 at
// the four-times lower carrier. Neither changes the production firmware.
template<unsigned Shift>
static inline uint8_t rcpdm8_shift(rc_pdm_t *p, int16_t pcm) {
    const uint32_t step = UINT32_MAX >> Shift;
    const uint32_t target = rc_pdm_target(pcm), half = step >> 1;
    const uint32_t limit = target > half ? target-half : 0;
    uint32_t state = p->rc, bits = 0;
    for (unsigned i=0;i<8;++i) {
        state -= state >> Shift;
        bits <<= 1;
        if (state < limit) { state += step; bits |= 1U; }
    }
    p->rc = state;
    return (uint8_t)bits;
}

// Quality control: alpha=round((1-exp(-1/(384000*10us)))*65536)/65536.
// Q16 uses 64-bit products; this is not proposed as an LX106 speed optimization.
static inline uint8_t rcpdm8_q16(rc_pdm_t *p, int16_t pcm, uint32_t alpha) {
    const uint32_t target = rc_pdm_target(pcm);
    uint32_t state=p->rc, bits=0;
    for (unsigned i=0;i<8;++i) {
        const uint32_t down=state-(uint32_t)(((uint64_t)state*alpha)>>16);
        const uint32_t up=state+(uint32_t)(((uint64_t)(UINT32_MAX-state)*alpha)>>16);
        const bool high=target > down+((up-down)>>1);
        state=high ? up : down;
        bits=(bits<<1)|(uint32_t)high;
    }
    p->rc=state;
    return (uint8_t)bits;
}
