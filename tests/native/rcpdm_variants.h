#pragma once
#include "rc_pdm.h"

/* Frozen original implementation. Experiments stay outside production. */
static inline uint32_t rc_candidate_original(rc_pdm_t *p, int16_t pcm) {
    uint32_t target = rc_pdm_target(pcm), state = p->rc, word = 0;
    for (unsigned i = 0; i < 32; ++i) {
        uint32_t down = state - (state >> 4);
        state = down;
        word <<= 1;
        if (target > down + (RC_PDM_STEP >> 1)) {
            state += RC_PDM_STEP;
            word |= 1U;
        }
    }
    p->rc = state;
    return word;
}

#define RC_TEST_STEP() do { \
    state -= state >> 4; \
    word <<= 1; \
    if (state < limit) { state += RC_PDM_STEP; word |= 1U; } \
} while (0)
#define RC_TEST_4(step) step(); step(); step(); step()
#define RC_TEST_8(step) RC_TEST_4(step); RC_TEST_4(step)
#define RC_TEST_32(step) RC_TEST_8(step); RC_TEST_8(step); RC_TEST_8(step); RC_TEST_8(step)
#define RC_TEST_FUNCTION(name, group, body) \
static inline uint32_t rc_candidate_##name(rc_pdm_t *p, int16_t pcm) { \
    const uint32_t target = rc_pdm_target(pcm); \
    const uint32_t half = RC_PDM_STEP >> 1; \
    const uint32_t limit = target > half ? target - half : 0; \
    uint32_t state = p->rc, word = 0; \
    for (unsigned i = 0; i < 32; i += group) { body; } \
    p->rc = state; return word; \
}
RC_TEST_FUNCTION(limit, 1, RC_TEST_STEP())
RC_TEST_FUNCTION(unroll4, 4, RC_TEST_4(RC_TEST_STEP))
RC_TEST_FUNCTION(unroll8, 8, RC_TEST_8(RC_TEST_STEP))
RC_TEST_FUNCTION(unroll32, 32, RC_TEST_32(RC_TEST_STEP))
#undef RC_TEST_STEP
#undef RC_TEST_FUNCTION

/* A C boolean/mask need not compile to branchless code on LX106. */
#define RC_TEST_MASK_STEP() do { \
    state -= state >> 4; \
    uint32_t high = state < limit; \
    state += (0U - high) & RC_PDM_STEP; \
    word = (word << 1) | high; \
} while (0)
static inline uint32_t rc_candidate_mask8(rc_pdm_t *p, int16_t pcm) {
    uint32_t target = rc_pdm_target(pcm), half = RC_PDM_STEP >> 1;
    uint32_t limit = target > half ? target - half : 0;
    uint32_t state = p->rc, word = 0;
    for (unsigned i = 0; i < 32; i += 8) { RC_TEST_8(RC_TEST_MASK_STEP); }
    p->rc = state;
    return word;
}
#undef RC_TEST_MASK_STEP

/* Target is an exact multiple of 65536. Comparing its high half to the
 * midpoint's high half is exact. Both halves fit in 16 bits, so the high
 * bit of their unsigned difference is a safe borrow indicator (no signed UB). */
#define RC_TEST_BRANCHLESS_STEP() do { \
    uint32_t down = state - (state >> 4); \
    uint32_t high = (((down + (RC_PDM_STEP >> 1)) >> 16) - target16) >> 31; \
    state = down + ((0U - high) & RC_PDM_STEP); \
    word = (word << 1) | high; \
} while (0)
static inline uint32_t rc_candidate_branchless8(rc_pdm_t *p, int16_t pcm) {
    uint32_t target16 = (uint32_t)((int32_t)pcm + 32768);
    uint32_t state = p->rc, word = 0;
    for (unsigned i = 0; i < 32; i += 8) { RC_TEST_8(RC_TEST_BRANCHLESS_STEP); }
    p->rc = state;
    return word;
}
#undef RC_TEST_BRANCHLESS_STEP
#undef RC_TEST_4
#undef RC_TEST_8
#undef RC_TEST_32
