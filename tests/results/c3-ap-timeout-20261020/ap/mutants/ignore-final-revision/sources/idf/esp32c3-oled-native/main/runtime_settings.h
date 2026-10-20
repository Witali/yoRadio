#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

#define RUNTIME_DEFAULT_AUDIO_INFO false
#define RUNTIME_DEFAULT_SOFTAP_DELAY_MIN 0U
// Ten 1600-byte blocks give a conservative 16 KiB default. Users may raise
// the compressed-stream reserve to 22.4 KiB when a high-bitrate station needs
// more jitter tolerance and the memory diagnostics confirm enough headroom.
#define RUNTIME_MIN_AUDIO_BUFFER_BLOCKS 5U
#define RUNTIME_MAX_AUDIO_BUFFER_BLOCKS 14U
#define RUNTIME_DEFAULT_AUDIO_BUFFER_BLOCKS 10U
#define RUNTIME_DEFAULT_MDNS_NAME "yoradio"
#define RUNTIME_DEFAULT_WATCHDOG true
#define RUNTIME_DEFAULT_STATION_TIMEOUT_SEC 10U
#define RUNTIME_MIN_STATION_TIMEOUT_SEC 1U
#define RUNTIME_MAX_STATION_TIMEOUT_SEC 120U
#define RUNTIME_DEFAULT_TZ_HOUR 0
#define RUNTIME_DEFAULT_TZ_MINUTE 0U
#define RUNTIME_DEFAULT_SNTP1 "pool.ntp.org"
#define RUNTIME_DEFAULT_SNTP2 "time.nist.gov"
#define RUNTIME_DEFAULT_TIME_SYNC_INTERVAL_MIN 60U
#define RUNTIME_SNTP_NAME_CAPACITY 35U
#define RUNTIME_DEFAULT_VOLUME_STEPS 1U
#define RUNTIME_MIN_ENCODER_ACCELERATION 0U
#define RUNTIME_MAX_ENCODER_ACCELERATION 1000U
#define RUNTIME_DEFAULT_ENCODER_ACCELERATION 200U

esp_err_t runtime_settings_init(void);

typedef struct {
    int8_t timezone_hour;
    uint8_t timezone_minute;
    uint16_t sync_interval_min;
    char servers[2][RUNTIME_SNTP_NAME_CAPACITY];
} runtime_time_settings_t;

// Checked coherent copy of the committed in-memory time settings. Call after
// init; timeout is finite (zero means try-lock). Failure leaves *output intact.
// Separate UI setting commands remain separate commits, not one NVS record.
esp_err_t runtime_settings_get_time_snapshot(runtime_time_settings_t *output,
                                            uint32_t timeout_ms);

bool runtime_settings_get_audio_info(void);
uint8_t runtime_settings_get_softap_delay_min(void);
typedef struct {
    uint32_t revision;
    uint8_t delay_min;
} runtime_softap_settings_t;
// Coherent committed RAM policy, including accepted same-value saves. The
// boot-local revision never wraps; exhausted writers fail before persistence.
runtime_softap_settings_t runtime_settings_get_softap_snapshot(void);
uint8_t runtime_settings_get_audio_buffer_blocks(void);
void runtime_settings_get_mdns_name(char *output, size_t output_size);
bool runtime_settings_get_watchdog(void);
uint8_t runtime_settings_get_station_timeout_sec(void);
int8_t runtime_settings_get_timezone_hour(void);
uint8_t runtime_settings_get_timezone_minute(void);
void runtime_settings_get_sntp1(char *output, size_t output_size);
void runtime_settings_get_sntp2(char *output, size_t output_size);
uint16_t runtime_settings_get_time_sync_interval_min(void);
uint8_t runtime_settings_get_volume_steps(void);
uint16_t runtime_settings_get_encoder_acceleration(void);

esp_err_t runtime_settings_set_audio_info(bool enabled);
esp_err_t runtime_settings_set_softap_delay_min(uint8_t minutes);
esp_err_t runtime_settings_set_audio_buffer_blocks(uint8_t blocks);
esp_err_t runtime_settings_set_mdns_name(const char *name);
esp_err_t runtime_settings_set_watchdog(bool enabled);
esp_err_t runtime_settings_set_station_timeout_sec(uint8_t seconds);
esp_err_t runtime_settings_set_timezone_hour(int8_t hour);
esp_err_t runtime_settings_set_timezone_minute(uint8_t minute);
esp_err_t runtime_settings_set_sntp1(const char *server);
esp_err_t runtime_settings_set_sntp2(const char *server);
esp_err_t runtime_settings_set_time_sync_interval_min(uint16_t minutes);
esp_err_t runtime_settings_set_volume_steps(uint8_t steps);
esp_err_t runtime_settings_set_encoder_acceleration(uint16_t acceleration);
