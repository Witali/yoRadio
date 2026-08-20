#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CUSTOM_LEGACY_AAC = 1,
    CUSTOM_LEGACY_MP3 = 2,
} custom_legacy_kind_t;

typedef struct custom_legacy_decoder custom_legacy_decoder_t;

typedef struct {
    uint32_t sample_rate;
    uint8_t bits_per_sample;
    uint8_t channels;
    uint32_t bitrate;
} custom_legacy_info_t;

typedef struct {
    uint64_t decode_us;
    uint32_t decode_calls;
    uint32_t max_call_us;
    uint32_t input_bytes;
} custom_legacy_feed_stats_t;

typedef bool (*custom_legacy_pcm_callback_t)(
    void *user, const custom_legacy_info_t *info, const uint8_t *pcm,
    size_t pcm_size);

custom_legacy_decoder_t *custom_legacy_decoder_create(
    custom_legacy_kind_t kind);
void custom_legacy_decoder_destroy(custom_legacy_decoder_t *decoder);

int custom_legacy_decoder_feed(custom_legacy_decoder_t *decoder,
                               const uint8_t *data, size_t size, bool eos,
                               custom_legacy_pcm_callback_t callback,
                               void *user,
                               custom_legacy_feed_stats_t *stats);

#ifdef __cplusplus
}
#endif
