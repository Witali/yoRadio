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
#include <stdio.h>
#include "lwip/tcpip.h"
#include "lwip/priv/tcp_priv.h"
#include "memory_tcp_snapshot.h"

static volatile bool s_tcp_pending;
static memory_tcp_snapshot_t s_tcp_snapshot;
static uint32_t s_tcp_samples, s_tcp_request_failures;
static const char s_tcp_log_request;
static void tcp_memory_sample(void *context) {
    memory_tcp_snapshot_t snapshot;
    memory_tcp_capture(&snapshot, tcp_active_pcbs, tcp_tw_pcbs,
                       xTaskGetTickCount() * portTICK_PERIOD_MS);
    taskENTER_CRITICAL();
    s_tcp_snapshot = snapshot;
    ++s_tcp_samples;
    s_tcp_pending = false;
    taskEXIT_CRITICAL();
    if (!context) return; /* HTTP-triggered samples never print in TCP/IP. */
    unsigned active = 0, timewait = 0;
    for (struct tcp_pcb *p = tcp_active_pcbs; p; p = p->next) {
        unsigned queued = 0;
#if TCP_QUEUE_OOSEQ
        for (struct tcp_seg *s = p->ooseq; s; s = s->next)
            if (s->p) queued += s->p->tot_len;
#endif
        ESP_LOGE("memory", "tcp local=%u remote=%u state=%u ooseq=%u refused=%u wnd=%u",
                 p->local_port, p->remote_port, p->state, queued,
                 p->refused_data ? p->refused_data->tot_len : 0, (unsigned)p->rcv_wnd);
        ++active;
    }
    for (struct tcp_pcb *p = tcp_tw_pcbs; p; p = p->next) ++timewait;
    ESP_LOGE("memory", "tcp active=%u timewait=%u", active, timewait);
}

static void request_tcp_sample(void *context) {
    taskENTER_CRITICAL();
    bool request = !s_tcp_pending;
    if (request) s_tcp_pending = true;
    taskEXIT_CRITICAL();
    if (request && tcpip_try_callback(tcp_memory_sample, context) != ERR_OK) {
        taskENTER_CRITICAL();
        ++s_tcp_request_failures;
        s_tcp_pending = false; /* A later request may retry; no busy loop. */
        taskEXIT_CRITICAL();
    }
}

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

int memory_profile_json(char *output, size_t capacity) {
    if (!output || !capacity) return -1;
    request_tcp_sample(NULL);
    heap_sample_t heap = sample_heap();
    memory_tcp_snapshot_t tcp;
    uint32_t samples, failures;
    bool pending;
    taskENTER_CRITICAL();
    tcp = s_tcp_snapshot;
    samples = s_tcp_samples;
    failures = s_tcp_request_failures;
    pending = s_tcp_pending;
    taskEXIT_CRITICAL();
    uint32_t now = xTaskGetTickCount() * portTICK_PERIOD_MS;
    int size = snprintf(output, capacity,
        "{\"current_dram\":%u,\"largest_dram\":%u,\"allocator_min_dram\":%u,"
        "\"free_blocks\":%u,\"heap_valid\":%s,\"heap_ms\":%u,"
        "\"tcp_valid\":%s,\"tcp_samples\":%u,\"tcp_age_ms\":%u,"
        "\"tcp_pending\":%s,\"tcp_queue_failures\":%u,\"tcp_timewait\":%u,"
        "\"web\":{\"pcbs\":%u,\"states\":%u,\"window\":%u,\"ooseq\":%u,"
        "\"refused\":%u,\"unsent\":%u,\"unacked\":%u},"
        "\"client\":{\"pcbs\":%u,\"states\":%u,\"window\":%u,\"ooseq\":%u,"
        "\"refused\":%u,\"unsent\":%u,\"unacked\":%u}}",
        heap.free, heap.largest, heap.low, heap.blocks, heap.valid ? "true" : "false", (unsigned)now,
        samples ? "true" : "false", (unsigned)samples, (unsigned)(samples ? now-tcp.sampled_ms : 0),
        pending ? "true" : "false", (unsigned)failures, (unsigned)tcp.timewait,
        (unsigned)tcp.web.pcbs, (unsigned)tcp.web.states, (unsigned)tcp.web.window,
        (unsigned)tcp.web.ooseq, (unsigned)tcp.web.refused, (unsigned)tcp.web.unsent, (unsigned)tcp.web.unacked,
        (unsigned)tcp.client.pcbs, (unsigned)tcp.client.states, (unsigned)tcp.client.window,
        (unsigned)tcp.client.ooseq, (unsigned)tcp.client.refused, (unsigned)tcp.client.unsent, (unsigned)tcp.client.unacked);
    return size >= 0 && (size_t)size < capacity ? size : -1;
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
    ESP_LOGE("memory", "station=%u codec=%s play=%u conn=%u kbps=%u "
             "dram_total=%u free=%u low=%u largest=%u window_free=%u "
             "window_largest=%u iram_free=%u blocks=%u valid=%u "
             "stack_app=%u stack_audio=%u stack_web=%u stack_idle=%u",
             state.station_index, native_codec_name(state.codec), state.playing,
             state.connecting, (unsigned)state.bitrate_kbps,
             sample.total, sample.free, sample.low, sample.largest,
             s_low_free, s_low_largest, sample.iram_free, sample.blocks,
             sample.valid, app, audio, web, idle);
    s_low_free = s_low_largest = UINT_MAX;
    /* Inspect PCBs only on the TCP/IP owner task; no unsafe cross-task walk.
     * This entire module is compiled out of ordinary production builds. */
    request_tcp_sample((void *)&s_tcp_log_request);
}
