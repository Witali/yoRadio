// Internal bounded integer primitives; public callers use successful plans.
#pragma once
#include "native_vorbis_floor0_spectrum.h"
enum { NATIVE_FLOOR0_SOURCE_LIMBS = 34, NATIVE_FLOOR0_PRODUCT_LIMBS = 36 };

bool native_floor0_source_valid(const native_vorbis_residue_layout_t *source);
bool native_floor0_sample_valid(const uint32_t *sample,
    const native_vorbis_residue_layout_t *source);
bool native_floor0_sample_zero(const uint32_t *sample, uint32_t limbs);

// A valid strict signed source domain, 1..34 words, and a nonnegative <=53-bit
// factor produce an exact unsigned magnitude in36 words. Return highest bit,
// or-1 forzero, and original source sign. All36 output words are initialized.
int32_t native_floor0_product(const uint32_t *sample, uint32_t limbs,
    uint64_t factor, uint32_t magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS], bool *negative);

// Round a NONZERO exact unsigned magnitude once, ties-even, with its highest
// bit supplied and target top in[-1022,638]. Inputs stay immutable. All outputs
// are normal binary64 and <=2^639, including a rounding carry. Zero is handled
// separately by materialize. No physical exponent or huge floating cast here.
double native_floor0_round(const uint32_t magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS],
    uint32_t highest_bit, int32_t working_top, bool negative);
