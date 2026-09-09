#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Incremental ICY demultiplexer. It retains no audio and allocates nothing.
 * raw is compacted in place; metadata uses the existing HTTP scratch array.
 * Keep the two arrays distinct, including for the initial HTTP body prefix. */
typedef struct {
    uint32_t interval, audio_left;
    size_t metadata_left, metadata_kept;
} stream_icy_t;

typedef void (*stream_metadata_callback_t)(size_t size, void *context);

static inline size_t stream_icy_audio(stream_icy_t *icy, uint8_t *raw,
        size_t size, uint8_t *metadata, size_t metadata_capacity,
        stream_metadata_callback_t callback, void *context) {
    if (!icy->interval) return size;
    size_t in = 0, out = 0;
    while (in < size) {
        if (icy->audio_left) {
            size_t count = size - in;
            if (count > icy->audio_left) count = icy->audio_left;
            memmove(raw + out, raw + in, count);
            out += count;
            in += count;
            icy->audio_left -= (uint32_t)count;
        } else if (icy->metadata_left) {
            size_t count = size - in;
            if (count > icy->metadata_left) count = icy->metadata_left;
            size_t keep = metadata_capacity - icy->metadata_kept;
            if (keep > count) keep = count;
            if (keep) memcpy(metadata + icy->metadata_kept, raw + in, keep);
            icy->metadata_kept += keep;
            icy->metadata_left -= count;
            in += count;
            if (!icy->metadata_left) {
                if (callback) callback(icy->metadata_kept, context);
                icy->audio_left = icy->interval;
            }
        } else {
            icy->metadata_left = (size_t)raw[in++] * 16U;
            icy->metadata_kept = 0;
            if (!icy->metadata_left) icy->audio_left = icy->interval;
        }
    }
    return out;
}

static inline bool stream_prefill_ready(size_t buffered, size_t capacity,
        bool ended, int64_t elapsed_us, uint32_t timeout_ms) {
    return buffered == capacity || ended ||
        elapsed_us >= (int64_t)timeout_ms * 1000;
}
