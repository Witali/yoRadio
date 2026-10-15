#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdalign.h>
#include <stddef.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef int BaseType_t;
typedef uint32_t TickType_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(pthread_mutex_lock(p) == 0)
#define portEXIT_CRITICAL(p) assert(pthread_mutex_unlock(p) == 0)
#define pdTRUE 1
#define pdFALSE 0
#define portMAX_DELAY UINT32_MAX
typedef struct {
    pthread_mutex_t mutex;
    pthread_cond_t condition;
    bool signalled;
} *SemaphoreHandle_t;
static atomic_int fail_after = -1;
static atomic_uint live_allocations, slot_frees;
static void (*after_allocation)(void);
typedef union { max_align_t alignment; size_t size; } allocation_header_t;
static void *checked_calloc(size_t count, size_t size) {
    if (size && count > SIZE_MAX / size) return NULL;
    int remaining = atomic_load(&fail_after);
    if (remaining == 0) return NULL;
    if (remaining > 0) atomic_fetch_sub(&fail_after, 1);
    size_t bytes = count * size;
    if (bytes > SIZE_MAX - sizeof(allocation_header_t)) return NULL;
    allocation_header_t *header = calloc(1, sizeof(*header) + bytes);
    if (!header) return NULL;
    header->size = bytes;
    atomic_fetch_add(&live_allocations, 1);
    if (after_allocation) {
        void (*hook)(void) = after_allocation;
        after_allocation = NULL;
        hook();
    }
    return header + 1;
}
static void *checked_malloc(size_t bytes) { return checked_calloc(1, bytes); }
static void checked_free(void *pointer) {
    if (!pointer) return;
    allocation_header_t *header = (allocation_header_t *)pointer - 1;
    if (header->size == 2060) atomic_fetch_add(&slot_frees, 1);
    atomic_fetch_sub(&live_allocations, 1);
    free(header);
}
static SemaphoreHandle_t xSemaphoreCreateBinary(void) {
    SemaphoreHandle_t s = checked_calloc(1, sizeof(*s));
    if (!s) return NULL;
    assert(!pthread_mutex_init(&s->mutex, NULL));
    assert(!pthread_cond_init(&s->condition, NULL));
    return s;
}
static void vSemaphoreDelete(SemaphoreHandle_t s) {
    assert(!pthread_cond_destroy(&s->condition));
    assert(!pthread_mutex_destroy(&s->mutex));
    checked_free(s);
}
static BaseType_t xSemaphoreGive(SemaphoreHandle_t s) {
    assert(!pthread_mutex_lock(&s->mutex));
    s->signalled = true;
    assert(!pthread_cond_signal(&s->condition));
    assert(!pthread_mutex_unlock(&s->mutex));
    return pdTRUE;
}
static BaseType_t xSemaphoreTake(SemaphoreHandle_t s, TickType_t timeout) {
    struct timespec until;
    assert(!clock_gettime(CLOCK_REALTIME, &until));
    until.tv_sec += timeout / 1000;
    until.tv_nsec += (timeout % 1000) * 1000000L;
    if (until.tv_nsec >= 1000000000L) { ++until.tv_sec; until.tv_nsec -= 1000000000L; }
    assert(!pthread_mutex_lock(&s->mutex));
    int error = 0;
    while (!s->signalled && !error) {
        error = timeout == portMAX_DELAY ? pthread_cond_wait(&s->condition, &s->mutex)
            : pthread_cond_timedwait(&s->condition, &s->mutex, &until);
    }
    assert(!error || error == ETIMEDOUT);
    bool ready = s->signalled;
    s->signalled = false;
    assert(!pthread_mutex_unlock(&s->mutex));
    return ready ? pdTRUE : pdFALSE;
}
static uint32_t tick_offset;
static TickType_t xTaskGetTickCount(void) {
    struct timespec now;
    assert(!clock_gettime(CLOCK_MONOTONIC, &now));
    return (TickType_t)((uint64_t)now.tv_sec * 1000 + now.tv_nsec / 1000000) + tick_offset;
}



typedef struct adaptive_input adaptive_input_t;
typedef struct {
    size_t packet_capacity;
    unsigned resident, minimum, target, occupied, limit;
    unsigned released;
    // Data slots only; unpublished WRITING/control storage is not ready audio.
    // Byte counts include the caller's packet header. READING counts the whole
    // retained packet, not the decoder's unconsumed suffix.
    unsigned ready, reading, writing;
    size_t ready_bytes, reading_bytes;
} adaptive_input_stats_t;

// One producer, one consumer. Each acquired pointer is a lease: reclaim never
// touches WRITING, READY or READING slots. The object lives until task teardown.
adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity);
void adaptive_input_destroy(adaptive_input_t *input); // Quiescent callers only.
BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout);
BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet);
// Publish a nonempty prefix of the acquired lease. Never extend its requested
// size. Failure preserves the WRITING lease for correction or cancellation.
BaseType_t adaptive_input_commit_size(adaptive_input_t *input, void *packet,
                                      size_t used);
// Single producer only: temporarily take the partial READY data tail back as
// a full-capacity WRITING lease. Never take the sole queued node, a control
// tail, a full packet or a READING lease. Returns its previous committed size.
// Copy outside the lock, then republish before any other producer commit or
// blocking operation. Preserve the original prefix on rejection/cancellation.
BaseType_t adaptive_input_reopen_tail(adaptive_input_t *input, void **packet,
                                      size_t *used);
// Optional caller-owned small control storage, attached once before use.
// It joins the same FIFO, independently of the data slots. Never reclaimed,
// counted as audio prefill, or freed by this queue. Storage must outlive input.
// Commit/cancel/receive/return have the same lease rules as normal packets.
bool adaptive_input_attach_control(adaptive_input_t *input, void *storage,
                                    size_t capacity);
BaseType_t adaptive_input_acquire_control(adaptive_input_t *input, void **packet,
                                          size_t size, TickType_t timeout);
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

#define calloc checked_calloc
#define malloc checked_malloc
#define free checked_free


enum { INPUT_MAX_SLOTS = 16, CONTROL_SLOT = INPUT_MAX_SLOTS,
       NO_SLOT = CONTROL_SLOT + 1 };
typedef enum { ABSENT, ALLOCATING, IDLE, WRITING, READY, READING } slot_state_t;
typedef struct {
    void *data;
    size_t size;
    slot_state_t state;
    unsigned next;
} input_slot_t;

struct adaptive_input {
    portMUX_TYPE lock;
    SemaphoreHandle_t data_ready, space_ready;
    size_t packet_capacity;
    unsigned target, minimum, resident, released, limit;
    unsigned head, tail;
    input_slot_t slots[INPUT_MAX_SLOTS];
    input_slot_t control;
    size_t control_capacity;
};

static input_slot_t *input_slot(adaptive_input_t *input, unsigned index) {
    return index == CONTROL_SLOT ? &input->control : &input->slots[index];
}

adaptive_input_stats_t adaptive_input_stats(adaptive_input_t *input) {
    adaptive_input_stats_t result = {0};
    if (!input) return result;
    portENTER_CRITICAL(&input->lock);
    result.packet_capacity = input->packet_capacity;
    result.resident = input->resident;
    result.minimum = input->minimum;
    result.target = input->target;
    result.limit = input->limit;
    result.released = input->released;
    for (unsigned i = 0; i < input->target; ++i) {
        slot_state_t state = input->slots[i].state;
        if (state == WRITING || state == READY || state == READING)
            ++result.occupied;
        if (state == READY) {
            ++result.ready;
            result.ready_bytes += input->slots[i].size;
        } else if (state == READING) {
            ++result.reading;
            result.reading_bytes += input->slots[i].size;
        } else if (state == WRITING) ++result.writing;
    }
    portEXIT_CRITICAL(&input->lock);
    return result;
}

bool adaptive_input_restore_one(adaptive_input_t *input) {
    if (!input) return false;
    for (unsigned i = 0; i < input->target; ++i) {
        portENTER_CRITICAL(&input->lock);
        bool allocate = input->resident < input->limit &&
                        input->slots[i].state == ABSENT;
        if (allocate) input->slots[i].state = ALLOCATING;
        portEXIT_CRITICAL(&input->lock);
        if (!allocate) continue;
        void *data = malloc(input->packet_capacity);
        portENTER_CRITICAL(&input->lock);
        // The policy can shrink while malloc runs. Never publish a new slot
        // beyond that limit, even if allocation itself succeeded.
        bool publish = data && input->resident < input->limit;
        input->slots[i].data = publish ? data : NULL;
        input->slots[i].state = publish ? IDLE : ABSENT;
        if (publish) ++input->resident;
        portEXIT_CRITICAL(&input->lock);
        if (publish) xSemaphoreGive(input->space_ready);
        else free(data);
        return publish;
    }
    return false;
}

void adaptive_input_restore(adaptive_input_t *input) {
    if (!input) return;
    // Bound work even if TLS keeps reclaiming slots during this refill.
    for (unsigned attempt = 0; attempt < input->target; ++attempt) {
        if (!adaptive_input_restore_one(input)) break;
    }
}

// Caller holds the queue lock. Keep the first limit resident buffers stable
// through ordinary stream shutdown. Busy later buffers retire on return.
// Emergency reclamation can leave holes, so rank resident pointers instead
// of assuming that every lower slot index still contains an allocation.
static bool should_retire_slot(const adaptive_input_t *input, unsigned index) {
    if (input->resident <= input->limit) return false;
    unsigned earlier = 0;
    for (unsigned i = 0; i < index; ++i)
        if (input->slots[i].data) ++earlier;
    return earlier >= input->limit;
}

void adaptive_input_set_limit(adaptive_input_t *input, unsigned slots) {
    if (!input) return;
    portENTER_CRITICAL(&input->lock);
    if (slots < input->minimum) slots = input->minimum;
    if (slots > input->target) slots = input->target;
    input->limit = slots;
    portEXIT_CRITICAL(&input->lock);
    for (unsigned i = input->target; i > 0; --i) {
        void *data = NULL;
        portENTER_CRITICAL(&input->lock);
        input_slot_t *slot = &input->slots[i - 1];
        if (slot->state == IDLE && should_retire_slot(input, i - 1)) {
            data = slot->data;
            slot->data = NULL;
            slot->state = ABSENT;
            --input->resident;
            ++input->released;
        }
        portEXIT_CRITICAL(&input->lock);
        free(data);
    }
}

adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity) {
    if (!packet_capacity) return NULL;
    // Round up so the legacy 8000-byte setting still provides at least that
    // much allocated packet storage; never silently lower the configured floor.
    size_t target = budget / packet_capacity + (budget % packet_capacity != 0);
    if (target < 2 || target > INPUT_MAX_SLOTS) return NULL;
    adaptive_input_t *input = calloc(1, sizeof(*input));
    if (!input) return NULL;
    input->lock = (portMUX_TYPE)portMUX_INITIALIZER_UNLOCKED;
    input->packet_capacity = packet_capacity;
    input->target = (unsigned)target;
    input->limit = input->target;
    // Round the minimum up, without overflowing on a malformed size argument.
    size_t minimum = minimum_bytes / packet_capacity +
                     (minimum_bytes % packet_capacity != 0);
    if (minimum < 2) minimum = 2;
    if (minimum > input->target) minimum = input->target;
    input->minimum = (unsigned)minimum;
    input->head = input->tail = NO_SLOT;
    input->data_ready = xSemaphoreCreateBinary();
    input->space_ready = xSemaphoreCreateBinary();
    if (!input->data_ready || !input->space_ready) {
        adaptive_input_destroy(input);
        return NULL;
    }
    adaptive_input_restore(input);
    if (input->resident < input->minimum) {
        adaptive_input_destroy(input);
        return NULL;
    }
    return input;
}

void adaptive_input_destroy(adaptive_input_t *input) {
    if (!input) return;
    for (unsigned i = 0; i < input->target; ++i) free(input->slots[i].data);
    if (input->data_ready) vSemaphoreDelete(input->data_ready);
    if (input->space_ready) vSemaphoreDelete(input->space_ready);
    free(input);
}

static bool wait_event(SemaphoreHandle_t event, TickType_t start,
                        TickType_t timeout) {
    TickType_t elapsed = xTaskGetTickCount() - start;
    if (timeout != portMAX_DELAY && elapsed >= timeout) return false;
    TickType_t remaining = timeout == portMAX_DELAY ? timeout : timeout - elapsed;
    return xSemaphoreTake(event, remaining) == pdTRUE;
}

BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout) {
    if (packet) *packet = NULL;
    if (!input || !packet || !size || size > input->packet_capacity) return pdFALSE;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        for (unsigned i = 0; i < input->target; ++i) {
            input_slot_t *slot = &input->slots[i];
            if (slot->state != IDLE) continue;
            slot->state = WRITING;
            slot->size = size;
            *packet = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return pdTRUE;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->space_ready, start, timeout));
    return pdFALSE;
}

static BaseType_t commit_packet(adaptive_input_t *input, void *packet,
                                size_t used, bool trim) {
    if (!input || !packet) return pdFALSE;
    portENTER_CRITICAL(&input->lock);
    for (unsigned scan = 0; scan <= input->target; ++scan) {
        unsigned i = scan == input->target ? CONTROL_SLOT : scan;
        input_slot_t *slot = input_slot(input, i);
        if (slot->data != packet || slot->state != WRITING) continue;
        if (trim) {
            if (!used || used > slot->size) {
                portEXIT_CRITICAL(&input->lock);
                return pdFALSE;
            }
            slot->size = used;
        }
        slot->state = READY;
        slot->next = NO_SLOT;
        if (input->tail != NO_SLOT) input_slot(input, input->tail)->next = i;
        else input->head = i;
        input->tail = i;
        portEXIT_CRITICAL(&input->lock);
        xSemaphoreGive(input->data_ready);
        return pdTRUE;
    }
    portEXIT_CRITICAL(&input->lock);
    return pdFALSE;
}

BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet) {
    return commit_packet(input, packet, 0, false);
}

BaseType_t adaptive_input_commit_size(adaptive_input_t *input, void *packet,
                                      size_t used) {
    return commit_packet(input, packet, used, true);
}

BaseType_t adaptive_input_reopen_tail(adaptive_input_t *input, void **packet,
                                      size_t *used) {
    if (packet) *packet = NULL;
    if (used) *used = 0;
    if (!input || !packet || !used) return pdFALSE;
    portENTER_CRITICAL(&input->lock);
    unsigned tail = input->tail;
    if (tail >= input->target || input->head == tail ||
        input->slots[tail].state != READY ||
        input->slots[tail].size == input->packet_capacity) {
        portEXIT_CRITICAL(&input->lock);
        return pdFALSE;
    }
    unsigned previous = input->head;
    // At most target data nodes and one control node; no heap work or copying
    // under the lock. The single producer will reinsert this same FIFO tail.
    while (input_slot(input, previous)->next != tail)
        previous = input_slot(input, previous)->next;
    input_slot(input, previous)->next = NO_SLOT;
    input->tail = previous;
    input_slot_t *slot = &input->slots[tail];
    *packet = slot->data;
    *used = slot->size;
    slot->size = input->packet_capacity;
    slot->state = WRITING;
    portEXIT_CRITICAL(&input->lock);
    return pdTRUE;
}

bool adaptive_input_attach_control(adaptive_input_t *input, void *storage,
                                    size_t capacity) {
    if (!input || !storage || !capacity) return false;
    portENTER_CRITICAL(&input->lock);
    bool available = input->control.data == NULL;
    for (unsigned i = 0; i < input->target; ++i)
        if (input->slots[i].data == storage) available = false;
    if (available) {
        input->control = (input_slot_t){.data=storage, .state=IDLE, .next=NO_SLOT};
        input->control_capacity = capacity;
    }
    portEXIT_CRITICAL(&input->lock);
    return available;
}

BaseType_t adaptive_input_acquire_control(adaptive_input_t *input, void **packet,
                                          size_t size, TickType_t timeout) {
    if (packet) *packet = NULL;
    if (!input || !packet || !size) return pdFALSE;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        if (size > input->control_capacity) {
            portEXIT_CRITICAL(&input->lock);
            return pdFALSE;
        }
        input_slot_t *slot = &input->control;
        if (slot->state == IDLE) {
            slot->state = WRITING;
            slot->size = size;
            *packet = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return pdTRUE;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->space_ready, start, timeout));
    return pdFALSE;
}

void *adaptive_input_receive(adaptive_input_t *input, size_t *size,
                             TickType_t timeout) {
    if (size) *size = 0;
    if (!input || !size) return NULL;
    TickType_t start = xTaskGetTickCount();
    do {
        portENTER_CRITICAL(&input->lock);
        if (input->head != NO_SLOT) {
            input_slot_t *slot = input_slot(input, input->head);
            input->head = slot->next;
            if (input->head == NO_SLOT) input->tail = NO_SLOT;
            slot->state = READING;
            *size = slot->size;
            void *data = slot->data;
            portEXIT_CRITICAL(&input->lock);
            return data;
        }
        portEXIT_CRITICAL(&input->lock);
    } while (wait_event(input->data_ready, start, timeout));
    return NULL;
}

static bool release_lease(adaptive_input_t *input, void *packet, slot_state_t expected) {
    if (!input || !packet) return false;
    portENTER_CRITICAL(&input->lock);
    for (unsigned scan = 0; scan <= input->target; ++scan) {
        unsigned i = scan == input->target ? CONTROL_SLOT : scan;
        input_slot_t *slot = input_slot(input, i);
        if (slot->data != packet || slot->state != expected) continue;
        bool release = i != CONTROL_SLOT && should_retire_slot(input, i);
        if (release) {
            slot->data = NULL;
            --input->resident;
            ++input->released;
        }
        slot->state = release ? ABSENT : IDLE;
        slot->size = 0;
        portEXIT_CRITICAL(&input->lock);
        if (release) free(packet);
        xSemaphoreGive(input->space_ready);
        return true;
    }
    portEXIT_CRITICAL(&input->lock);
    return false;
}

bool adaptive_input_return(adaptive_input_t *input, void *packet) {
    return release_lease(input, packet, READING);
}

bool adaptive_input_cancel(adaptive_input_t *input, void *packet) {
    return release_lease(input, packet, WRITING);
}

bool adaptive_input_release_one(adaptive_input_t *input) {
    if (!input) return false;
    void *data = NULL;
    portENTER_CRITICAL(&input->lock);
    if (input->resident > input->minimum) {
        for (unsigned i = input->target; i > 0; --i) {
            input_slot_t *slot = &input->slots[i - 1];
            if (slot->state != IDLE) continue;
            data = slot->data;
            slot->data = NULL;
            slot->state = ABSENT;
            --input->resident;
            ++input->released;
            break;
        }
    }
    portEXIT_CRITICAL(&input->lock);
    // Never call the heap allocator while holding the queue's spinlock.
    bool released = data != NULL;
    free(data);
    return released;
}

#undef calloc
#undef malloc
#undef free

#include "stream_confirm.h"
#include "audio_completion.h"


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


#define STREAM_CHUNK_SIZE 2048
#define pdMS_TO_TICKS(x) (x)
typedef enum {NATIVE_CODEC_AUTO,NATIVE_CODEC_MP3,NATIVE_CODEC_AAC,
              NATIVE_CODEC_FLAC,NATIVE_CODEC_OGG} native_codec_t;
typedef struct {uint32_t generation; native_codec_t codec; uint16_t data_size;
                uint8_t end_of_stream; uint8_t data[];} encoded_packet_t;
static adaptive_input_t *s_encoded;
static atomic_uint s_generation;
#define encoded_acquire adaptive_input_acquire
static BaseType_t encoded_commit(adaptive_input_t *input, encoded_packet_t *packet) {
    return adaptive_input_commit_size(input,packet,sizeof(*packet)+packet->data_size);
}
static bool send_encoded(uint32_t gen,native_codec_t codec,const uint8_t *data,size_t size,uint8_t eos) {
    encoded_packet_t *packet=NULL;
    // Any attempt to route around the dedicated control node while the
    // candidate owns all slots must fail this test, never hang indefinitely.
    assert(adaptive_input_acquire(s_encoded,(void **)&packet,sizeof(*packet)+size,0));
    packet->generation=gen;packet->codec=codec;packet->data_size=size;packet->end_of_stream=eos;
    if(size)memcpy(packet->data,data,size);
    return adaptive_input_commit(s_encoded,packet)==pdTRUE;
}
#include "stream_encoded_router.h"

enum {CONTROL_PAYLOAD=128,MAX_BYTES=8202};
static alignas(encoded_packet_t) uint8_t control[sizeof(encoded_packet_t)+CONTROL_PAYLOAD];
static uint8_t input[MAX_BYTES],expected[MAX_BYTES],captured[MAX_BYTES];
static native_codec_t kinds[MAX_BYTES];
static size_t captured_size,markers[4];
static unsigned marker_count,packets;
static atomic_bool finished;
static bool cancel_first;
static void *consume(void *unused) {
    (void)unused;
    while (true) {
        size_t size;
        encoded_packet_t *p=adaptive_input_receive(s_encoded,&size,10);
        if(!p) {if(atomic_load(&finished))break;else continue;}
        assert((void *)p==control && p->generation==42);
        assert(p->data_size<=CONTROL_PAYLOAD && size<=sizeof(control));
        ++packets;
        if(p->end_of_stream) {
            assert(p->end_of_stream==AUDIO_DRAIN_CODEC && !p->data_size && marker_count<4);
            markers[marker_count++]=captured_size;
        } else {
            assert(captured_size+p->data_size<=sizeof(captured));
            memcpy(captured+captured_size,p->data,p->data_size);
            for(unsigned i=0;i<p->data_size;++i)kinds[captured_size+i]=p->codec;
            captured_size+=p->data_size;
        }
        if(cancel_first && packets==1) atomic_store(&s_generation,43);
        assert(adaptive_input_return(s_encoded,p));
    }
    return NULL;
}
static size_t add_frame(size_t offset,const uint8_t *frame,size_t n) {
    memcpy(input+offset,frame,n);memcpy(expected+offset,frame,n);return offset+n;
}
int main(void) {
    uint8_t mp3[417];memset(mp3,0x55,sizeof(mp3));memcpy(mp3,"\xff\xfb\x90\0",4);
    uint8_t aac[12]={0xff,0xf1,0x4c,0x80,1,0x9f,0xfc,1,2,3,4,5};
    size_t length=0;
    for(unsigned i=0;i<9;++i)length=add_frame(length,mp3,sizeof(mp3));
    size_t to_aac=length;
    for(unsigned i=0;i<330;++i)length=add_frame(length,aac,sizeof(aac));
    size_t to_mp3=length;
    length=add_frame(length,mp3,sizeof(mp3));
    assert(length>3*STREAM_CHUNK_SIZE && length<sizeof(input));
    const size_t chunks[]={1,7,2048};
    for(unsigned cancelled=0;cancelled<2;++cancelled)for(unsigned chunk=0;chunk<3;++chunk) {
        size_t capacity=sizeof(encoded_packet_t)+STREAM_CHUNK_SIZE;
        s_encoded=adaptive_input_create(4*capacity,4*capacity,capacity);assert(s_encoded);
        assert(adaptive_input_attach_control(s_encoded,control,sizeof(control)));
        stream_staging_t storage={0};
        assert(stream_staging_init(&storage,s_encoded,sizeof(encoded_packet_t),STREAM_CHUNK_SIZE));
        assert(stream_staging_append(&storage,input,length)==length);
        assert(adaptive_input_stats(s_encoded).occupied==4);
        atomic_store(&fail_after,0);
        captured_size=marker_count=packets=0;cancel_first=cancelled;
        atomic_store(&finished,false);atomic_store(&s_generation,42);stream_route_reset();
        native_codec_t codec=NATIVE_CODEC_MP3;
        stream_route_context_t route={.generation=42,.codec=&codec,.control_payload_bytes=CONTROL_PAYLOAD};
        pthread_t thread;assert(!pthread_create(&thread,NULL,consume,NULL));
        bool ok=true;
        for(size_t offset=0;offset<length && ok;) {
            size_t available;uint8_t *span=stream_staging_span(&storage,offset,&available);
            if(available>chunks[chunk])available=chunks[chunk];
            ok=stream_route_feed(&route,span,available);
            offset+=available;
        }
        if(ok)ok=stream_route_flush(&route);
        if(!ok)stream_route_cancel(&route);
        stream_staging_cancel(&storage); // Consumer still owns only its copied control fragment.
        atomic_store(&finished,true);assert(!pthread_join(thread,NULL));
        assert(!route.packet && !adaptive_input_stats(s_encoded).occupied);
        if(cancelled) {
            assert(!ok && captured_size<=CONTROL_PAYLOAD && !marker_count);
        } else {
            assert(ok && captured_size==length && !memcmp(captured,expected,length));
            assert(marker_count==2 && markers[0]==to_aac && markers[1]==to_mp3);
            assert(stream_route_complete(codec));
            for(size_t i=0;i<length;++i)assert(kinds[i]==(i>=to_aac && i<to_mp3?NATIVE_CODEC_AAC:NATIVE_CODEC_MP3));
        }
        adaptive_input_destroy(s_encoded);assert(!atomic_load(&live_allocations));
        atomic_store(&fail_after,-1);
    }
    puts("PASS staging router: four held data slots, independent 128-byte fragments, MP3/AAC/MP3 ordered drain markers, concurrent consumer cancellation, exact bytes, chunks 1/7/2048; ASan/UBSan");
}
