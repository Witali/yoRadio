#pragma once

#include <stdint.h>
#include <string.h>
#include "adaptive_input.h"

// Producer-owned startup window. Packet storage belongs to adaptive_input;
// these are unpublished WRITING leases, protected from TLS reclamation.
// No allocation, blocking acquisition, or decoder publication happens here.
// The caller must cancel on every terminal path and before reinitialization.
enum { STREAM_STAGING_SLOTS = 4, STREAM_STAGING_LOOKAHEAD = 10 };
typedef struct {
    adaptive_input_t *queue;
    size_t header_bytes, payload_bytes;
    void *packet[STREAM_STAGING_SLOTS];
    size_t length[STREAM_STAGING_SLOTS];
    unsigned count, look_used;
    uint8_t look[STREAM_STAGING_LOOKAHEAD];
} stream_staging_t;

static inline bool stream_staging_init(stream_staging_t *s,
        adaptive_input_t *queue, size_t header_bytes, size_t payload_bytes) {
    adaptive_input_stats_t stats = adaptive_input_stats(queue);
    if (!payload_bytes || header_bytes > stats.packet_capacity ||
        payload_bytes > stats.packet_capacity - header_bytes ||
        stats.minimum < STREAM_STAGING_SLOTS) return false;
    *s = (stream_staging_t){.queue=queue, .header_bytes=header_bytes,
                            .payload_bytes=payload_bytes};
    return true;
}

static inline size_t stream_staging_size(const stream_staging_t *s) {
    size_t bytes = s->look_used;
    for (unsigned i=0; i<s->count; ++i) bytes += s->length[i];
    return bytes;
}

static inline void stream_staging_cancel(stream_staging_t *s) {
    for (unsigned i=0; i<s->count; ++i) {
        adaptive_input_cancel(s->queue, s->packet[i]);
        s->packet[i] = NULL;
        s->length[i] = 0;
    }
    s->count = s->look_used = 0;
}

static inline uint8_t *stream_staging_span(stream_staging_t *s,
        size_t offset, size_t *available) {
    for (unsigned i=0; i<s->count; ++i) {
        if (offset < s->length[i]) {
            *available = s->length[i] - offset;
            return (uint8_t *)s->packet[i] + s->header_bytes + offset;
        }
        offset -= s->length[i];
    }
    if (offset < s->look_used) {
        *available = s->look_used - offset;
        return s->look + offset;
    }
    *available = 0;
    return NULL;
}

// Suitable directly as stream_confirm_read_fn. Bounds checked before copying.
static inline bool stream_staging_read(void *opaque, size_t offset,
        uint8_t *destination, size_t count) {
    stream_staging_t *s = opaque;
    size_t bytes = stream_staging_size(s);
    if (offset > bytes || count > bytes-offset) return false;
    while (count) {
        size_t n;
        uint8_t *source = stream_staging_span(s, offset, &n);
        if (n > count) n = count;
        memcpy(destination, source, n);
        destination += n; offset += n; count -= n;
    }
    return true;
}

// Returns the accepted prefix. A short result means storage backpressure or
// the fixed window limit; the caller retains the rest and handles its deadline.
static inline size_t stream_staging_append(stream_staging_t *s,
        const uint8_t *data, size_t bytes) {
    size_t accepted = 0;
    while (accepted < bytes) {
        if (!s->count || s->length[s->count-1] == s->payload_bytes) {
            if (s->count == STREAM_STAGING_SLOTS) {
                size_t n = sizeof(s->look) - s->look_used;
                if (n > bytes-accepted) n = bytes-accepted;
                memcpy(s->look+s->look_used, data+accepted, n);
                s->look_used += n;
                return accepted+n;
            }
            void *packet = NULL;
            if (adaptive_input_acquire(s->queue, &packet,
                    s->header_bytes+s->payload_bytes, 0) != pdTRUE) return accepted;
            s->packet[s->count] = packet;
            s->length[s->count++] = 0;
        }
        unsigned last = s->count-1;
        size_t room = s->payload_bytes-s->length[last];
        uint8_t *end = (uint8_t *)s->packet[last]+s->header_bytes+s->length[last];
        // After handing off the first packet, the old lookahead may need to
        // move into a newly acquired slot before any newer bytes are appended.
        if (s->look_used) {
            size_t n = s->look_used < room ? s->look_used : room;
            memcpy(end, s->look, n);
            memmove(s->look, s->look+n, s->look_used-n);
            s->look_used -= n; s->length[last] += n;
            continue;
        }
        size_t n = bytes-accepted;
        if (n > room) n = room;
        memcpy(end, data+accepted, n);
        s->length[last] += n; accepted += n;
    }
    return accepted;
}

// Remove proven junk or already received metadata. Compaction is forward and
// span-bounded, preserving every remaining byte even for overlapping ranges.
static inline bool stream_staging_erase(stream_staging_t *s,
        size_t offset, size_t count) {
    size_t bytes = stream_staging_size(s);
    if (offset > bytes || count > bytes-offset) return false;
    if (!count) return true;
    size_t destination = offset, source = offset+count;
    while (source < bytes) {
        size_t source_span, destination_span;
        uint8_t *from = stream_staging_span(s, source, &source_span);
        uint8_t *to = stream_staging_span(s, destination, &destination_span);
        size_t n = source_span < destination_span ? source_span : destination_span;
        memmove(to, from, n);
        source += n; destination += n;
    }
    size_t retained = bytes-count;
    unsigned keep = 0;
    for (unsigned i=0; i<s->count; ++i) {
        if (retained) {
            if (s->length[i] > retained) s->length[i] = retained;
            retained -= s->length[i]; ++keep;
        } else {
            adaptive_input_cancel(s->queue, s->packet[i]);
            s->packet[i] = NULL; s->length[i] = 0;
        }
    }
    s->count = keep;
    s->look_used = retained;
    return true;
}

// Transfer ownership of the first lease to the caller without copying its
// payload. The caller fills its header and commits or cancels it exactly once.
// Only call after framing/codec decisions; this function does not validate them.
// The small lookahead remains here when there are no packet leases left.
static inline void *stream_staging_take(stream_staging_t *s, size_t *bytes) {
    *bytes = 0;
    if (!s->count) return NULL;
    void *packet = s->packet[0];
    *bytes = s->length[0];
    --s->count;
    for (unsigned i=0; i<s->count; ++i) {
        s->packet[i] = s->packet[i+1];
        s->length[i] = s->length[i+1];
    }
    s->packet[s->count] = NULL;
    s->length[s->count] = 0;
    return packet;
}
