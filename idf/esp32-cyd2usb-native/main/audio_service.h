#pragma once

#include "esp_err.h"
#include "native_state.h"

typedef enum {
    NATIVE_CODEC_AUTO = 0,
    NATIVE_CODEC_MP3,
    NATIVE_CODEC_AAC,
    NATIVE_CODEC_FLAC,
    NATIVE_CODEC_OGG,
} native_codec_t;

esp_err_t audio_service_start(native_state_t *state);
esp_err_t audio_service_play(const char *url, native_codec_t codec);
void audio_service_stop(void);

