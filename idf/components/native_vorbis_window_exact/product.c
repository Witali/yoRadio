// Preserve both binary64 operands exactly, including minimum subnormals.
#include "native_vorbis_window_exact.h"
#include <float.h>
#include <string.h>

_Static_assert(sizeof(double) == sizeof(uint64_t) && FLT_RADIX == 2 &&
    DBL_MANT_DIG == 53 && DBL_MIN_EXP == -1021 && DBL_MAX_EXP == 1024,
    "binary64 storage required");

typedef struct { uint64_t magnitude; int32_t shift; } dyadic_t;

static dyadic_t odd_dyadic(uint64_t absolute_bits) {
    uint32_t field = (uint32_t)(absolute_bits >> 52);
    uint64_t magnitude = absolute_bits & UINT64_C(0x000fffffffffffff);
    if (field) magnitude |= UINT64_C(1) << 52;
    int32_t shift = field ? (int32_t)field - 1075 : -1074;
    // The caller has excluded zero; at most 52 trailing bits can be removed.
    while (!(magnitude & 1U)) { magnitude >>= 1; ++shift; }
    return (dyadic_t){.magnitude = magnitude, .shift = shift};
}

static void multiply_53(uint64_t a, uint64_t b, uint64_t *low, uint64_t *high) {
    uint32_t a0 = (uint32_t)a, b0 = (uint32_t)b;
    uint32_t a1 = (uint32_t)(a >> 32), b1 = (uint32_t)(b >> 32);
    uint64_t p00 = (uint64_t)a0 * b0;
    uint64_t p01 = (uint64_t)a0 * b1;
    uint64_t p10 = (uint64_t)a1 * b0;
    uint64_t p11 = (uint64_t)a1 * b1;
    // Each middle addend is at most 32 bits; their sum fits 34 bits. High
    // partial products use at most 21-bit halves, so the final sum fits uint64.
    // Since a,b < 2^53 the complete product is less than 2^106.
    uint64_t middle = (p00 >> 32) + (uint32_t)p01 + (uint32_t)p10;
    *low = (uint32_t)p00 | ((uint64_t)(uint32_t)middle << 32);
    *high = p11 + (p01 >> 32) + (p10 >> 32) + (middle >> 32);
}

native_vorbis_numeric_status_t native_vorbis_window_multiply_exact(
    double sample, double factor, int64_t exponent,
    native_vorbis_window_product_t *result) {
    if (!result) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint64_t sample_bits, factor_bits;
    memcpy(&sample_bits, &sample, sizeof(sample_bits));
    memcpy(&factor_bits, &factor, sizeof(factor_bits));
    uint64_t sample_absolute = sample_bits & UINT64_C(0x7fffffffffffffff);
    uint64_t factor_absolute = factor_bits & UINT64_C(0x7fffffffffffffff);
    if ((sample_absolute >> 52) == 2047 || (factor_absolute >> 52) == 2047 ||
        factor_absolute > UINT64_C(0x3ff0000000000000) ||
        ((factor_bits >> 63) && factor_absolute)) return NATIVE_VORBIS_NUMERIC_RANGE;
    native_vorbis_window_product_t candidate;
    memset(&candidate, 0, sizeof(candidate));
    if (sample_absolute && factor_absolute) {
        dyadic_t a = odd_dyadic(sample_absolute), b = odd_dyadic(factor_absolute);
        multiply_53(a.magnitude, b.magnitude, &candidate.low, &candidate.high);
        // Each decoded shift is bounded; factor <= 1 also gives b.shift <= 0.
        // Their sum lies in [-2148,1023], independent of the base exponent.
        candidate.shift = a.shift + b.shift;
        candidate.exponent = exponent;
        candidate.negative = (sample_bits >> 63) != 0;
    }
    memcpy(result, &candidate, sizeof(candidate));
    return NATIVE_VORBIS_NUMERIC_OK;
}
