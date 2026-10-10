#pragma once
// Experimental storage alternatives. DSP inputs/outputs retain their native scale.
#include "packed_complex16_fast.h"
#include <assert.h>

typedef enum {
    PC_STORAGE_SHARED16 = 1,
    PC_STORAGE_SPLIT16,
    PC_STORAGE_SHARED17_FIVE,
    PC_STORAGE_SHARED17_FOUR,
    PC_STORAGE_SHARED18_FOUR,
    PC_STORAGE_SHARED19_THREE
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
    PC17_MAX_SHIFT = PC_EXPONENT_MASK,
    PC18_COMPONENT_BITS = 18,
    PC18_HIGH_BITS = PC18_COMPONENT_BITS - PC_COMPONENT_LOW_BITS,
    PC18_HIGH_MASK = (1u << PC18_HIGH_BITS) - 1u,
    PC18_HIGH_SIGN = 1u << (PC18_HIGH_BITS - 1u),
    PC18_REAL_HIGH_BIT = PC_EXPONENT_BITS,
    PC18_IMAG_HIGH_BIT = PC_EXPONENT_BITS + PC18_HIGH_BITS,
    PC18_MANTISSA_MIN = -(1 << (PC18_COMPONENT_BITS - 1)),
    PC18_MANTISSA_MAX = (1 << (PC18_COMPONENT_BITS - 1)) - 1,
    PC18_MAX_SHIFT = PC_WORD_BITS - PC18_COMPONENT_BITS,
    PC19_COMPONENT_BITS = 19,
    PC19_HIGH_BITS = PC19_COMPONENT_BITS - PC_COMPONENT_LOW_BITS,
    PC19_HIGH_MASK = (1u << PC19_HIGH_BITS) - 1u,
    PC19_HIGH_SIGN = 1u << (PC19_HIGH_BITS - 1u),
    PC19_REAL_HIGH_BIT = PC_EXPONENT_BITS,
    PC19_IMAG_HIGH_BIT = PC_EXPONENT_BITS + PC19_HIGH_BITS,
    PC19_ENTRY_BITS = PC_EXPONENT_BITS + 2 * PC19_HIGH_BITS,
    PC19_MAIN_METADATA_BITS = 8,
    PC19_EXTRA_METADATA_BITS = PC19_ENTRY_BITS - PC19_MAIN_METADATA_BITS,
    PC19_EXTRA_METADATA_MASK = (1u << PC19_EXTRA_METADATA_BITS) - 1u,
    PC19_EXTRA_METADATA_PER_WORD = PC_WORD_BITS / PC19_EXTRA_METADATA_BITS,
    PC19_MANTISSA_MIN = -(1 << (PC19_COMPONENT_BITS - 1)),
    PC19_MANTISSA_MAX = (1 << (PC19_COMPONENT_BITS - 1)) - 1,
    PC19_MAX_SHIFT = PC_WORD_BITS - PC19_COMPONENT_BITS
};

// One byte: [Im high 2][Re high 2][shared shift 4]. The low halves stay in
// an aligned 32-bit mantissa word. Shift 15 is reserved; signed int32 needs 0..14.
static inline uint32_t pc18_pack(int32_t real, int32_t imag,
                                unsigned *metadata, unsigned *saturations) {
    uint32_t width = (real < 0 ? ~(uint32_t)real : (uint32_t)real) |
                     (imag < 0 ? ~(uint32_t)imag : (uint32_t)imag);
    unsigned shift = width < (1u << PC18_COMPONENT_BITS) ? 0 :
                     PC18_MAX_SHIFT - (unsigned)__builtin_clz(width);
    int32_t r = shift ? pc16_round(real, shift) : real;
    int32_t i = shift ? pc16_round(imag, shift) : imag;
    while (shift < PC18_MAX_SHIFT &&
           (r > PC18_MANTISSA_MAX || i > PC18_MANTISSA_MAX ||
            r < PC18_MANTISSA_MIN || i < PC18_MANTISSA_MIN)) {
        ++shift; r = pc16_round(real, shift); i = pc16_round(imag, shift);
    }
    *saturations = (r > PC18_MANTISSA_MAX) + (i > PC18_MANTISSA_MAX);
    if (r > PC18_MANTISSA_MAX) r = PC18_MANTISSA_MAX;
    if (i > PC18_MANTISSA_MAX) i = PC18_MANTISSA_MAX;
    *metadata = shift |
        (((uint32_t)r >> PC_COMPONENT_LOW_BITS & PC18_HIGH_MASK) << PC18_REAL_HIGH_BIT) |
        (((uint32_t)i >> PC_COMPONENT_LOW_BITS & PC18_HIGH_MASK) << PC18_IMAG_HIGH_BIT);
    return ((uint32_t)r & PC_COMPONENT_LOW_MASK) | ((uint32_t)i << PC_COMPONENT_LOW_BITS);
}
static inline void pc18_unpack(uint32_t word, unsigned metadata, int32_t *real, int32_t *imag) {
    unsigned shift = metadata & PC_EXPONENT_MASK;
    assert(shift <= PC18_MAX_SHIFT);
    unsigned r_high = (metadata >> PC18_REAL_HIGH_BIT) & PC18_HIGH_MASK;
    unsigned i_high = (metadata >> PC18_IMAG_HIGH_BIT) & PC18_HIGH_MASK;
    // Sign-extend the two high bits without implementation-defined signed shifts.
    int32_t r = (int32_t)(word & PC_COMPONENT_LOW_MASK) +
                ((int32_t)(r_high ^ PC18_HIGH_SIGN) - PC18_HIGH_SIGN) * (1 << PC_COMPONENT_LOW_BITS);
    int32_t i = (int32_t)(word >> PC_COMPONENT_LOW_BITS) +
                ((int32_t)(i_high ^ PC18_HIGH_SIGN) - PC18_HIGH_SIGN) * (1 << PC_COMPONENT_LOW_BITS);
    *real = r * (int32_t)(1u << shift); *imag = i * (int32_t)(1u << shift);
}

// Ten metadata bits: [Im high 3][Re high 3][shared shift 4]. Three complex
// values share an aligned metadata word; the top two bits are unused.
// Keep the established 18-bit arithmetic above untouched for A/B controls.
static inline uint32_t pc19_pack(int32_t real, int32_t imag,
                                unsigned *metadata, unsigned *saturations) {
    uint32_t width = (real < 0 ? ~(uint32_t)real : (uint32_t)real) |
                     (imag < 0 ? ~(uint32_t)imag : (uint32_t)imag);
    unsigned shift = width < (1u << PC19_COMPONENT_BITS) ? 0 :
                     PC19_MAX_SHIFT - (unsigned)__builtin_clz(width);
    int32_t r = shift ? pc16_round(real, shift) : real;
    int32_t i = shift ? pc16_round(imag, shift) : imag;
    while (shift < PC19_MAX_SHIFT &&
           (r > PC19_MANTISSA_MAX || i > PC19_MANTISSA_MAX ||
            r < PC19_MANTISSA_MIN || i < PC19_MANTISSA_MIN)) {
        ++shift; r = pc16_round(real, shift); i = pc16_round(imag, shift);
    }
    *saturations = (r > PC19_MANTISSA_MAX) + (i > PC19_MANTISSA_MAX);
    if (r > PC19_MANTISSA_MAX) r = PC19_MANTISSA_MAX;
    if (i > PC19_MANTISSA_MAX) i = PC19_MANTISSA_MAX;
    *metadata = shift |
        (((uint32_t)r >> PC_COMPONENT_LOW_BITS & PC19_HIGH_MASK) << PC19_REAL_HIGH_BIT) |
        (((uint32_t)i >> PC_COMPONENT_LOW_BITS & PC19_HIGH_MASK) << PC19_IMAG_HIGH_BIT);
    return ((uint32_t)r & PC_COMPONENT_LOW_MASK) | ((uint32_t)i << PC_COMPONENT_LOW_BITS);
}
static inline void pc19_unpack(uint32_t word, unsigned metadata, int32_t *real, int32_t *imag) {
    unsigned shift = metadata & PC_EXPONENT_MASK;
    assert(shift <= PC19_MAX_SHIFT);
    unsigned r_high = (metadata >> PC19_REAL_HIGH_BIT) & PC19_HIGH_MASK;
    unsigned i_high = (metadata >> PC19_IMAG_HIGH_BIT) & PC19_HIGH_MASK;
    int32_t r = (int32_t)(word & PC_COMPONENT_LOW_MASK) +
                ((int32_t)(r_high ^ PC19_HIGH_SIGN) - PC19_HIGH_SIGN) * (1 << PC_COMPONENT_LOW_BITS);
    int32_t i = (int32_t)(word >> PC_COMPONENT_LOW_BITS) +
                ((int32_t)(i_high ^ PC19_HIGH_SIGN) - PC19_HIGH_SIGN) * (1 << PC_COMPONENT_LOW_BITS);
    *real = r * (int32_t)(1u << shift); *imag = i * (int32_t)(1u << shift);
}
static inline unsigned pc_storage_entry_bits(pc_storage_format_t format) {
    if (format == PC_STORAGE_SHARED19_THREE) return PC19_ENTRY_BITS;
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
    if (format == PC_STORAGE_SHARED18_FOUR) return pc18_pack(real, imag, metadata, saturations);
    if (format == PC_STORAGE_SHARED19_THREE) return pc19_pack(real, imag, metadata, saturations);
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
    if (format == PC_STORAGE_SHARED18_FOUR) { pc18_unpack(word, metadata, real, imag); return; }
    if (format == PC_STORAGE_SHARED19_THREE) { pc19_unpack(word, metadata, real, imag); return; }
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

// Equivalent PC19 metadata split over the existing byte-per-pair array and
// two extra bits per pair. Keeps a near-32-KiB owner in its allocator bucket.
static inline unsigned pc19_split_metadata_load(const uint32_t *main_words,
                                               const uint32_t *extra_words,size_t index) {
    unsigned low=pc_storage_load_metadata(PC_STORAGE_SHARED18_FOUR,main_words,index);
    unsigned bit=(index%PC19_EXTRA_METADATA_PER_WORD)*PC19_EXTRA_METADATA_BITS;
    unsigned high=(extra_words[index/PC19_EXTRA_METADATA_PER_WORD]>>bit)&PC19_EXTRA_METADATA_MASK;
    return low|(high<<PC19_MAIN_METADATA_BITS);
}
static inline void pc19_split_metadata_store(uint32_t *main_words,uint32_t *extra_words,
                                            size_t index,unsigned metadata) {
    pc_storage_store_metadata(PC_STORAGE_SHARED18_FOUR,main_words,index,metadata);
    unsigned bit=(index%PC19_EXTRA_METADATA_PER_WORD)*PC19_EXTRA_METADATA_BITS;
    uint32_t *word=extra_words+index/PC19_EXTRA_METADATA_PER_WORD;
    *word=(*word&~((uint32_t)PC19_EXTRA_METADATA_MASK<<bit))|
          (((metadata>>PC19_MAIN_METADATA_BITS)&PC19_EXTRA_METADATA_MASK)<<bit);
}
