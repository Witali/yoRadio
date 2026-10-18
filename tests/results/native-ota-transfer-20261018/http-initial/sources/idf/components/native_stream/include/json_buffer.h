#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    char *data;
    size_t capacity, length;
    bool failed;
} json_buffer_t;

static inline void json_buffer_init(json_buffer_t *out, char *data, size_t capacity) {
    *out = (json_buffer_t){.data=data, .capacity=capacity};
    if (capacity) data[0] = '\0';
}

static inline void json_buffer_bytes(json_buffer_t *out, const char *data, size_t size) {
    if (out->failed) return;
    if (out->length >= out->capacity || size >= out->capacity - out->length) {
        out->failed = true;
        return;
    }
    memcpy(out->data + out->length, data, size);
    out->length += size;
    out->data[out->length] = '\0';
}

static inline void json_buffer_raw(json_buffer_t *out, const char *text) {
    json_buffer_bytes(out, text, strlen(text));
}

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

static inline void json_buffer_string(json_buffer_t *out, const char *text) {
    static const char hex[] = "0123456789abcdef";
    json_buffer_raw(out, "\"");
    const uint8_t *p = (const uint8_t *)text;
    while (*p && !out->failed) {
        if (*p == '"' || *p == '\\') {
            const char escaped[2] = {'\\', (char)*p++};
            json_buffer_bytes(out, escaped, sizeof(escaped));
        } else if (*p < 0x20) {
            const char escaped[6] = {'\\','u','0','0',hex[*p >> 4],hex[*p & 15]};
            ++p; json_buffer_bytes(out, escaped, sizeof(escaped));
        } else if (*p < 0x80) {
            json_buffer_bytes(out, (const char *)p++, 1);
        } else {
            size_t count = json_utf8_sequence(p);
            if (count) { json_buffer_bytes(out, (const char *)p, count); p += count; }
            else { json_buffer_raw(out, "\\ufffd"); ++p; }
        }
    }
    json_buffer_raw(out, "\"");
}
