// Owned floor0 arithmetic for a future wide Vorbis synthesis path.
// Equations: Vorbis I 6.2.3; no vendor handles, allocation or Q24 conversion.
#pragma once
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NATIVE_VORBIS_NUMERIC_OK = 0,
    NATIVE_VORBIS_NUMERIC_INVALID = -1,
    NATIVE_VORBIS_NUMERIC_RANGE = -2,
    NATIVE_VORBIS_NUMERIC_TRUNCATED = -3,
    NATIVE_VORBIS_NUMERIC_CAPACITY = -4,
    NATIVE_VORBIS_NUMERIC_NO_LOOKUP = -5
} native_vorbis_numeric_status_t;

// Value = mantissa * 2^exponent. Zero is {0,0}; a nonzero finite mantissa
// satisfies .5 <= abs(mantissa) < 1. No conversion to a linear gain is implied.
typedef struct {
    double mantissa;
    int32_t exponent;
} native_vorbis_scaled_t;

// Exact affine VQ value: unpack(minimum_bits)*minimum_multiplier +
// unpack(delta_bits)*delta_multiplier. Packed words use Vorbis I 9.2.2,
// not IEEE float32; all 32-bit words and multipliers are accepted. Each term
// is exactly representable as binary64, but their floating sum need not be.
typedef struct {
    uint32_t minimum_bits, delta_bits;
    uint32_t minimum_multiplier, delta_multiplier;
} native_vorbis_affine_t;

typedef struct {
    uint64_t raw_amplitude;
    uint32_t amplitude_bits;   // Complete six-bit field: 0..63.
    uint32_t amplitude_offset; // Complete eight-bit field: 0..255.
} native_vorbis_floor0_amplitude_t;

typedef enum {
    NATIVE_VORBIS_FLOOR0_PRESENT = 0,
    NATIVE_VORBIS_FLOOR0_ABSENT = 1,
    NATIVE_VORBIS_FLOOR0_POLE = 2,
    NATIVE_VORBIS_FLOOR0_INDETERMINATE = 3
} native_vorbis_floor0_kind_t;

typedef struct {
    native_vorbis_floor0_kind_t kind;
    // For PRESENT only: this represents log2(linear gain), not linear gain.
    // log2_gain={0,0} means unity. ABSENT means an unused/zero floor.
    // POLE means positive amplitude / zero denominator; INDETERMINATE means
    // zero scaled amplitude / zero denominator. Neither invents a PCM policy.
    native_vorbis_scaled_t log2_gain;
} native_vorbis_floor0_gain_t;

// These helpers do not read or write beyond the declared arrays. Arrays must
// be valid for order elements; order is 1..255. Invalid calls leave outputs
// unchanged. In-place angles==coefficients is supported for cosine preparation.
// Preparation is a binary64 libm approximation: tiny angles can round 2*cos
// to 2. A precision-preserving angle path must not rely on that conversion.
native_vorbis_numeric_status_t native_vorbis_floor0_prepare_cosines(
    const double *angles, size_t order, double *coefficients, size_t capacity);

// Exact polynomial domain for the supplied binary64 coefficients/w in [-2,2].
// Return scaled D=P+Q, retaining nonzero tiny products instead of underflowing.
// This is separate from gain so a future stable angle implementation can
// supply its scaled denominator without first rounding angles to cosines.
native_vorbis_numeric_status_t native_vorbis_floor0_denominator(
    const double *coefficients, size_t order, double w,
    native_vorbis_scaled_t *denominator);

// D must be normalized, nonnegative and finite in the scaled representation.
// Raw zero (including bits0/raw0) returns ABSENT and does not require D.
// Amplitude scaling uses binary64 rounding, without the old Q4 truncation.
// The specification's literal 0.11512925 is retained in the dB conversion.
native_vorbis_numeric_status_t native_vorbis_floor0_gain_from_denominator(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const native_vorbis_scaled_t *denominator, native_vorbis_floor0_gain_t *gain);

native_vorbis_numeric_status_t native_vorbis_floor0_gain_at_cosine(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const double *coefficients, size_t order, double w,
    native_vorbis_floor0_gain_t *gain);

// Bark metadata uses the full positive16-bit fields. Bin count is 1..4096.
// Floating half-rate preserves odd rates. No sentinel element is written.
native_vorbis_numeric_status_t native_vorbis_floor0_bark_map(
    uint32_t rate, size_t bins, uint32_t bark_map_size,
    uint16_t *map, size_t capacity);

// w=2*cos(pi*bin/size), including exact rational-cosine cardinal points.
native_vorbis_numeric_status_t native_vorbis_floor0_bin_cosine(
    uint32_t bin, uint32_t bark_map_size, double *w);

native_vorbis_numeric_status_t native_vorbis_floor0_gain_at_bin(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const double *coefficients, size_t order, uint32_t bin,
    uint32_t bark_map_size, native_vorbis_floor0_gain_t *gain);

// Original-angle path: theta is mathematical pi*bin/bark_map_size, not a
// rounded binary64 bin cosine. All finite binary64 angles are accepted,
// including negatives, subnormals and angles outside [0,pi]. The internal
// fixed-point phase reduction and sine products avoid cosine cancellation.
// order is 1..255; bin < bark_map_size, with map size 1..65535. Inputs remain
// unchanged and an invalid call leaves the output unchanged. No allocation.
native_vorbis_numeric_status_t native_vorbis_floor0_denominator_at_bin(
    const double *angles, size_t order, uint32_t bin, uint32_t bark_map_size,
    native_vorbis_scaled_t *denominator);

// Raw zero returns ABSENT without reading angles, after validating amplitude,
// order and bin metadata. Otherwise evaluate the original-angle denominator
// and the same full-width amplitude / scaled-log2 gain as the coefficient API.
native_vorbis_numeric_status_t native_vorbis_floor0_gain_from_angles(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const double *angles, size_t order, uint32_t bin, uint32_t bark_map_size,
    native_vorbis_floor0_gain_t *gain);

// Evaluate original exact affine LSPs without rounding the sum of their two
// terms. Terms are reduced separately and combined in the integer phase grid.
// The same order/bin/output-preservation and absent-floor contracts apply.
native_vorbis_numeric_status_t native_vorbis_floor0_denominator_from_affine(
    const native_vorbis_affine_t *angles, size_t order, uint32_t bin,
    uint32_t bark_map_size, native_vorbis_scaled_t *denominator);
native_vorbis_numeric_status_t native_vorbis_floor0_gain_from_affine(
    const native_vorbis_floor0_amplitude_t *amplitude,
    const native_vorbis_affine_t *angles, size_t order, uint32_t bin,
    uint32_t bark_map_size, native_vorbis_floor0_gain_t *gain);

#ifdef __cplusplus
}
#endif
