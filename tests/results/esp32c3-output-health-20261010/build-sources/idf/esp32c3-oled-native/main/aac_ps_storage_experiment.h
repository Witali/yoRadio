#pragma once
#include "aac_sbr_abi.h"
#include "packed_complex_storage.h"
enum { AAC_PS_STORAGE_MIN_ENTRIES = PC_WORD_BITS / (2 * PC_EXPONENT_BITS) };
typedef struct AAC_ABI_VIEW {
    uint8_t prefix[offsetof(aac_sbr_packed_ps_overlay_abi_t, mantissas)];
    uint32_t mantissas[AAC_PS_PACKED_PAIRS];
    uint32_t exponents[(AAC_PS_PACKED_PAIRS + AAC_PS_STORAGE_MIN_ENTRIES - 1) / AAC_PS_STORAGE_MIN_ENTRIES];
} aac_ps_storage_experiment_t;
_Static_assert(offsetof(aac_ps_storage_experiment_t,exponents)==
               offsetof(aac_sbr_packed_ps_overlay_abi_t,exponents), "Same mantissa pool");
_Static_assert(sizeof(aac_ps_storage_experiment_t)<offsetof(aac_sbr_ps_overlay_abi_t,relocated_ps),
               "Expanded metadata must precede relocated PS state");
void aac_ps_storage_select(pc_storage_format_t format);
