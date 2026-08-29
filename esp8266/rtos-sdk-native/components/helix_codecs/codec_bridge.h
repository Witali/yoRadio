#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum { HELIX_CODEC_MP3 = 1, HELIX_CODEC_AAC = 2 } helix_codec_kind_t;

typedef struct helix_codec helix_codec_t;

typedef struct {
    uint32_t sample_rate;
    uint32_t bitrate;
    uint8_t channels;
    uint8_t bits_per_sample;
} helix_stream_info_t;

typedef bool (*helix_pcm_callback_t)(void *context,
                                     const helix_stream_info_t *info,
                                     int16_t *pcm, size_t samples);

helix_codec_t *helix_codec_create(helix_codec_kind_t kind,
                                  size_t reserve_heap_bytes);
void helix_codec_destroy(helix_codec_t *codec);
int helix_codec_switch(helix_codec_t *codec, helix_codec_kind_t kind);
helix_codec_kind_t helix_codec_detect(const uint8_t *data, size_t size);
uint8_t *helix_codec_write_pointer(helix_codec_t *codec, size_t *capacity);
int helix_codec_commit(helix_codec_t *codec, size_t size,
                       helix_pcm_callback_t callback, void *context);
int helix_codec_feed(helix_codec_t *codec, const uint8_t *data, size_t size,
                     bool end_of_stream, helix_pcm_callback_t callback,
                     void *context);
size_t helix_codec_workspace_size(void);
size_t helix_codec_arena_used(const helix_codec_t *codec);

#ifdef __cplusplus
}
#endif
