#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

enum {
    STREAM_ID3_HEADER_BYTES = 10,
    // Application resource bound, not the maximum allowed by ID3.
    STREAM_ID3_RUN_BYTES = 1024 * 1024,
};

static inline bool stream_id3_prefix(const uint8_t *p, size_t size) {
    return memcmp(p, "ID3", size < 3 ? size : 3) == 0;
}

// Requires a complete ten-byte header. Skip the encoded body without decoding
// tag frames, extended headers or unsynchronisation. This is an envelope check,
// not validation of tag contents or footer. Size excludes header and footer.
static inline bool stream_id3_size(const uint8_t *p, uint32_t *total) {
    unsigned reserved_flags = p[3] == 2 ? 0x3f : p[3] == 3 ? 0x1f : 0x0f;
    if (!stream_id3_prefix(p, 3) || p[3] < 2 || p[3] > 4 || p[4] == 0xff ||
        (p[5] & reserved_flags) || ((p[6] | p[7] | p[8] | p[9]) & 0x80))
        return false;
    uint32_t body = ((uint32_t)p[6] << 21) | ((uint32_t)p[7] << 14) |
                    ((uint32_t)p[8] << 7) | p[9];
    uint32_t footer = p[3] == 4 && (p[5] & 0x10) ? STREAM_ID3_HEADER_BYTES : 0;
    *total = STREAM_ID3_HEADER_BYTES + body + footer;
    return true;
}
