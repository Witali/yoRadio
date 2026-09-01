#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"
#include "freertos/FreeRTOS.h"

esp_err_t esp8266_nodac_i2s_init(uint32_t silence_word);
esp_err_t esp8266_nodac_i2s_write(const uint32_t *words, size_t word_count,
                                  TickType_t ticks_to_wait);
void esp8266_nodac_i2s_silence(uint32_t silence_word);

