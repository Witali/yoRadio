#pragma once

/* Minimal compatibility surface required by the original yoRadio Helix
 * sources. This is not Arduino and does not pull Arduino core code. */
#include <algorithm>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "esp_log.h"

#ifndef PROGMEM
#define PROGMEM __attribute__((section(".rodata")))
#endif
#define pgm_read_byte(address) (*(const uint8_t *)(address))
#define pgm_read_word(address) (*(const uint16_t *)(address))
#define log_e(format, ...) ESP_LOGE("helix", format, ##__VA_ARGS__)
#define log_w(format, ...) ESP_LOGW("helix", format, ##__VA_ARGS__)
#define log_i(format, ...) ESP_LOGI("helix", format, ##__VA_ARGS__)
#define log_d(format, ...) do { } while (0)
