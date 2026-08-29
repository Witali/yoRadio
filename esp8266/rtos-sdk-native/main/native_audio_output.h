#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

esp_err_t native_audio_output_init(void);
esp_err_t native_audio_output_write(int16_t *samples, size_t sample_count,
                                    uint32_t sample_rate, uint8_t channels);
void native_audio_output_silence(void);
