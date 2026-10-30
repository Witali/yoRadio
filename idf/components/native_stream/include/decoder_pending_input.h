#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// Task-owned storage for a public decoder's unconsumed input prefix. Ordinary
// packets remain borrowed and require no copy or allocation. This is an API
// representation/resource bound, not a restriction on the encoded format.
typedef struct {
    uint8_t *data;
    size_t size, capacity;
} decoder_pending_input_t;

typedef enum {
    DECODER_PENDING_INPUT_OK = 0,
    DECODER_PENDING_INPUT_NO_MEMORY,
    DECODER_PENDING_INPUT_TOO_LARGE,
    DECODER_PENDING_INPUT_INVALID,
} decoder_pending_input_status_t;

static inline decoder_pending_input_status_t decoder_pending_input_reserve(
        decoder_pending_input_t *pending, size_t needed) {
    if (needed > UINT32_MAX) return DECODER_PENDING_INPUT_TOO_LARGE;
    if (needed <= pending->capacity) return DECODER_PENDING_INPUT_OK;
    size_t capacity = pending->capacity ? pending->capacity : 16;
    while (capacity < needed) {
        if (capacity > UINT32_MAX / 2U) { capacity = needed; break; }
        capacity *= 2U;
    }
    uint8_t *larger = realloc(pending->data, capacity);
    if (!larger) return DECODER_PENDING_INPUT_NO_MEMORY;
    pending->data = larger;
    pending->capacity = capacity;
    return DECODER_PENDING_INPUT_OK;
}

// external is a distinct borrowed packet, never an alias of pending storage.
// On success, size becomes zero: the caller now owns the active raw view until
// it finishes processing or explicitly retains its remaining suffix. Failure
// preserves the retained prefix and all output parameters for owner cleanup.
static inline decoder_pending_input_status_t decoder_pending_input_prepare(
        decoder_pending_input_t *pending, uint8_t *external, size_t bytes,
        uint8_t **buffer, uint32_t *length, bool *owned) {
    if (bytes && !external) return DECODER_PENDING_INPUT_INVALID;
    if (bytes > UINT32_MAX || pending->size > UINT32_MAX - bytes)
        return DECODER_PENDING_INPUT_TOO_LARGE;
    if (!pending->size) {
        *buffer = external;
        *length = (uint32_t)bytes;
        *owned = false;
        return DECODER_PENDING_INPUT_OK;
    }
    size_t total = pending->size + bytes;
    decoder_pending_input_status_t result = decoder_pending_input_reserve(pending, total);
    if (result != DECODER_PENDING_INPUT_OK) return result;
    if (bytes) memcpy(pending->data + pending->size, external, bytes);
    *buffer = pending->data;
    *length = (uint32_t)total;
    *owned = true;
    pending->size = 0;
    return DECODER_PENDING_INPUT_OK;
}

// owned describes provenance explicitly; comparing unrelated pointers would
// be undefined. An owned suffix must be inside the last prepared raw view.
static inline decoder_pending_input_status_t decoder_pending_input_retain(
        decoder_pending_input_t *pending, const uint8_t *remaining, size_t bytes,
        bool owned) {
    if (bytes && !remaining) return DECODER_PENDING_INPUT_INVALID;
    if (bytes > UINT32_MAX) return DECODER_PENDING_INPUT_TOO_LARGE;
    if (owned) {
        if (bytes > pending->capacity) return DECODER_PENDING_INPUT_INVALID;
        if (bytes) memmove(pending->data, remaining, bytes);
    } else {
        decoder_pending_input_status_t result = decoder_pending_input_reserve(pending, bytes);
        if (result != DECODER_PENDING_INPUT_OK) return result;
        if (bytes) memcpy(pending->data, remaining, bytes);
    }
    pending->size = bytes;
    return DECODER_PENDING_INPUT_OK;
}

static inline void decoder_pending_input_clear(decoder_pending_input_t *pending) {
    free(pending->data);
    *pending = (decoder_pending_input_t){0};
}
