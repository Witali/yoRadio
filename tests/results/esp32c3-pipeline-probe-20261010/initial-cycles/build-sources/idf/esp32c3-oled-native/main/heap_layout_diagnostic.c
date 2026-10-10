#include "heap_layout_capture.h"
#include "cpu_profiler.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include <inttypes.h>
#include <string.h>

_Static_assert(sizeof(heap_layout_capture_t) <= 1600, "Bound C3 diagnostic stack use");

static bool capture_block(walker_heap_into_t heap, walker_block_info_t block, void *data) {
    // IDF invokes this with the individual heap locked. No logging, allocation,
    // task inspection or other heap APIs are allowed here.
    heap_layout_record(data, (uintptr_t)heap.start, (uintptr_t)block.ptr, block.size, block.used);
    return true;
}

static void snapshot(const char *stage) {
    heap_layout_capture_t state = {0};
    int64_t start = esp_timer_get_time();
    heap_caps_walk(MALLOC_CAP_8BIT, capture_block, &state);
    int64_t elapsed = esp_timer_get_time() - start;
    // All locks are released before printing. Different heaps are captured
    // sequentially, so the combined report is not an atomic global snapshot.
    ESP_LOGI("heap_layout", "PERF HEAP: stage=%s blocks=%u selected=%u dropped=%u free_raw=%u used_raw=%u walk_us=%" PRId64,
             stage, (unsigned)state.blocks, (unsigned)state.count, (unsigned)state.dropped,
             (unsigned)state.free_bytes, (unsigned)state.used_bytes, elapsed);
    for (size_t i = 0; i < state.count; ++i) {
        const heap_layout_row_t *r = &state.rows[i];
        ESP_LOGI("heap_layout", "PERF BLOCK: stage=%s heap=0x%08" PRIxPTR " address=0x%08" PRIxPTR " bytes=%u used=%u",
                 stage, r->heap, r->address, (unsigned)(r->size_used & UINT32_C(0x7fffffff)),
                 (unsigned)(r->size_used >> 31));
    }
}

void __real_cpu_profiler_memory(const char *stage);
void __wrap_cpu_profiler_memory(const char *stage) {
    __real_cpu_profiler_memory(stage);
    // AAC runs on the retained 16 KiB decoder stack. Do not consume this
    // additional stack on app_main or HTTP paths with smaller budgets.
    if (strncmp(stage, "aac-", 4) == 0) snapshot(stage);
}

void *__real_media_lib_module_malloc(const char *, size_t);
void *__real_media_lib_module_calloc(const char *, size_t, size_t);
void *__wrap_media_lib_module_malloc(const char *module, size_t size) {
    void *p = __real_media_lib_module_malloc(module, size);
    if (size >= 1024)
        ESP_LOGI("heap_layout", "PERF CODEC_ALLOC: kind=malloc requested=%u address=0x%08" PRIxPTR,
                 (unsigned)size, (uintptr_t)p);
    return p;
}
void *__wrap_media_lib_module_calloc(const char *module, size_t n, size_t size) {
    void *p = __real_media_lib_module_calloc(module, n, size);
    if (size && n <= SIZE_MAX/size && n*size >= 1024)
        ESP_LOGI("heap_layout", "PERF CODEC_ALLOC: kind=calloc requested=%u address=0x%08" PRIxPTR,
                 (unsigned)(n*size), (uintptr_t)p);
    return p;
}
