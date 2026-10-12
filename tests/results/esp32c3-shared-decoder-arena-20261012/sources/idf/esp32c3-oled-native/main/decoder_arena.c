#include "decoder_arena.h"
#include <stdint.h>
#include <string.h>
#include "multi_heap.h"
#include "esp_attr.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/* This heap is deliberately NOT registered with heap_caps. Its bytes are
 * reserved before boot allocations and never lent to TLS, Wi-Fi or DMA.
 * No generation reset: every allocation retains its lifetime across Stop. */
static _Alignas(max_align_t) unsigned char storage[CONFIG_YORADIO_SHARED_DECODER_ARENA_BYTES];
static multi_heap_handle_t arena;
static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
static _Thread_local bool selected;
static decoder_arena_stats_t stats;

typedef struct { void *base; size_t requested; } allocation_t;
enum { ALIGNMENT = _Alignof(max_align_t) };
#define OVERHEAD (sizeof(allocation_t) + ALIGNMENT - 1U)

void *__real_malloc(size_t size);
void *__real_calloc(size_t count, size_t size);
void *__real_realloc(void *pointer, size_t size);
void __real_free(void *pointer);
size_t __real_heap_caps_get_allocated_size(void *pointer);

bool decoder_arena_init(void) {
    portENTER_CRITICAL(&lock);
    if (!arena) arena = multi_heap_register(storage, sizeof(storage));
    bool ready = arena != NULL;
    portEXIT_CRITICAL(&lock);
    return ready;
}

bool decoder_arena_select(bool enable) {
    bool previous = selected;
    selected = enable;
    return previous;
}

bool IRAM_ATTR decoder_arena_owns(const void *pointer) {
    uintptr_t address = (uintptr_t)pointer;
    return address >= (uintptr_t)storage && address < (uintptr_t)storage + sizeof(storage);
}

static inline void *payload(void *base) {
    return (void *)(((uintptr_t)base + OVERHEAD) & ~(uintptr_t)(ALIGNMENT - 1U));
}
static inline allocation_t *header(void *pointer) { return (allocation_t *)pointer - 1; }
static inline void account(size_t old_size, size_t new_size) {
    stats.live = stats.live - old_size + new_size;
    if (stats.live > stats.peak) stats.peak = stats.live;
}
static inline bool use_arena(void) { return !xPortInIsrContext() && selected; }

void *IRAM_ATTR __wrap_malloc(size_t size) {
    if (!use_arena()) return __real_malloc(size);
    if (!size) return NULL;
    portENTER_CRITICAL(&lock);
    void *base = arena && size <= SIZE_MAX - OVERHEAD ?
        multi_heap_malloc(arena, size + OVERHEAD) : NULL;
    void *result = NULL;
    if (base) {
        result = payload(base);
        *header(result) = (allocation_t){base, size};
        account(0, size);
        ++stats.blocks;
    } else ++stats.failures;
    portEXIT_CRITICAL(&lock);
    return result;
}

void *IRAM_ATTR __wrap_calloc(size_t count, size_t size) {
    if (!use_arena()) return __real_calloc(count, size);
    if (size && count > SIZE_MAX / size) {
        portENTER_CRITICAL(&lock);
        ++stats.failures;
        portEXIT_CRITICAL(&lock);
        return NULL;
    }
    void *result = __wrap_malloc(count * size);
    if (result) memset(result, 0, count * size);
    return result;
}

void IRAM_ATTR __wrap_free(void *pointer) {
    if (!decoder_arena_owns(pointer)) { __real_free(pointer); return; }
    portENTER_CRITICAL(&lock);
    allocation_t old = *header(pointer);
    account(old.requested, 0);
    --stats.blocks;
    multi_heap_free(arena, old.base);
    portEXIT_CRITICAL(&lock);
}

void *IRAM_ATTR __wrap_realloc(void *pointer, size_t size) {
    if (!pointer) return __wrap_malloc(size);
    /* Existing system allocations keep their domain, even in a codec call. */
    if (!decoder_arena_owns(pointer)) return __real_realloc(pointer, size);
    if (!size) { __wrap_free(pointer); return NULL; }
    portENTER_CRITICAL(&lock);
    allocation_t old = *header(pointer);
    size_t offset = (unsigned char *)pointer - (unsigned char *)old.base;
    void *base = size <= SIZE_MAX - OVERHEAD ?
        multi_heap_realloc(arena, old.base, size + OVERHEAD) : NULL;
    void *result = NULL;
    if (base) {
        result = payload(base);
        /* The base may move with a different alignment. Save the old header
         * first; memmove also handles overlapping payload/header locations. */
        memmove(result, (unsigned char *)base + offset,
                old.requested < size ? old.requested : size);
        *header(result) = (allocation_t){base, size};
        account(old.requested, size);
    } else ++stats.failures;
    portEXIT_CRITICAL(&lock);
    return result;
}

size_t IRAM_ATTR __wrap_heap_caps_get_allocated_size(void *pointer) {
    if (!decoder_arena_owns(pointer)) return __real_heap_caps_get_allocated_size(pointer);
    return header(pointer)->requested;
}

decoder_arena_stats_t decoder_arena_stats(void) {
    portENTER_CRITICAL(&lock);
    decoder_arena_stats_t result = stats;
    result.capacity = sizeof(storage);
    if (arena) {
        multi_heap_info_t info;
        multi_heap_get_info(arena, &info);
        result.free_bytes = info.total_free_bytes;
        result.largest = info.largest_free_block;
    }
    portEXIT_CRITICAL(&lock);
    return result;
}
