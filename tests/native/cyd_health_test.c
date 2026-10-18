#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "native_health.c"

static esp_alloc_failed_hook_t allocation_callback;
static bool fail_registration,fail_create,fail_ipc,fail_snapshot,replace_role;
static unsigned create_calls,ipc_calls;
static BaseType_t current_core;
static configRUN_TIME_COUNTER_TYPE fake_total;
static TaskStatus_t fake_tasks[6];
static int64_t clock_us;
esp_err_t heap_caps_register_failed_alloc_callback(esp_alloc_failed_hook_t callback) {
    if (fail_registration)return ESP_FAIL;
    allocation_callback=callback;return ESP_OK;
}
int64_t esp_timer_get_time(void) {return clock_us;}
BaseType_t xPortGetCoreID(void) {return current_core;}
esp_err_t esp_ipc_call_blocking(uint32_t core,void (*callback)(void *),void *argument) {
    assert(core==((unsigned)current_core^1U));++ipc_calls;
    if (fail_ipc)return ESP_FAIL;
    callback(argument);return ESP_OK;
}
TaskHandle_t xTaskGetIdleTaskHandleForCore(BaseType_t core) {
    assert(core==0 || core==1);return (void *)(uintptr_t)(16+core);
}
BaseType_t xTaskCreatePinnedToCore(void (*task)(void *),const char *name,unsigned stack,
        void *arg,unsigned priority,TaskHandle_t *handle,BaseType_t core) {
    assert(task && !strcmp(name,"native_health") && stack==4096 && !arg && priority==1 && !handle && core==0);
    ++create_calls;return fail_create ? 0 : pdPASS;
}
void vTaskDelay(TickType_t ticks) {(void)ticks;assert(false);}
UBaseType_t uxTaskGetSystemState(TaskStatus_t *output,UBaseType_t capacity,
                                configRUN_TIME_COUNTER_TYPE *total) {
    assert(capacity==32 && output && total);
    if (fail_snapshot)return 0;
    memcpy(output,fake_tasks,sizeof(fake_tasks));*total=fake_total;
    if (replace_role) {
        replace_role=false;native_health_track_task(NATIVE_HEALTH_DECODE,(void *)99);
    }
    return 6;
}
static void *fault_writer(void *arg) {
    unsigned id=(unsigned)(uintptr_t)arg;
    for (unsigned i=0;i<30000;++i) {
        allocation_callback(64+id,256+id,"ignored");
        native_health_decoder_failure(id,id,NATIVE_HEALTH_PROCESS,-(int32_t)id,100+id,200+id);
        native_health_output_failure(id,NATIVE_HEALTH_OUTPUT_WRITE,-(int32_t)id);
        native_health_stream_failure(id,100+id,-(int32_t)id);
        native_health_faults_t f=native_health_snapshot().faults;
        assert(f.decoder_generation==f.decoder_codec && f.decoder_result==-(int32_t)f.decoder_codec);
        assert(f.decoder_completion==100+f.decoder_codec && f.decoder_input_bytes==200+f.decoder_codec);
        assert(f.decoder_allocation_sequence<=f.allocation_failures);
        assert(f.allocation_caps==256+f.allocation_size-64);
        assert(f.output_result==-(int32_t)f.output_generation);
        assert(f.stream_result==-(int32_t)f.stream_generation && f.stream_completion==100+f.stream_generation);
    }
    return NULL;
}
#ifdef TEST_DIAGNOSTIC
static void profile_begin(configRUN_TIME_COUNTER_TYPE total) {
    s_health_primed=false;fake_total=total;fail_ipc=fail_snapshot=replace_role=false;
    clock_us=10000000;
    for(unsigned i=0;i<6;++i) {
        fake_tasks[i]=(TaskStatus_t){.xHandle=(void *)(uintptr_t)(i<2 ? 16+i : 30+i),
            .pcTaskName=(const char *)1, // Deliberately invalid: names must never be dereferenced.
            .xTaskNumber=100+i,.ulRunTimeCounter=total/2,.usStackHighWaterMark=1000+i};
        if(i>=2)native_health_track_task((native_health_task_t)(i-2),fake_tasks[i].xHandle);
    }
}
static void profile_step(configRUN_TIME_COUNTER_TYPE elapsed,
                         configRUN_TIME_COUNTER_TYPE idle0,configRUN_TIME_COUNTER_TYPE idle1,
                         configRUN_TIME_COUNTER_TYPE decode) {
    fake_total+=elapsed;clock_us+=(int64_t)elapsed;
    fake_tasks[0].ulRunTimeCounter+=idle0;fake_tasks[1].ulRunTimeCounter+=idle1;
    fake_tasks[3].ulRunTimeCounter+=decode;native_health_sample();
}
static void test_cpu(void) {
    assert(!health_interval_supported(0) && !health_interval_supported(UINT64_MAX));
    profile_begin(1000);native_health_sample();assert(!native_health_snapshot().cpu.available);
    assert(native_health_snapshot().cpu.task[NATIVE_HEALTH_DECODE].present);
    assert(!native_health_snapshot().cpu.task[NATIVE_HEALTH_DECODE].available);
    assert(native_health_snapshot().cpu.task[NATIVE_HEALTH_DECODE].stack_free_min==1003);
    profile_step(1000,1000,0,600);
    native_health_cpu_t cpu=native_health_snapshot().cpu;
    assert(cpu.enabled && cpu.available && cpu.core_tenths[0]==0 && cpu.core_tenths[1]==1000);
    assert(cpu.overall_tenths==500 && cpu.task[NATIVE_HEALTH_DECODE].percent_tenths==600);
    assert(cpu.task[NATIVE_HEALTH_DECODE].stack_free_min==1003);
    current_core=1;profile_step(1000,500,500,1000);current_core=0;
    cpu=native_health_snapshot().cpu;assert(cpu.overall_tenths==500);
    assert(cpu.core_tenths[0]==500 && cpu.core_tenths[1]==500 && cpu.task[NATIVE_HEALTH_DECODE].percent_tenths==1000);
    // The same address can belong to a new task. Do not subtract its counter
    // from the deleted task's counter, or report a huge wrapped CPU spike.
    ++fake_tasks[3].xTaskNumber;fake_tasks[3].ulRunTimeCounter=0;
    profile_step(1000,500,500,100);assert(!native_health_snapshot().cpu.task[NATIVE_HEALTH_DECODE].available);
    profile_step(1000,500,500,250);assert(native_health_snapshot().cpu.task[NATIVE_HEALTH_DECODE].percent_tenths==250);
    replace_role=true;profile_step(1000,500,500,250);
    assert(!native_health_snapshot().cpu.task[NATIVE_HEALTH_DECODE].available);
    assert(!native_health_snapshot().cpu.task[NATIVE_HEALTH_DECODE].stack_free_min);
    fail_snapshot=true;native_health_sample();fail_snapshot=false;
    cpu=native_health_snapshot().cpu;assert(!cpu.available && cpu.snapshot_failures==1);
    profile_step(1000,500,500,100);assert(!native_health_snapshot().cpu.available);
    profile_step(1000,500,500,100);assert(native_health_snapshot().cpu.available);
    fail_ipc=true;native_health_sample();fail_ipc=false;
    assert(!native_health_snapshot().cpu.available && native_health_snapshot().cpu.snapshot_failures==2);
    // Exercise wrap at the selected SDK counter width, not the host's size_t.
    configRUN_TIME_COUNTER_TYPE maximum=(configRUN_TIME_COUNTER_TYPE)-1;
    profile_begin(maximum-100);
    fake_tasks[0].ulRunTimeCounter=maximum-150;
    fake_tasks[3].ulRunTimeCounter=maximum-50;
    native_health_sample();
    profile_step(300,300,0,150);cpu=native_health_snapshot().cpu;
    assert(cpu.available && cpu.overall_tenths==500 && cpu.task[NATIVE_HEALTH_DECODE].percent_tenths==500);
    native_health_sample();assert(!native_health_snapshot().cpu.available); // Zero interval.
    puts("PASS CYD CPU: both cores/denominator, per-task capacity, IPC accounting seam, no task-name dereference, handle reuse/replacement, 32/64-bit wrap and unavailable snapshots");
}
#endif
static void test_json(void) {
    native_health_snapshot_t snapshot={.faults={
        .allocation_failures=UINT32_MAX,.allocation_size=UINT32_MAX,.allocation_caps=UINT32_MAX,
        .decoder_failures=UINT32_MAX,.decoder_generation=UINT32_MAX,.decoder_codec=UINT32_MAX,
        .decoder_stage=UINT32_MAX,.decoder_result=INT32_MIN,.decoder_completion=UINT32_MAX,
        .decoder_input_bytes=UINT32_MAX,.decoder_allocation_sequence=UINT32_MAX,
        .stream_failures=UINT32_MAX,.stream_generation=UINT32_MAX,.stream_completion=UINT32_MAX,.stream_result=INT32_MIN,
        .output_failures=UINT32_MAX,.output_generation=UINT32_MAX,.output_result=INT32_MIN,
        .output_stage=UINT32_MAX,.output_write_errors=UINT32_MAX,.output_configure_errors=UINT32_MAX,.output_flush_errors=UINT32_MAX},
        .cpu={.enabled=true,.available=true,.sampled_us=UINT64_MAX,.snapshot_failures=UINT32_MAX,
              .overall_tenths=500,.core_tenths={0,1000}}};
    for(unsigned role=0;role<NATIVE_HEALTH_TASKS;++role)
        snapshot.cpu.task[role]=(native_health_task_cpu_t){.present=true,.available=true,
            .percent_tenths=600,.stack_free_min=UINT32_MAX};
    native_health_runtime_t runtime={.boot_id=UINT64_MAX,.uptime_ms=UINT64_MAX,.reset_reason=UINT32_MAX,
        .heap_free=UINT32_MAX,.heap_largest=UINT32_MAX,.heap_minimum=UINT32_MAX,.tasks=UINT32_MAX,.cores=2,
        .internal_free=UINT32_MAX,.internal_largest=UINT32_MAX,.dma_free=UINT32_MAX,.dma_largest=UINT32_MAX,
        .input={.available=true,.leased=true,.resident=UINT32_MAX,.minimum=UINT32_MAX,.target=UINT32_MAX,
            .limit=UINT32_MAX,.ready=UINT32_MAX,.reading=UINT32_MAX,.writing=UINT32_MAX,.released=UINT32_MAX,
            .ready_payload_bytes=UINT32_MAX,.reading_payload_bytes=UINT32_MAX}};
    char complete[4096];assert(native_health_format_json(complete,sizeof(complete),&snapshot,&runtime));
    size_t bytes=strlen(complete);assert(bytes<2304);
    printf("HEALTH_MAX=%s\n",complete);
    for(size_t capacity=0;capacity<=bytes+1;++capacity) {
        char guarded[4096];memset(guarded,0x7e,sizeof(guarded));
        bool ok=native_health_format_json(guarded,capacity,&snapshot,&runtime);
        assert(ok==(capacity>bytes));
        for(size_t i=capacity;i<sizeof(guarded);++i)assert(guarded[i]==0x7e);
        if(ok)assert(!strcmp(guarded,complete));
    }
    snapshot.cpu=(native_health_cpu_t){0};
    assert(native_health_format_json(complete,sizeof(complete),&snapshot,&runtime));
    assert(strstr(complete,"\"overall_percent\":null") && strstr(complete,"\"stack_free_min\":null"));
    runtime.cores=1;assert(native_health_format_json(complete,sizeof(complete),&snapshot,&runtime));
    assert(strstr(complete,"\"core_percent\":[null]"));
    runtime.cores=3;assert(!native_health_format_json(complete,sizeof(complete),&snapshot,&runtime));
    assert(!native_health_format_json(NULL,0,&snapshot,&runtime));
    puts("PASS CYD health JSON: uint32/uint64/int32 limits fit 2304 bytes; every capacity preserves canaries; unavailable CPU/stack remain null");
}
int main(void) {
    fail_registration=true;assert(!native_health_start());fail_registration=false;
#ifdef TEST_DIAGNOSTIC
    fail_create=true;assert(!native_health_start());fail_create=false;
    assert(native_health_snapshot().cpu.enabled && !native_health_snapshot().cpu.available && !ipc_calls);
    create_calls=0;
#endif
    assert(native_health_start() && allocation_callback);
    native_health_track_task((native_health_task_t)-1,(void *)99);
    native_health_track_task(NATIVE_HEALTH_TASKS,(void *)99);
    pthread_t first,second;
    assert(!pthread_create(&first,NULL,fault_writer,(void *)1));
    assert(!pthread_create(&second,NULL,fault_writer,(void *)2));
    assert(!pthread_join(first,NULL) && !pthread_join(second,NULL));
    native_health_faults_t f=native_health_snapshot().faults;
    assert(f.allocation_failures==60000 && f.decoder_failures==60000 && f.output_failures==60000 && f.stream_failures==60000);
    assert(f.output_write_errors==60000 && !f.output_configure_errors && !f.output_flush_errors);
    native_health_output_failure(1,NATIVE_HEALTH_OUTPUT_CONFIGURE,-1);
    native_health_output_failure(2,NATIVE_HEALTH_OUTPUT_FLUSH,-2);
    f=native_health_snapshot().faults;
    assert(f.output_failures==60002 && f.output_write_errors==60000 && f.output_configure_errors==1 && f.output_flush_errors==1);
    assert(f.output_stage==NATIVE_HEALTH_OUTPUT_FLUSH && f.output_generation==2 && f.output_result==-2);
#ifdef TEST_DIAGNOSTIC
    assert(create_calls==1);test_cpu();
#else
    assert(!create_calls && !ipc_calls && !native_health_snapshot().cpu.enabled);
#endif
    assert(native_health_snapshot().faults.allocation_failures==60000);
    test_json();
    puts("PASS CYD health: 60000 concurrent allocation/decoder/output/stream events per category; coherent snapshots; quiet mode has no sampler/IPC; ASan/UBSan");
    return 0;
}
