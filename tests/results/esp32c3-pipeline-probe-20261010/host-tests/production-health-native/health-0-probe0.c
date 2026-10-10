#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#define IRAM_ATTR
#define DRAM_ATTR
#define CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS 0
#define MALLOC_CAP_8BIT 1
#define HTTPD_500_INTERNAL_SERVER_ERROR 500
typedef int esp_err_t;
typedef unsigned UBaseType_t;
typedef struct { uint32_t allocation_failures, task_watchdog_events; } cpu_profiler_faults_t;
static unsigned interrupt_level;
static unsigned mask_calls;
static unsigned mask_interrupts(void) {
    unsigned previous = interrupt_level;
    interrupt_level = 31;
    ++mask_calls;
    return previous;
}
#define portSET_INTERRUPT_MASK_FROM_ISR() mask_interrupts()
#define portCLEAR_INTERRUPT_MASK_FROM_ISR(previous) (interrupt_level = (previous))
static void (*failed_callback)(size_t,uint32_t,const char *);
static int register_result;
static esp_err_t heap_caps_register_failed_alloc_callback(void (*fn)(size_t,uint32_t,const char *)) {
    failed_callback = fn;
    return register_result;
}



static DRAM_ATTR volatile uint32_t s_allocation_failures;

static void IRAM_ATTR record_allocation_failure(size_t size, uint32_t caps,
                                                const char *function) {
    (void)size;
    (void)caps;
    (void)function;
    // C3 is single-core. Preserve the previous interrupt level so task and
    // ISR callers cannot lose an increment. No heap, logging or Flash data.
    UBaseType_t saved_level = portSET_INTERRUPT_MASK_FROM_ISR();
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
    cpu_profiler_faults_t result = {.allocation_failures = s_allocation_failures};
#if CONFIG_ESP_TASK_WDT_EN
    result.task_watchdog_events = s_task_watchdog_events;
#endif
    return result;
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
    UBaseType_t count = uxTaskGetSystemState(
        current, CPU_PROFILE_MAX_TASKS, &total);
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
        } else if (name_is(name, "tcpip") || name_is(name, "tiT") ||
                   name_is(name, "tcpip_task")) {
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




typedef struct {
    bool available;
    uint32_t completion_queue_drops;
    uint32_t write_errors;
} native_audio_output_health_t;
static native_audio_output_health_t output_sample;
static native_audio_output_health_t native_audio_output_health(void) { return output_sample; }

typedef struct { size_t total_free_bytes, largest_free_block, minimum_free_bytes; } multi_heap_info_t;
static multi_heap_info_t heap_sample;
static void heap_caps_get_info(multi_heap_info_t *h, unsigned caps) { assert(caps==1); *h=heap_sample; }
static int64_t uptime_us;
static int64_t esp_timer_get_time(void) { return uptime_us; }
static unsigned esp_reset_reason(void) { return UINT32_MAX; }
static unsigned uxTaskGetNumberOfTasks(void) { return UINT32_MAX; }
static uint64_t s_health_boot_id = UINT64_MAX;
typedef struct { int unused; } httpd_req_t;
static char response[2048];
static esp_err_t httpd_resp_send(httpd_req_t *r, const char *body, int length) {
    (void)r; assert(length>=0 && (size_t)length<sizeof(response));
    memcpy(response,body,(size_t)length);response[length]=0;return 0;
}
static esp_err_t httpd_resp_send_err(httpd_req_t *r, int status, const char *text) {
    (void)r;(void)status;(void)text;return -1;
}
static void httpd_resp_set_type(httpd_req_t *r, const char *type) { (void)r;assert(strstr(type,"application/json")); }
static void httpd_resp_set_hdr(httpd_req_t *r, const char *key, const char *value) {
    (void)r;assert(!strcmp(key,"Cache-Control") && !strcmp(value,"no-store"));
}
static esp_err_t health_handler(httpd_req_t *request) {
    // Snapshot on demand: no sampler task, retained buffers or console output.
    // Use the same 8-bit allocation capability as the existing heap profiler.
    multi_heap_info_t heap;
    heap_caps_get_info(&heap, MALLOC_CAP_8BIT);
    cpu_profiler_faults_t faults = cpu_profiler_faults();
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    // The diagnostic event sequence and output counter must describe the
    // same ISR boundary. Serialize the copied data after restoring IRQs.
    UBaseType_t previous_mask = portSET_INTERRUPT_MASK_FROM_ISR();
    native_audio_output_health_t output = native_audio_output_health();
    audio_pipeline_probe_t probe = s_audio_pipeline_probe;
    portCLEAR_INTERRUPT_MASK_FROM_ISR(previous_mask);
    char body[2048];
#else
    native_audio_output_health_t output = native_audio_output_health();
    char body[512];
#endif
    int length = snprintf(body, sizeof(body),
        "{\"schema\":1,\"boot_id\":\"%016llx\",\"uptime_ms\":%llu,"
        "\"reset_reason\":%u,\"heap\":%lu,\"largest\":%lu,"
        "\"minimum_heap\":%lu,\"tasks\":%lu,"
        "\"allocation_failures\":%lu,\"task_watchdog_events\":%lu,"
        "\"output\":{\"available\":%s,\"completion_queue_drops\":%lu,\"write_errors\":%lu}}",
        (unsigned long long)s_health_boot_id,
        (unsigned long long)(esp_timer_get_time() / 1000),
        (unsigned)esp_reset_reason(), (unsigned long)heap.total_free_bytes,
        (unsigned long)heap.largest_free_block,
        (unsigned long)heap.minimum_free_bytes,
        (unsigned long)uxTaskGetNumberOfTasks(),
        (unsigned long)faults.allocation_failures,
        (unsigned long)faults.task_watchdog_events,
        output.available ? "true" : "false",
        (unsigned long)output.completion_queue_drops,
        (unsigned long)output.write_errors);
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    length = audio_pipeline_probe_append(body, sizeof(body), length, &probe);
#endif
    if (length < 0 || (size_t)length >= sizeof(body)) {
        return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR,
                                   "Health response overflow");
    }
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_send(request, body, length);
}



int main(void) {
    assert(cpu_profiler_faults().allocation_failures==0);
    assert(cpu_profiler_faults().task_watchdog_events==0);
    register_result=-7;assert(cpu_profiler_start()==-7);
    register_result=0;assert(cpu_profiler_start()==0 && failed_callback);
    for (unsigned mask=0;mask<20;++mask) {
        interrupt_level=mask;
        failed_callback(1,0,NULL);
        assert(interrupt_level==mask);
        assert(cpu_profiler_faults().allocation_failures==mask+1);
    }
    assert(mask_calls==20);
#if CONFIG_ESP_TASK_WDT_EN
    for (int i=0;i<17;++i) esp_task_wdt_isr_user_handler();
    assert(cpu_profiler_faults().task_watchdog_events==17);
    s_task_watchdog_events=UINT32_MAX;
#endif
    s_allocation_failures=UINT32_MAX;
    uptime_us=INT64_MAX;
    heap_sample=(multi_heap_info_t){UINT32_MAX,UINT32_MAX,UINT32_MAX};
    output_sample=(native_audio_output_health_t){true,UINT32_MAX,UINT32_MAX};
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    // Check every phase, ring overwrite and unsigned sequence/timer wrap.
    for (unsigned n=0;n<40;++n) {
        s_audio_pipeline_probe.output_wait=n & 1;
        s_audio_pipeline_probe.decoder_wait=n & 2;
        s_audio_pipeline_probe.stream_read=n & 4;
        s_audio_pipeline_probe.output_us=UINT32_MAX-4;
        audio_pipeline_probe_overrun(3);
        assert(s_audio_pipeline_probe.events[(n+1)&15].output_age==8);
        assert(s_audio_pipeline_probe.events[(n+1)&15].phases==(n&7));
    }
    assert(s_audio_pipeline_probe.valid_count==16);
    for (unsigned n=0;n<8;++n) assert(s_audio_pipeline_probe.phase_drops[n]==5);
    s_audio_pipeline_probe.sequence=UINT32_MAX-8;
    memset((void *)s_audio_pipeline_probe.phase_drops,0,sizeof(s_audio_pipeline_probe.phase_drops));
    s_audio_pipeline_probe.phase_drops[7]=UINT32_MAX-8;
    for (unsigned n=0;n<17;++n) audio_pipeline_probe_overrun(UINT32_MAX);
    assert(s_audio_pipeline_probe.sequence==8);
    audio_pipeline_probe_t snapshot=s_audio_pipeline_probe;
    char tiny[8]="{}";
    assert(audio_pipeline_probe_append(tiny,sizeof(tiny),2,&snapshot)==-1);
    assert(audio_pipeline_probe_append(tiny,sizeof(tiny),INT_MAX,&snapshot)==-1);
    output_sample.completion_queue_drops=8;
#endif
    assert(health_handler(NULL)==0);
    puts(response);
#ifndef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    output_sample.available=false;
#endif
    assert(health_handler(NULL)==0);
    puts(response);
    puts("PASS: quiet counters, registration errors, interrupt mask restoration, watchdog and bounded JSON");
}
