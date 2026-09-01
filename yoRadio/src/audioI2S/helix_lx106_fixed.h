#pragma once

#include <stdint.h>

/* ESP8266 LX106 has a fast 32-bit low multiply but no high-half 32 x 32
 * instruction.  Expressing fixed-point multiply as int64_t makes GCC call
 * the ROM __muldi3 helper for every coefficient.  Helix executes thousands
 * of these operations per frame, so form the exact signed high half from
 * four native 32-bit multiplies instead.
 */
static inline __attribute__((always_inline)) int32_t
helix_lx106_mulshift32(int32_t x, int32_t y) {
    const int32_t x_hi = x >> 16;
    const int32_t y_hi = y >> 16;
    const uint32_t x_lo = (uint16_t)x;
    const uint32_t y_lo = (uint16_t)y;
    const uint32_t low = x_lo * y_lo;
    const int32_t cross0 = x_hi * (int32_t)y_lo + (int32_t)(low >> 16);
    const int32_t cross1 = y_hi * (int32_t)x_lo +
                           (int32_t)(uint16_t)cross0;

    return x_hi * y_hi + (cross0 >> 16) + (cross1 >> 16);
}

/* Exact unsigned high half using only native 16 x 16/32-bit products. */
static inline __attribute__((always_inline)) uint32_t
helix_lx106_umulshift32(uint32_t x, uint32_t y) {
    const uint32_t x_hi = x >> 16;
    const uint32_t y_hi = y >> 16;
    const uint32_t x_lo = (uint16_t)x;
    const uint32_t y_lo = (uint16_t)y;
    const uint32_t low = x_lo * y_lo;
    const uint32_t cross0 = x_hi * y_lo + (low >> 16);
    const uint32_t cross1 = y_hi * x_lo + (uint16_t)cross0;

    return x_hi * y_hi + (cross0 >> 16) + (cross1 >> 16);
}

/* Divide an unsigned value by a compile-time constant through its Q32
 * reciprocal. reciprocal_ceil must be floor(2^32 / divisor) + 1. The
 * reciprocal product can overestimate the quotient by one, so correct it to
 * retain the exact truncating-division result expected by the bitstream
 * parser.
 */
static inline __attribute__((always_inline)) uint32_t
helix_lx106_udiv_recip(uint32_t value, uint32_t divisor,
                       uint32_t reciprocal_ceil) {
    uint32_t quotient = helix_lx106_umulshift32(value, reciprocal_ceil);
    quotient -= (quotient * divisor > value);
    return quotient;
}

/* Add the exact two's-complement 32 x 32 product without invoking __muldi3.
 * The uint64_t addition is compiled as a carry-propagating pair of 32-bit
 * additions on LX106.
 */
static inline __attribute__((always_inline)) uint64_t
helix_lx106_madd64(uint64_t sum, int32_t x, int32_t y) {
    const uint32_t low = (uint32_t)x * (uint32_t)y;
    const uint32_t high = (uint32_t)helix_lx106_mulshift32(x, y);
    const uint64_t product = ((uint64_t)high << 32) | low;
    return sum + product;
}
