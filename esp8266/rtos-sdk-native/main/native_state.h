#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

typedef enum {
    NETWORK_STARTING,
    NETWORK_CLIENT,
    NETWORK_ACCESS_POINT,
    NETWORK_ERROR,
} network_mode_t;

typedef enum {
    CODEC_NONE,
    CODEC_HELIX_MP3,
    CODEC_HELIX_AAC,
} codec_type_t;

typedef struct {
    network_mode_t network_mode;
    bool playing;
    bool connecting;
    int8_t wifi_rssi;
    uint16_t station_index;
    uint16_t station_count;
    uint16_t buffer_percent;
    uint32_t bitrate_kbps;
    uint32_t sample_rate_hz;
    uint8_t channels;
    codec_type_t codec;
    char station[128];
    char title[192];
    char error[96];
} native_state_t;

void native_state_init(void);
void native_state_snapshot(native_state_t *output);
void native_state_update(const native_state_t *input);
const char *native_codec_name(codec_type_t codec);

