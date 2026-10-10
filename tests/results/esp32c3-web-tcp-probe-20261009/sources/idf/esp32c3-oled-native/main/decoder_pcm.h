#pragma once

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

// 2048 SBR samples/channel * stereo * signed 16-bit PCM.
#define NATIVE_AAC_PCM_FRAME_BYTES 8192
#define DECODE_BUFFER_INITIAL 12288

// Realloc failure leaves the old workspace and its capacity valid.
static inline bool decoder_pcm_resize(uint8_t **buffer, size_t *capacity,
                                      size_t required) {
    if (!required) return false;
    if (*capacity == required) return true;
    uint8_t *resized = realloc(*buffer, required);
    if (!resized) return false;
    *buffer = resized;
    *capacity = required;
    return true;
}

// Call only after closing the old decoder and copying its PCM into the queue.
// AAC also shrinks a workspace retained from another codec. Other codecs keep
// their existing high-water capacity and their needed_size growth contract.
static inline bool decoder_pcm_prepare(uint8_t **buffer, size_t *capacity,
                                       bool aac) {
    size_t required = aac ? NATIVE_AAC_PCM_FRAME_BYTES : DECODE_BUFFER_INITIAL;
    if (!aac && *capacity >= required) return true;
    return decoder_pcm_resize(buffer, capacity, required);
}
