#include "cpu_profiler.h"

#include <inttypes.h>
#include <stdbool.h>
#include <string.h>

#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#if CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS

#define CPU_PROFILE_INTERVAL_MS 5000U
#define CPU_PROFILE_MAX_TASKS 32U
#define CPU_PROFILE_STACK_BYTES 4096U

static const char *const TAG = "cpu_profile";

typedef struct {
    TaskHandle_t handle;
    configRUN_TIME_COUNTER_TYPE counter;
} task_sample_t;

static task_sample_t s_previous[CPU_PROFILE_MAX_TASKS];
static UBaseType_t s_previous_count;
static configRUN_TIME_COUNTER_TYPE s_previous_total;

static configRUN_TIME_COUNTER_TYPE previous_counter(TaskHandle_t handle) {
    for (UBaseType_t i = 0; i < s_previous_count; ++i) {
        if (s_previous[i].handle == handle) {
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
    return actual != NULL && strcmp(actual, expected) == 0;
}

static void cpu_profiler_task(void *argument) {
    (void)argument;
    TaskStatus_t current[CPU_PROFILE_MAX_TASKS];
    task_sample_t next[CPU_PROFILE_MAX_TASKS];
    bool primed = false;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(CPU_PROFILE_INTERVAL_MS));

        configRUN_TIME_COUNTER_TYPE total = 0;
        UBaseType_t count = uxTaskGetSystemState(
            current, CPU_PROFILE_MAX_TASKS, &total);
        if (count == 0 || count > CPU_PROFILE_MAX_TASKS) {
            ESP_LOGW(TAG, "Task snapshot unavailable (tasks=%u)",
                     (unsigned)count);
            continue;
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
                current[i].ulRunTimeCounter - previous_counter(current[i].xHandle);
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
            } else if (name_is(name, "tiT") || name_is(name, "tcpip_task")) {
                tcpip += delta;
            } else if (name_is(name, "httpd") ||
                       name_is(name, "websocket_status")) {
                web += delta;
            }
            next[i].handle = current[i].xHandle;
            next[i].counter = current[i].ulRunTimeCounter;
        }
        memcpy(s_previous, next, count * sizeof(next[0]));
        s_previous_count = count;
        s_previous_total = total;

        if (!primed || interval_total == 0) {
            primed = true;
            continue;
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
    }
}

esp_err_t cpu_profiler_start(void) {
    return xTaskCreate(cpu_profiler_task, "cpu_profile",
                       CPU_PROFILE_STACK_BYTES, NULL, 1, NULL) == pdPASS
               ? ESP_OK
               : ESP_ERR_NO_MEM;
}

#else

esp_err_t cpu_profiler_start(void) { return ESP_OK; }

#endif
