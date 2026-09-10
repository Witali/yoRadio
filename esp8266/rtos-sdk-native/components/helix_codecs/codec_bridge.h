#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum { HELIX_CODEC_MP3 = 1, HELIX_CODEC_AAC = 2, HELIX_CODEC_OPUS = 3 } helix_codec_kind_t;

typedef struct helix_codec helix_codec_t;

typedef struct {
    uint32_t sample_rate;
    uint32_t bitrate;
    uint8_t channels; /* Interleaved PCM channels passed to the output callback. */
    uint8_t bits_per_sample;
    uint8_t source_channels; /* Stream channels before optional mono synthesis. */
} helix_stream_info_t;

typedef bool (*helix_pcm_callback_t)(void *context,
                                     const helix_stream_info_t *info,
                                     int16_t *pcm, size_t samples);

bool helix_codec_prepare(void);
helix_codec_t *helix_codec_create(helix_codec_kind_t kind,
                                  size_t reserve_heap_bytes);
void helix_codec_destroy(helix_codec_t *codec);
int helix_codec_switch(helix_codec_t *codec, helix_codec_kind_t kind);
helix_codec_kind_t helix_codec_detect(const uint8_t *data, size_t size);
uint8_t *helix_codec_write_pointer(helix_codec_t *codec, size_t *capacity);
/* Queue compressed bytes without decoding; no second FIFO is allocated.
 * After every process/commit, reacquire the write pointer before writing. */
int helix_codec_buffer_commit(helix_codec_t *codec, size_t size);
size_t helix_codec_buffered(const helix_codec_t *codec);
size_t helix_codec_input_capacity(void);
/* Actual read-ahead capacity, which can be smaller for experimental Opus. */
size_t helix_codec_active_input_capacity(const helix_codec_t *codec);
/* 0 = progress, 1 = incomplete frame (needs input), negative = error.
 * Decodes at most one compressed frame; PCM callbacks may run in blocks. */
int helix_codec_process_one(helix_codec_t *codec,
                            helix_pcm_callback_t callback, void *context);
/* Validate end-of-stream after process_one has drained available packets. */
int helix_codec_finish(helix_codec_t *codec);
const char *helix_codec_error_message(helix_codec_kind_t kind, int result);
/* Compatibility API: append and drain all complete frames. */
int helix_codec_commit(helix_codec_t *codec, size_t size,
                       helix_pcm_callback_t callback, void *context);
int helix_codec_feed(helix_codec_t *codec, const uint8_t *data, size_t size,
                     bool end_of_stream, helix_pcm_callback_t callback,
                     void *context);
size_t helix_codec_workspace_size(void);
size_t helix_codec_arena_used(const helix_codec_t *codec);
size_t helix_codec_dram_used(const helix_codec_t *codec);
size_t helix_codec_iram_used(const helix_codec_t *codec);

#if YORADIO_ESP8266_OPUS_STREAM_TEST
typedef enum {
    HELIX_OPUS_INIT_NONE = 0,
    HELIX_OPUS_INIT_CODEC = 1,
    HELIX_OPUS_INIT_INPUT = 2,
    HELIX_OPUS_INIT_PCM = 3,
    HELIX_OPUS_INIT_ARENA_BIND = 4,
    HELIX_OPUS_INIT_WORKSPACE = 5,
    HELIX_OPUS_INIT_IRAM = 6,
    HELIX_OPUS_INIT_STATE = 7,
    HELIX_OPUS_INIT_SCRATCH = 8,
    HELIX_OPUS_INIT_NATIVE = 9,
    HELIX_OPUS_INIT_RESERVE = 10
} helix_opus_init_stage_t;
/* First failure of the latest create/switch attempt, captured before cleanup.
 * free_dram is CAP8, not the SDK's combined CAP32 free-heap value. detail is
 * the native error at NATIVE, combined CAP32 free bytes at RESERVE, else zero.
 * requested_bytes is the failed allocation size (logical capacity at
 * ARENA_BIND, state size at NATIVE, required reserve at RESERVE). */
typedef struct {
    uint32_t stage;
    uint32_t free_dram;
    uint32_t requested_bytes;
    uint32_t reserve_bytes;
    int32_t detail;
} helix_opus_init_failure_t;
void helix_codec_opus_init_failure_snapshot(helix_opus_init_failure_t *out);
#endif

#ifdef __cplusplus
}
#endif
