// One correctly rounded binary64 boundary after exact residue/floor1 arithmetic.
#include "native_vorbis_transform.h"
#include <float.h>
#include <string.h>

_Static_assert(sizeof(double) == sizeof(uint64_t) && DBL_MANT_DIG == 53 &&
    DBL_MAX_EXP == 1024 && FLT_RADIX == 2, "binary64 storage required");
enum { MAX_LIMBS = 36, WORKING_SHIFT = 512 };

static bool shape_valid(const native_vorbis_floor1_product_layout_t *shape) {
    if (!shape->bins || shape->bins > 4096 ||
        shape->limb_count != (uint64_t)shape->bins * shape->limbs) return false;
    if (!shape->limbs) return !shape->magnitude_bits && !shape->exponent;
    return shape->limbs <= MAX_LIMBS && shape->magnitude_bits &&
        shape->magnitude_bits <= MAX_LIMBS * 32 - 1 &&
        shape->limbs == (shape->magnitude_bits + 32) / 32;
}

static bool sample_valid(const uint32_t *sample,
                         const native_vorbis_floor1_product_layout_t *shape) {
    uint32_t word = shape->magnitude_bits / 32, bit = shape->magnitude_bits % 32;
    uint32_t low_mask = bit ? (UINT32_C(1) << bit) - 1 : 0;
    bool negative = (sample[shape->limbs - 1] >> 31) != 0;
    bool lower_nonzero = (sample[word] & low_mask) != 0;
    for (uint32_t i = 0; i < word; ++i) lower_nonzero |= sample[i] != 0;
    for (uint32_t i = word; i < shape->limbs; ++i) {
        uint32_t mask = i == word ? ~low_mask : UINT32_MAX;
        if ((sample[i] & mask) != (negative ? mask : 0)) return false;
    }
    return !negative || lower_nonzero;
}

static bool bit_at(const uint32_t *words, uint32_t bit) {
    return ((words[bit / 32] >> (bit % 32)) & 1U) != 0;
}

static bool lower_nonzero(const uint32_t *words, uint32_t bits) {
    for (uint32_t i = 0; i < bits / 32; ++i) if (words[i]) return true;
    uint32_t rest = bits % 32;
    return rest && (words[bits / 32] & ((UINT32_C(1) << rest) - 1));
}

static double convert(const uint32_t *sample, uint32_t limbs) {
    bool negative = (sample[limbs - 1] >> 31) != 0;
    uint32_t absolute[MAX_LIMBS], carry = negative ? 1 : 0, high = 0;
    bool nonzero = false;
    for (uint32_t i = 0; i < limbs; ++i) {
        uint64_t value = (uint64_t)(negative ? ~sample[i] : sample[i]) + carry;
        absolute[i] = (uint32_t)value;
        carry = (uint32_t)(value >> 32);
        if (absolute[i]) { nonzero = true; high = i * 32; }
    }
    if (!nonzero) return 0.0;
    uint32_t head = absolute[high / 32];
    while (head >>= 1) ++high;
    uint32_t shift = high > 52 ? high - 52 : 0;
    uint64_t significand = 0;
    for (uint32_t i = 0; i < 53 && shift + i <= high; ++i)
        if (bit_at(absolute, shift + i)) significand |= UINT64_C(1) << i;
    if (high < 52) significand <<= 52 - high;
    else if (shift && bit_at(absolute, shift - 1) &&
             (lower_nonzero(absolute, shift - 1) || (significand & 1U))) {
        ++significand;
        if (significand == (UINT64_C(1) << 53)) { significand >>= 1; ++high; }
    }
    // 0<=high<=1151 after rounding: exponent is in[-512,639], all normal.
    uint64_t bits = ((uint64_t)negative << 63) |
        ((uint64_t)(high + 1023 - WORKING_SHIFT) << 52) |
        (significand & ((UINT64_C(1) << 52) - 1));
    double result;
    memcpy(&result, &bits, sizeof(result));
    return result;
}

native_vorbis_numeric_status_t native_vorbis_spectrum_to_binary64(
    const native_vorbis_floor1_product_t *source, size_t limb_capacity,
    double *output, size_t output_capacity,
    native_vorbis_transform_block_t *result) {
    if (!source || !result || !shape_valid(&source->layout)) return NATIVE_VORBIS_NUMERIC_INVALID;
    const native_vorbis_floor1_product_layout_t *shape = &source->layout;
    if (limb_capacity > SIZE_MAX / sizeof(uint32_t) ||
        output_capacity > SIZE_MAX / sizeof(*output) ||
        shape->limb_count > SIZE_MAX / sizeof(uint32_t)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (limb_capacity < shape->limb_count || output_capacity < shape->bins)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!output || (shape->limbs && !source->samples)) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (shape->limbs) {
        for (size_t bin = 0; bin < shape->bins; ++bin)
            if (!sample_valid(source->samples + bin * shape->limbs, shape))
                return NATIVE_VORBIS_NUMERIC_INVALID;
        for (size_t bin = 0; bin < shape->bins; ++bin)
            output[bin] = convert(source->samples + bin * shape->limbs, shape->limbs);
    } else {
        for (size_t bin = 0; bin < shape->bins; ++bin) output[bin] = 0.0;
    }
    *result = (native_vorbis_transform_block_t){.count = shape->bins,
        .exponent = shape->limbs ? (int64_t)shape->exponent + WORKING_SHIFT : 0,
        .samples = output};
    return NATIVE_VORBIS_NUMERIC_OK;
}
