#pragma once
#ifndef YORADIO_OPUS_FIR_FLASH_WORD
#define YORADIO_OPUS_FIR_FLASH_WORD 0
#endif
#if YORADIO_OPUS_FIR_FLASH_WORD != 0 && YORADIO_OPUS_FIR_FLASH_WORD != 1
#error "YORADIO_OPUS_FIR_FLASH_WORD must be 0 or 1"
#endif
#if YORADIO_OPUS_FIR_FLASH_WORD
#include "opus_memory.h"
#if defined(YORADIO_OPUS_FIR_TEST_HOOKS)
void yoradio_opus_fir_test_pair(const void *p);
#endif
/* Only the explicitly word-aligned, 96-byte static FIR table. Each row is
 * eight bytes and both pairs stay within it. Never use on PCM or MMIO. */
static inline yoradio_opus_table_pair yoradio_opus_fir_pair(const int16_t *p) {
#if defined(YORADIO_OPUS_FIR_TEST_HOOKS)
    yoradio_opus_fir_test_pair(p);
#endif
    return yoradio_opus_table_load_pair(p);
}
#endif
