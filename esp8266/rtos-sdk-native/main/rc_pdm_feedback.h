#pragma once
#include <stdint.h>
#include <stddef.h>

/* Experimental RC tracking with accumulated output error. All quantities are
 * integer: one PCM LSB is 8192 state units. Headroom is reserved for feedback;
 * this is deliberately not the rail-to-rail uint32_t format of rc_pdm.h.
 * Do not substitute this algorithm into an existing bit-exact backend. */
#define RC_FB_FULL INT32_C(536870912)
#define RC_FB_ERROR_LIMIT INT32_C(1073741824)
#define RC_FB_DEFAULT_SEED UINT32_C(0x9e3779b9)
typedef struct {
    int32_t rc;
    int32_t error;
    int32_t previous;
    uint32_t random;
} rc_pdm_feedback_t;

static inline void rc_pdm_feedback_init(rc_pdm_feedback_t *p, uint32_t seed) {
    p->rc = RC_FB_FULL / 2;
    p->previous = RC_FB_FULL / 2;
    p->error = 0;
    p->random = seed ? seed : RC_FB_DEFAULT_SEED;
}

/* Defined floor division, including negative values; no signed-left-shift UB
 * and no dependency on implementation-defined signed right shift. */
static inline int32_t rc_fb_shift(int32_t value, unsigned shift) {
    return value >= 0 ? value >> shift : -1 - (int32_t)((uint32_t)(-(value + 1)) >> shift);
}

static inline uint32_t rc_fb_random(rc_pdm_feedback_t *p) {
    uint32_t x = p->random;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    p->random = x;
    return x;
}

/* bits=8,16,32,64,128; RC shift=2..6; feedback shift=0..6.
 * dither=0:none, 1:uniform +/-half a decision step, 2:TPDF +/-half,
 * 3:TPDF +/-one step. Dither only perturbs the decision, never the desired PCM
 * in the accumulated error. These selectors are compile-time constants in a
 * hardware wrapper and runtime parameters only in the quality sweep.
 * out contains chronological MSB-first words; 8/16-bit frames use low bits.
 * An interpolated PCM step is EXACT in this scale for every supported bits
 * value, so even +/-1 PCM LSB is not rounded away. */
static inline void rc_pdm_feedback_frame(rc_pdm_feedback_t *p, int16_t pcm,
        uint32_t *out, unsigned bits, unsigned shift, unsigned feedback_shift,
        unsigned dither, int interpolate) {
    const int32_t target = ((int32_t)pcm + 32768) * 8192;
    const int32_t increment = interpolate ? (target - p->previous) / (int32_t)bits : 0;
    int32_t desired = interpolate ? p->previous : target;
    const int32_t step = RC_FB_FULL >> shift;
    uint32_t word = 0;
    unsigned output = 0;
    for (unsigned bit = 0; bit < bits; ++bit) {
        desired += increment;
        int32_t noise = 0;
        if (dither) {
            const uint32_t r = rc_fb_random(p);
            const int32_t triangle = (int32_t)(r & 65535U) + (int32_t)(r >> 16) - 65535;
            noise = dither == 1 ? (int32_t)(r >> (shift + 3)) - step / 2
                  : triangle * (INT32_C(1) << (dither == 3 ? 13 - shift : 12 - shift));
        }
        const int32_t down = p->rc - (p->rc >> shift);
        const int32_t adjusted = desired + rc_fb_shift(p->error, feedback_shift) + noise;
        const uint32_t high = adjusted > down + step / 2;
        p->rc = down + (high ? step : 0);
        /* |error| <= 2^30, |desired-rc| <= 2^29, so this addition and the
         * comparison path stay strictly inside signed 32-bit range. Clamp
         * prevents windup for unattainable targets at full-scale transitions. */
        const int32_t error = p->error + (desired - p->rc);
        p->error = error > RC_FB_ERROR_LIMIT ? RC_FB_ERROR_LIMIT
                 : error < -RC_FB_ERROR_LIMIT ? -RC_FB_ERROR_LIMIT : error;
        word = (word << 1) | high;
        if ((bit + 1) % 32 == 0 || bit + 1 == bits) {
            out[output++] = word;
            word = 0;
        }
    }
    p->previous = target;
}

/* Selected 48-kHz/32-bit profile: unity accumulated-error feedback, TPDF
 * decision dither and causal linear interpolation. The dither generator is
 * deliberately deterministic across resets for regression reproducibility. */
static inline uint32_t rc_pdm_feedback_sample(rc_pdm_feedback_t *p, int16_t pcm) {
    uint32_t word;
    rc_pdm_feedback_frame(p, pcm, &word, 32, 4, 0, 2, 1);
    return word;
}
static inline void rc_pdm_feedback_fill(rc_pdm_feedback_t *p, uint32_t *out,
        const int16_t *pcm, size_t frames, unsigned channels) {
    rc_pdm_feedback_t current = *p;
    for (size_t i = 0; i < frames; ++i) {
        int32_t mono = pcm[i * channels];
        if (channels == 2) mono = (mono + pcm[i * channels + 1]) / 2;
        out[i] = rc_pdm_feedback_sample(&current, (int16_t)mono);
    }
    *p = current;
}
