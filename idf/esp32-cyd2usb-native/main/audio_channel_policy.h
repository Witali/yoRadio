#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#ifdef ESP_PLATFORM
#include "sdkconfig.h"
#endif
#if CONFIG_YORADIO_AUDIO_STEREO_ONLY
#include "stream_frames.h"
#endif

static inline bool audio_channel_limit_exceeded(unsigned channels) {
#if CONFIG_YORADIO_AUDIO_STEREO_ONLY
    return channels > 2;
#else
    (void)channels;
    return false;
#endif
}

/* A Vorbis identification packet occupies the entire CRC-verified BOS page. */
static inline unsigned audio_vorbis_header_channels(const uint8_t *page, size_t bytes) {
    if (bytes != 58 || !(page[5] & 2u) || page[26] != 1 || page[27] != 30 ||
        memcmp(page + 28, "\x01vorbis\0\0\0\0", 11)) return 0;
    return page[39];
}

#if CONFIG_YORADIO_AUDIO_STEREO_ONLY
enum { AUDIO_FLAC_CHANNEL_PREFIX_BYTES = 21 };

typedef struct {
    uint8_t bytes[AUDIO_FLAC_CHANNEL_PREFIX_BYTES];
    size_t used;
} audio_channel_probe_t;

/* Read the stream prefix once, including when it spans encoded queue packets. */
static inline bool audio_channel_prefix_ready(audio_channel_probe_t *probe,
        const uint8_t *data, size_t bytes, size_t required) {
    if (probe->used >= required || !bytes) return false;
    size_t remaining = required - probe->used;
    size_t count = bytes < remaining ? bytes : remaining;
    memcpy(probe->bytes + probe->used, data, count);
    probe->used += count;
    return probe->used == required;
}

static inline unsigned audio_flac_channel_probe(audio_channel_probe_t *probe,
        const uint8_t *data, size_t bytes) {
    if (!audio_channel_prefix_ready(probe, data, bytes, AUDIO_FLAC_CHANNEL_PREFIX_BYTES)) return 0;
    const uint8_t *prefix = probe->bytes;
    if (memcmp(prefix, "fLaC", 4) || (prefix[4] & 0x7f) ||
        prefix[5] || prefix[6] || prefix[7] != 34) return 0;
    /* The channel count follows the 20-bit sample rate in STREAMINFO. */
    return ((prefix[20] >> 1) & 7u) + 1u;
}

static inline unsigned audio_adts_channel_probe(audio_channel_probe_t *probe,
        const uint8_t *data, size_t bytes) {
    if (!audio_channel_prefix_ready(probe, data, bytes, STREAM_FRAME_ADTS_FIXED_BYTES)) return 0;
    stream_frame_info_t info;
    if (stream_frame_header(probe->bytes, probe->used, &info) != STREAM_FRAME_READY ||
        info.codec != STREAM_FRAME_ADTS) return 0;
    return info.core_channels;
}
#endif
