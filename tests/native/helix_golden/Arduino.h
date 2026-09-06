#pragma once

#include <algorithm>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifndef PROGMEM
#define PROGMEM
#endif
#define pgm_read_byte(address) (*(const uint8_t *)(address))
#define pgm_read_word(address) (*(const uint16_t *)(address))

#define log_e(...) do { } while (0)
#define log_w(...) do { } while (0)
#define log_i(...) do { } while (0)
#define log_d(...) do { } while (0)

#if defined(_MSC_VER)
#include <intrin.h>
#define __attribute__(value)
static inline int yoradio_host_clz(uint32_t value) {
    unsigned long index;
    return _BitScanReverse(&index, value) ? 31 - (int)index : 32;
}
#define __builtin_clz(value) yoradio_host_clz((uint32_t)(value))
#define __builtin_abs(value) abs(value)
#endif
