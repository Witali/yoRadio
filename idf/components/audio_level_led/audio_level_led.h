#pragma once

#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

esp_err_t audio_level_led_init(void);
void audio_level_led_update_peak(uint16_t peak);
void audio_level_led_update_pcm(const uint8_t *data, size_t size,
                                uint8_t bits_per_sample, uint8_t channels);

#ifdef __cplusplus
}
#endif
