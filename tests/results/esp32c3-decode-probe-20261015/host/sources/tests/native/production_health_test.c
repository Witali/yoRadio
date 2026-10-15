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
/* PROFILER_TYPES */
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
/* PROFILER_SOURCE */

/* PIPELINE_PROBE_SOURCE */

/* OUTPUT_HEALTH_TYPE */
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
typedef struct {
    unsigned resident,occupied,minimum,limit,packet_capacity;
    unsigned ready,reading,writing,ready_bytes,reading_bytes;
} adaptive_input_stats_t;
static adaptive_input_stats_t tls_input_reserve_input_stats(void) {
    // Deliberately maximal fields test serialization bounds, not queue consistency.
    return (adaptive_input_stats_t){UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,
        UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX,UINT32_MAX};
}
#endif
#ifdef CONFIG_YORADIO_SHARED_DECODER_ARENA
enum { ARENA_MALLOC,ARENA_FREE,ARENA_REALLOC,ARENA_SNAPSHOT };
typedef struct {
    unsigned capacity,live,peak,blocks,free_bytes,largest,failures;
    struct { uint32_t calls,max_us; } timing[4];
} decoder_arena_stats_t;
static decoder_arena_stats_t decoder_arena_stats(void) {
    decoder_arena_stats_t stats;
    memset(&stats,0xff,sizeof(stats));
    return stats;
}
#endif
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
static char response[4096];
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
/* HEALTH_HANDLER */

int main(void) {
    assert(cpu_profiler_faults().allocation_failures==0);
    assert(cpu_profiler_faults().task_watchdog_events==0);
    register_result=-7;assert(cpu_profiler_start()==-7);
    register_result=0;assert(cpu_profiler_start()==0 && failed_callback);
    for (unsigned mask=0;mask<20;++mask) {
        interrupt_level=mask;
        failed_callback(100+mask, mask, NULL);
        assert(interrupt_level==mask);
        assert(cpu_profiler_faults().allocation_failures==mask+1);
        assert(cpu_profiler_faults().allocation_size==100+mask);
        assert(cpu_profiler_faults().allocation_caps==mask);
        assert(interrupt_level==mask);
    }
    assert(mask_calls>=20);
    cpu_profiler_decoder_failure(2, DECODER_FAILURE_PROCESS, -2, 7, 1234);
    cpu_profiler_faults_t fault = cpu_profiler_faults();
    assert(fault.decoder_failures==1 && fault.decoder_codec==2);
    assert(fault.decoder_result==-2 && fault.decoder_stage==DECODER_FAILURE_PROCESS);
    assert(fault.decoder_completion==7 && fault.decoder_input_bytes==1234);
    assert(fault.decoder_allocation_sequence==20 && interrupt_level==19);
    // Cleanup failures must not change the allocation sequence at decoder failure.
    failed_callback(UINT32_MAX,UINT32_MAX,NULL);
    assert(cpu_profiler_faults().decoder_allocation_sequence==20);
    cpu_profiler_decoder_failure(UINT32_MAX, (decoder_failure_stage_t)UINT32_MAX,
        INT32_MIN, UINT32_MAX, UINT32_MAX);
    s_decoder_failure.decoder_failures=UINT32_MAX;
    s_decoder_failure.decoder_allocation_sequence=UINT32_MAX;
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
    // Feed time includes callbacks, but the separately measured process does not.
    AUDIO_PROBE_DECODE_BEGIN(UINT32_MAX-9);
    uptime_us=UINT32_MAX-4;
    AUDIO_PROBE_PCM_BEGIN();
    audio_pipeline_probe_overrun(5);
    assert(s_audio_pipeline_probe.events[1].work_flags==3);
    assert(s_audio_pipeline_probe.events[1].feed_age==15);
    assert(s_audio_pipeline_probe.events[1].pcm_wait_age==10);
    AUDIO_PROBE_PCM_END();
    audio_pipeline_probe_overrun(6);
    assert(s_audio_pipeline_probe.events[2].work_flags==1);
    assert(s_audio_pipeline_probe.events[2].pcm_wait_age==0);
    AUDIO_PROBE_DECODE_END(1234);
    AUDIO_PROBE_DECODE_BEGIN(8);
    AUDIO_PROBE_DECODE_END(100);
    audio_pipeline_probe_overrun(10);
    assert(s_audio_pipeline_probe.events[3].work_flags==0);
    assert(s_audio_pipeline_probe.events[3].feed_age==0);
    assert(s_audio_pipeline_probe.events[3].last_process_max_us==100);
    assert(s_audio_pipeline_probe.process_max_us==1234);
    memset((void *)&s_audio_pipeline_probe,0,sizeof(s_audio_pipeline_probe));
    uptime_us=INT64_MAX;
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
    // Longest event fields, including inactive/active combinations above.
    s_audio_pipeline_probe.process_max_us=UINT32_MAX;
    for (unsigned n=0;n<AUDIO_PROBE_EVENTS;++n) {
        volatile audio_pipeline_probe_event_t *event=&s_audio_pipeline_probe.events[n];
        event->timestamp_us=UINT32_MAX;
        event->output_age=event->pcm_age=event->input_age=event->network_age=UINT32_MAX;
        event->work_flags=AUDIO_PROBE_FEED_ACTIVE|AUDIO_PROBE_PCM_WAIT_ACTIVE;
        event->feed_age=event->pcm_wait_age=event->last_process_max_us=UINT32_MAX;
    }
    audio_pipeline_probe_t snapshot=s_audio_pipeline_probe;
    // Exercise the longest signed and unsigned failure fields in bounded JSON.
    s_audio_pipeline_probe.stream_failure=(audio_stream_failure_t){
        UINT32_MAX,UINT32_MAX,INT32_MIN,INT32_MIN,INT32_MIN,INT32_MIN};
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
