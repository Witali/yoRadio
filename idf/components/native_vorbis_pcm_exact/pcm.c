// Compare exact two-word dyadics with S16 half-integer rounding thresholds.
#include "native_vorbis_pcm_exact.h"

_Static_assert(INT16_MIN == -32768 && INT16_MAX == 32767,
    "signed 16-bit PCM storage required");

// Signed two's-complement 128-bit exponent, represented only by unsigned words.
// It holds every int64 base plus all bounded normalization and PCM offsets.
typedef struct { uint64_t high, low; } exponent_t;
typedef struct { uint64_t low, high; } magnitude_t;
typedef struct { magnitude_t magnitude; exponent_t exponent; int sign; } term_t;

static exponent_t exponent_from(int64_t base) {
    return (exponent_t){.high = base < 0 ? UINT64_MAX : 0, .low = (uint64_t)base};
}

static exponent_t exponent_add(exponent_t value, int32_t offset) {
    uint64_t old = value.low;
    value.low += (uint64_t)(int64_t)offset;
    value.high += (offset < 0 ? UINT64_MAX : 0) + (value.low < old);
    return value;
}

static int exponent_compare(exponent_t a, exponent_t b) {
    if (a.high != b.high) {
        uint64_t sign = UINT64_C(1) << 63;
        return (a.high ^ sign) < (b.high ^ sign) ? -1 : 1;
    }
    return (a.low > b.low) - (a.low < b.low);
}

static bool magnitude_zero(magnitude_t value) {
    return !value.low && !value.high;
}

static unsigned word_width(uint64_t value) {
    unsigned result = 0;
    while (value) { ++result; value >>= 1; }
    return result;
}

static unsigned magnitude_width(magnitude_t value) {
    return value.high ? 64 + word_width(value.high) : word_width(value.low);
}

// Internal shifts are in [0,107], and every result fits at most 108 bits.
// For shifts >=64 this bound guarantees that the input high word is zero.
static magnitude_t magnitude_shift(magnitude_t value, unsigned shift) {
    if (!shift) return value;
    if (shift < 64) return (magnitude_t){.low = value.low << shift,
        .high = (value.high << shift) | (value.low >> (64 - shift))};
    return (magnitude_t){.low = 0, .high = value.low << (shift - 64)};
}

static int words_compare(magnitude_t a, magnitude_t b) {
    if (a.high != b.high) return a.high > b.high ? 1 : -1;
    return (a.low > b.low) - (a.low < b.low);
}

// The only addition combines a <=107-bit value and a <=106-bit value.
static magnitude_t magnitude_add(magnitude_t a, magnitude_t b) {
    uint64_t low = a.low + b.low;
    return (magnitude_t){.low = low, .high = a.high + b.high + (low < a.low)};
}

// Only called with a >= b, so the unsigned borrow leaves the exact difference.
static magnitude_t magnitude_subtract(magnitude_t a, magnitude_t b) {
    return (magnitude_t){.low = a.low - b.low,
        .high = a.high - b.high - (a.low < b.low)};
}

// Original nonzero terms have exactly 106 magnitude bits. Zero's scale is unused.
static term_t normalized(magnitude_t magnitude, exponent_t exponent, int sign) {
    if (magnitude_zero(magnitude)) return (term_t){0};
    unsigned shift = 106 - magnitude_width(magnitude);
    return (term_t){.magnitude = magnitude_shift(magnitude, shift),
        .exponent = exponent_add(exponent, -(int32_t)shift), .sign = sign};
}

static bool canonical(const native_vorbis_window_product_t *product) {
    if (!product->low && !product->high)
        return product->exponent == 0 && product->shift == 0 && !product->negative;
    return (product->low & 1U) && product->high < (UINT64_C(1) << 42) &&
        product->shift >= -2148 && product->shift <= 1023;
}

static term_t scaled_product(const native_vorbis_window_product_t *product) {
    magnitude_t magnitude = {.low = product->low, .high = product->high};
    // Validation bounds shift+15 to [-2133,1038]; the base is never added in int64.
    exponent_t exponent = exponent_add(exponent_from(product->exponent), product->shift + 15);
    return normalized(magnitude, exponent, product->negative ? -1 : 1);
}

static int magnitude_compare(term_t a, term_t b) {
    unsigned a_width = magnitude_width(a.magnitude), b_width = magnitude_width(b.magnitude);
    int top = exponent_compare(exponent_add(a.exponent, (int32_t)a_width - 1),
        exponent_add(b.exponent, (int32_t)b_width - 1));
    if (top) return top;
    // Equal top positions require only a width difference, never exponent
    // subtraction. The alignment and its result remain bounded by 108 bits.
    if (a_width < b_width) a.magnitude = magnitude_shift(a.magnitude, b_width - a_width);
    else b.magnitude = magnitude_shift(b.magnitude, a_width - b_width);
    return words_compare(a.magnitude, b.magnitude);
}

static int two_sign(term_t a, term_t b) {
    if (magnitude_zero(a.magnitude)) return b.sign;
    if (magnitude_zero(b.magnitude) || a.sign == b.sign) return a.sign;
    int comparison = magnitude_compare(a, b);
    return comparison > 0 ? a.sign : comparison < 0 ? b.sign : 0;
}

// All three inputs are normalized to 106 bits. A top exponent gap >=2 makes
// the first magnitude exceed the sum of both smaller magnitudes. Otherwise
// the leading pair merges exactly into <=108 bits before comparing the third.
static int three_sign(term_t a, term_t b, term_t c) {
    term_t terms[3] = {a, b, c};
    unsigned count = 0;
    for (unsigned i = 0; i < 3; ++i) {
        term_t input = terms[i];
        if (magnitude_zero(input.magnitude)) continue;
        unsigned at = count++;
        while (at && exponent_compare(input.exponent, terms[at - 1].exponent) > 0) {
            terms[at] = terms[at - 1];
            --at;
        }
        terms[at] = input;
    }
    if (!count) return 0;
    if (count == 1) return terms[0].sign;
    if (count == 2) return two_sign(terms[0], terms[1]);
    if (exponent_compare(terms[0].exponent, exponent_add(terms[1].exponent, 1)) > 0)
        return terms[0].sign;
    unsigned shift = exponent_compare(terms[0].exponent, terms[1].exponent) != 0;
    magnitude_t first = magnitude_shift(terms[0].magnitude, shift);
    magnitude_t second = terms[1].magnitude;
    term_t merged = {.exponent = terms[1].exponent};
    if (terms[0].sign == terms[1].sign) {
        merged.magnitude = magnitude_add(first, second);
        merged.sign = terms[0].sign;
    } else {
        int comparison = words_compare(first, second);
        merged.magnitude = comparison >= 0 ? magnitude_subtract(first, second) :
            magnitude_subtract(second, first);
        merged.sign = comparison > 0 ? terms[0].sign : comparison < 0 ? terms[1].sign : 0;
    }
    return two_sign(merged, terms[2]);
}

static int16_t rounded_sample(term_t a, term_t b) {
    int32_t low = -32768, high = 32767;
    // The inclusive 65536-value interval halves exactly on each of 16 steps.
    for (unsigned step = 0; step < 16; ++step) {
        int32_t middle = low + (high - low) / 2;
        int32_t twice_boundary = 2 * middle + 1;
        magnitude_t magnitude = {.low = (uint64_t)(twice_boundary < 0 ?
            -twice_boundary : twice_boundary)};
        // Add the negation of middle+.5 to the exact scaled sum. At a tie,
        // choose the adjacent even integer, including for negative boundaries.
        term_t boundary = normalized(magnitude, exponent_from(-1), twice_boundary < 0 ? 1 : -1);
        int comparison = three_sign(a, b, boundary);
        if (comparison > 0 || (comparison == 0 && middle % 2 != 0)) low = middle + 1;
        else high = middle;
    }
    return (int16_t)low;
}

native_vorbis_numeric_status_t native_vorbis_pcm_s16_product_pair(
    const native_vorbis_window_product_t *previous,
    const native_vorbis_window_product_t *current, int16_t *result) {
    if (!previous || !current || !result || !canonical(previous) || !canonical(current))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    int16_t candidate = rounded_sample(scaled_product(previous), scaled_product(current));
    *result = candidate;
    return NATIVE_VORBIS_NUMERIC_OK;
}
