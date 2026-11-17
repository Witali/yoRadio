#ifndef YORADIO_OGG_PAGE_INPUT_H
#define YORADIO_OGG_PAGE_INPUT_H

/* One owned encoded page, verified before any of its bytes reach a decoder.
 * Feed ORIGINAL input once. A ready page and its timeline event remain owned
 * until acknowledge; a LINK_END must be acknowledged only after real EOS drain
 * and decoder close. No original caller pointer is retained. A zero-byte feed
 * can finish a nil page. All state has one decoder-task owner.
 */
#include <stdlib.h>
#include "ogg_opus_timeline.h"

#ifndef OGG_PAGE_INPUT_REALLOC
#define OGG_PAGE_INPUT_REALLOC realloc
#endif
#ifndef OGG_PAGE_INPUT_FREE
#define OGG_PAGE_INPUT_FREE free
#endif

enum { OGG_PAGE_INPUT_MAX = 27 + 255 + 255 * 255 };
typedef enum {
    OPI_MORE = 0, OPI_PAGE = 1, OPI_FINISHED = 2,
    OPI_INVALID = -1, OPI_UNSUPPORTED = -2, OPI_UNALIGNED = -3,
    OPI_TRUNCATED = -4, OPI_LIMIT = -5, OPI_NO_MEMORY = -6
} ogg_page_input_status;

typedef struct {
    void *(*allocate)(size_t);
    void (*release)(void *);
} ogg_page_word_allocator;

typedef struct {
    ogg_opus_timeline timeline;
    uint8_t *page;
    size_t size, capacity;
    bool ready;
    oopt_event event;
    const ogg_page_word_allocator *word_allocator;
    volatile uint32_t *word_payload;
    size_t word_capacity;
    bool word_page;
} ogg_page_input;

static inline void opi_release_word_payload(ogg_page_input *s)
{
    if (s->word_payload) s->word_allocator->release((void *)s->word_payload);
    s->word_payload = NULL;
    s->word_capacity = 0;
    s->word_page = false;
}

/* Storage must initially be {0}. Reset releases the page, including after OOM
 * or incomplete input, and preserves the observer's monotonically unique ACK
 * tokens. It is also the final clear operation when the stream is abandoned.
 */
static inline void opi_reset(ogg_page_input *s, uint32_t generation)
{
    OGG_PAGE_INPUT_FREE(s->page);
    s->page = NULL;
    s->size = s->capacity = 0;
    s->ready = false;
    opi_release_word_payload(s);
    s->word_allocator = NULL;
    memset(&s->event, 0, sizeof(s->event));
    oopt_reset(&s->timeline, generation);
}

/* Select the optional word-capable payload store between pages. Keep the Ogg
 * header and lacing table byte-addressable. Its caller must read payload via
 * opi_copy_payload() when word_page is set. The allocator outlives the link.
 */
static inline bool opi_set_word_allocator(ogg_page_input *s,
                                         const ogg_page_word_allocator *allocator)
{
    if (s->ready || s->size || (allocator && (!allocator->allocate || !allocator->release)))
        return false;
    if (s->word_allocator == allocator) return true;
    opi_release_word_payload(s);
    s->word_allocator = allocator;
    if (allocator && s->capacity > 27u + 255u) {
        OGG_PAGE_INPUT_FREE(s->page);
        s->page = NULL;
        s->capacity = 0;
    }
    return true;
}

static inline bool opi_reserve_word_payload(ogg_page_input *s, size_t bytes)
{
    if (bytes <= s->word_capacity) return true;
    /* A new page owns no payload yet. Release the old capacity before growing
     * rather than copying it or holding two full pages at the same time. */
    opi_release_word_payload(s);
    size_t capacity = (bytes + 3u) & ~(size_t)3u;
    void *payload = s->word_allocator->allocate(capacity);
    if (!payload) return false;
    if ((uintptr_t)payload & 3u) {
        s->word_allocator->release(payload);
        return false;
    }
    s->word_payload = payload;
    s->word_capacity = capacity;
    return true;
}

static inline void opi_store_word_payload(volatile uint32_t *payload, size_t at,
                                         const uint8_t *source, size_t bytes)
{
    while (bytes) {
        unsigned byte = at & 3u;
        size_t word_index = at / 4u;
        uint32_t value = byte ? payload[word_index] : 0;
        do {
            value |= (uint32_t)*source++ << (8u * byte++);
            ++at;
            --bytes;
        } while (byte < 4u && bytes);
        payload[word_index] = value;
    }
}

static inline void opi_copy_payload(const ogg_page_input *s, size_t at,
                                    uint8_t *output, size_t bytes)
{
    if (!s->word_page) {
        memcpy(output, s->page + at, bytes);
        return;
    }
    at -= 27u + s->page[26];
    while (bytes) {
        unsigned byte = at & 3u;
        uint32_t value = s->word_payload[at / 4u] >> (8u * byte);
        do {
            *output++ = (uint8_t)value;
            value >>= 8;
            ++byte;
            ++at;
            --bytes;
        } while (byte < 4u && bytes);
    }
}

static inline bool opi_ack(ogg_page_input *s, uint32_t generation,
                           uint64_t token)
{
    if (!s->ready || !oopt_ack(&s->timeline, generation, token)) return false;
    s->ready = false;
    s->size = 0;
    memset(&s->event, 0, sizeof(s->event));
    return true;
}

/* Copy a slice of the complete verified encoding, including its header.
 * Word payloads are read only through aligned 32-bit accesses. */
static inline bool opi_copy_page(const ogg_page_input *s, size_t at,
                                 uint8_t *output, size_t bytes)
{
    if (!s->ready || at > s->size || bytes > s->size - at || (bytes && !output))
        return false;
    if (!bytes) return true;
    size_t header = 27u + s->page[26];
    if (at < header) {
        size_t count = header - at;
        if (count > bytes) count = bytes;
        if (count) memcpy(output, s->page + at, count);
        at += count;
        output += count;
        bytes -= count;
    }
    if (bytes) opi_copy_payload(s, at, output, bytes);
    return true;
}

/* Header consumers keep their own state after ACK. Retain the small header
 * allocation, so a large tag page cannot hold RAM across decoder creation. */
static inline void opi_release_idle_large_page(ogg_page_input *s)
{
    if (s->ready || s->size) return;
    if (s->capacity > 27u + 255u) {
        OGG_PAGE_INPUT_FREE(s->page);
        s->page = NULL;
        s->capacity = 0;
    }
    opi_release_word_payload(s);
}

static inline ogg_page_input_status opi_observe(ogg_page_input *s,
                                                const uint8_t *data, size_t size)
{
    size_t at = 0;
    for (;;) {
        size_t used = 0;
        oopt_event event;
        oopt_status status = oopt_feed(&s->timeline,
            size ? data + at : NULL, size - at, &used, &event);
        if (used > size - at) return OPI_INVALID;
        at += used;
        if (status < 0) return (ogg_page_input_status)status;
        if (status == OOPT_EVENT) {
            if (event.flags & OOPT_PAGE) {
                if (!event.crc_verified || at != size) return OPI_INVALID;
                s->event = event;
                s->ready = true;
                return OPI_PAGE;
            }
            /* Provisional bounds are intentionally never exposed to playback.
             * Continue until the complete page has passed its CRC/timeline.
             */
            if (event.flags != OOPT_PROVISIONAL_END ||
                !oopt_ack(&s->timeline, event.generation, event.token))
                return OPI_INVALID;
            continue;
        }
        return at == size && status == OOPT_MORE ? OPI_MORE : OPI_INVALID;
    }
}

/* The returned page is valid until ACK or reset. When word_page is set only
 * its header and lacing table are contiguous at s->page.
 * Allocation refusal leaves already consumed bytes intact and can be retried
 * with precisely the unconsumed suffix. Invalid pages never become ready.
 */
static inline ogg_page_input_status opi_feed(ogg_page_input *s,
    const uint8_t *data, size_t size, size_t *used)
{
    if (!used) return OPI_INVALID;
    *used = 0;
    if (s->ready) return OPI_PAGE;
    if (size && !data) return OPI_INVALID;
    if (s->timeline.fault) return (ogg_page_input_status)s->timeline.fault;
    if (!s->size) s->word_page = false;
    for (;;) {
        size_t target = 27;
        size_t payload_at = 0;
        if (s->size >= 27) {
            target += s->page[26];
            if (s->size >= target) {
                payload_at = target;
                for (size_t i = 27; i < 27u + s->page[26]; ++i)
                    target += s->page[i];
            }
        }
        if (target > OGG_PAGE_INPUT_MAX || s->size > target)
            return OPI_INVALID;
        if (s->size == target) {
            /* All zero-lace/zero-payload work must run even with no new bytes. */
            ogg_page_input_status status = opi_observe(s, NULL, 0);
            return status == OPI_MORE ? OPI_INVALID : status;
        }
        if (*used == size) return OPI_MORE;
        /* Small pages keep their inexpensive borrowed-packet path. Allocate
         * large payloads in word RAM before attempting a contiguous byte page. */
        if (payload_at && s->size == payload_at && target - payload_at >= 4096 &&
            s->word_allocator) {
            s->word_page = opi_reserve_word_payload(s, target - payload_at);
        }
        if (!s->word_page && target > s->capacity) {
            uint8_t *larger = OGG_PAGE_INPUT_REALLOC(s->page, target);
            if (!larger) return OPI_NO_MEMORY;
            s->page = larger;
            s->capacity = target;
        }
        size_t take = target - s->size;
        if (take > size - *used) take = size - *used;
        const uint8_t *fresh = data + *used;
        if (s->word_page) {
            opi_store_word_payload(s->word_payload, s->size - payload_at, fresh, take);
        } else {
            memcpy(s->page + s->size, fresh, take);
            fresh = s->page + s->size;
        }
        s->size += take;
        *used += take;
        ogg_page_input_status status = opi_observe(s, fresh, take);
        if (status != OPI_MORE) return status;
    }
}

static inline ogg_page_input_status opi_finish(ogg_page_input *s)
{
    if (s->ready) return OPI_PAGE;
    oopt_event event;
    oopt_status status = oopt_finish(&s->timeline, &event);
    return status == OOPT_FINISHED ? OPI_FINISHED :
           status < 0 ? (ogg_page_input_status)status : OPI_INVALID;
}

#endif
