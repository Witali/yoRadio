#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cpu_profiler.c"

static unsigned scheduler_depth, destroyed_names, snapshots, cpu_logs, stack_logs;
static bool unavailable;
static char *borrowed_names[9];
static configRUN_TIME_COUNTER_TYPE test_total=1000, counters[9];
static UBaseType_t numbers[9]={1,2,3,4,5,6,7,8,9};
static char last_cpu[1024];
static const char *const names[9]={"IDLE","radio_stream","audio_decode","audio_output",
    "wifi","tcpip","httpd","websocket_statu","temporary"};

void vTaskSuspendAll(void) { ++scheduler_depth; }
BaseType_t xTaskResumeAll(void) {
    assert(scheduler_depth);
    if (!--scheduler_depth) for (unsigned i=0;i<9;++i) {
        if (borrowed_names[i]) {free(borrowed_names[i]);borrowed_names[i]=NULL;++destroyed_names;}
    }
    return 0;
}
UBaseType_t uxTaskGetSystemState(TaskStatus_t *out,UBaseType_t limit,configRUN_TIME_COUNTER_TYPE *total) {
    assert(limit>=9); ++snapshots;
    // Like IDF, the kernel snapshot protects TCBs only until it resumes the
    // scheduler. Simulate a task exit/idle cleanup immediately after resume.
    vTaskSuspendAll();
    *total=test_total;
    unsigned count=unavailable ? 0 : 9;
    for (unsigned i=0;i<count;++i) {
        borrowed_names[i]=malloc(configMAX_TASK_NAME_LEN);assert(borrowed_names[i]);
        snprintf(borrowed_names[i],configMAX_TASK_NAME_LEN,"%s",names[i]);
        out[i]=(TaskStatus_t){.xHandle=(void *)(uintptr_t)(i+1),.pcTaskName=borrowed_names[i],
            .xTaskNumber=numbers[i],.ulRunTimeCounter=counters[i],.usStackHighWaterMark=123+i};
    }
    xTaskResumeAll();
    return count;
}
void test_log(const char *format,...) {
    assert(!scheduler_depth); // No blocking logging while lifetime is pinned.
    char line[1024]; va_list args;va_start(args,format);vsnprintf(line,sizeof(line),format,args);va_end(args);
    if (strstr(line,"PERF CPU:")) {++cpu_logs;snprintf(last_cpu,sizeof(last_cpu),"%s",line);}
    if (strstr(line,"PERF STACK:")) {
        unsigned index=stack_logs%9;
        assert(strstr(line,names[index]));assert(strstr(line,"minimum_free="));++stack_logs;
    }
}
void heap_caps_get_info(multi_heap_info_t *out,uint32_t caps) {(void)caps;memset(out,0,sizeof(*out));}
size_t heap_caps_get_free_size(uint32_t caps) {(void)caps;return 12345;}
size_t heap_caps_get_largest_free_block(uint32_t caps) {(void)caps;return 8192;}
esp_err_t heap_caps_register_failed_alloc_callback(void (*callback)(size_t,uint32_t,const char *)) {(void)callback;return ESP_OK;}
BaseType_t xTaskCreate(void (*fn)(void *),const char *name,unsigned bytes,void *arg,unsigned priority,TaskHandle_t *handle) {
    (void)fn;(void)name;(void)bytes;(void)arg;(void)priority;(void)handle;return pdPASS;
}
void vTaskDelay(TickType_t ticks) {(void)ticks;abort();}
int64_t esp_timer_get_time(void) {return 0;}

static void advance(void) {
    test_total+=1000;
    for (unsigned i=0;i<9;++i) counters[i]+=100;
    cpu_profiler_sample(); assert(!scheduler_depth);
}
int main(void) {
    for (unsigned i=0;i<9;++i) counters[i]=100;
    cpu_profiler_sample(); assert(!cpu_logs && destroyed_names==9);
    advance(); assert(cpu_logs==1);
    assert(strstr(last_cpu,"busy=90.0%") && strstr(last_cpu,"decode=10.0%"));
    assert(strstr(last_cpu,"web=20.0%"));
    // Reuse the same TCB address for a fresh task. Never subtract the previous
    // task's larger counter from this task's new smaller one.
    ++numbers[2]; counters[2]=5; test_total+=1000;
    for (unsigned i=0;i<9;++i) if (i!=2) counters[i]+=100;
    cpu_profiler_sample(); assert(strstr(last_cpu,"decode=0.5%"));
    for (unsigned i=0;i<9;++i) counters[i]=((configRUN_TIME_COUNTER_TYPE)-1)-50;
    test_total=((configRUN_TIME_COUNTER_TYPE)-1)-500;
    cpu_profiler_sample(); advance(); // Runtime counters wrap at either width.
    assert(strstr(last_cpu,"busy=90.0%") && strstr(last_cpu,"decode=10.0%"));
    advance(); assert(stack_logs==9); // Stack survey reads only copied names.
    unsigned before=cpu_logs; cpu_profiler_sample(); assert(cpu_logs==before);
    unavailable=true;cpu_profiler_sample();assert(!scheduler_depth);
    unavailable=false;advance();
    assert(destroyed_names==(snapshots-1)*9);
    puts("PASS C3 profiler: deleted task names copied under scheduler suspension; logs after resume; TCB reuse, counter wrap, zero/unavailable snapshots; ASan/UBSan");
    return 0;
}
