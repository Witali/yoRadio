#ifndef YORADIO_PCM_HEADER_GAIN_H
#define YORADIO_PCM_HEADER_GAIN_H

/* Application gain on already quantized PCM, not pre-quantization synthesis.
 * RFC 7845 section 5.1: factor = 10^(signed Q7.8 dB / (20 * 256)).
 * Initialize storage with {0}; begin once per logical link and reset on its
 * completion/cancellation. All formats are packed little endian. U8 is
 * offset-binary (silence128); S8 is two's-complement (silence0), matching the
 * current native output path. No heap, pointers or PCM are retained.
 *
 * Apply validates the complete span before modifying any byte. It rounds to
 * nearest with halfway cases away from zero, then saturates to the format's
 * integer range, matching the existing output gain policy. Zero dB validates
 * the same contract and leaves every input byte exact. The factor uses the
 * platform's finite double/libm arithmetic; this is not a universal bit-exact
 * real-number or libopus floating-synthesis equivalence claim.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#ifndef PCM_HEADER_GAIN_POW
#define PCM_HEADER_GAIN_POW pow
#endif

typedef enum {
    PHG_PCM_U8 = 0, PHG_PCM_S8, PHG_PCM_S16LE, PHG_PCM_S24LE, PHG_PCM_S32LE
} pcm_header_gain_format;
typedef enum {
    PHG_OK = 0, PHG_INVALID = -1, PHG_UNALIGNED = -2, PHG_MATH = -3
} pcm_header_gain_status;
typedef struct {
    double factor;
    uint32_t generation;
    int16_t gain_q8;
    bool active;
} pcm_header_gain;

static inline void phg_reset(pcm_header_gain *s)
{
    if (s) memset(s, 0, sizeof(*s));
}

/* On every error the existing state is unchanged, including math refusal. */
static inline pcm_header_gain_status phg_begin(pcm_header_gain *s,
    uint32_t generation, int32_t gain_q8)
{
    if (!s || s->active || gain_q8 < INT16_MIN || gain_q8 > INT16_MAX)
        return PHG_INVALID;
    double factor = gain_q8 ?
        PCM_HEADER_GAIN_POW(10.0, (double)gain_q8 / (20.0 * 256.0)) : 1.0;
    if (!isfinite(factor) || factor <= 0.0) return PHG_MATH;
    pcm_header_gain next;
    memset(&next, 0, sizeof(next));
    next.factor = factor;
    next.generation = generation;
    next.gain_q8 = (int16_t)gain_q8;
    next.active = true;
    *s = next;
    return PHG_OK;
}

static inline unsigned phg_width(pcm_header_gain_format format)
{
    switch (format) {
    case PHG_PCM_U8: case PHG_PCM_S8: return 1;
    case PHG_PCM_S16LE: return 2;
    case PHG_PCM_S24LE: return 3;
    case PHG_PCM_S32LE: return 4;
    default: return 0;
    }
}

/* Internal conversion receives only a validated format/width and storage. */
static inline int64_t phg_read(const uint8_t *p, unsigned width,
                               pcm_header_gain_format format)
{
    uint64_t value = 0;
    for (unsigned i = 0; i < width; ++i) value |= (uint64_t)p[i] << (8u * i);
    if (format == PHG_PCM_U8) return (int64_t)value - 128;
    uint64_t sign = UINT64_C(1) << (width * 8u - 1u);
    return value & sign ? (int64_t)value - (int64_t)(sign * 2u) : (int64_t)value;
}

static inline void phg_write(uint8_t *p, unsigned width,
                              pcm_header_gain_format format, int64_t sample)
{
    uint64_t encoded = format == PHG_PCM_U8 ? (uint64_t)(sample + 128) : (uint64_t)sample;
    for (unsigned i = 0; i < width; ++i) p[i] = (uint8_t)(encoded >> (8u * i));
}

static inline pcm_header_gain_status phg_apply(const pcm_header_gain *s,
    uint32_t generation, pcm_header_gain_format format, uint8_t channels,
    uint8_t *data, size_t buffer_bytes, size_t offset, size_t bytes)
{
    unsigned width = phg_width(format);
    if (!s || !s->active || s->generation != generation || !width || !channels ||
        !isfinite(s->factor) || s->factor <= 0.0 || (!data && buffer_bytes) ||
        offset > buffer_bytes || bytes > buffer_bytes - offset)
        return PHG_INVALID;
    size_t frame = (size_t)channels * width; /* <=255*4, never overflows. */
    if (buffer_bytes % frame || offset % frame || bytes % frame)
        return PHG_UNALIGNED;
    if (!bytes || !s->gain_q8) return PHG_OK;
    int64_t low = -(INT64_C(1) << (width * 8u - 1u));
    int64_t high = -low - 1;
    for (size_t at = 0; at < bytes; at += width) {
        uint8_t *sample_bytes = data + offset + at;
        int64_t sample = phg_read(sample_bytes, width, format);
        double scaled = (double)sample * s->factor;
        int64_t result;
        /* Clamp before conversion: even corrupted finite factors producing
         * infinity cannot reach an undefined floating-to-integer cast.
         * Every remaining magnitude is bounded by 2^31 + 0.5 in int64_t.
         */
        if (scaled >= (double)high) result = high;
        else if (scaled <= (double)low) result = low;
        else result = scaled >= 0.0 ? (int64_t)(scaled + 0.5) : -(int64_t)(-scaled + 0.5);
        phg_write(sample_bytes, width, format, result);
    }
    return PHG_OK;
}

#endif
