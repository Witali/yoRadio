#pragma once

// Minimal Arduino compatibility surface required by yoRadio's legacy codec
// sources. The native firmware does not link Arduino Core.
#include <algorithm>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "esp_heap_caps.h"
#include "esp_log.h"

using byte = uint8_t;
using boolean = bool;

#ifndef PROGMEM
#define PROGMEM
#endif
#ifndef pgm_read_byte
#define pgm_read_byte(address) (*(const uint8_t *)(address))
#endif
#ifndef pgm_read_word
#define pgm_read_word(address) (*(const uint16_t *)(address))
#endif
#ifndef pgm_read_dword
#define pgm_read_dword(address) (*(const uint32_t *)(address))
#endif

static inline bool psramFound(void) { return false; }
static inline void *ps_malloc(size_t size) {
    return heap_caps_malloc(size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
}

class NativeEspHeapInfo {
public:
    uint32_t getFreeHeap() const {
        return (uint32_t)heap_caps_get_free_size(MALLOC_CAP_8BIT);
    }
    uint32_t getMaxAllocHeap() const {
        return (uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    }
};

static const NativeEspHeapInfo ESP = {};

#define log_e(...) ESP_LOGE("custom_codec", __VA_ARGS__)
#define log_w(...) ESP_LOGW("custom_codec", __VA_ARGS__)
#define log_i(...) ESP_LOGI("custom_codec", __VA_ARGS__)
#define log_d(...) ESP_LOGD("custom_codec", __VA_ARGS__)
#define log_v(...) ESP_LOGV("custom_codec", __VA_ARGS__)
