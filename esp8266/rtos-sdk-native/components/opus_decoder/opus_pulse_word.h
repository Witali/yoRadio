#pragma once
#ifndef YORADIO_OPUS_PULSE_FLASH_WORD
#define YORADIO_OPUS_PULSE_FLASH_WORD 0
#endif
#if YORADIO_OPUS_PULSE_FLASH_WORD != 0 && YORADIO_OPUS_PULSE_FLASH_WORD != 1
#error "YORADIO_OPUS_PULSE_FLASH_WORD must be 0 or 1"
#endif
/* Only the fixed-point static 48 kHz mode's padded/aligned cache tables.
 * Custom-mode tables may be dynamically allocated and are never widened. */
#if YORADIO_OPUS_PULSE_FLASH_WORD && defined(YORADIO_OPUS_BOUNDED) && defined(FIXED_POINT) && !defined(CUSTOM_MODES)
#define YORADIO_OPUS_PULSE_WORD_ENABLED 1
#include "opus_memory.h"
#if defined(YORADIO_OPUS_PULSE_TEST_HOOKS)
void yoradio_opus_pulse_test_word(const void *p);
#endif
static inline uint32_t yoradio_opus_pulse_word(const void *p) {
#if defined(YORADIO_OPUS_PULSE_TEST_HOOKS)
    yoradio_opus_pulse_test_word(p);
#endif
    return yoradio_opus_table_load_pair(p).word;
}
static inline unsigned char yoradio_opus_pulse_read8(const unsigned char *p) {
    uintptr_t address = (uintptr_t)p;
    const uint32_t value = yoradio_opus_pulse_word((const void *)(address & ~(uintptr_t)3U));
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    return (unsigned char)(value >> ((3U - (address & 3U)) * 8U));
#else
    return (unsigned char)(value >> ((address & 3U) * 8U));
#endif
}
static inline int16_t yoradio_opus_pulse_read16(const int16_t *p) {
    uintptr_t address = (uintptr_t)p;
    yoradio_opus_table_pair pair;
    pair.word = yoradio_opus_pulse_word((const void *)(address & ~(uintptr_t)3U));
    return address & 2U ? pair.half[1] : pair.half[0];
}
#else
#define YORADIO_OPUS_PULSE_WORD_ENABLED 0
#define yoradio_opus_pulse_read8(p) (*(p))
#define yoradio_opus_pulse_read16(p) (*(p))
#endif
