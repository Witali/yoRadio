#pragma once
// Experimental storage alternatives. DSP inputs/outputs retain their native scale.
#include "packed_complex16_fast.h"

typedef enum {
    PC_STORAGE_SHARED16 = 1,
    PC_STORAGE_SPLIT16,
    PC_STORAGE_SHARED17_FIVE,
    PC_STORAGE_SHARED17_FOUR
} pc_storage_format_t;

enum {
    PC_WORD_BITS = 32,
    PC_COMPONENT_LOW_BITS = 16,
    PC_COMPONENT_LOW_MASK = 0xffff,
    PC_EXPONENT_BITS = 4,
    PC_EXPONENT_MASK = 15,
    PC17_REAL_HIGH_BIT = PC_EXPONENT_BITS,
    PC17_IMAG_HIGH_BIT = PC_EXPONENT_BITS + 1,
    PC17_COMPONENT_SIGN = 1 << PC_COMPONENT_LOW_BITS,
    PC17_MANTISSA_MAX = PC17_COMPONENT_SIGN - 1,
    PC17_MANTISSA_MIN = -PC17_COMPONENT_SIGN,
    PC17_MAX_SHIFT = PC_EXPONENT_MASK
};
static inline unsigned pc_storage_entry_bits(pc_storage_format_t format) {
    return format == PC_STORAGE_SHARED16 ? PC_EXPONENT_BITS :
           format == PC_STORAGE_SHARED17_FIVE ? PC_EXPONENT_BITS + 2 : 2 * PC_EXPONENT_BITS;
}
static inline unsigned pc_storage_entries(pc_storage_format_t format) {
    return PC_WORD_BITS / pc_storage_entry_bits(format);
}
static inline size_t pc_storage_metadata_words(pc_storage_format_t format, size_t count) {
    unsigned entries = pc_storage_entries(format);
    return count / entries + (count % entries != 0);
}
static inline size_t pc_storage_bytes(pc_storage_format_t format, size_t count) {
    return sizeof(uint32_t) * (count + pc_storage_metadata_words(format, count));
}
static inline uint32_t pc_storage_pack(pc_storage_format_t format, int32_t real, int32_t imag,
                                     unsigned *metadata, unsigned *saturations) {
    if (format == PC_STORAGE_SHARED16) return pc16_pack_fast(real, imag, metadata, saturations);
    if (format == PC_STORAGE_SPLIT16) {
        unsigned real_exp, imag_exp, real_clip, imag_clip;
        uint32_t r = pc16_pack_fast(real, 0, &real_exp, &real_clip);
        uint32_t i = pc16_pack_fast(imag, 0, &imag_exp, &imag_clip);
        *metadata = real_exp | (imag_exp << PC_EXPONENT_BITS);
        *saturations = real_clip + imag_clip;
        return (r & PC_COMPONENT_LOW_MASK) | (i << PC_COMPONENT_LOW_BITS);
    }
    uint32_t width = (real < 0 ? ~(uint32_t)real : (uint32_t)real) |
                     (imag < 0 ? ~(uint32_t)imag : (uint32_t)imag);
    // Start below the truncation estimate: negative rounding can still fit
    // the previous exponent at an asymmetric signed-mantissa boundary.
    unsigned shift = width < (1u << (PC_COMPONENT_LOW_BITS + 1)) ? 0 :
                     PC17_MAX_SHIFT - (unsigned)__builtin_clz(width);
    int32_t r = shift ? pc16_round(real, shift) : real;
    int32_t i = shift ? pc16_round(imag, shift) : imag;
    while (shift < PC17_MAX_SHIFT &&
           (r > PC17_MANTISSA_MAX || i > PC17_MANTISSA_MAX ||
            r < PC17_MANTISSA_MIN || i < PC17_MANTISSA_MIN)) {
        ++shift; r = pc16_round(real, shift); i = pc16_round(imag, shift);
    }
    *saturations = (r > PC17_MANTISSA_MAX) + (i > PC17_MANTISSA_MAX);
    if (r > PC17_MANTISSA_MAX) r = PC17_MANTISSA_MAX;
    if (i > PC17_MANTISSA_MAX) i = PC17_MANTISSA_MAX;
    *metadata = shift | (((uint32_t)r >> PC_COMPONENT_LOW_BITS & 1u) << PC17_REAL_HIGH_BIT) |
                (((uint32_t)i >> PC_COMPONENT_LOW_BITS & 1u) << PC17_IMAG_HIGH_BIT);
    return ((uint32_t)r & PC_COMPONENT_LOW_MASK) | ((uint32_t)i << PC_COMPONENT_LOW_BITS);
}
static inline void pc_storage_unpack(pc_storage_format_t format, uint32_t word, unsigned metadata,
                                     int32_t *real, int32_t *imag) {
    if (format == PC_STORAGE_SHARED16) { pc16_unpack(word, metadata, real, imag); return; }
    if (format == PC_STORAGE_SPLIT16) {
        *real = pc16_expand(word, (metadata & PC_EXPONENT_MASK) + 1u);
        *imag = pc16_expand(word >> PC_COMPONENT_LOW_BITS,
                            ((metadata >> PC_EXPONENT_BITS) & PC_EXPONENT_MASK) + 1u);
        return;
    }
    int32_t r = (int32_t)(word & PC_COMPONENT_LOW_MASK) -
                (int32_t)((metadata >> PC17_REAL_HIGH_BIT) & 1u) * PC17_COMPONENT_SIGN;
    int32_t i = (int32_t)(word >> PC_COMPONENT_LOW_BITS) -
                (int32_t)((metadata >> PC17_IMAG_HIGH_BIT) & 1u) * PC17_COMPONENT_SIGN;
    int32_t scale = (int32_t)(1u << (metadata & PC_EXPONENT_MASK));
    *real = r * scale; *imag = i * scale;
}
static inline void pc_storage_store_metadata(pc_storage_format_t format, uint32_t *words,
                                             size_t index, unsigned metadata) {
    unsigned entry_bits = pc_storage_entry_bits(format), entries = pc_storage_entries(format);
    unsigned bit = (index % entries) * entry_bits;
    uint32_t mask = (1u << entry_bits) - 1u;
    words[index / entries] = (words[index / entries] & ~(mask << bit)) | ((metadata & mask) << bit);
}
static inline unsigned pc_storage_load_metadata(pc_storage_format_t format, const uint32_t *words,
                                                size_t index) {
    unsigned entry_bits = pc_storage_entry_bits(format), entries = pc_storage_entries(format);
    return (words[index / entries] >> ((index % entries) * entry_bits)) & ((1u << entry_bits) - 1u);
}
static inline unsigned pc_storage_max_shift(pc_storage_format_t format, unsigned metadata) {
    unsigned r = metadata & PC_EXPONENT_MASK;
    if (format == PC_STORAGE_SPLIT16) {
        unsigned i = (metadata >> PC_EXPONENT_BITS) & PC_EXPONENT_MASK;
        return (r > i ? r : i) + 1u;
    }
    return r + (format == PC_STORAGE_SHARED16);
}
