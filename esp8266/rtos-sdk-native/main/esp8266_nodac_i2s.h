#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"
#include "freertos/FreeRTOS.h"

/* Exactly two 2048-byte descriptors implement true ping-pong DMA while
 * keeping the static output ring at 4 KiB. */
#define ESP8266_NODAC_DMA_BUFFER_COUNT 2U
#define ESP8266_NODAC_DMA_BUFFER_WORDS 512U

esp_err_t esp8266_nodac_i2s_init(uint32_t silence_word,
                                 uint8_t bck_div, uint8_t clkm_div);
esp_err_t esp8266_nodac_i2s_write(const uint32_t *words, size_t word_count,
                                  TickType_t ticks_to_wait);
void esp8266_nodac_i2s_silence(uint32_t silence_word);
void esp8266_nodac_i2s_reset_underruns(void);
uint32_t esp8266_nodac_i2s_underruns(void);
