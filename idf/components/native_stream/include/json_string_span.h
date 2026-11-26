#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Return a valid UTF-8 sequence length, or zero for an invalid/truncated byte.
static inline size_t json_utf8_sequence(const uint8_t *p) {
    unsigned count = p[0] >= 0xc2 && p[0] <= 0xdf ? 2U :
                     p[0] >= 0xe0 && p[0] <= 0xef ? 3U :
                     p[0] >= 0xf0 && p[0] <= 0xf4 ? 4U : 0U;
    if (!count) return 0;
    for (unsigned i=1; i<count; ++i) {
        if ((p[i] & 0xc0U) != 0x80U) return 0;
    }
    if ((p[0] == 0xe0 && p[1] < 0xa0) || (p[0] == 0xed && p[1] >= 0xa0) ||
        (p[0] == 0xf0 && p[1] < 0x90) || (p[0] == 0xf4 && p[1] >= 0x90)) return 0;
    return count;
}

// Return one encoded content span and advance a NUL-terminated input cursor.
// The returned span is synchronous: it either points into the input or into
// the caller's six-byte scratch. Consume it before reusing that scratch.
// A false result means end of input; no pointer is retained by this helper.
static inline bool json_string_next_span(const uint8_t **cursor, char scratch[6],
                                         const char **span, size_t *size) {
    static const char hex[] = "0123456789abcdef";
    const uint8_t *p = *cursor;
    if (!*p) { *span = NULL; *size = 0; return false; }
    if (*p == '"' || *p == '\\') {
        scratch[0] = '\\'; scratch[1] = (char)*p;
        *span = scratch; *size = 2; ++p;
    } else if (*p < 0x20) {
        scratch[0] = '\\'; scratch[1] = 'u'; scratch[2] = '0'; scratch[3] = '0';
        scratch[4] = hex[*p >> 4]; scratch[5] = hex[*p & 15];
        *span = scratch; *size = 6; ++p;
    } else if (*p < 0x80) {
        *span = (const char *)p; *size = 1; ++p;
    } else {
        size_t count = json_utf8_sequence(p);
        if (count) { *span = (const char *)p; *size = count; p += count; }
        else {
            scratch[0] = '\\'; scratch[1] = 'u'; scratch[2] = 'f';
            scratch[3] = 'f'; scratch[4] = 'f'; scratch[5] = 'd';
            *span = scratch; *size = 6; ++p;
        }
    }
    *cursor = p;
    return true;
}
