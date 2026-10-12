#pragma once
// Combined numerical probes. Bits refer to disjoint logical data areas;
// physical SBR/PS overlay accounting is handled separately in the report.
enum {
    AAC_COMB_HIGH_QMF = 1u << 1,
    AAC_COMB_HYBRID_HISTORY = 1u << 2,
    AAC_COMB_SMOOTH_MANTISSA = 1u << 4,
    AAC_COMB_SMOOTH_EXPONENT = 1u << 5,
    AAC_COMB_PREVIOUS_MIX = 1u << 6,
    AAC_COMB_HYBRID_OUTPUT = 1u << 7,
    AAC_COMB_PS_ENERGY = 1u << 8,
    AAC_COMB_LOW_QMF = 1u << 9,
    AAC_COMB_PS_DELAYS = 1u << 10,
    AAC_COMB_ALL = AAC_COMB_HIGH_QMF | AAC_COMB_HYBRID_HISTORY |
        AAC_COMB_SMOOTH_MANTISSA | AAC_COMB_SMOOTH_EXPONENT |
        AAC_COMB_PREVIOUS_MIX | AAC_COMB_HYBRID_OUTPUT | AAC_COMB_PS_ENERGY |
        AAC_COMB_LOW_QMF | AAC_COMB_PS_DELAYS,
    AAC_COMB_BULK = AAC_COMB_HIGH_QMF | AAC_COMB_LOW_QMF |
        AAC_COMB_SMOOTH_MANTISSA | AAC_COMB_SMOOTH_EXPONENT | AAC_COMB_PS_DELAYS,
    AAC_COMB_EXACT_VARIANT = 8,
    AAC_COMB_VARIANTS = 14
};
static const unsigned aac_combined_masks[AAC_COMB_VARIANTS] = {
    0,
    AAC_COMB_ALL,
    AAC_COMB_BULK,
    AAC_COMB_LOW_QMF | AAC_COMB_PS_DELAYS,
    AAC_COMB_BULK & ~AAC_COMB_PS_DELAYS,
    AAC_COMB_HIGH_QMF | AAC_COMB_LOW_QMF | AAC_COMB_SMOOTH_EXPONENT,
    AAC_COMB_LOW_QMF,
    AAC_COMB_PS_DELAYS,
    AAC_COMB_ALL,
    AAC_COMB_ALL, // 9: low QMF16; other areas18
    AAC_COMB_ALL, // 10: low QMF16 + PS16; other areas18
    AAC_COMB_ALL, // 11: all lossy areas16
    AAC_COMB_BULK, // 12: bulk areas16
    AAC_COMB_ALL // 13: bulk16, small PS histories18
};

static inline unsigned aac_combined_area_format(unsigned variant, unsigned area) {
    return variant == 11 || variant == 12 ||
        (variant == 13 && (area == 1 || area == 4 || area == 9)) ||
        ((variant == 9 || variant == 10) && area == 9) ?
        PC_STORAGE_SHARED16 : PC_STORAGE_SHARED18_FOUR;
}
static inline unsigned aac_combined_ps_format(unsigned variant) {
    return variant >= 10 ? PC_STORAGE_SHARED16 : PC_STORAGE_SHARED18_FOUR;
}
