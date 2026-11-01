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
    ogg_opus_timeline timeline;
    uint8_t *page;
    size_t size, capacity;
    bool ready;
    oopt_event event;
} ogg_page_input;

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
    memset(&s->event, 0, sizeof(s->event));
    oopt_reset(&s->timeline, generation);
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

/* The returned page is s->page[0..s->size), valid until ACK or reset.
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
    for (;;) {
        size_t target = 27;
        if (s->size >= 27) {
            target += s->page[26];
            if (s->size >= target) {
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
        if (target > s->capacity) {
            uint8_t *larger = OGG_PAGE_INPUT_REALLOC(s->page, target);
            if (!larger) return OPI_NO_MEMORY;
            s->page = larger;
            s->capacity = target;
        }
        size_t take = target - s->size;
        if (take > size - *used) take = size - *used;
        memcpy(s->page + s->size, data + *used, take);
        const uint8_t *fresh = s->page + s->size;
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
