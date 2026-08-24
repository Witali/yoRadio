#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

#define NATIVE_AUDIO_DEFAULT_VOLUME 192U
#define NATIVE_AUDIO_DEFAULT_BALANCE 0
#define NATIVE_AUDIO_DEFAULT_NORMALIZATION false
#define NATIVE_AUDIO_DEFAULT_NORMALIZATION_GAIN_DB 20U
#define NATIVE_AUDIO_DEFAULT_NORMALIZATION_TARGET_DBFS -3
#define NATIVE_AUDIO_DEFAULT_NORMALIZATION_TIME_MS 2000U
#define NATIVE_AUDIO_VOLUME_SAVE_DELAY_MS 3000U

esp_err_t native_audio_settings_init(void);

uint8_t native_audio_settings_get_volume(void);
int8_t native_audio_settings_get_balance(void);
bool native_audio_settings_get_normalization(void);
uint8_t native_audio_settings_get_normalization_gain_db(void);
int8_t native_audio_settings_get_normalization_target_dbfs(void);
uint16_t native_audio_settings_get_normalization_time_ms(void);

esp_err_t native_audio_settings_set_volume(uint8_t volume);
esp_err_t native_audio_settings_set_balance(int8_t balance);
esp_err_t native_audio_settings_set_normalization(bool enabled);
esp_err_t native_audio_settings_set_normalization_gain_db(uint8_t gain_db);
esp_err_t native_audio_settings_set_normalization_target_dbfs(int8_t target_dbfs);
esp_err_t native_audio_settings_set_normalization_time_ms(uint16_t time_ms);

// Primarily used by orderly shutdowns and deterministic tests. Normal volume
// changes are committed automatically after the Arduino-compatible delay.
esp_err_t native_audio_settings_flush(void);
