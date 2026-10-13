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
} adaptive_input_stats_t;

// One producer, one consumer. Each acquired pointer is a lease: reclaim never
// touches WRITING, READY or READING slots. The object lives until task teardown.
adaptive_input_t *adaptive_input_create(size_t budget, size_t minimum_bytes,
                                        size_t packet_capacity);
void adaptive_input_destroy(adaptive_input_t *input); // Quiescent callers only.
BaseType_t adaptive_input_acquire(adaptive_input_t *input, void **packet,
                                  size_t size, TickType_t timeout);
BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet);
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

BaseType_t adaptive_input_commit(adaptive_input_t *input, void *packet) {
    if (!input || !packet) return pdFALSE;
    portENTER_CRITICAL(&input->lock);
    for (unsigned scan = 0; scan <= input->target; ++scan) {
        unsigned i = scan == input->target ? CONTROL_SLOT : scan;
        input_slot_t *slot = input_slot(input, i);
        if (slot->data != packet || slot->state != WRITING) continue;
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

#include "stream_probe.h"
#include "audio_completion.h"
#define CONFIG_YORADIO_FRAME_ROUTER 1
#define CONFIG_YORADIO_STREAM_CONFIRM 1
#define STREAM_CHUNK_SIZE 2048
#define pdMS_TO_TICKS(x) (x)
typedef enum {NATIVE_CODEC_AUTO,NATIVE_CODEC_MP3,NATIVE_CODEC_AAC,
              NATIVE_CODEC_FLAC,NATIVE_CODEC_OGG} native_codec_t;
typedef struct {uint32_t generation;native_codec_t codec;uint16_t data_size;
                uint8_t end_of_stream;uint8_t data[];} encoded_packet_t;
static adaptive_input_t *s_encoded;
static atomic_uint s_generation;
static int64_t clock_offset;
#define encoded_acquire adaptive_input_acquire
static atomic_uint consumed_data_packets;
static unsigned committed_data_packets, provisional_updates;
static atomic_bool decoder_metadata_published;
static BaseType_t encoded_commit(adaptive_input_t *input, void *packet) {
    bool data=((encoded_packet_t *)packet)->data_size != 0;
    BaseType_t result=adaptive_input_commit(input,packet);
    if (result==pdTRUE && data) {
        unsigned expected=++committed_data_packets;
        // Force the valid scheduling order that exposed the hardware race,
        // including a one-frame file published only at EOF.
        while (atomic_load(&consumed_data_packets)<expected) sched_yield();
    }
    return result;
}
static int64_t esp_timer_get_time(void) {return (int64_t)xTaskGetTickCount()*1000+clock_offset;}
static void vTaskDelay(unsigned ticks) {struct timespec delay={ticks/1000,(ticks%1000)*1000000L};nanosleep(&delay,NULL);}
static const char *codec_name(native_codec_t codec) {(void)codec;return "codec";}
static void state_set_audio(unsigned generation,bool playing,const char *name) {
    assert(generation==42 && playing && name);
    assert(!atomic_load(&decoder_metadata_published));
    ++provisional_updates;
}
static bool send_encoded(uint32_t generation, native_codec_t codec,
                         const uint8_t *data, size_t size, uint8_t eos) {
    size_t packet_size = sizeof(encoded_packet_t) + size;
    encoded_packet_t *packet = NULL;
    while (encoded_acquire(s_encoded, (void **)&packet, packet_size,
                                  pdMS_TO_TICKS(250)) != pdTRUE) {
        // A slow decoder must apply TCP backpressure, not terminate the
        // station. Short waits still let a station change cancel promptly.
        if (atomic_load(&s_generation) != generation) return false;
    }
    packet->generation = generation;
    packet->codec = codec;
    packet->data_size = (uint16_t)size;
    packet->end_of_stream = eos;
    if (size) memcpy(packet->data, data, size);
    return encoded_commit(s_encoded, packet) == pdTRUE;
}

#ifdef CONFIG_YORADIO_FRAME_ROUTER
#include "stream_encoded_router.h"
#endif
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
#include "stream_start.h"
#endif

static inline void stream_transport_reset(void) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    stream_start_abort();
#endif
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    stream_route_reset();
#endif
}

static inline bool stream_initial_pending(native_codec_t codec, bool first) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    return first && stream_start_eligible(codec);
#else
    (void)first;
    return codec == NATIVE_CODEC_AUTO;
#endif
}

static bool send_stream_audio(uint32_t generation, native_codec_t *codec,
                              const uint8_t *data, size_t size,
                              bool *first_chunk, stream_probe_t *probe) {
    if (!size) return true;
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    stream_route_context_t route = {.generation = generation, .codec = codec};
#endif
    if (*first_chunk) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
        if (stream_start_eligible(*codec)) {
            size_t consumed;
            stream_confirm_result_t result=stream_start_feed(generation,codec,data,size,&consumed,false);
            if (result==STREAM_CONFIRM_MORE) return true;
            stream_start_abort();
            if (result!=STREAM_CONFIRM_READY) {probe->result=STREAM_PROBE_INVALID;return false;}
            data+=consumed;size-=consumed;
            *first_chunk = false; // stream_start_publish already set the provisional status.
        } else
#endif
        if (*codec == NATIVE_CODEC_AUTO) {
            size_t consumed = 0;
            switch (stream_probe_feed(probe, data, size, &consumed)) {
                case STREAM_PROBE_MORE: return true;
                case STREAM_PROBE_MP3: *codec = NATIVE_CODEC_MP3; break;
                case STREAM_PROBE_AAC: *codec = NATIVE_CODEC_AAC; break;
                case STREAM_PROBE_FLAC: *codec = NATIVE_CODEC_FLAC; break;
                case STREAM_PROBE_OGG: *codec = NATIVE_CODEC_OGG; break;
                default: return false;
            }
            state_set_audio(generation, true, codec_name(*codec));
            *first_chunk = false;
            // Replay the assembled header exactly once, before this read's tail.
#ifdef CONFIG_YORADIO_FRAME_ROUTER
            if (!stream_route_feed(&route, probe->header, probe->used))
#else
            if (!send_encoded(generation, *codec, probe->header, probe->used, false))
#endif
                return false;
            data += consumed;
            size -= consumed;
        }
        if (*first_chunk) state_set_audio(generation, true, codec_name(*codec));
        *first_chunk = false;
    }
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    return stream_route_feed(&route, data, size) && stream_route_flush(&route);
#else
    return !size || send_encoded(generation, *codec, data, size, false);
#endif
}

static inline uint8_t finish_stream_audio(uint32_t generation, native_codec_t *codec,
        bool *first_chunk, uint8_t reason) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    if (*first_chunk && stream_start_eligible(*codec) && reason==AUDIO_END_EOF) {
        // EOF rescan can discard the incomplete candidate. Preserve its
        // presence before finalization so truncation is not reported as empty.
        bool incomplete=s_stream_start.skip || stream_staging_size(&s_stream_start.window);
        size_t consumed;
        stream_confirm_result_t result=stream_start_feed(generation,codec,NULL,0,&consumed,true);
        if (result==STREAM_CONFIRM_READY) {
            *first_chunk=false;
        } else {
            reason=incomplete || s_stream_start.skip || stream_staging_size(&s_stream_start.window)
                ? AUDIO_END_FRAME_TRUNCATED : AUDIO_END_FORMAT_UNKNOWN;
        }
    }
    stream_start_abort();
#else
    (void)generation;(void)first_chunk;
#endif
    if (*codec==NATIVE_CODEC_AUTO &&
        (reason==AUDIO_END_EOF || reason==AUDIO_END_BUFFER_STALLED)) reason=AUDIO_END_FORMAT_UNKNOWN;
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    reason=stream_route_end(*codec,reason);
#endif
    return reason;
}



static uint8_t capture[1024*1024];
static size_t captured;
static unsigned terminal,drains,control_packets;
static void *consume(void *unused) {
    (void)unused;
    while (true) {
        size_t size;encoded_packet_t *p=adaptive_input_receive(s_encoded,&size,5000);assert(p);
        if((void *)p==s_start_control) ++control_packets;
        assert(size>=sizeof(*p) && p->data_size<=size-sizeof(*p));
        assert(captured+p->data_size<=sizeof(capture));
        if(p->data_size)memcpy(capture+captured,p->data,p->data_size);
        captured+=p->data_size;
        if(p->data_size) {
            atomic_store(&decoder_metadata_published,true);
            atomic_fetch_add(&consumed_data_packets,1);
        }
        bool end=audio_completion_is_terminal(p->end_of_stream);
        if(end)terminal=p->end_of_stream;
        if(p->end_of_stream==AUDIO_DRAIN_CODEC)++drains;
        assert(adaptive_input_return(s_encoded,p));
        if(end)return NULL;
    }
}
static void begin(void) {
    clock_offset=0;captured=terminal=drains=control_packets=0;atomic_store(&s_generation,42);
    committed_data_packets=provisional_updates=0;
    atomic_store(&consumed_data_packets,0);atomic_store(&decoder_metadata_published,false);
    size_t capacity=sizeof(encoded_packet_t)+STREAM_CHUNK_SIZE;
    s_encoded=adaptive_input_create(4*capacity,4*capacity,capacity);assert(s_encoded);
    s_start_control_attached=false;stream_transport_reset();
    atomic_store(&fail_after,0);
}
static void finish(void) {
    assert(!s_stream_start.active && !adaptive_input_stats(s_encoded).occupied);
    adaptive_input_destroy(s_encoded);assert(!atomic_load(&live_allocations));
    atomic_store(&fail_after,-1);
}
static void run_case(const uint8_t *input,size_t bytes,const uint8_t *expected,
        size_t expected_bytes,unsigned expected_end,size_t chunk,native_codec_t initial) {
    begin();pthread_t thread;assert(!pthread_create(&thread,NULL,consume,NULL));
    native_codec_t codec=initial;bool first=true;stream_probe_t probe={0};
    uint8_t end=AUDIO_END_EOF;
    for(size_t pos=0;pos<bytes;) {
        size_t n=bytes-pos;if(n>chunk)n=chunk;
        if(!send_stream_audio(42,&codec,input+pos,n,&first,&probe)) {end=AUDIO_END_BUFFER_STALLED;break;}
        pos+=n;
    }
    end=finish_stream_audio(42,&codec,&first,end);
    assert(send_encoded(42,codec,NULL,0,end));assert(!pthread_join(thread,NULL));
    if(terminal!=expected_end || captured!=expected_bytes)
        fprintf(stderr,"input=%zu chunk=%zu initial=%u terminal=%u expected=%u bytes=%zu expected_bytes=%zu\n",
                bytes,chunk,initial,terminal,expected_end,captured,expected_bytes);
    assert(terminal==expected_end && captured==expected_bytes);
    assert(provisional_updates==(expected_bytes ? 1u : 0u));
    if(expected_bytes)assert(!memcmp(capture,expected,expected_bytes));
    finish();
}
int main(int argc,char **argv) {
    const size_t chunks[]={1,7,2048};
    if(argc==3 || argc==4) {
        FILE *file=fopen(argv[1],"rb");assert(file);assert(!fseek(file,0,SEEK_END));
        long size=ftell(file);assert(size>0);rewind(file);uint8_t *data=malloc(size);assert(data);
        assert(fread(data,1,size,file)==(size_t)size);fclose(file);
        size_t discard=strtoul(argv[2],NULL,10);assert(discard<(size_t)size);
        for(unsigned i=0;i<3;++i) {
            run_case(data,size,data+discard,size-discard,AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
            if(argc==4) {
                assert(!strcmp(argv[3],"require-control") && control_packets);
                printf("CONTROL chunk=%zu packets=%u\n",chunks[i],control_packets);
            }
        }
        free(data);puts("PASS startup corpus: exact replay and clean EOF, chunks 1/7/2048");return 0;
    }
    assert(argc==1);
    uint8_t mp3[417];memset(mp3,0x55,sizeof(mp3));memcpy(mp3,"\xff\xfb\x90\0",4);
    uint8_t aac[12]={0xff,0xf1,0x4c,0x80,1,0x9f,0xfc,1,2,3,4,5};
    uint8_t mixed[441];memcpy(mixed,mp3,417);memcpy(mixed+417,aac,12);memcpy(mixed+429,aac,12);
    uint8_t tail[417+128]={0};memcpy(tail,mp3,417);memcpy(tail+417,"TAG",3);
    uint8_t tagged[441+10];memcpy(tagged,mixed,417);memcpy(tagged+417,"ID3\4\0\0\0\0\0\0",10);memcpy(tagged+427,mixed+417,24);
    uint8_t duplicate[417+256];memcpy(duplicate,tail,sizeof(tail));memcpy(duplicate+sizeof(tail),tail+417,128);
    const uint8_t oversized[]={'I','D','3',4,0,0,0,64,0,0};
    const uint8_t free_format[]={0xff,0xfb,0,0,1,2,3};
    const uint8_t flac[]={'f','L','a','C',0,0,0,34,1,2,3};
    const uint8_t ogg[]={'O','g','g','S',0,1,2,3};
    for(unsigned i=0;i<3;++i) {
        run_case(NULL,0,NULL,0,AUDIO_END_FORMAT_UNKNOWN,chunks[i],NATIVE_CODEC_AUTO);
        run_case(duplicate,sizeof(duplicate),NULL,0,AUDIO_END_FORMAT_UNKNOWN,chunks[i],NATIVE_CODEC_AUTO);
        run_case(oversized,sizeof(oversized),NULL,0,AUDIO_END_FORMAT_UNKNOWN,chunks[i],NATIVE_CODEC_AUTO);
        run_case(free_format,sizeof(free_format),free_format,sizeof(free_format),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(flac,sizeof(flac),flac,sizeof(flac),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(ogg,sizeof(ogg),ogg,sizeof(ogg),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(mixed,sizeof(mixed),mixed,sizeof(mixed),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        assert(drains==1);
        run_case(mixed,sizeof(mixed),mixed,sizeof(mixed),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AAC); // Wrong MIME hint corrected.
        run_case(mp3,sizeof(mp3),mp3,sizeof(mp3),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(aac,sizeof(aac),aac,sizeof(aac),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(mp3,300,NULL,0,AUDIO_END_FRAME_TRUNCATED,chunks[i],NATIVE_CODEC_AUTO);
        run_case(tail,sizeof(tail),mp3,sizeof(mp3),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        run_case(tagged,sizeof(tagged),mixed,sizeof(mixed),AUDIO_END_EOF,chunks[i],NATIVE_CODEC_AUTO);
        for(unsigned n=1;n<128;++n)
            run_case(tail,417+n,NULL,0,AUDIO_END_FRAME_TRUNCATED,chunks[i],NATIVE_CODEC_AUTO);
    }
    uint8_t large_tag[10010+441];memset(large_tag,0xff,sizeof(large_tag));
    memcpy(large_tag,"ID3\4\0\0\0\0\x4e\x10",10); // Synchsafe 10000 bytes.
    memcpy(large_tag+10010,mixed,441);
    run_case(large_tag,sizeof(large_tag),mixed,441,AUDIO_END_EOF,7,NATIVE_CODEC_AUTO);
    uint8_t maximum[8191+12];memset(maximum,0x55,sizeof(maximum));memcpy(maximum,aac,7);
    maximum[3]|=3;maximum[4]=255;maximum[5]|=0xe0;memcpy(maximum+8191,aac,12);
    run_case(maximum,sizeof(maximum),maximum,sizeof(maximum),AUDIO_END_EOF,2048,NATIVE_CODEC_AUTO);
    // Live lifetime paths before any candidate was published.
    for(unsigned action=0;action<4;++action) {
        begin();native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;stream_probe_t probe={0};
        assert(send_stream_audio(42,&codec,mp3,200,&first,&probe));
        assert(first && s_stream_start.active && adaptive_input_stats(s_encoded).occupied);
        if(action==0) {atomic_store(&s_generation,43);stream_transport_reset();}
        if(action==1) assert(finish_stream_audio(42,&codec,&first,AUDIO_END_READ_FAILED)==AUDIO_END_READ_FAILED);
        if(action==2) {
            clock_offset=(int64_t)STREAM_PROBE_TIMEOUT_MS*1000;
            assert(!send_stream_audio(42,&codec,mp3+200,1,&first,&probe));
        }
        if(action==3) {atomic_store(&s_generation,43);assert(!send_stream_audio(42,&codec,mp3+200,1,&first,&probe));}
        finish();
    }
    puts("PASS startup: actual send/finish path, mono-frame EOF, wrong MIME, MP3/AAC transition, ID3 streaming and all 127 truncated tails, duplicate/oversized metadata, FLAC/Ogg/free-format passthrough, empty input, max ADTS, Stop/reset/read-failure/deadline cancellation; ASan/UBSan");
}
