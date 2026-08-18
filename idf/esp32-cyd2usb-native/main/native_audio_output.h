#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

esp_err_t native_audio_output_init(void);
esp_err_t native_audio_output_configure(uint32_t input_sample_rate);
esp_err_t native_audio_output_write_pcm(const uint8_t *data, size_t size,
                                        uint8_t bits_per_sample,
                                        uint8_t channels);
void native_audio_output_idle(void);
const char *native_audio_output_name(void);
