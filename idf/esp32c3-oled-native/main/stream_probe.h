#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

// Initial elementary-stream/container probe, after HTTP/ICY removal.
// This does not parse frames of an already selected codec or switch codecs.
enum {
    STREAM_PROBE_MP3_HEADER_BYTES = 4,
    STREAM_PROBE_ADTS_HEADER_BYTES = 7,
    STREAM_PROBE_FLAC_PREFIX_BYTES = 8,
    STREAM_PROBE_OGG_PREFIX_BYTES = 5,
    STREAM_PROBE_HEADER_BYTES = 10,
    STREAM_PROBE_SEARCH_BYTES = 4096,
    STREAM_PROBE_TAG_BYTES = 1024 * 1024,
    STREAM_PROBE_TIMEOUT_MS = 10000,
};
typedef enum {
    STREAM_PROBE_MORE = 0,
    STREAM_PROBE_MP3,
    STREAM_PROBE_AAC,
    STREAM_PROBE_FLAC,
    STREAM_PROBE_OGG,
    STREAM_PROBE_INVALID,
} stream_probe_result_t;

typedef struct {
    uint8_t header[STREAM_PROBE_HEADER_BYTES];
    size_t used;
    uint32_t searched;
    uint32_t tag_bytes;
    uint32_t skip;
    stream_probe_result_t result;
} stream_probe_t;

static inline stream_probe_result_t stream_probe_header(const uint8_t *p,
                                                        size_t n) {
    // Native FLAC starts with the mandatory 34-byte STREAMINFO block.
    if (n >= STREAM_PROBE_FLAC_PREFIX_BYTES && memcmp(p, "fLaC", 4) == 0 &&
        (p[4] & 0x7f) == 0 && p[5] == 0 && p[6] == 0 && p[7] == 34)
        return STREAM_PROBE_FLAC;
    // Ogg is a container. Its parser identifies Vorbis/Opus inside it.
    if (n >= STREAM_PROBE_OGG_PREFIX_BYTES && memcmp(p, "OggS", 4) == 0 && p[4] == 0)
        return STREAM_PROBE_OGG;
    if (n >= STREAM_PROBE_ADTS_HEADER_BYTES && p[0] == 0xff && (p[1] & 0xf6) == 0xf0 &&
        ((p[2] >> 2) & 15) <= 12) {
        unsigned frame_bytes = ((p[3] & 3U) << 11) | (p[4] << 3) | (p[5] >> 5);
        unsigned header_bytes = (p[1] & 1U) ? 7U : 9U;
        if (frame_bytes >= header_bytes) return STREAM_PROBE_AAC;
    }
    if (n >= STREAM_PROBE_MP3_HEADER_BYTES && p[0] == 0xff && (p[1] & 0xe0) == 0xe0 &&
        ((p[1] >> 3) & 3) != 1 && // Reserved MPEG version.
        ((p[1] >> 1) & 3) == 1 && // Layer III; ADTS has layer bits zero.
        (p[2] >> 4) != 15 && ((p[2] >> 2) & 3) != 3 &&
        (p[3] & 3) != 2) // Reserved emphasis; free bitrate (index 0) is legal.
        return STREAM_PROBE_MP3;
    return STREAM_PROBE_MORE;
}

// Keep only prefixes that can still become a supported header. Waiting for
// all ten bytes on an impossible candidate delays short headers after junk.
static inline bool stream_probe_needs_more(const uint8_t *p, size_t n) {
    if (!n) return true;
    if (p[0] == 0xff) {
        if (n < 2) return true;
        if ((p[1] & 0xf6) == 0xf0) return n < STREAM_PROBE_ADTS_HEADER_BYTES;
        if ((p[1] & 0xe0) == 0xe0) return n < STREAM_PROBE_MP3_HEADER_BYTES;
        return false;
    }
    if (memcmp(p, "ID3", n < 3 ? n : 3) == 0)
        return n < STREAM_PROBE_HEADER_BYTES;
    if (memcmp(p, "fLaC", n < 4 ? n : 4) == 0)
        return n < STREAM_PROBE_FLAC_PREFIX_BYTES;
    if (memcmp(p, "OggS", n < 4 ? n : 4) == 0)
        return n < STREAM_PROBE_OGG_PREFIX_BYTES;
    return false;
}

// Consume only the prefix needed to identify the codec. On success header[used]
// is retained verbatim for delivery before the unconsumed input. Tags/junk are
// discarded. No allocation, no input pointer retained, no MP3 fallback.
static inline stream_probe_result_t stream_probe_feed(stream_probe_t *probe,
    const uint8_t *data, size_t size, size_t *consumed) {
    *consumed = 0;
    while (*consumed < size && probe->result == STREAM_PROBE_MORE) {
        if (probe->skip) {
            size_t count = size - *consumed;
            if (count > probe->skip) count = probe->skip;
            probe->skip -= (uint32_t)count;
            *consumed += count;
            continue;
        }
        probe->header[probe->used++] = data[(*consumed)++];
        // Revisit every retained suffix now, including incomplete ID3, rather
        // than requiring another network read just to shift the candidate.
        while (probe->used && probe->result == STREAM_PROBE_MORE) {
            if (probe->used >= 3 && memcmp(probe->header, "ID3", 3) == 0) {
                if (probe->used < STREAM_PROBE_HEADER_BYTES) break;
                const uint8_t *p = probe->header;
                // ID3v2.2/2.3/2.4 sizes are synchsafe and exclude the header.
                // A v2.4 footer, when flagged, adds ten further bytes.
                unsigned reserved_flags = p[3] == 2 ? 0x3f : p[3] == 3 ? 0x1f : 0x0f;
                if (p[3] < 2 || p[3] > 4 || p[4] == 0xff ||
                    (p[5] & reserved_flags) || ((p[6] | p[7] | p[8] | p[9]) & 0x80)) {
                    probe->result = STREAM_PROBE_INVALID;
                    break;
                }
                uint32_t body = ((uint32_t)p[6] << 21) | ((uint32_t)p[7] << 14) |
                                ((uint32_t)p[8] << 7) | p[9];
                uint32_t tail = p[3] == 4 && (p[5] & 0x10) ? 10U : 0U;
                uint32_t total = STREAM_PROBE_HEADER_BYTES + body + tail;
                if (total > STREAM_PROBE_TAG_BYTES - probe->tag_bytes) {
                    probe->result = STREAM_PROBE_INVALID;
                    break;
                }
                probe->tag_bytes += total;
                probe->skip = body + tail;
                probe->used = 0;
                break;
            }
            probe->result = stream_probe_header(probe->header, probe->used);
            if (probe->result != STREAM_PROBE_MORE) break;
            if (stream_probe_needs_more(probe->header, probe->used)) break;
            if (++probe->searched >= STREAM_PROBE_SEARCH_BYTES) {
                probe->result = STREAM_PROBE_INVALID;
                break;
            }
            memmove(probe->header, probe->header + 1, --probe->used);
        }
    }
    return probe->result;
}
