#include "cpu_profiler.h"
#include "network_heap_profile.h"
#include "tls_path_profile.h"

#include <inttypes.h>
#include <stdbool.h>
#include <string.h>

#include "esp_attr.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static DRAM_ATTR volatile uint32_t s_allocation_failures;
static DRAM_ATTR volatile uint32_t s_allocation_size;
static DRAM_ATTR volatile uint32_t s_allocation_caps;
static DRAM_ATTR struct {
    uint32_t decoder_failures, decoder_codec, decoder_stage;
    int32_t decoder_result;
    uint32_t decoder_completion, decoder_input_bytes, decoder_allocation_sequence;
} s_decoder_failure;

static void IRAM_ATTR record_allocation_failure(size_t size, uint32_t caps,
                                                const char *function) {
    (void)function;
    // C3 is single-core. Preserve the previous interrupt level so task and
    // ISR callers cannot lose an increment. No heap, logging or Flash data.
    UBaseType_t saved_level = portSET_INTERRUPT_MASK_FROM_ISR();
    s_allocation_size = (uint32_t)size;
    s_allocation_caps = caps;
    ++s_allocation_failures;
    portCLEAR_INTERRUPT_MASK_FROM_ISR(saved_level);
}

#if CONFIG_ESP_TASK_WDT_EN
// One ISR writer and one sampler on this single-core C3. Aligned 32-bit
// volatile loads/stores do not tear; the counter publishes no other state.
// Keep the callback in IRAM with no logging, allocation or helper calls.
static DRAM_ATTR volatile uint32_t s_task_watchdog_events;

void IRAM_ATTR esp_task_wdt_isr_user_handler(void) {
    ++s_task_watchdog_events;
}
#endif

cpu_profiler_faults_t cpu_profiler_faults(void) {
    UBaseType_t saved_level = portSET_INTERRUPT_MASK_FROM_ISR();
    cpu_profiler_faults_t result = {
        .decoder_failures = s_decoder_failure.decoder_failures,
        .decoder_codec = s_decoder_failure.decoder_codec,
        .decoder_stage = s_decoder_failure.decoder_stage,
        .decoder_result = s_decoder_failure.decoder_result,
        .decoder_completion = s_decoder_failure.decoder_completion,
        .decoder_input_bytes = s_decoder_failure.decoder_input_bytes,
        .decoder_allocation_sequence = s_decoder_failure.decoder_allocation_sequence,
    };
    result.allocation_failures = s_allocation_failures;
    result.allocation_size = s_allocation_size;
    result.allocation_caps = s_allocation_caps;
#if CONFIG_ESP_TASK_WDT_EN
    result.task_watchdog_events = s_task_watchdog_events;
#endif
    portCLEAR_INTERRUPT_MASK_FROM_ISR(saved_level);
    return result;
}

void cpu_profiler_decoder_failure(uint32_t codec, decoder_failure_stage_t stage,
                                  int32_t result, uint32_t completion,
                                  uint32_t input_bytes) {
    UBaseType_t saved_level = portSET_INTERRUPT_MASK_FROM_ISR();
    ++s_decoder_failure.decoder_failures;
    s_decoder_failure.decoder_codec = codec;
    s_decoder_failure.decoder_stage = stage;
    s_decoder_failure.decoder_result = result;
    s_decoder_failure.decoder_completion = completion;
    s_decoder_failure.decoder_input_bytes = input_bytes;
    s_decoder_failure.decoder_allocation_sequence = s_allocation_failures;
    portCLEAR_INTERRUPT_MASK_FROM_ISR(saved_level);
}

#if CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS

#define CPU_PROFILE_INTERVAL_MS 5000U
#define CPU_PROFILE_MAX_TASKS 32U
#define CPU_PROFILE_STACK_BYTES 4096U

static const char *const TAG = "cpu_profile";

#if CONFIG_ESP_TASK_WDT_EN
static void report_task_watchdog(void) {
    static uint32_t reported;
    uint32_t current = s_task_watchdog_events;
    if (current != reported) {
        reported = current;
        ESP_LOGE(TAG, "PERF watchdog: task_timeouts=%" PRIu32, current);
    }
}
#else
static void report_task_watchdog(void) {}
#endif

void cpu_profiler_memory(const char *stage) {
    multi_heap_info_t info;
    heap_caps_get_info(&info, MALLOC_CAP_8BIT);
    ESP_LOGI(TAG, "PERF RAM: stage=%s free=%u largest=%u allocated=%u blocks=%u",
             stage, (unsigned)info.total_free_bytes,
             (unsigned)info.largest_free_block,
             (unsigned)info.total_allocated_bytes,
             (unsigned)info.allocated_blocks);
}

static void allocation_failed(size_t size, uint32_t caps, const char *function) {
    record_allocation_failure(size, caps, function);
    ESP_LOGE(TAG, "PERF allocation failed: requested=%u caps=0x%lx function=%s free=%u largest=%u",
             (unsigned)size, (unsigned long)caps, function,
             (unsigned)heap_caps_get_free_size(caps),
             (unsigned)heap_caps_get_largest_free_block(caps));
}

typedef struct {
    TaskHandle_t handle;
    UBaseType_t number;
    configRUN_TIME_COUNTER_TYPE counter;
} task_sample_t;

static task_sample_t s_previous[CPU_PROFILE_MAX_TASKS];
static UBaseType_t s_previous_count;
static configRUN_TIME_COUNTER_TYPE s_previous_total;
// The diagnostic sampler has exactly one caller (its task or HTTP task).
// C3 scheduler suspension protects TCB lifetime only on this single core.
_Static_assert(configNUMBER_OF_CORES == 1, "C3 task-name snapshot requires one core");
static char s_task_names[CPU_PROFILE_MAX_TASKS][configMAX_TASK_NAME_LEN];

static configRUN_TIME_COUNTER_TYPE previous_counter(TaskHandle_t handle, UBaseType_t number) {
    for (UBaseType_t i = 0; i < s_previous_count; ++i) {
        if (s_previous[i].handle == handle && s_previous[i].number == number) {
            return s_previous[i].counter;
        }
    }
    return 0;
}

static uint32_t percent_tenths(configRUN_TIME_COUNTER_TYPE part,
                               configRUN_TIME_COUNTER_TYPE total) {
    if (total == 0) {
        return 0;
    }
    return (uint32_t)(((uint64_t)part * 1000ULL + total / 2U) / total);
}

static bool name_is(const char *actual, const char *expected) {
    // FreeRTOS stores at most configMAX_TASK_NAME_LEN - 1 characters.
    // In the C3 configuration, "websocket_status" becomes "websocket_statu".
    return actual != NULL &&
           strncmp(actual, expected, configMAX_TASK_NAME_LEN - 1U) == 0;
}

static void cpu_profiler_sample(void) {
    report_task_watchdog();
    TaskStatus_t current[CPU_PROFILE_MAX_TASKS];
    task_sample_t next[CPU_PROFILE_MAX_TASKS];
    static bool primed = false;
    static unsigned stack_interval = 0;

    configRUN_TIME_COUNTER_TYPE total = 0;
    vTaskSuspendAll();
    UBaseType_t count = uxTaskGetSystemState(
        current, CPU_PROFILE_MAX_TASKS, &total);
    if (count <= CPU_PROFILE_MAX_TASKS) {
        for (UBaseType_t i=0; i<count; ++i) {
            // pcTaskName belongs to the TCB, which may be deleted as soon as
            // the scheduler resumes. Copy while pinned; never log here.
            s_task_names[i][0] = '\0';
            if (current[i].pcTaskName)
                memcpy(s_task_names[i], current[i].pcTaskName, configMAX_TASK_NAME_LEN-1U);
            s_task_names[i][configMAX_TASK_NAME_LEN-1U] = '\0';
            current[i].pcTaskName = s_task_names[i];
        }
    }
    xTaskResumeAll();
    if (count == 0 || count > CPU_PROFILE_MAX_TASKS) {
        ESP_LOGW(TAG, "Task snapshot unavailable (tasks=%u)",
                 (unsigned)count);
        return;
    }

    // Report bytes of minimum unused stack, not instantaneous free space.
    // This survey is diagnostic evidence, not permission to shrink stacks
    // before exercising TLS, OTA, all codecs and user interactions.
    if (++stack_interval == 6) {
        stack_interval = 0;
        for (UBaseType_t i = 0; i < count; ++i) {
            ESP_LOGI(TAG, "PERF STACK: name=%s minimum_free=%u",
                     current[i].pcTaskName,
                     (unsigned)current[i].usStackHighWaterMark);
        }
    }

    configRUN_TIME_COUNTER_TYPE interval_total = total - s_previous_total;
    configRUN_TIME_COUNTER_TYPE idle = 0;
    configRUN_TIME_COUNTER_TYPE stream = 0;
    configRUN_TIME_COUNTER_TYPE decode = 0;
    configRUN_TIME_COUNTER_TYPE output = 0;
    configRUN_TIME_COUNTER_TYPE wifi = 0;
    configRUN_TIME_COUNTER_TYPE tcpip = 0;
    configRUN_TIME_COUNTER_TYPE web = 0;

    for (UBaseType_t i = 0; i < count; ++i) {
        configRUN_TIME_COUNTER_TYPE delta =
            current[i].ulRunTimeCounter - previous_counter(current[i].xHandle, current[i].xTaskNumber);
        const char *name = current[i].pcTaskName;
        if (name != NULL && strncmp(name, "IDLE", 4) == 0) {
            idle += delta;
        } else if (name_is(name, "radio_stream")) {
            stream += delta;
        } else if (name_is(name, "audio_decode")) {
            decode += delta;
        } else if (name_is(name, "audio_output")) {
            output += delta;
        } else if (name_is(name, "wifi")) {
            wifi += delta;
        } else if (name_is(name, "tcpip") || name_is(name, "tiT") ||
                   name_is(name, "tcpip_task")) {
            tcpip += delta;
        } else if (name_is(name, "httpd") ||
                   name_is(name, "websocket_status")) {
            web += delta;
        }
        next[i].handle = current[i].xHandle;
        next[i].number = current[i].xTaskNumber;
        next[i].counter = current[i].ulRunTimeCounter;
    }
    memcpy(s_previous, next, count * sizeof(next[0]));
    s_previous_count = count;
    s_previous_total = total;

    if (!primed || interval_total == 0) {
        primed = true;
        return;
    }

    configRUN_TIME_COUNTER_TYPE busy =
        interval_total > idle ? interval_total - idle : 0;
    uint32_t busy_pct = percent_tenths(busy, interval_total);
    uint32_t idle_pct = percent_tenths(idle, interval_total);
    uint32_t stream_pct = percent_tenths(stream, interval_total);
    uint32_t decode_pct = percent_tenths(decode, interval_total);
    uint32_t output_pct = percent_tenths(output, interval_total);
    uint32_t wifi_pct = percent_tenths(wifi, interval_total);
    uint32_t tcpip_pct = percent_tenths(tcpip, interval_total);
    uint32_t web_pct = percent_tenths(web, interval_total);
    ESP_LOGI(TAG,
             "PERF CPU: busy=%" PRIu32 ".%" PRIu32
             "%% idle=%" PRIu32 ".%" PRIu32
             "%% stream=%" PRIu32 ".%" PRIu32
             "%% decode=%" PRIu32 ".%" PRIu32
             "%% output=%" PRIu32 ".%" PRIu32
             "%% wifi=%" PRIu32 ".%" PRIu32
             "%% tcpip=%" PRIu32 ".%" PRIu32
             "%% web=%" PRIu32 ".%" PRIu32
             "%% heap=%u largest=%u tasks=%u",
             busy_pct / 10U, busy_pct % 10U,
             idle_pct / 10U, idle_pct % 10U,
             stream_pct / 10U, stream_pct % 10U,
             decode_pct / 10U, decode_pct % 10U,
             output_pct / 10U, output_pct % 10U,
             wifi_pct / 10U, wifi_pct % 10U,
             tcpip_pct / 10U, tcpip_pct % 10U,
             web_pct / 10U, web_pct % 10U,
             (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT),
             (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),
             (unsigned)count);
#ifndef CONFIG_YORADIO_WEB_TCP_PROBE
    network_heap_profile_poll();
#endif
    tls_path_profile_poll();
}

#ifdef CONFIG_YORADIO_CPU_PROFILE_HTTP
void cpu_profiler_poll(void) {
    // Called only by the single HTTP server task; no second sampler/task.
    // Report an ISR event on the next request, without waiting five seconds.
    report_task_watchdog();
    static int64_t previous_us;
    int64_t now = esp_timer_get_time();
    if (now - previous_us < CPU_PROFILE_INTERVAL_MS * 1000LL) return;
    previous_us = now;
    cpu_profiler_sample();
}
#else
static void cpu_profiler_task(void *argument) {
    (void)argument;
    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(CPU_PROFILE_INTERVAL_MS));
        cpu_profiler_sample();
    }
}
#endif

esp_err_t cpu_profiler_start(void) {
    ESP_ERROR_CHECK(heap_caps_register_failed_alloc_callback(allocation_failed));
#ifdef CONFIG_YORADIO_CPU_PROFILE_HTTP
    return ESP_OK;
#else
    return xTaskCreate(cpu_profiler_task, "cpu_profile",
                       CPU_PROFILE_STACK_BYTES, NULL, 1, NULL) == pdPASS
               ? ESP_OK
               : ESP_ERR_NO_MEM;
#endif
}

#else

esp_err_t cpu_profiler_start(void) {
    return heap_caps_register_failed_alloc_callback(record_allocation_failure);
}

#endif
