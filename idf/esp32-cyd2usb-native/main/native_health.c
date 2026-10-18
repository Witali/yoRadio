#include "native_health.h"

#include <stddef.h>
#include <string.h>
#include "sdkconfig.h"
#include "esp_attr.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static DRAM_ATTR portMUX_TYPE s_health_lock = portMUX_INITIALIZER_UNLOCKED;
static DRAM_ATTR native_health_snapshot_t s_health;
static void *s_health_tasks[NATIVE_HEALTH_TASKS];

static void IRAM_ATTR record_allocation_failure(size_t size, uint32_t caps,
                                                const char *function) {
    (void)function;
    // May run in a task or ISR on either core. No heap, logging or Flash data.
    portENTER_CRITICAL_ISR(&s_health_lock);
    ++s_health.faults.allocation_failures;
    s_health.faults.allocation_size = (uint32_t)size;
    s_health.faults.allocation_caps = caps;
    portEXIT_CRITICAL_ISR(&s_health_lock);
}

void native_health_decoder_failure(uint32_t generation, uint32_t codec,
        native_health_decoder_stage_t stage, int32_t result, uint32_t completion,
        uint32_t input_bytes) {
    portENTER_CRITICAL(&s_health_lock);
    native_health_faults_t *faults = &s_health.faults;
    ++faults->decoder_failures;
    faults->decoder_generation = generation;
    faults->decoder_codec = codec;
    faults->decoder_stage = (uint32_t)stage;
    faults->decoder_result = result;
    faults->decoder_completion = completion;
    faults->decoder_input_bytes = input_bytes;
    faults->decoder_allocation_sequence = faults->allocation_failures;
    portEXIT_CRITICAL(&s_health_lock);
}

void native_health_stream_failure(uint32_t generation, uint32_t completion, int32_t result) {
    portENTER_CRITICAL(&s_health_lock);
    ++s_health.faults.stream_failures;
    s_health.faults.stream_generation = generation;
    s_health.faults.stream_completion = completion;
    s_health.faults.stream_result = result;
    portEXIT_CRITICAL(&s_health_lock);
}

void native_health_output_failure(uint32_t generation, int32_t result) {
    portENTER_CRITICAL(&s_health_lock);
    ++s_health.faults.output_failures;
    s_health.faults.output_generation = generation;
    s_health.faults.output_result = result;
    portEXIT_CRITICAL(&s_health_lock);
}

void native_health_track_task(native_health_task_t role, void *handle) {
    if ((unsigned)role >= NATIVE_HEALTH_TASKS) return;
    portENTER_CRITICAL(&s_health_lock);
    if (s_health_tasks[role] != handle) {
        s_health_tasks[role] = handle;
        s_health.cpu.task[role] = (native_health_task_cpu_t){0};
    }
    portEXIT_CRITICAL(&s_health_lock);
}

native_health_snapshot_t native_health_snapshot(void) {
    portENTER_CRITICAL(&s_health_lock);
    native_health_snapshot_t result = s_health;
    portEXIT_CRITICAL(&s_health_lock);
    return result;
}

#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
#include "esp_ipc.h"
#if !CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS || !CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER
#error "CYD diagnostics require FreeRTOS runtime stats using the global ESP timer"
#endif
_Static_assert(configNUMBER_OF_CORES == 2, "CYD profiling expects both ESP32 cores");

enum { HEALTH_MAX_TASKS = 32, HEALTH_SAMPLE_MS = 5000, HEALTH_STACK_BYTES = 4096 };
typedef struct {
    TaskHandle_t handle;
    UBaseType_t number;
    configRUN_TIME_COUNTER_TYPE runtime;
    uint32_t stack_free;
    bool found;
} health_task_sample_t;

static TaskStatus_t s_task_status[HEALTH_MAX_TASKS]; // Diagnostic sampler owns this workspace.
static health_task_sample_t s_previous_task[NATIVE_HEALTH_TASKS], s_previous_idle[2];
static configRUN_TIME_COUNTER_TYPE s_previous_total;
static bool s_health_primed;

static health_task_sample_t find_task(TaskHandle_t handle, UBaseType_t count) {
    health_task_sample_t result = {0};
    if (!handle) return result;
    for (UBaseType_t i=0; i<count; ++i) {
        if (s_task_status[i].xHandle == handle) {
            result = (health_task_sample_t){.handle=handle,
                .number=s_task_status[i].xTaskNumber,
                .runtime=s_task_status[i].ulRunTimeCounter,
                .stack_free=(uint32_t)s_task_status[i].usStackHighWaterMark, .found=true};
            break;
        }
    }
    // Never dereference pcTaskName: the SDK explicitly invalidates it when a
    // task is deleted after uxTaskGetSystemState, which can happen on core 1.
    return result;
}

static bool same_task(health_task_sample_t a, health_task_sample_t b) {
    return a.found && b.found && a.handle == b.handle && a.number == b.number;
}

static uint16_t health_percent(uint64_t part, uint64_t total) {
    if (part > total) part = total;
    // Callers reject impractically long intervals before multiplying.
    return (uint16_t)((part * 1000U + total / 2U) / total);
}

static bool health_interval_supported(uint64_t interval) {
    return interval && interval <= UINT64_MAX / 1001U;
}

static void profile_ipc_yield(void *unused) { (void)unused; }

static void native_health_sample(void) {
    void *handles[NATIVE_HEALTH_TASKS];
    native_health_cpu_t next = {.enabled=true};
    portENTER_CRITICAL(&s_health_lock);
    memcpy(handles, s_health_tasks, sizeof(handles));
    next.snapshot_failures = s_health.cpu.snapshot_failures;
    portEXIT_CRITICAL(&s_health_lock);

    // uxTaskGetSystemState returns cached task counters. Switching the other
    // core through the public IPC API accounts for its current idle/runtime
    // interval first. The sampler itself already switched out local idle.
    unsigned other_core = (unsigned)xPortGetCoreID() ^ 1U;
    esp_err_t ipc = esp_ipc_call_blocking(other_core, profile_ipc_yield, NULL);
    configRUN_TIME_COUNTER_TYPE total = 0;
    UBaseType_t count = ipc == ESP_OK
        ? uxTaskGetSystemState(s_task_status, HEALTH_MAX_TASKS, &total) : 0;
    if (!count || count > HEALTH_MAX_TASKS) {
        ++next.snapshot_failures;
        s_health_primed = false;
        goto publish;
    }
    configRUN_TIME_COUNTER_TYPE interval = total - s_previous_total;
    health_task_sample_t idle[2];
    bool valid = s_health_primed && health_interval_supported(interval);
    for (unsigned core=0; core<2; ++core) {
        idle[core] = find_task(xTaskGetIdleTaskHandleForCore((BaseType_t)core), count);
        valid = valid && same_task(idle[core], s_previous_idle[core]);
    }
    next.sampled_us = (uint64_t)esp_timer_get_time();
    if (valid) {
        next.available = true;
        for (unsigned core=0; core<2; ++core) {
            configRUN_TIME_COUNTER_TYPE delta = idle[core].runtime - s_previous_idle[core].runtime;
            next.core_tenths[core] = (uint16_t)(1000U - health_percent(delta, interval));
        }
        // Per-task figures use one core's capacity. Overall CPU averages both
        // cores; summing idle counters against a single-core total is wrong.
        next.overall_tenths = (uint16_t)((next.core_tenths[0] + next.core_tenths[1] + 1U) / 2U);
    }
    for (unsigned role=0; role<NATIVE_HEALTH_TASKS; ++role) {
        health_task_sample_t current = find_task(handles[role], count);
        next.task[role].present = current.found;
        next.task[role].stack_free_min = current.stack_free;
        if (valid && same_task(current, s_previous_task[role])) {
            configRUN_TIME_COUNTER_TYPE delta = current.runtime - s_previous_task[role].runtime;
            next.task[role].available = true;
            next.task[role].percent_tenths = health_percent(delta, interval);
        }
        s_previous_task[role] = current;
    }
    memcpy(s_previous_idle, idle, sizeof(idle));
    s_previous_total = total;
    s_health_primed = true;
publish:
    portENTER_CRITICAL(&s_health_lock);
    for (unsigned role=0; role<NATIVE_HEALTH_TASKS; ++role)
        if (handles[role] != s_health_tasks[role]) next.task[role] = (native_health_task_cpu_t){0};
    s_health.cpu = next;
    portEXIT_CRITICAL(&s_health_lock);
}

static void health_task(void *unused) {
    (void)unused;
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(HEALTH_SAMPLE_MS));
        native_health_sample();
    }
}
#endif

bool native_health_start(void) {
    if (heap_caps_register_failed_alloc_callback(record_allocation_failure) != ESP_OK) return false;
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    portENTER_CRITICAL(&s_health_lock);
    s_health.cpu.enabled = true;
    portEXIT_CRITICAL(&s_health_lock);
    return xTaskCreatePinnedToCore(health_task, "native_health", HEALTH_STACK_BYTES,
        NULL, 1, NULL, 0) == pdPASS;
#else
    return true;
#endif
}
