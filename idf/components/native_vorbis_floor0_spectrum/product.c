// Exact signed residue magnitude times a positive binary64 significand.
#include "product.h"
#include <float.h>
#include <string.h>

_Static_assert(sizeof(double) == sizeof(uint64_t) && DBL_MANT_DIG == 53 &&
    DBL_MAX_EXP == 1024 && FLT_RADIX == 2, "binary64 storage required");

bool native_floor0_source_valid(const native_vorbis_residue_layout_t *source) {
    if (!source || !source->bins || source->bins > 4096 || !source->channels ||
        source->channels > 255 ||
        source->sample_count != (uint64_t)source->bins * source->channels ||
        source->limb_count != source->sample_count * source->limbs) return false;
    if (!source->limbs) return !source->magnitude_bits && !source->exponent;
    return source->limbs <= NATIVE_FLOOR0_SOURCE_LIMBS && source->magnitude_bits &&
        source->magnitude_bits <= NATIVE_FLOOR0_SOURCE_LIMBS * 32 - 1 &&
        source->limbs == (source->magnitude_bits + 32) / 32;
}

bool native_floor0_sample_valid(const uint32_t *sample,
    const native_vorbis_residue_layout_t *source) {
    if (!native_floor0_source_valid(source)) return false;
    if (!source->limbs) return true;
    if (!sample) return false;
    uint32_t word = source->magnitude_bits / 32, bit = source->magnitude_bits % 32;
    uint32_t low_mask = bit ? (UINT32_C(1) << bit) - 1 : 0;
    bool negative = (sample[source->limbs - 1] >> 31) != 0;
    bool lower_nonzero = (sample[word] & low_mask) != 0;
    for (uint32_t i = 0; i < word; ++i) lower_nonzero |= sample[i] != 0;
    for (uint32_t i = word; i < source->limbs; ++i) {
        uint32_t mask = i == word ? ~low_mask : UINT32_MAX;
        if ((sample[i] & mask) != (negative ? mask : 0)) return false;
    }
    // -2^M is excluded, just like +2^M; the strict domain is abs(S)<2^M.
    return !negative || lower_nonzero;
}

bool native_floor0_sample_zero(const uint32_t *sample, uint32_t limbs) {
    if (limbs && !sample) return false;
    for (uint32_t i = 0; i < limbs; ++i) if (sample[i]) return false;
    return true;
}

int32_t native_floor0_product(const uint32_t *sample, uint32_t limbs,
    uint64_t factor, uint32_t magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS], bool *negative) {
    bool sign = (sample[limbs - 1] >> 31) != 0;
    uint32_t absolute[NATIVE_FLOOR0_PRODUCT_LIMBS] = {0};
    uint64_t carry = sign ? 1 : 0;
    for (uint32_t i = 0; i < limbs; ++i) {
        uint64_t value = (uint64_t)(sign ? ~sample[i] : sample[i]) + carry;
        absolute[i] = (uint32_t)value; carry = value >> 32;
    }
    uint32_t low = (uint32_t)factor, high = (uint32_t)(factor >> 32);
    carry = 0;
    // A 32x32 product plus its carry is <=2^64-2^32, without overflow.
    for (uint32_t i = 0; i < NATIVE_FLOOR0_PRODUCT_LIMBS; ++i) {
        uint64_t value = (uint64_t)absolute[i] * low + carry;
        magnitude[i] = (uint32_t)value; carry = value >> 32;
    }
    carry = 0;
    // The second factor half is at most21 bits. Including existing word and
    // carry gives less than2^54; all arithmetic fits uint64. Source magnitude
    // <2^1087 times factor<2^53 fits1140 bits, hence all36 words retain it.
    for (uint32_t i = 1; i < NATIVE_FLOOR0_PRODUCT_LIMBS; ++i) {
        uint64_t value = (uint64_t)absolute[i - 1] * high + magnitude[i] + carry;
        magnitude[i] = (uint32_t)value; carry = value >> 32;
    }
    *negative = sign;
    for (uint32_t i = NATIVE_FLOOR0_PRODUCT_LIMBS; i; --i) {
        uint32_t head = magnitude[i - 1];
        if (head) {
            int32_t top = (int32_t)((i - 1) * 32);
            while (head >>= 1) ++top;
            return top;
        }
    }
    return -1;
}

static bool bit_at(const uint32_t *words, uint32_t bit) {
    return ((words[bit / 32] >> (bit % 32)) & 1U) != 0;
}

static bool lower_nonzero(const uint32_t *words, uint32_t bits) {
    for (uint32_t i = 0; i < bits / 32; ++i) if (words[i]) return true;
    uint32_t rest = bits % 32;
    return rest && (words[bits / 32] & ((UINT32_C(1) << rest) - 1));
}

double native_floor0_round(const uint32_t magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS],
    uint32_t highest_bit, int32_t working_top, bool negative) {
    uint32_t shift = highest_bit > 52 ? highest_bit - 52 : 0;
    uint64_t significand = 0;
    for (uint32_t i = 0; i < 53 && shift + i <= highest_bit; ++i)
        if (bit_at(magnitude, shift + i)) significand |= UINT64_C(1) << i;
    if (highest_bit < 52) significand <<= 52 - highest_bit;
    else if (shift && bit_at(magnitude, shift - 1) &&
        (lower_nonzero(magnitude, shift - 1) || (significand & 1U))) {
        ++significand;
        if (significand == (UINT64_C(1) << 53)) { significand >>= 1; ++working_top; }
    }
    uint64_t bits = ((uint64_t)negative << 63) |
        ((uint64_t)(working_top + 1023) << 52) |
        (significand & ((UINT64_C(1) << 52) - 1));
    double result; memcpy(&result, &bits, sizeof(result)); return result;
}
