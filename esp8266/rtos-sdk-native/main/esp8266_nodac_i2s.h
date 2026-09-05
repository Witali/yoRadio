#pragma once

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"
#include "freertos/FreeRTOS.h"

/* Two 2048-byte buffers implement producer/DMA ping-pong at 4 KiB.
 * Only complete buffers are submitted; no unguarded circular DMA link. */
#define ESP8266_NODAC_DMA_BUFFER_COUNT 2U
#define ESP8266_NODAC_DMA_BUFFER_WORDS 512U

esp_err_t esp8266_nodac_i2s_init(uint32_t silence_word,
                                 uint8_t bck_div, uint8_t clkm_div);
esp_err_t esp8266_nodac_i2s_write(const uint32_t *words, size_t word_count,
                                  TickType_t ticks_to_wait);
/* Single-producer API: call silence between writes, never concurrently.
 * Mute is applied at the next EOF, without modifying active DMA memory. */
void esp8266_nodac_i2s_silence(uint32_t silence_word);
void esp8266_nodac_i2s_reset_underruns(void);
uint32_t esp8266_nodac_i2s_underruns(void);

#if YORADIO_ESP8266_AUDIO_PROFILE || YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
typedef struct {
    uint32_t eof_count;
    uint32_t empty_starts;
    uint32_t blocked_partial;
    uint32_t missing_words;
    uint32_t fifo_empty;
} esp8266_nodac_profile_t;
void esp8266_nodac_i2s_profile(esp8266_nodac_profile_t *stats);
#endif

#if YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK
bool esp8266_nodac_i2s_test_stalled_producer(void);
#endif
