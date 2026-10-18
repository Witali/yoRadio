#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "icy_title.h"

typedef bool (*stream_body_audio_fn)(void *, const uint8_t *, size_t);
typedef void (*stream_body_title_fn)(void *, const char *);

typedef struct {
    uint32_t interval, audio_remaining, metadata_remaining;
    icy_title_parser_t title;
} stream_body_t;

static inline bool stream_body_interval(const char *text, uint32_t *interval) {
    if (!text || !interval) return false;
    while (*text == ' ' || *text == '\t') ++text;
    if (*text < '0' || *text > '9') return false;
    uint32_t value = 0;
    do {
        unsigned digit = (unsigned)(*text++ - '0');
        if (value > (UINT32_MAX - digit) / 10U) return false;
        value = value * 10U + digit;
    } while (*text >= '0' && *text <= '9');
    while (*text == ' ' || *text == '\t') ++text;
    if (*text) return false;
    *interval = value;
    return true;
}

static inline void stream_body_init(stream_body_t *body, uint32_t interval) {
    *body = (stream_body_t){.interval=interval, .audio_remaining=interval};
}

// ICY framing is independent of TCP read boundaries and codec detection.
// No input pointer escapes a call. Only the bounded title prefix is retained.
static inline bool stream_body_feed(stream_body_t *body, const uint8_t *data,
        size_t size, stream_body_audio_fn audio, stream_body_title_fn title,
        void *context) {
    if (!size) return true;
    if (!body->interval) return audio(context, data, size);
    while (size) {
        if (body->metadata_remaining) {
            size_t chunk = size < body->metadata_remaining ? size : body->metadata_remaining;
            icy_title_feed(&body->title, data, chunk);
            data += chunk; size -= chunk; body->metadata_remaining -= (uint32_t)chunk;
            if (!body->metadata_remaining) {
                const char *text = icy_title_finish(&body->title);
                if (text && title) title(context, text);
                body->audio_remaining = body->interval;
            }
        } else if (!body->audio_remaining) {
            body->metadata_remaining = (uint32_t)*data++ * ICY_METADATA_BLOCK_BYTES;
            --size;
            if (body->metadata_remaining) icy_title_begin(&body->title);
            else body->audio_remaining = body->interval;
        } else {
            size_t chunk = size < body->audio_remaining ? size : body->audio_remaining;
            if (!audio(context, data, chunk)) return false;
            data += chunk; size -= chunk; body->audio_remaining -= (uint32_t)chunk;
        }
    }
    return true;
}
