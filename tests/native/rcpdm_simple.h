#pragma once
#include "rc_pdm.h"

/* ESP32 also uses Xtensa on some models: do not select by ISA alone.
 * FORCE_C keeps an explicit reference/backend override for diagnostics. */
#ifndef RCPDM_SIMPLE_FORCE_C
#define RCPDM_SIMPLE_FORCE_C 0
#endif
/* Opt-in four-bit groups for the isolated LX106 speed comparison. */
#ifndef RCPDM_SIMPLE_UNROLL4
#define RCPDM_SIMPLE_UNROLL4 0
#endif
#if defined(__GNUC__) && defined(__XTENSA__) && !RCPDM_SIMPLE_FORCE_C && \
    (defined(ESP8266) || (defined(YORADIO_ESP8266_NATIVE) && YORADIO_ESP8266_NATIVE))
#define RCPDM_SIMPLE_LX106_ASM 1
#else
#define RCPDM_SIMPLE_LX106_ASM 0
#endif

/* Experimental direct PCM/current-state comparison, no look-ahead.
 * count is 1..32; shift is 1..31 (benchmarks use 2 and 4). State and target
 * have the same unsigned fixed32 scale as production RCPDM. MSB first.
 * This changes the modulation algorithm, not just its implementation. */
static inline uint32_t rcpdm_simple_bits_c(rc_pdm_t *p, int16_t pcm,
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

static inline uint32_t rcpdm_simple_bits(rc_pdm_t *p, int16_t pcm,
                                        unsigned count, unsigned shift) {
#if RCPDM_SIMPLE_LX106_ASM
    /* The hardware profile uses alpha=1/16; other coefficients retain C.
     * Zero must not enter the decrement-and-branch assembly loop. */
    if (shift == 4U && count != 0U) {
        const uint32_t target = rc_pdm_target(pcm);
        const uint32_t step = UINT32_MAX >> 4;
        uint32_t state = p->rc, word = 0, decay;
        /* Exact unsigned identity (including rounding):
         * ((UINT32_MAX-state)>>4) == step-(state>>4).
         * Compare OLD state; save its decay before adding step. The temporary
         * add may wrap modulo 2^32; subtracting decay yields the bounded final
         * RC state. After shifting word its LSB is zero, so +1 equals |1.
         * Early-clobbers keep loop-carried outputs distinct from invariant
         * inputs for ALL iterations, not merely the first. No memory/SAR/IRQ
         * changes: GCC handles register allocation and the normal ABI. */
#define RCPDM_SIMPLE_ASM_BIT \
            "srli %[decay], %[state], 4\n\t" \
            "slli %[word], %[word], 1\n\t" \
            "bgeu %[state], %[target], 2f\n\t" \
            "add %[state], %[state], %[step]\n\t" \
            "addi %[word], %[word], 1\n\t" \
            "2:\n\t" \
            "sub %[state], %[state], %[decay]\n\t"
#if RCPDM_SIMPLE_UNROLL4
        if ((count & 3U) == 0U) {
            /* Sequential dependent steps, not four independent samples.
             * .rept bounds expansion to four; GCC cannot unroll this asm.
             * 2f binds the next local label inside EACH repeated step. */
            unsigned groups = count >> 2;
            __asm__ volatile (
                "1:\n\t"
                ".rept 4\n\t"
                RCPDM_SIMPLE_ASM_BIT
                ".endr\n\t"
                "addi %[groups], %[groups], -1\n\t"
                "bnez %[groups], 1b\n\t"
                : [state] "+&r" (state), [word] "+&r" (word),
                  [groups] "+&r" (groups), [decay] "=&r" (decay)
                : [target] "r" (target), [step] "r" (step)
            );
            p->rc = state;
            return word;
        }
#endif
        /* Non-multiples of four retain the one-bit loop (no padding bits). */
        __asm__ volatile (
            "1:\n\t"
            RCPDM_SIMPLE_ASM_BIT
            "addi %[count], %[count], -1\n\t"
            "bnez %[count], 1b\n\t"
            : [state] "+&r" (state), [word] "+&r" (word),
              [count] "+&r" (count), [decay] "=&r" (decay)
            : [target] "r" (target), [step] "r" (step)
        );
#undef RCPDM_SIMPLE_ASM_BIT
        p->rc = state;
        return word;
    }
#endif
    return rcpdm_simple_bits_c(p, pcm, count, shift);
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
