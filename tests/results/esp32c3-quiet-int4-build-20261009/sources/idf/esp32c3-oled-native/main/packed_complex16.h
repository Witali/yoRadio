#pragma once

// Experimental storage ABI: one [Im16:Re16] word per complex sample, plus
// eight independent exponent nibbles per exponent word (sample 0 in bits 3..0).
// shift = exponent + 1, i.e. 1..16. This header does not change codec allocation.
#include <stddef.h>
#include <stdint.h>

static inline int32_t pc16_round(int32_t value, unsigned shift) {
    uint32_t magnitude = value < 0 ? 0u - (uint32_t)value : (uint32_t)value;
    int32_t m = (int32_t)((magnitude + (1u << (shift - 1))) >> shift);
    return value < 0 ? -m : m; // Nearest; ties away from zero.
}

// Select the smallest supported shift for which BOTH rounded mantissas fit.
// At shift 16, positive rounding carry is clamped to 32767 and reported.
// INT32_MIN is represented exactly; INT32_MAX reconstructs to 2147418112.
static inline uint32_t pc16_pack(int32_t real, int32_t imag,
                                unsigned *exponent, unsigned *saturations) {
    unsigned shift = 1;
    int32_t r = pc16_round(real, shift), i = pc16_round(imag, shift);
    while (shift < 16 && (r > 32767 || i > 32767 || r < -32768 || i < -32768)) {
        ++shift;
        r = pc16_round(real, shift);
        i = pc16_round(imag, shift);
    }
    unsigned clipped = (r > 32767) + (i > 32767);
    if (r > 32767) r = 32767;
    if (i > 32767) i = 32767;
    *exponent = shift - 1;
    if (saturations) *saturations = clipped;
    return (((uint32_t)i & 0xffffu) << 16) | ((uint32_t)r & 0xffffu);
}

static inline int32_t pc16_expand(uint32_t bits, unsigned shift) {
    int32_t m = (int32_t)(bits & 0x7fffu) - (int32_t)(bits & 0x8000u);
    // All products fit int32 for every valid word and shift, including -2^31.
    return m * (int32_t)(1u << shift);
}

static inline void pc16_unpack(uint32_t mantissas, unsigned exponent,
                              int32_t *real, int32_t *imag) {
    unsigned shift = (exponent & 15u) + 1u;
    *real = pc16_expand(mantissas, shift);
    *imag = pc16_expand(mantissas >> 16, shift);
}

static inline size_t pc16_exponent_words(size_t count) {
    return count / 8u + (count % 8u != 0);
}

// Full-block path: eight independent exponents in one returned/stored word.
// This avoids eight read/modify/write operations on the exponent array.
// Input and output arrays must not overlap. Use store/load for a partial tail.
static inline uint32_t pc16_pack8(const int32_t *real, const int32_t *imag,
                                 uint32_t *mantissas, unsigned *saturations) {
    uint32_t exponents = 0;
    unsigned clipped = 0;
    for (unsigned n = 0; n < 8; ++n) {
        unsigned exponent, pair_clipped;
        mantissas[n] = pc16_pack(real[n], imag[n], &exponent, &pair_clipped);
        exponents |= exponent << (n * 4u);
        clipped += pair_clipped;
    }
    if (saturations) *saturations = clipped;
    return exponents;
}

static inline void pc16_unpack8(const uint32_t *mantissas, uint32_t exponents,
                               int32_t *real, int32_t *imag) {
    for (unsigned n = 0; n < 8; ++n) {
        pc16_unpack(mantissas[n], exponents & 15u, real + n, imag + n);
        exponents >>= 4;
    }
}

// Caller owns N mantissa words and ceil(N/8) ZERO-INITIALIZED exponent words.
// No padded per-sample struct. Updating a nibble requires single-writer access.
static inline void pc16_store(uint32_t *mantissas, uint32_t *exponents, size_t n,
                             int32_t real, int32_t imag, unsigned *saturations) {
    unsigned exponent, bit = (unsigned)(n & 7u) * 4u;
    mantissas[n] = pc16_pack(real, imag, &exponent, saturations);
    uint32_t word = exponents[n / 8u];
    exponents[n / 8u] = (word & ~(15u << bit)) | (exponent << bit);
}

static inline void pc16_load(const uint32_t *mantissas, const uint32_t *exponents,
                            size_t n, int32_t *real, int32_t *imag) {
    unsigned exponent = (exponents[n / 8u] >> ((n & 7u) * 4u)) & 15u;
    pc16_unpack(mantissas[n], exponent, real, imag);
}
