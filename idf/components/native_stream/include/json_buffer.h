#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "json_string_span.h"

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

static inline void json_buffer_string(json_buffer_t *out, const char *text) {
    json_buffer_raw(out, "\"");
    const uint8_t *p = (const uint8_t *)text;
    char scratch[6];
    const char *span;
    size_t size;
    while (!out->failed && json_string_next_span(&p, scratch, &span, &size))
        json_buffer_bytes(out, span, size);
    json_buffer_raw(out, "\"");
}
