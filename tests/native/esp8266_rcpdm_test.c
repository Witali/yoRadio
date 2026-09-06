#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>

#include "rc_pdm.h"
#include "rcpdm_variants.h"

static void check_candidates(uint32_t seed, int16_t pcm, uint32_t word, uint32_t state) {
    uint32_t (*const candidates[])(rc_pdm_t *, int16_t) = {
        rc_candidate_original, rc_candidate_limit, rc_candidate_unroll4,
        rc_candidate_unroll8, rc_candidate_unroll32, rc_candidate_mask8,
        rc_candidate_branchless8
    };
    for (unsigned i = 0; i < sizeof(candidates) / sizeof(candidates[0]); ++i) {
        rc_pdm_t actual = {seed};
        assert(candidates[i](&actual, pcm) == word);
        assert(actual.rc == state);
    }
}

/* Deliberately independent, wider reference: calculate both candidates as
 * in the supplied RC description, not the production constant-step shortcut. */
static uint32_t reference_sample(uint32_t *rc, int16_t pcm) {
    uint64_t target = (uint64_t)((int32_t)pcm + 32768) * 65536U;
    uint64_t state = *rc;
    uint32_t word = 0;
    for (unsigned bit = 0; bit < 32; ++bit) {
        uint64_t down = state - state / 16U;
        uint64_t up = state + (UINT32_MAX - state) / 16U;
        uint64_t midpoint = down + (up - down) / 2U;
        assert(up <= UINT32_MAX && down <= up);
        uint32_t high = target > midpoint;
        state = high ? up : down;
        word = (word << 1) | high;
    }
    *rc = (uint32_t)state;
    return word;
}

static uint32_t random_word(uint32_t *seed) {
    *seed = *seed * UINT32_C(1664525) + UINT32_C(1013904223);
    return *seed;
}

int main(void) {
    assert(sizeof(rc_pdm_t) == 4);
    assert(RC_PDM_BITS_PER_SAMPLE == 32);
    assert(rc_pdm_target(INT16_MIN) == 0);
    assert(rc_pdm_target(0) == UINT32_C(0x80000000));
    assert(rc_pdm_target(INT16_MAX) == UINT32_C(0xffff0000));

    const uint32_t seeds[] = {0, 1, 15, UINT32_C(0x80000000),
                              UINT32_MAX - 15U, UINT32_MAX};
    for (unsigned i = 0; i < sizeof(seeds) / sizeof(seeds[0]); ++i) {
        for (int32_t pcm = INT16_MIN; pcm <= INT16_MAX; ++pcm) {
            rc_pdm_t actual = {seeds[i]};
            uint32_t reference = seeds[i];
            uint32_t expected = reference_sample(&reference, (int16_t)pcm);
            assert(rc_pdm_sample(&actual, (int16_t)pcm) == expected);
            assert(actual.rc == reference);
            check_candidates(seeds[i], (int16_t)pcm, expected, reference);
        }
    }

    rc_pdm_t actual;
    rc_pdm_init(&actual);
    uint32_t reference = actual.rc;
    uint32_t rng = 1;
    for (unsigned i = 0; i < 100000; ++i) {
        int16_t pcm = (int16_t)((int32_t)(random_word(&rng) & 65535U) - 32768);
        uint32_t before = reference;
        uint32_t expected = reference_sample(&reference, pcm);
        assert(rc_pdm_sample(&actual, pcm) == expected);
        assert(actual.rc == reference);
        check_candidates(before, pcm, expected, reference);
    }

    /* Continuous zero must match the neutral DMA word, including across
     * batch boundaries. Reset/stop must restart the same deterministic model. */
    for (unsigned reset = 0; reset < 2; ++reset) {
        rc_pdm_init(&actual);
        assert(actual.rc == UINT32_C(0x80000000));
        for (unsigned i = 0; i < 4096; ++i)
            assert(rc_pdm_sample(&actual, 0) == UINT32_C(0xaaaaaaaa));
    }
    rc_pdm_init(&actual);
    assert(rc_pdm_sample(&actual, INT16_MIN) == 0);
    rc_pdm_init(&actual);
    assert(rc_pdm_sample(&actual, INT16_MAX) == UINT32_MAX);
    puts("RCPDM32 tests passed: 493216 reference words, zero, rails, reset");
    return 0;
}
