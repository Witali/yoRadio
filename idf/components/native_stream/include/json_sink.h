#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#include "json_string_span.h"

typedef bool (*json_sink_write_t)(void *context, const char *data, size_t size);

typedef struct {
    size_t capacity, length;
    bool failed;
    json_sink_write_t write;
    void *context;
} json_sink_t;

// Capacity retains the buffer API's reserved terminal-NUL byte, although a
// sink emits only logical payload bytes. A NULL writer is count-only.
static inline void json_sink_init(json_sink_t *out, size_t capacity,
                                  json_sink_write_t write, void *context) {
    *out = (json_sink_t){.capacity=capacity, .write=write, .context=context};
}

// The callback must consume this span synchronously and must not retain it.
// Length counts completed spans only. On callback failure its external side
// effects may be partial; failure becomes sticky and no later output occurs.
static inline void json_sink_bytes(json_sink_t *out, const char *data, size_t size) {
    if (out->failed) return;
    if (out->length >= out->capacity || size >= out->capacity - out->length) {
        out->failed = true;
        return;
    }
    if (size && out->write && !out->write(out->context, data, size)) {
        out->failed = true;
        return;
    }
    out->length += size;
}

static inline void json_sink_raw(json_sink_t *out, const char *text) {
    if (out->failed) return;
    json_sink_bytes(out, text, strlen(text));
}

static inline void json_sink_string(json_sink_t *out, const char *text) {
    json_sink_raw(out, "\"");
    const uint8_t *p = (const uint8_t *)text;
    char scratch[6];
    const char *span;
    size_t size;
    while (!out->failed && json_string_next_span(&p, scratch, &span, &size))
        json_sink_bytes(out, span, size);
    json_sink_raw(out, "\"");
}
