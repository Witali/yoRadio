#pragma once
#include <stdlib.h>
#include "esp_audio_simple_dec.h"
#include "native_aac_decoder.h"

// PCM ownership is independent of successful decoder initialization. Queued
// audio owns copies (send_pcm), so close can release this workspace before the
// generation-tagged terminal marker is forwarded to the output queue.
static inline void decoder_resources_release(
    esp_audio_simple_dec_handle_t *simple, native_aac_decoder_t **aac,
    uint8_t **pcm, size_t *capacity) {
    if (*simple) esp_audio_simple_dec_close(*simple);
    *simple = NULL;
    if (*aac) native_aac_decoder_destroy(*aac);
    *aac = NULL;
    free(*pcm);
    *pcm = NULL;
    *capacity = 0;
}
