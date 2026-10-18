#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

typedef enum {
    NATIVE_NETWORK_STARTING = 0,
    NATIVE_NETWORK_CLIENT,
    NATIVE_NETWORK_ACCESS_POINT,
    NATIVE_NETWORK_ERROR,
} native_network_mode_t;

typedef enum {
    NATIVE_BITRATE_NONE = 0, NATIVE_BITRATE_ICY, NATIVE_BITRATE_DECODER, NATIVE_BITRATE_MEASURED,
} native_bitrate_source_t;

typedef struct {
    SemaphoreHandle_t lock;
    native_network_mode_t network_mode;
    bool web_ready;
    bool audio_running;
    bool audio_pending;
    bool audio_failed;
    uint32_t audio_generation;
    int8_t wifi_rssi;
    uint32_t ipv4;
    uint32_t bitrate_kbps;
    native_bitrate_source_t bitrate_source;
    uint32_t sample_rate_hz;
    uint8_t channels, bits_per_sample;
    uint32_t pcm_sample_rate_hz;
    uint8_t pcm_channels;
    bool channels_are_core, format_is_pcm;
    char codec[16];
    char station[96];
    char stream_format[48];
    char title[192];
} native_state_t;

void native_state_init(native_state_t *state);
void native_state_set_network(native_state_t *state,
                              native_network_mode_t mode,
                              uint32_t ipv4);
void native_state_snapshot(native_state_t *state, native_state_t *snapshot);
void native_state_begin_audio(native_state_t *state, uint32_t generation,
                              const char *station, const char *format);
// Caller already owns state->lock. Performs the same metadata/title reset
// as begin_audio without taking the mutex again; NULL station preserves label.
void native_state_begin_audio_locked(native_state_t *state, uint32_t generation,
                                     const char *station, const char *format);
void native_state_set_audio(native_state_t *state, uint32_t generation,
                            bool running, const char *format);
void native_state_set_title(native_state_t *state, uint32_t generation,
                            const char *title);
void native_state_set_station(native_state_t *state, const char *station);
void native_state_set_pending(native_state_t *state, uint32_t generation, bool pending);
void native_state_set_connecting(native_state_t *state, uint32_t generation);
void native_state_fail_audio(native_state_t *state, uint32_t generation, const char *status);
typedef struct {
    const char *codec;
    uint32_t sample_rate_hz;
    uint8_t channels, bits_per_sample;
    uint32_t pcm_sample_rate_hz;
    uint8_t pcm_channels;
    bool channels_are_core, format_is_pcm;
} native_stream_info_t;
bool native_state_set_stream_info(native_state_t *state, uint32_t generation,
                                  const native_stream_info_t *info);
void native_state_set_bitrate(native_state_t *state, uint32_t generation, uint32_t bitrate_kbps);
void native_state_publish_bitrate(native_state_t *state, uint32_t generation, uint32_t bitrate_kbps,
                                  native_bitrate_source_t source);
void native_state_format_stream_details(const native_state_t *state, char *output, size_t output_size);

