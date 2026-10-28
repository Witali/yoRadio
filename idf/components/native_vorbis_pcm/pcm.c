// Exact dyadic comparisons avoid overflow, underflow, and premature clipping.
#include "native_vorbis_pcm.h"
#include <float.h>
#include <string.h>

_Static_assert(sizeof(double) == sizeof(uint64_t) && DBL_MANT_DIG == 53 &&
    DBL_MAX_EXP == 1024 && FLT_RADIX == 2, "binary64 storage required");

// A signed two-word exponent holds int64 scale plus binary64/PCM offsets.
// All arithmetic on its representation is unsigned, including carries.
typedef struct { uint64_t high, low; } exponent_t;
typedef struct { uint64_t magnitude; exponent_t exponent; int sign; } term_t;

static exponent_t exponent_from(int64_t scale) {
    return (exponent_t){.high = scale < 0 ? UINT64_MAX : 0, .low = (uint64_t)scale};
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

static unsigned width(uint64_t value) {
    unsigned result = 0;
    while (value) { ++result; value >>= 1; }
    return result;
}

// All original terms have exactly53 magnitude bits; zero's exponent is unused.
static term_t normalized(uint64_t magnitude, exponent_t exponent, int sign) {
    if (!magnitude) return (term_t){0};
    unsigned shift = 53 - width(magnitude);
    return (term_t){.magnitude = magnitude << shift,
        .exponent = exponent_add(exponent, -(int32_t)shift), .sign = sign};
}

static uint64_t binary64_word(const double *value) {
    uint64_t word; memcpy(&word, value, sizeof(word)); return word;
}

static term_t scaled_double(const double *value, int64_t scale) {
    uint64_t word = binary64_word(value);
    uint32_t field = (uint32_t)((word >> 52) & 2047);
    uint64_t magnitude = word & UINT64_C(0x000fffffffffffff);
    if (field) magnitude |= UINT64_C(1) << 52;
    int32_t offset = field ? (int32_t)field - 1060 : -1059;
    return normalized(magnitude, exponent_add(exponent_from(scale), offset), word >> 63 ? -1 : 1);
}

static int magnitude_compare(term_t a, term_t b) {
    unsigned a_width = width(a.magnitude), b_width = width(b.magnitude);
    int top = exponent_compare(exponent_add(a.exponent, (int32_t)a_width - 1),
        exponent_add(b.exponent, (int32_t)b_width - 1));
    if (top) return top;
    // Equal top positions: alignment needs at most54 shifts and the aligned
    // result has at most55 bits. No exponent subtraction or unbounded shift.
    if (a_width < b_width) a.magnitude <<= b_width - a_width;
    else b.magnitude <<= a_width - b_width;
    return (a.magnitude > b.magnitude) - (a.magnitude < b.magnitude);
}

static int two_sign(term_t a, term_t b) {
    if (!a.magnitude) return b.sign;
    if (!b.magnitude || a.sign == b.sign) return a.sign;
    int comparison = magnitude_compare(a, b);
    return comparison > 0 ? a.sign : comparison < 0 ? b.sign : 0;
}

// Exact sign of three original normalized53-bit terms. Sort by top exponent.
// A gap>=2 makes the top term larger than the sum of both smaller terms.
// Otherwise merge the first two exactly into <=55 bits, then compare the third.
static int three_sign(term_t a, term_t b, term_t c) {
    term_t terms[3]; unsigned count = 0;
    const term_t input[3] = {a, b, c};
    for (unsigned i = 0; i < 3; ++i) {
        if (!input[i].magnitude) continue;
        unsigned at = count++;
        while (at && exponent_compare(input[i].exponent, terms[at - 1].exponent) > 0) {
            terms[at] = terms[at - 1]; --at;
        }
        terms[at] = input[i];
    }
    if (!count) return 0;
    if (count == 1) return terms[0].sign;
    if (count == 2) return two_sign(terms[0], terms[1]);
    if (exponent_compare(terms[0].exponent, exponent_add(terms[1].exponent, 1)) > 0)
        return terms[0].sign;
    unsigned shift = exponent_compare(terms[0].exponent, terms[1].exponent) != 0;
    uint64_t first = terms[0].magnitude << shift, second = terms[1].magnitude;
    term_t merged = {.exponent = terms[1].exponent};
    if (terms[0].sign == terms[1].sign) {
        merged.magnitude = first + second; merged.sign = terms[0].sign;
    } else if (first >= second) {
        merged.magnitude = first - second; merged.sign = first == second ? 0 : terms[0].sign;
    } else {
        merged.magnitude = second - first; merged.sign = terms[1].sign;
    }
    return two_sign(merged, terms[2]);
}

static int16_t sample(term_t a, term_t b) {
    int32_t low = -32768, high = 32767;
    while (low < high) {
        int32_t middle = low + (high - low) / 2;
        int32_t twice_boundary = 2 * middle + 1;
        // Compare the scaled PCM sum with middle+.5 by adding its negation.
        uint64_t magnitude = (uint64_t)(twice_boundary < 0 ? -twice_boundary : twice_boundary);
        term_t boundary = normalized(magnitude, exponent_from(-1), twice_boundary < 0 ? 1 : -1);
        int comparison = three_sign(a, b, boundary);
        if (comparison > 0 || (comparison == 0 && middle % 2 != 0)) low = middle + 1;
        else high = middle;
    }
    return (int16_t)low;
}

native_vorbis_numeric_status_t native_vorbis_pcm_s16_pair(
    const native_vorbis_transform_block_t *previous, size_t previous_capacity,
    const native_vorbis_transform_block_t *current, size_t current_capacity,
    int16_t *output, size_t output_capacity) {
    if (!previous || !current || previous->count != current->count)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (previous_capacity > SIZE_MAX / sizeof(*previous->samples) ||
        current_capacity > SIZE_MAX / sizeof(*current->samples) ||
        output_capacity > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    uint32_t count = previous->count;
    if (previous_capacity < count || current_capacity < count || output_capacity < count)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (count && (!previous->samples || !current->samples || !output))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    for (uint32_t i = 0; i < count; ++i) {
        if (((binary64_word(previous->samples + i) >> 52) & 2047) == 2047 ||
            ((binary64_word(current->samples + i) >> 52) & 2047) == 2047)
            return NATIVE_VORBIS_NUMERIC_RANGE;
    }
    for (uint32_t i = 0; i < count; ++i)
        output[i] = sample(scaled_double(previous->samples + i, previous->exponent),
            scaled_double(current->samples + i, current->exponent));
    return NATIVE_VORBIS_NUMERIC_OK;
}
