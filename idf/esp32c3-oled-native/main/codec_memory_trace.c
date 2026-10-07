#include "codec_memory_trace.h"

#if CONFIG_YORADIO_CODEC_MEMORY_TRACE
#include <stdint.h>
#include <stdlib.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// ABI verified against esp_audio_codec 2.6.2 and media_lib_os.h. These strong
// definitions replace only the codec's weak libc shims, never system malloc.
// Fixed storage and no logging inside allocation hooks keep the trace bounded.
#define TRACE_SLOTS 64
#define TRACE_EVENTS 64
typedef struct { void *pointer; size_t size; uint32_t id; const char *module; } slot_t;
typedef struct {
    const char *module;
    void *pointer;
    size_t size;
    uint32_t id, live;
    char operation;
} event_t;
static slot_t slots[TRACE_SLOTS];
static event_t events[TRACE_EVENTS];
static unsigned count, lost, next_id;
static size_t live, peak;
static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;

static unsigned find_pointer(void *pointer) {
    for (unsigned i = 0; i < TRACE_SLOTS; ++i)
        if (pointer && slots[i].pointer == pointer) return i;
    return TRACE_SLOTS;
}

static void event(char operation, const char *module, void *pointer,
                  size_t size, uint32_t id) {
    if (count == TRACE_EVENTS) { ++lost; return; }
    events[count++] = (event_t){module, pointer, size, id, live, operation};
}

static void track_alloc(const char *module, void *pointer, size_t size) {
    if (!pointer) { event('!', module, NULL, size, 0); return; }
    for (unsigned i = 0; i < TRACE_SLOTS; ++i) {
        if (!slots[i].pointer) {
            slots[i] = (slot_t){pointer, size, ++next_id, module};
            live += size;
            if (live > peak) peak = live;
            event('+', module, pointer, size, next_id);
            return;
        }
    }
    ++lost;
}

static void untrack(unsigned slot) {
    if (slot == TRACE_SLOTS) return;
    slot_t *item = &slots[slot];
    live -= item->size;
    event('-', item->module, item->pointer, item->size, item->id);
    *item = (slot_t){0};
}

void *media_lib_module_malloc(const char *module, size_t size) {
    void *pointer = malloc(size);
    taskENTER_CRITICAL(&lock);
    track_alloc(module, pointer, size);
    taskEXIT_CRITICAL(&lock);
    return pointer;
}

void *media_lib_module_calloc(const char *module, size_t n, size_t size) {
    if (size && n > SIZE_MAX / size) return NULL;
    void *pointer = calloc(n, size);
    taskENTER_CRITICAL(&lock);
    track_alloc(module, pointer, n * size);
    taskEXIT_CRITICAL(&lock);
    return pointer;
}

void media_lib_free(void *pointer) {
    taskENTER_CRITICAL(&lock);
    untrack(find_pointer(pointer));
    taskEXIT_CRITICAL(&lock);
    free(pointer);
}

void *media_lib_module_realloc(const char *module, void *pointer, size_t size) {
    taskENTER_CRITICAL(&lock);
    unsigned slot = find_pointer(pointer);
    uint32_t id = slot == TRACE_SLOTS ? 0 : slots[slot].id;
    taskEXIT_CRITICAL(&lock);
    void *resized = realloc(pointer, size);
    taskENTER_CRITICAL(&lock);
    // A failed nonzero realloc leaves the old allocation and its contents live.
    if (resized || !size) {
        if (id && slots[slot].id == id) untrack(slot);
        if (resized) track_alloc(module, resized, size);
    } else {
        event('!', module, NULL, size, id);
    }
    taskEXIT_CRITICAL(&lock);
    return resized;
}

void codec_memory_trace_dump(const char *phase) {
    // Called by the decoder task after an SDK call, not from the hooks. The
    // diagnostic AAC decoder is synchronous; do not use this as a timing probe.
    taskENTER_CRITICAL(&lock);
    unsigned pending = count;
    size_t current = live, high = peak;
    unsigned dropped = lost;
    taskEXIT_CRITICAL(&lock);
    if (!pending && !dropped) return;
    ESP_LOGI("codec_memory", "PERF ALLOC: phase=%s live=%u peak=%u lost=%u storage=%u",
             phase, (unsigned)current, (unsigned)high, dropped,
             (unsigned)(sizeof(slots) + sizeof(events)));
    for (unsigned i = 0; i < pending; ++i) {
        taskENTER_CRITICAL(&lock);
        event_t row = events[i];
        taskEXIT_CRITICAL(&lock);
        ESP_LOGI("codec_memory", "PERF ALLOC: phase=%s op=%c id=%lu module=%s size=%u live=%lu pointer=%p",
                 phase, row.operation, (unsigned long)row.id,
                 row.module ? row.module : "unknown", (unsigned)row.size,
                 (unsigned long)row.live, row.pointer);
    }
    taskENTER_CRITICAL(&lock);
    // Preserve events appended by another task during logging.
    for (unsigned i = pending; i < count; ++i) events[i-pending] = events[i];
    count -= pending;
    taskEXIT_CRITICAL(&lock);
}
#endif
