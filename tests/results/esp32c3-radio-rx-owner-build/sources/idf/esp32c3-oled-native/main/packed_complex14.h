#pragma once

// Storage ABI: [exponent:4][imaginary:14][real:14], shift = exponent + 3.
// Arithmetic stays int32. Never use C bitfields, signed shifts or abs(INT_MIN).
#include <stdbool.h>
#include <stdint.h>

typedef enum { PC14_NEAREST, PC14_MIDPOINT } pc14_mode_t;

static inline int32_t pc14_mantissa(int32_t x, unsigned shift, pc14_mode_t mode) {
    uint32_t magnitude = x < 0 ? 0u - (uint32_t)x : (uint32_t)x;
    uint32_t bias = mode == PC14_NEAREST ? (1u << (shift - 1)) :
                    (x < 0 ? (1u << shift) - 1u : 0u);
    int32_t m = (int32_t)((magnitude + bias) >> shift);
    return x < 0 ? -m : m;
}

static inline uint32_t pc14_pack(int32_t real, int32_t imag, pc14_mode_t mode,
                                unsigned *saturations) {
    unsigned shift = 3;
    int32_t mr = pc14_mantissa(real, shift, mode);
    int32_t mi = pc14_mantissa(imag, shift, mode);
    while (shift < 18 && (mr > 8191 || mi > 8191 || mr < -8192 || mi < -8192)) {
        ++shift;
        mr = pc14_mantissa(real, shift, mode);
        mi = pc14_mantissa(imag, shift, mode);
    }
    unsigned clipped = (mr > 8191) + (mi > 8191);
    if (mr > 8191) mr = 8191;
    if (mi > 8191) mi = 8191;
    if (saturations) *saturations = clipped;
    return ((shift - 3u) << 28) | (((uint32_t)mi & 0x3fffu) << 14) |
           ((uint32_t)mr & 0x3fffu);
}

static inline int32_t pc14_sign_extend(uint32_t bits) {
    return (int32_t)(bits & 0x1fffu) - (int32_t)(bits & 0x2000u);
}

static inline int32_t pc14_expand(int32_t m, unsigned shift, pc14_mode_t mode) {
    int32_t value = m * (int32_t)(1u << shift);
    if (mode == PC14_MIDPOINT && m) value += (int32_t)(1u << (shift - 1));
    return value;
}

static inline void pc14_unpack(uint32_t packed, pc14_mode_t mode,
                               int32_t *real, int32_t *imag) {
    unsigned shift = (packed >> 28) + 3u;
    *real = pc14_expand(pc14_sign_extend(packed & 0x3fffu), shift, mode);
    *imag = pc14_expand(pc14_sign_extend((packed >> 14) & 0x3fffu), shift, mode);
}
