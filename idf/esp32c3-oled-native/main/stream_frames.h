#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "stream_tags.h"

// Experimental boundary walker. Not yet connected to audio_service.
// Input starts at a known elementary-stream frame/tag boundary, after ICY.
// Never search a frame payload for sync words. AAC rates/channels here describe
// the ADTS core; decoded SBR/PS/PCE metadata remains authoritative for the UI.
enum {
    STREAM_FRAME_MP3_HEADER_BYTES = 4,
    STREAM_FRAME_ADTS_FIXED_BYTES = 7,
    STREAM_FRAME_CRC_BYTES = 2,
    STREAM_FRAME_MPEG1_SAMPLES = 1152,
    STREAM_FRAME_MPEG_LSF_SAMPLES = 576,
    STREAM_FRAME_AAC_BLOCK_SAMPLES = 1024,
    STREAM_FRAME_BITS_PER_BYTE = 8,
};

typedef enum { STREAM_FRAME_MP3 = 1, STREAM_FRAME_ADTS } stream_frame_codec_t;
typedef enum {
    STREAM_FRAME_MORE = 0,
    STREAM_FRAME_READY,
    STREAM_FRAME_INVALID,
    // Bitrate index zero is legal MP3, but header alone cannot give its length.
    // Caller must preserve the bytes and use a free-format-aware decoder/parser.
    STREAM_FRAME_FREE_FORMAT,
    STREAM_FRAME_SINK_FAILED,
} stream_frame_result_t;

typedef struct {
    stream_frame_codec_t codec;
    uint32_t core_rate;
    uint16_t bytes;
    uint16_t core_samples;
    uint8_t core_channels; // Zero: AAC PCE, not a known channel count.
    uint8_t configuration; // MPEG version bits, or AAC audio object type.
} stream_frame_info_t;

static inline stream_frame_result_t stream_frame_header(const uint8_t *p,
        size_t size, stream_frame_info_t *out) {
    if (!size) return STREAM_FRAME_MORE;
    if (p[0] != 0xff) return STREAM_FRAME_INVALID;
    if (size < 2) return STREAM_FRAME_MORE;
    stream_frame_info_t info = {0};
    if ((p[1] & 0xf6) == 0xf0) {
        if (size < STREAM_FRAME_ADTS_FIXED_BYTES) return STREAM_FRAME_MORE;
        static const uint32_t rates[] = {
            96000, 88200, 64000, 48000, 44100, 32000, 24000,
            22050, 16000, 12000, 11025, 8000, 7350
        };
        unsigned rate_index = (p[2] >> 2) & 15U;
        if (rate_index >= sizeof(rates) / sizeof(rates[0]))
            return STREAM_FRAME_INVALID;
        unsigned bytes = ((p[3] & 3U) << 11) | (p[4] << 3) | (p[5] >> 5);
        unsigned header_bytes = STREAM_FRAME_ADTS_FIXED_BYTES +
            ((p[1] & 1U) ? 0 : STREAM_FRAME_CRC_BYTES);
        if (bytes < header_bytes) return STREAM_FRAME_INVALID;
        unsigned channel_config = ((p[2] & 1U) << 2) | (p[3] >> 6);
        info.codec = STREAM_FRAME_ADTS;
        info.core_rate = rates[rate_index];
        info.bytes = (uint16_t)bytes;
        info.core_samples = STREAM_FRAME_AAC_BLOCK_SAMPLES * ((p[6] & 3U) + 1U);
        info.core_channels = channel_config == 7 ? 8 : channel_config;
        info.configuration = (p[2] >> 6) + 1U;
    } else {
        unsigned version = (p[1] >> 3) & 3U;
        unsigned layer = (p[1] >> 1) & 3U;
        if ((p[1] & 0xe0) != 0xe0 || version == 1 || layer != 1)
            return STREAM_FRAME_INVALID;
        if (size < STREAM_FRAME_MP3_HEADER_BYTES) return STREAM_FRAME_MORE;
        unsigned rate_index = (p[2] >> 2) & 3U;
        unsigned bitrate_index = p[2] >> 4;
        if (rate_index == 3 || bitrate_index == 15 || (p[3] & 3U) == 2)
            return STREAM_FRAME_INVALID;
        static const uint16_t bitrate_kbps[2][15] = {
            {0,32,40,48,56,64,80,96,112,128,160,192,224,256,320},
            {0,8,16,24,32,40,48,56,64,80,96,112,128,144,160}
        };
        static const uint32_t rates[] = {44100,48000,32000};
        unsigned rate_shift = version == 3 ? 0 : version == 2 ? 1 : 2;
        info.codec = STREAM_FRAME_MP3;
        info.core_rate = rates[rate_index] >> rate_shift;
        info.core_samples = version == 3 ? STREAM_FRAME_MPEG1_SAMPLES
                                         : STREAM_FRAME_MPEG_LSF_SAMPLES;
        info.core_channels = (p[3] >> 6) == 3 ? 1 : 2;
        info.configuration = version;
        if (!bitrate_index) {
            *out = info;
            return STREAM_FRAME_FREE_FORMAT;
        }
        uint32_t bitrate = bitrate_kbps[version != 3][bitrate_index] * 1000U;
        unsigned padding = (p[2] >> 1) & 1U;
        info.bytes = (uint16_t)((info.core_samples / STREAM_FRAME_BITS_PER_BYTE)
                                 * bitrate / info.core_rate + padding);
    }
    *out = info;
    return STREAM_FRAME_READY;
}

// Callbacks are synchronous; payload pointers are borrowed for that call only.
// begin can flush an old decoder before a different codec's bytes are emitted.
// A queue adapter must coalesce these spans: one queue slot per header would
// unnecessarily reduce the compressed-input capacity. No queue adapter yet.
typedef bool (*stream_frame_begin_fn)(void *, const stream_frame_info_t *);
typedef bool (*stream_frame_data_fn)(void *, const uint8_t *, size_t);
typedef struct {
    uint8_t header[STREAM_ID3_HEADER_BYTES];
    uint8_t used;
    uint16_t remaining;
    uint32_t skip;
    uint32_t tag_bytes; // Consecutive metadata only; reset at each audio frame.
    stream_frame_result_t result;
} stream_frames_t;

static inline stream_frame_result_t stream_frames_feed(stream_frames_t *s,
        const uint8_t *data, size_t size, size_t *consumed,
        stream_frame_begin_fn begin, stream_frame_data_fn emit, void *context) {
    *consumed = 0;
    // Errors are sticky. Reset explicitly before retrying a different stream.
    if (s->result != STREAM_FRAME_MORE) return s->result;
    while (*consumed < size) {
        if (s->skip) {
            size_t count = size - *consumed;
            if (count > s->skip) count = s->skip;
            *consumed += count;
            s->skip -= (uint32_t)count;
            continue;
        }
        if (s->remaining) {
            size_t count = size - *consumed;
            if (count > s->remaining) count = s->remaining;
            if (!emit(context, data + *consumed, count)) {
                s->result = STREAM_FRAME_SINK_FAILED;
                break;
            }
            *consumed += count;
            s->remaining -= count;
            continue;
        }
        s->header[s->used++] = data[(*consumed)++];
        if (stream_id3_prefix(s->header, s->used)) {
            if (s->used < STREAM_ID3_HEADER_BYTES) continue;
            uint32_t total;
            if (!stream_id3_size(s->header, &total) ||
                total > STREAM_ID3_RUN_BYTES - s->tag_bytes) {
                s->result = STREAM_FRAME_INVALID;
                break;
            }
            s->tag_bytes += total;
            s->skip = total - STREAM_ID3_HEADER_BYTES;
            s->used = 0;
            continue;
        }
        stream_frame_info_t info;
        stream_frame_result_t result = stream_frame_header(s->header, s->used, &info);
        if (result == STREAM_FRAME_MORE) continue;
        if (result != STREAM_FRAME_READY) {
            s->result = result;
            break;
        }
        if (!begin(context, &info) || !emit(context, s->header, s->used)) {
            s->result = STREAM_FRAME_SINK_FAILED;
            break;
        }
        s->remaining = info.bytes - s->used;
        s->tag_bytes = 0;
        s->used = 0;
    }
    return s->result;
}

static inline bool stream_frames_complete(const stream_frames_t *s) {
    return s->result == STREAM_FRAME_MORE && !s->used && !s->remaining && !s->skip;
}
