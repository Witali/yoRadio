#pragma once
#include <stdint.h>
#include "rc_pdm.h"

// Research candidates only. Never included by a firmware target.
struct RcRunStats {
    uint64_t checks = 0, groups = 0, high_groups = 0, words_with_group = 0;
};

// FixedBound reproduces the previously verified conservative difference bound.
// Otherwise use a bound on the next K-1 state increments/decrements. Each step
// toward a rail gets smaller, and down(s)=s-(s>>4) is monotone and 1-Lipschitz.
// Ordered subtraction avoids overflow when the upper bound exceeds UINT32_MAX.
template<unsigned K, bool FixedBound, bool EntryOnly, bool Count>
static inline uint32_t rc_run_sample(rc_pdm_t *p, int16_t pcm, RcRunStats *stats) {
    static_assert(K == 2 || K == 4 || K == 8, "bounded constant-bit group size");
    const uint32_t target = rc_pdm_target(pcm), half = RC_PDM_STEP >> 1;
    const uint32_t limit = target > half ? target - half : 0;
    uint32_t state = p->rc, word = 0;
    unsigned left = 32;
    bool first = true, grouped = false;
    while (left) {
        const uint32_t down = state - (state >> 4);
        const bool high = down < limit;
        bool accept = false;
        if (left >= K && (!EntryOnly || first)) {
            if constexpr (Count) ++stats->checks;
            if constexpr (FixedBound) {
                const uint32_t difference = target >= state ? target - state : state - target;
                accept = difference >= K * RC_PDM_STEP - half;
            } else {
                accept = high ? limit - down > (K - 1) * (RC_PDM_STEP - (state >> 4))
                              : down - limit >= (K - 1) * (state >> 4);
            }
        }
        first = false;
        if (accept) {
            uint32_t distance = high ? UINT32_MAX - state : state;
            for (unsigned i = 0; i < K; ++i) distance -= distance >> 4;
            state = high ? UINT32_MAX - distance : distance;
            word = (word << K) | (high ? (1U << K) - 1U : 0);
            left -= K;
            if constexpr (Count) {
                ++stats->groups; stats->high_groups += high; grouped = true;
            }
        } else {
            state = down + (high ? RC_PDM_STEP : 0);
            word = (word << 1) | (uint32_t)high;
            --left;
        }
    }
    if constexpr (Count) stats->words_with_group += grouped;
    p->rc = state;
    return word;
}

// Check once at PCM entry. Keep the common no-group path literally identical
// to production, instead of adding a first-iteration flag to every bit step.
template<unsigned K, bool FixedBound, bool Count>
static inline uint32_t rc_run_entry_split(rc_pdm_t *p, int16_t pcm, RcRunStats *stats) {
    const uint32_t target = rc_pdm_target(pcm), half = RC_PDM_STEP >> 1;
    const uint32_t limit = target > half ? target - half : 0;
    uint32_t state = p->rc;
    const uint32_t down = state - (state >> 4);
    const bool high = down < limit;
    bool accept;
    if constexpr (FixedBound) {
        const uint32_t difference = target >= state ? target-state : state-target;
        accept = difference >= K*RC_PDM_STEP-half;
    } else {
        accept = high ? limit-down > (K-1)*(RC_PDM_STEP-(state>>4))
                      : down-limit >= (K-1)*(state>>4);
    }
    if constexpr (Count) ++stats->checks;
    if (!accept) return rc_pdm_sample(p,pcm);
    if constexpr (Count) {
        ++stats->groups; stats->high_groups += high; ++stats->words_with_group;
    }
    uint32_t distance = high ? UINT32_MAX-state : state;
    for (unsigned i=0; i<K; ++i) distance -= distance>>4;
    state = high ? UINT32_MAX-distance : distance;
    uint32_t word = high ? (1U<<K)-1 : 0;
    for (unsigned i=K; i<32; ++i) {
        state -= state>>4; word <<= 1;
        if (state < limit) { state += RC_PDM_STEP; word |= 1U; }
    }
    p->rc = state;
    return word;
}
