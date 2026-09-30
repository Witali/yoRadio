#pragma once

#include "esp_audio_simple_dec.h"

typedef struct native_aac_decoder native_aac_decoder_t;

native_aac_decoder_t *native_aac_decoder_create(void);
void native_aac_decoder_destroy(native_aac_decoder_t *decoder);
esp_audio_err_t native_aac_decoder_process(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *output);
esp_audio_err_t native_aac_decoder_get_info(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_info_t *info);
// The SDK exposes PCM only. Identify extensions only when the decoded layout
// proves them; an unchanged ADTS header cannot prove that SBR/PS is absent.
const char *native_aac_decoder_label(native_aac_decoder_t *decoder,
    const esp_audio_simple_dec_info_t *info, bool *format_is_pcm);
