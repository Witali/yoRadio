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
    NATIVE_BITRATE_NONE = 0,
    NATIVE_BITRATE_ICY,
    NATIVE_BITRATE_DECODER,
    NATIVE_BITRATE_MEASURED,
} native_bitrate_source_t;

typedef struct {
    SemaphoreHandle_t lock;
    native_network_mode_t network_mode;
    bool web_ready;
    bool audio_running;
    bool audio_pending;
    int8_t wifi_rssi;
    uint32_t ipv4;
    uint32_t bitrate_kbps;
    native_bitrate_source_t bitrate_source;
    uint32_t sample_rate_hz;
    uint8_t channels;
    uint8_t bits_per_sample;
    uint32_t pcm_sample_rate_hz;
    uint8_t pcm_channels;
    bool channels_are_core;
    bool format_is_pcm; // Backend cannot confirm the nominal source layout.
    uint32_t audio_generation;
    char station[144];
    char title[192];
    char codec[16];
    char stream_format[48];
} native_state_t;

void native_state_init(native_state_t *state);
void native_state_set_network(native_state_t *state,
                              native_network_mode_t mode,
                              uint32_t ipv4);
void native_state_set_wifi_rssi(native_state_t *state, int8_t rssi);
typedef struct {
    const char *codec;
    uint32_t sample_rate_hz;
    uint8_t channels;
    uint8_t bits_per_sample;
    uint32_t pcm_sample_rate_hz;
    uint8_t pcm_channels;
    bool channels_are_core;
    bool format_is_pcm;
} native_stream_info_t;

void native_state_begin_stream(native_state_t *state, uint32_t generation);
// Caller owns state->lock. Same monotonic generation check and metadata reset
// as begin_stream, without taking that mutex again.
void native_state_begin_stream_locked(native_state_t *state, uint32_t generation);
void native_state_set_audio(native_state_t *state, uint32_t generation,
                            bool running, const char *status);
void native_state_set_bitrate(native_state_t *state, uint32_t generation,
                              uint32_t bitrate_kbps);
void native_state_publish_bitrate(native_state_t *state, uint32_t generation,
                                  uint32_t bitrate_kbps,
                                  native_bitrate_source_t source);
void native_state_set_pending(native_state_t *state, uint32_t generation, bool pending);
void native_state_set_connecting(native_state_t *state, uint32_t generation);
// Returns true only when the current generation's confirmed format changes.
bool native_state_set_stream_info(native_state_t *state, uint32_t generation,
                                  const native_stream_info_t *info);
void native_state_format_stream_details(const native_state_t *state,
                                        char *output, size_t output_size);
void native_state_set_station(native_state_t *state, const char *station);
void native_state_set_title(native_state_t *state, const char *title);
// Metadata callbacks must check the stream identity under the state mutex.
void native_state_set_stream_title(native_state_t *state, uint32_t generation,
                                    const char *title);
void native_state_snapshot(native_state_t *state, native_state_t *snapshot);

