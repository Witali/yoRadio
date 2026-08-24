#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

#define RUNTIME_DEFAULT_AUDIO_INFO false
#define RUNTIME_DEFAULT_SOFTAP_DELAY_MIN 0U
// Arduino's abuff unit is one 1600-byte block. Ten blocks are 16 kB.
#define RUNTIME_DEFAULT_AUDIO_BUFFER_BLOCKS 10U
#define RUNTIME_DEFAULT_MDNS_NAME "yoradio"
#define RUNTIME_DEFAULT_WATCHDOG true
#define RUNTIME_DEFAULT_TZ_HOUR 0
#define RUNTIME_DEFAULT_TZ_MINUTE 0U
#define RUNTIME_DEFAULT_SNTP1 "pool.ntp.org"
#define RUNTIME_DEFAULT_SNTP2 "time.nist.gov"
#define RUNTIME_DEFAULT_TIME_SYNC_INTERVAL_MIN 60U
#define RUNTIME_DEFAULT_VOLUME_STEPS 1U

esp_err_t runtime_settings_init(void);

bool runtime_settings_get_audio_info(void);
uint8_t runtime_settings_get_softap_delay_min(void);
uint8_t runtime_settings_get_audio_buffer_blocks(void);
void runtime_settings_get_mdns_name(char *output, size_t output_size);
bool runtime_settings_get_watchdog(void);
int8_t runtime_settings_get_timezone_hour(void);
uint8_t runtime_settings_get_timezone_minute(void);
void runtime_settings_get_sntp1(char *output, size_t output_size);
void runtime_settings_get_sntp2(char *output, size_t output_size);
uint16_t runtime_settings_get_time_sync_interval_min(void);
uint8_t runtime_settings_get_volume_steps(void);

esp_err_t runtime_settings_set_audio_info(bool enabled);
esp_err_t runtime_settings_set_softap_delay_min(uint8_t minutes);
esp_err_t runtime_settings_set_audio_buffer_blocks(uint8_t blocks);
esp_err_t runtime_settings_set_mdns_name(const char *name);
esp_err_t runtime_settings_set_watchdog(bool enabled);
esp_err_t runtime_settings_set_timezone_hour(int8_t hour);
esp_err_t runtime_settings_set_timezone_minute(uint8_t minute);
esp_err_t runtime_settings_set_sntp1(const char *server);
esp_err_t runtime_settings_set_sntp2(const char *server);
esp_err_t runtime_settings_set_time_sync_interval_min(uint16_t minutes);
esp_err_t runtime_settings_set_volume_steps(uint8_t steps);
