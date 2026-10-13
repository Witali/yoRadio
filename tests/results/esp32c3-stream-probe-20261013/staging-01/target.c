#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
typedef int BaseType_t; typedef uint32_t TickType_t;
#define pdTRUE 1


typedef struct adaptive_input adaptive_input_t;
typedef struct {
    size_t packet_capacity;
    unsigned resident, minimum, target, occupied, limit;
    unsigned released;
} adaptive_input_stats_t;

// One producer, one consumer. Each acquired pointer is a lease: reclaim never
// touches WRITING, READY or READING slots. The object lives until task teardown.
adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity);
void adaptive_input_destroy(adaptive_input_t *input); // Quiescent callers only.
BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout);
BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet);
// Producer only: give up an uncommitted WRITING lease. Queued/READING pointers
// cannot be cancelled. The pointer is invalid after a successful cancellation.
bool adaptive_input_cancel(adaptive_input_t *input, void *packet);
void *adaptive_input_receive(adaptive_input_t *input, size_t *size,
                             TickType_t timeout);
bool adaptive_input_return(adaptive_input_t *input, void *packet);
bool adaptive_input_release_one(adaptive_input_t *input);
// Only the producer calls restore, between connections after old TLS closes.
// Does not change queued data or leases and never waits for consumers.
void adaptive_input_restore(adaptive_input_t *input);
// Producer only. Best-effort allocation of one absent slot, up to the current
// limit. Existing leases/queued bytes are untouched; allocation stays unlocked.
bool adaptive_input_restore_one(adaptive_input_t *input);
// Bound resident storage between minimum and configured target. Shrink idle
// excess slots immediately and busy excess slots on consumer return, keeping
// the earliest resident buffers. Real allocation-pressure reclamation can
// still free any idle slot above the minimum resident count.
// May overlap reclamation/consumer return and a producer allocation in flight.
void adaptive_input_set_limit(adaptive_input_t *input, unsigned slots);
adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input);


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

_Static_assert(sizeof(stream_staging_t)==64, "C3 staging state size");
bool init_window(stream_staging_t *s,adaptive_input_t *q) {return stream_staging_init(s,q,12,2048);}
size_t append_window(stream_staging_t *s,const uint8_t *data,size_t bytes) {return stream_staging_append(s,data,bytes);}
bool read_window(stream_staging_t *s,size_t offset,uint8_t *dest,size_t bytes) {return stream_staging_read(s,offset,dest,bytes);}
bool erase_window(stream_staging_t *s,size_t offset,size_t bytes) {return stream_staging_erase(s,offset,bytes);}
void cancel_window(stream_staging_t *s) {stream_staging_cancel(s);}
void *take_window(stream_staging_t *s,size_t *bytes) {return stream_staging_take(s,bytes);}
