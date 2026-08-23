#pragma once

#include <stdint.h>

#include "esp_err.h"

#define NATIVE_AUDIO_DEFAULT_VOLUME 192U
#define NATIVE_AUDIO_DEFAULT_BALANCE 0
#define NATIVE_AUDIO_VOLUME_SAVE_DELAY_MS 3000U

esp_err_t native_audio_settings_init(void);

uint8_t native_audio_settings_get_volume(void);
int8_t native_audio_settings_get_balance(void);

esp_err_t native_audio_settings_set_volume(uint8_t volume);
esp_err_t native_audio_settings_set_balance(int8_t balance);

// Primarily used by orderly shutdowns and deterministic tests. Normal volume
// changes are committed automatically after the Arduino-compatible delay.
esp_err_t native_audio_settings_flush(void);
