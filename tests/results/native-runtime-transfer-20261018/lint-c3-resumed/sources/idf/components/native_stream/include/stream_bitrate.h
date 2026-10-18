#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define STREAM_BITRATE_WINDOW_US INT64_C(5000000)

// Stream producer owns this meter. Bytes must exclude HTTP and ICY metadata.
// This is delivered audio throughput, not a claim about nominal codec bitrate.
typedef struct {
    uint64_t audio_bytes;
    int64_t started_us;
    bool initialized;
} stream_bitrate_meter_t;

static inline uint32_t stream_bitrate_meter_add(stream_bitrate_meter_t *meter,
                                                size_t bytes, int64_t now_us) {
    if (!meter || !bytes || now_us < 0) return 0;
    if (!meter->initialized || now_us < meter->started_us) {
        meter->initialized = true;
        meter->started_us = now_us;
        meter->audio_bytes = 0;
    }
    // A corrupt/unrepresentable count cannot wrap into a plausible estimate.
    const uint64_t maximum_bytes = UINT64_MAX / UINT64_C(8000000);
    if (bytes > maximum_bytes || meter->audio_bytes > maximum_bytes - bytes) {
        meter->started_us = now_us;
        meter->audio_bytes = 0;
        return 0;
    }
    meter->audio_bytes += bytes;
    int64_t elapsed_us = now_us - meter->started_us;
    if (elapsed_us < STREAM_BITRATE_WINDOW_US) return 0;
    uint64_t bps = meter->audio_bytes * UINT64_C(8000000) / (uint64_t)elapsed_us;
    meter->started_us = now_us;
    meter->audio_bytes = 0;
    if (!bps || bps > UINT32_MAX) return 0;
    return (uint32_t)((bps + 500U) / 1000U);
}
