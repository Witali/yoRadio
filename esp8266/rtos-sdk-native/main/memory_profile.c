/* Diagnostic-only adapter for ESP8266_RTOS_SDK v3.4's region allocator.
 * No trial allocations, extra task, heap tracing or audio-path logging.
 * The private SDK helpers are intentional: this SDK has no public largest-
 * block API. Keep this adapter coupled to its actual allocator definitions. */
#include "memory_profile.h"
#include "esp_heap_caps.h"
#include "esp_heap_port.h"
#include "priv/esp_heap_caps_priv.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_state.h"
#include <limits.h>

#ifdef CONFIG_HEAP_TRACING
#error "Memory profile expects the production untraced allocator layout"
#endif

extern heap_region_t g_heap_region[];
extern size_t g_heap_region_num;

static TaskHandle_t s_tasks[MEMORY_TASKS];
static TickType_t s_last_report;
static unsigned s_low_free = UINT_MAX;
static unsigned s_low_largest = UINT_MAX;

typedef struct {
    unsigned total, free, low, largest, iram_free, blocks;
    bool valid;
} heap_sample_t;

static heap_sample_t sample_heap(void) {
    heap_sample_t sample = {.valid = true};
    /* Same interrupt lock as malloc/free. Do not log, scan stacks or access
     * the state mutex here. Read all regions as one consistent snapshot. */
    _heap_caps_lock(0);
    for (size_t i = 0; i < g_heap_region_num; ++i) {
        heap_region_t *region = &g_heap_region[i];
        if (!(region->caps & MALLOC_CAP_8BIT)) {
            if (region->caps & MALLOC_CAP_32BIT)
                sample.iram_free += region->free_bytes;
            continue;
        }
        sample.total += region->total_size;
        sample.free += region->free_bytes;
        sample.low += region->min_free_bytes;
        uintptr_t start = (uintptr_t)region->start_addr;
        uintptr_t end = start + region->total_size;
        mem_blk_t *block = region->free_blk;
        while (block) {
            uintptr_t address = (uintptr_t)block;
            if (address < start || address > end - MEM_HEAD_SIZE) {
                sample.valid = false;
                break;
            }
            mem_blk_t *next = mem_blk_next(block);
            if (!next) break; /* terminal sentinel, never allocatable */
            if ((uintptr_t)next <= address ||
                (uintptr_t)next > end - MEM_HEAD_SIZE) {
                sample.valid = false;
                break;
            }
            if (!mem_blk_is_used(block)) {
                /* malloc aligns request + header upward. Round this span
                 * downward before subtracting the untraced header. */
                size_t span = blk_link_size(block) & ~(HEAP_ALIGN_SIZE - 1U);
                size_t payload = span > MEM_HEAD_SIZE ? span - MEM_HEAD_SIZE : 0;
                if (payload > sample.largest) sample.largest = payload;
                ++sample.blocks;
            }
            block = next;
        }
    }
    _heap_caps_unlock(0);
    return sample;
}

void memory_profile_register(enum memory_profile_task task) {
    if ((unsigned)task < MEMORY_TASKS)
        s_tasks[task] = xTaskGetCurrentTaskHandle();
}

static unsigned stack_free(enum memory_profile_task task) {
    return s_tasks[task] ? uxTaskGetStackHighWaterMark(s_tasks[task]) : 0;
}

void memory_profile_poll(void) {
    TickType_t now = xTaskGetTickCount();
    /* Called by the existing app loop (at most every 250 ms, sometimes
     * earlier on BOOT activity). Largest-block minima are SAMPLED, unlike
     * the allocator's lifetime region low-water values. */
    heap_sample_t sample = sample_heap();
    if (sample.free < s_low_free) s_low_free = sample.free;
    if (sample.largest < s_low_largest) s_low_largest = sample.largest;
    if (now - s_last_report < pdMS_TO_TICKS(10000)) return;
    s_last_report = now;
    native_state_t state;
    native_state_snapshot(&state);
    unsigned app = stack_free(MEMORY_APP);
    unsigned audio = stack_free(MEMORY_AUDIO);
    unsigned web = stack_free(MEMORY_WEB);
    unsigned idle = uxTaskGetStackHighWaterMark(xTaskGetIdleTaskHandle());
    /* StackType_t is uint8_t in this port: these high-water values are bytes.
     * Avoid all-task trace arrays, which would alter the RAM under test. */
    ESP_LOGI("memory", "station=%u codec=%s play=%u conn=%u kbps=%u "
             "dram_total=%u free=%u low=%u largest=%u window_free=%u "
             "window_largest=%u iram_free=%u blocks=%u valid=%u "
             "stack_app=%u stack_audio=%u stack_web=%u stack_idle=%u",
             state.station_index, native_codec_name(state.codec), state.playing,
             state.connecting, (unsigned)state.bitrate_kbps,
             sample.total, sample.free, sample.low, sample.largest,
             s_low_free, s_low_largest, sample.iram_free, sample.blocks,
             sample.valid, app, audio, web, idle);
    s_low_free = s_low_largest = UINT_MAX;
}
