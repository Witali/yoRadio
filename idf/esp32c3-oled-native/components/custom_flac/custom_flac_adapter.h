#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct custom_flac_decoder custom_flac_decoder_t;

typedef struct {
    uint32_t sample_rate;
    uint8_t bits_per_sample;
    uint8_t channels;
    uint32_t bitrate;
} custom_flac_info_t;

typedef struct {
    uint64_t decode_us;
    uint32_t decode_calls;
    uint32_t max_call_us;
    uint32_t input_bytes;
} custom_flac_feed_stats_t;

typedef bool (*custom_flac_pcm_callback_t)(
    void *user, const custom_flac_info_t *info, const uint8_t *pcm,
    size_t pcm_size);

custom_flac_decoder_t *custom_flac_decoder_create(void);
void custom_flac_decoder_destroy(custom_flac_decoder_t *decoder);

// Returns 0 when the data was accepted, 1 when the stream needs more data,
// and a negative value for an invalid or unsupported FLAC stream.
int custom_flac_decoder_feed(custom_flac_decoder_t *decoder,
                             const uint8_t *data, size_t size, bool eos,
                             custom_flac_pcm_callback_t callback, void *user,
                             custom_flac_feed_stats_t *stats);

#ifdef __cplusplus
}
#endif
