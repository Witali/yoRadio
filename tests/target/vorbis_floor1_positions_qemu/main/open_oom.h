#pragma once
// Test-only direct public raw callback observer. No decoder-private fields.
#include <stdatomic.h>

#define OOM_LIMIT 256u
typedef struct oom_worker oom_worker_t;
typedef struct {
    unsigned id,calls,injected,fail_n,unexpected;
    bool persistent,overflow,first_success;
    int nested_pair,core;
    size_t sizes[OOM_LIMIT];
    oom_worker_t *worker;
} oom_context_t;
typedef struct {
    int result,close_result;
    unsigned handle,calls,injected,live,packets,bytes;
    bool guards,exact,valid_observation;
} oom_result_t;
typedef struct {
    void *base,*user;
    size_t bytes;
    unsigned id;
    TaskHandle_t owner;
} oom_allocation_t;
static _Thread_local oom_context_t *oom_active;
static portMUX_TYPE oom_lock=portMUX_INITIALIZER_UNLOCKED;
static oom_allocation_t oom_ledger[OOM_LIMIT];
static unsigned oom_next_id;
static bool oom_guards_ok=true;
static uint8_t oom_baseline[28160];
static uint32_t oom_pcm_offsets[15];
static unsigned oom_captured,oom_captured_bytes,oom_discovered[14],oom_bad_calls[14];
static struct {
    unsigned valid,malformed,discoveries,faults,recoveries,recovery_packets,recovery_pcm,nested,tasks;
} oom_totals;
static TaskHandle_t oom_controller;
static void oom_nested_callback(oom_context_t *context);
static void oom_worker_pause(oom_worker_t *worker);
static void oom_worker_first(oom_worker_t *worker);
extern void *__real_media_lib_module_calloc(const char *,size_t,size_t);
extern void __real_media_lib_free(void *);

static unsigned oom_live(unsigned id) {
    unsigned live=0;
    portENTER_CRITICAL(&oom_lock);
    for(unsigned i=0;i<OOM_LIMIT;i++) if(oom_ledger[i].user && (!id || oom_ledger[i].id==id)) live++;
    portEXIT_CRITICAL(&oom_lock);
    return live;
}
static bool oom_guards(void) {
    portENTER_CRITICAL(&oom_lock);bool ok=oom_guards_ok;portEXIT_CRITICAL(&oom_lock);
    return ok;
}
static void oom_init(oom_context_t *context,unsigned nth,bool persistent) {
    memset(context,0,sizeof(*context));context->nested_pair=-1;
    context->fail_n=nth;context->persistent=persistent;context->core=xPortGetCoreID();
    portENTER_CRITICAL(&oom_lock);context->id=++oom_next_id;portEXIT_CRITICAL(&oom_lock);
}
void *__wrap_media_lib_module_calloc(const char *module,size_t count,size_t bytes) {
    oom_context_t *context=oom_active;
    if(!context || !module || strcmp(module,"AUD_Codec"))
        return __real_media_lib_module_calloc(module,count,bytes);
    if(!count || !bytes || count>SIZE_MAX/bytes || count*bytes>UINT32_MAX-47u) {
        context->overflow=true;return NULL;
    }
    size_t size=count*bytes;
    unsigned call=++context->calls;
    if(call>OOM_LIMIT) { context->overflow=true;return NULL; }
    context->sizes[call-1]=size;
    if(call==1 && context->nested_pair>=0) oom_nested_callback(context);
    if(call==1 && context->worker) oom_worker_pause(context->worker);
    if(context->fail_n && (call==context->fail_n || (context->persistent && call>=context->fail_n))) {
        context->injected++;return NULL;
    }
    uint8_t *base=__real_media_lib_module_calloc(module,1,size+47u);
    if(!base) { context->unexpected++;return NULL; }
    uint8_t *user=(uint8_t *)(((uintptr_t)base+31u)&~(uintptr_t)15u);
    memset(user-16,0xa5,16);memset(user+size,0x5a,16);
    bool stored=false;
    portENTER_CRITICAL(&oom_lock);
    for(unsigned i=0;i<OOM_LIMIT;i++) if(!oom_ledger[i].user) {
        oom_ledger[i]=(oom_allocation_t){base,user,size,context->id,xTaskGetCurrentTaskHandle()};
        stored=true;break;
    }
    portEXIT_CRITICAL(&oom_lock);
    if(!stored) { context->overflow=true;__real_media_lib_free(base);return NULL; }
    if(call==1) { context->first_success=true;if(context->worker) oom_worker_first(context->worker); }
    return user;
}
void __wrap_media_lib_free(void *pointer) {
    oom_allocation_t found={0};
    portENTER_CRITICAL(&oom_lock);
    for(unsigned i=0;i<OOM_LIMIT;i++) if(oom_ledger[i].user==pointer && pointer) {
        found=oom_ledger[i];memset(&oom_ledger[i],0,sizeof(oom_ledger[i]));break;
    }
    portEXIT_CRITICAL(&oom_lock);
    if(!found.user) { __real_media_lib_free(pointer);return; }
    uint8_t *user=found.user;
    bool ok=found.owner==xTaskGetCurrentTaskHandle();
    for(unsigned i=0;i<16;i++) if(user[(int)i-16]!=0xa5 || user[found.bytes+i]!=0x5a) ok=false;
    if(!ok) { portENTER_CRITICAL(&oom_lock);oom_guards_ok=false;portEXIT_CRITICAL(&oom_lock); }
    __real_media_lib_free(found.base);
}
static void oom_begin(void) {
    oom_controller=xTaskGetCurrentTaskHandle();
#if CONFIG_IDF_TARGET_ESP32
    printf("VORBIS_OPEN_OOM_BEGIN target=esp32 machine=94 core=%d\n",xPortGetCoreID());
#else
    printf("VORBIS_OPEN_OOM_BEGIN target=esp32c3 machine=243 core=%d\n",xPortGetCoreID());
#endif
}
static void oom_capture(unsigned packet,const uint8_t *data,uint32_t size) {
    if(packet==0) { oom_captured=0;oom_captured_bytes=0;oom_pcm_offsets[0]=0; }
    check(packet==oom_captured && packet<14 && size==fixture_expected_bytes[packet] &&
        size<=sizeof(oom_baseline)-oom_captured_bytes,"oom_baseline_capture");
    oom_pcm_offsets[packet]=oom_captured_bytes;
    memcpy(oom_baseline+oom_captured_bytes,data,size);oom_captured_bytes+=size;
    oom_pcm_offsets[packet+1]=oom_captured_bytes;oom_captured++;
}
static bool oom_decode(void *handle,const uint8_t *packets,const uint32_t *offsets,oom_result_t *result) {
    esp_audio_dec_info_t info={0};
    for(unsigned packet=0;packet<14;packet++) {
        uint32_t size=oom_pcm_offsets[packet+1]-oom_pcm_offsets[packet];
        uint32_t len=offsets[packet+1]-offsets[packet];
        esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)packets+offsets[packet],.len=len};
        esp_audio_dec_out_frame_t out={.buffer=pcm.data,.len=sizeof(pcm.data)};
        arm();int status=__wrap_esp_vorbis_dec_decode(handle,&raw,&out,&info);guard();
        if(status!=ESP_AUDIO_ERR_OK || raw.consumed!=len || out.decoded_size!=size || size>sizeof(pcm.data) ||
           info.sample_rate!=48000 || info.channel!=2 || info.bits_per_sample!=16 ||
           memcmp(pcm.data,oom_baseline+oom_pcm_offsets[packet],size)) return false;
        result->packets++;result->bytes+=size;
        if(!(packet&3)) vTaskDelay(1);
    }
    return result->packets==14 && result->bytes==28160;
}
static oom_result_t oom_open(const floor1_case_t *c,oom_context_t *context,
    const uint8_t *packets,const uint32_t *offsets,bool decode) {
    esp_vorbis_dec_cfg_t cfg={.info_header=(uint8_t *)fixture_info,.info_size=sizeof(fixture_info),
        .setup_header=(uint8_t *)c->setup,.setup_size=c->setup_size};
    void *handle=NULL;oom_context_t *previous=oom_active;oom_active=context;
    oom_result_t result={.close_result=ESP_AUDIO_ERR_OK};
    result.result=__wrap_esp_vorbis_dec_open(&cfg,sizeof(cfg),&handle);
    // A nested caller must not attribute any decode/close allocation to its
    // suspended outer open. The observer covers only each direct open interval.
    oom_active=NULL;
    result.handle=handle!=NULL;
    if(result.result==ESP_AUDIO_ERR_OK && handle) {
        if(decode) result.exact=oom_decode(handle,packets,offsets,&result);
        result.close_result=esp_vorbis_dec_close(handle);
    }
    oom_active=previous;
    result.calls=context->calls;result.injected=context->injected;
    result.live=oom_live(context->id);result.guards=oom_guards();
    result.valid_observation=!context->overflow && !context->unexpected;
    return result;
}
static void oom_clean(oom_result_t result) {
    check(result.valid_observation,"oom_observer_capacity_or_real_failure");
    check(result.live==0 && result.guards && result.close_result==ESP_AUDIO_ERR_OK,"oom_allocation_cleanup");
    check(heap_caps_check_integrity_all(true),"oom_heap_integrity");
}
static void oom_exercise(const floor1_case_t *c,const uint8_t *packets,const uint32_t *offsets) {
    check(c->valid && !checked_owned && oom_captured==14 && oom_captured_bytes==28160,"oom_complete_baseline");
    oom_context_t context;oom_init(&context,0,false);
    oom_result_t discovery=oom_open(c,&context,packets,offsets,true);
    printf("VORBIS_OPEN_OOM_DISCOVER case=%u calls=%u live=%u guards=%u core=%d\n",
        case_index,discovery.calls,discovery.live,(unsigned)discovery.guards,xPortGetCoreID());
    for(unsigned n=0;n<context.calls && n<OOM_LIMIT;n++)
        printf("VORBIS_OPEN_OOM_ALLOC case=%u call=%u bytes=%" PRIu32 "\n",case_index,n+1,(uint32_t)context.sizes[n]);
    oom_clean(discovery);
    check(discovery.result==ESP_AUDIO_ERR_OK && discovery.handle && discovery.exact && discovery.calls>=4,"oom_discovery_result");
    unsigned count=discovery.calls;oom_discovered[case_index]=count;oom_totals.discoveries++;
    for(unsigned mode=0;mode<2;mode++) for(unsigned nth=1;nth<=count;nth++) {
        oom_init(&context,nth,mode!=0);
        oom_result_t fault=oom_open(c,&context,NULL,NULL,false);
        printf("VORBIS_OPEN_OOM_FAULT case=%u mode=%s nth=%u calls=%u injected=%u result=%d handle=%u live=%u guards=%u core=%d\n",
            case_index,mode ? "persistent" : "once",nth,fault.calls,fault.injected,fault.result,
            fault.handle,fault.live,(unsigned)fault.guards,xPortGetCoreID());
        oom_clean(fault);
        check(fault.calls>=nth && fault.calls<=count && fault.injected==(mode ? fault.calls-nth+1 : 1),"oom_fault_observed");
        check(fault.result==ESP_AUDIO_ERR_MEM_LACK,"oom_memory_error");
        check(!fault.handle,"oom_failed_handle_null");oom_totals.faults++;
        oom_init(&context,0,false);
        oom_result_t recovery=oom_open(c,&context,packets,offsets,true);
        printf("VORBIS_OPEN_OOM_RECOVER case=%u mode=%s nth=%u packets=%u pcm=%u baseline_exact=%u live=%u guards=%u core=%d\n",
            case_index,mode ? "persistent" : "once",nth,recovery.packets,recovery.bytes,(unsigned)recovery.exact,
            recovery.live,(unsigned)recovery.guards,xPortGetCoreID());
        oom_clean(recovery);
        check(recovery.result==ESP_AUDIO_ERR_OK && recovery.handle && recovery.exact &&
            recovery.calls==count && !recovery.injected,"oom_full_recovery");
        oom_totals.recoveries++;oom_totals.recovery_packets+=recovery.packets;oom_totals.recovery_pcm+=recovery.bytes;
    }
    oom_totals.valid++;
}
static void oom_malformed(const floor1_case_t *c) {
    oom_context_t context;oom_init(&context,0,false);
    oom_result_t result=oom_open(c,&context,NULL,NULL,false);
    printf("VORBIS_OPEN_OOM_MALFORMED case=%u calls=%u injected=%u result=%d handle=%u live=%u guards=%u core=%d\n",
        case_index,result.calls,result.injected,result.result,result.handle,result.live,(unsigned)result.guards,xPortGetCoreID());
    oom_clean(result);check(!c->valid && result.result==ESP_AUDIO_ERR_FAIL && !result.handle &&
        !result.injected,"oom_malformed_error");oom_bad_calls[case_index]=result.calls;oom_totals.malformed++;
}

static oom_result_t oom_inner;
static void oom_nested_callback(oom_context_t *outer) {
    unsigned pair=(unsigned)outer->nested_pair;
    printf("VORBIS_OPEN_OOM_NEST_ENTER pair=%u outer_call=%u core=%d\n",pair,outer->calls,xPortGetCoreID());
    oom_context_t inner;oom_init(&inner,pair==0 ? 4 : pair==3 ? 1 : 0,false);
    oom_inner=oom_open(&cases[pair==1 ? 8 : 0],&inner,NULL,NULL,false);
    printf("VORBIS_OPEN_OOM_NEST_INNER pair=%u result=%d handle=%u calls=%u injected=%u live=%u guards=%u core=%d\n",
        pair,oom_inner.result,oom_inner.handle,oom_inner.calls,oom_inner.injected,oom_inner.live,
        (unsigned)oom_inner.guards,xPortGetCoreID());
    // The test observer's TLS stack must itself have returned to its outer scope.
    outer->nested_pair=-1;
    if(oom_active!=outer) outer->overflow=true;
}
static void oom_nested(void) {
    for(unsigned pair=0;pair<4;pair++) {
        oom_context_t outer;oom_init(&outer,(pair==1 || pair==2) ? 4 : 0,false);outer.nested_pair=(int)pair;
        oom_result_t result=oom_open(&cases[(pair==0 || pair==3) ? 8 : 0],&outer,NULL,NULL,false);
        bool nested=outer.nested_pair==-1;
        printf("VORBIS_OPEN_OOM_NEST_OUTER pair=%u result=%d handle=%u calls=%u injected=%u live=%u guards=%u nested=%u core=%d\n",
            pair,result.result,result.handle,result.calls,result.injected,result.live,(unsigned)result.guards,
            (unsigned)nested,xPortGetCoreID());
        oom_clean(oom_inner);oom_clean(result);
        int expected_inner=pair==1 ? ESP_AUDIO_ERR_FAIL : pair==2 ? ESP_AUDIO_ERR_OK : ESP_AUDIO_ERR_MEM_LACK;
        int expected_outer=(pair==0 || pair==3) ? ESP_AUDIO_ERR_FAIL : ESP_AUDIO_ERR_MEM_LACK;
        unsigned inner_calls=pair==0 ? 4 : pair==1 ? oom_bad_calls[8] : pair==2 ? oom_discovered[0] : 1;
        check(nested && oom_inner.result==expected_inner && oom_inner.handle==(pair==2) &&
            oom_inner.calls==inner_calls && oom_inner.injected==((pair==0 || pair==3) ? 1u : 0u) &&
            result.result==expected_outer && !result.handle && result.calls==((pair==0 || pair==3) ? oom_bad_calls[8] : 4) &&
            result.injected==((pair==1 || pair==2) ? 1u : 0u),"oom_nested_error_isolation");
        oom_totals.nested++;
    }
}

struct oom_worker {
    TaskHandle_t task;
    unsigned role,scenario;
    int core;
    oom_context_t context;
    oom_result_t result;
    atomic_uint done;
};
static oom_worker_t oom_workers[2];
static unsigned oom_pending;
static void oom_notify(unsigned bit) { xTaskNotify(oom_controller,bit,eSetBits); }
static void oom_wait(unsigned bit) {
    while(!(oom_pending&bit)) {
        uint32_t events=0;
        check(xTaskNotifyWait(0,UINT32_MAX,&events,pdMS_TO_TICKS(5000))==pdTRUE,"oom_task_barrier_timeout");
        oom_pending|=events;
    }
    oom_pending&=~bit;
}
static void oom_worker_pause(oom_worker_t *worker) {
    oom_notify(1u<<worker->role);
    check(ulTaskNotifyTake(pdTRUE,pdMS_TO_TICKS(5000))!=0,"oom_task_release_timeout");
}
static void oom_worker_first(oom_worker_t *worker) {
    if(worker->role==1) oom_notify(16u);
}
static void oom_worker_task(void *argument) {
    oom_worker_t *worker=argument;worker->core=xPortGetCoreID();
    oom_init(&worker->context,worker->role==0 ? 1 : worker->scenario==0 ? 4 : 0,false);
    worker->context.worker=worker;
    worker->result=oom_open(&cases[worker->role==1 && worker->scenario==1 ? 8 : 0],&worker->context,NULL,NULL,false);
    atomic_store_explicit(&worker->done,1,memory_order_release);oom_notify(4u<<worker->role);
    vTaskSuspend(NULL);
}
static void oom_task_result(unsigned scenario,unsigned role) {
    oom_worker_t *worker=&oom_workers[role];oom_result_t result=worker->result;
    printf("VORBIS_OPEN_OOM_TASK_RESULT scenario=%u role=%c result=%d handle=%u calls=%u injected=%u live=%u guards=%u core=%d\n",
        scenario,'A'+(int)role,result.result,result.handle,result.calls,result.injected,result.live,
        (unsigned)result.guards,worker->core);
}
static void oom_tasks(void) {
    for(unsigned scenario=0;scenario<2;scenario++) {
        memset(oom_workers,0,sizeof(oom_workers));oom_pending=0;
        for(unsigned role=0;role<2;role++) {
            oom_worker_t *worker=&oom_workers[role];worker->role=role;worker->scenario=scenario;atomic_init(&worker->done,0);
            int core=role==0 ? 0 : DECODE_CORE;
            check(xTaskCreatePinnedToCore(oom_worker_task,role==0 ? "oom_a" : "oom_b",16384,worker,3,&worker->task,core)==pdPASS,
                "oom_worker_task_create");
            oom_wait(1u<<role);
            printf("VORBIS_OPEN_OOM_TASK_WAIT scenario=%u role=%c call=%u core=%d\n",
                scenario,'A'+(int)role,worker->context.calls,worker->core);
        }
        printf("VORBIS_OPEN_OOM_TASK_RELEASE scenario=%u role=A\n",scenario);
        xTaskNotifyGive(oom_workers[0].task);oom_wait(4u);
        check(atomic_load_explicit(&oom_workers[0].done,memory_order_acquire)==1,"oom_task_a_done");
        oom_task_result(scenario,0);
        printf("VORBIS_OPEN_OOM_TASK_RELEASE scenario=%u role=B\n",scenario);
        xTaskNotifyGive(oom_workers[1].task);oom_wait(16u);
        printf("VORBIS_OPEN_OOM_TASK_FIRST scenario=%u role=B call=1 success=%u core=%d\n",
            scenario,(unsigned)oom_workers[1].context.first_success,oom_workers[1].core);
        oom_wait(8u);check(atomic_load_explicit(&oom_workers[1].done,memory_order_acquire)==1,"oom_task_b_done");
        oom_task_result(scenario,1);
        vTaskDelete(oom_workers[0].task);vTaskDelete(oom_workers[1].task);
        oom_result_t a=oom_workers[0].result,b=oom_workers[1].result;
        oom_clean(a);oom_clean(b);
        check(oom_workers[0].core==0 && oom_workers[1].core==DECODE_CORE &&
            a.result==ESP_AUDIO_ERR_MEM_LACK && !a.handle && a.calls==1 && a.injected==1 &&
            b.result==(scenario==0 ? ESP_AUDIO_ERR_MEM_LACK : ESP_AUDIO_ERR_FAIL) && !b.handle &&
            b.calls==(scenario==0 ? 4 : oom_bad_calls[8]) && b.injected==(scenario==0 ? 1u : 0u) &&
            oom_workers[1].context.first_success,"oom_task_error_isolation");
        printf("VORBIS_OPEN_OOM_TASK_DONE scenario=%u isolated=1\n",scenario);oom_totals.tasks++;
    }
}
static void oom_summary(void) {
    oom_nested();oom_tasks();
    unsigned sum=0;for(unsigned i=0;i<8;i++) sum+=oom_discovered[i];
    unsigned live=oom_live(0);bool guards=oom_guards();
    printf("VORBIS_OPEN_OOM_COMPLETE valid=%u malformed=%u discoveries=%u faults=%u recoveries=%u recovery_packets=%u recovery_pcm=%u nested=%u task_scenarios=%u live=%u guards=%u core=%d\n",
        oom_totals.valid,oom_totals.malformed,oom_totals.discoveries,oom_totals.faults,oom_totals.recoveries,
        oom_totals.recovery_packets,oom_totals.recovery_pcm,oom_totals.nested,oom_totals.tasks,live,
        (unsigned)guards,xPortGetCoreID());
    check(oom_totals.valid==8 && oom_totals.malformed==6 && oom_totals.discoveries==8 &&
        oom_totals.faults==2*sum && oom_totals.recoveries==2*sum && oom_totals.recovery_packets==28*sum &&
        oom_totals.recovery_pcm==56320*sum && oom_totals.nested==4 && oom_totals.tasks==2 && !live && guards,
        "oom_complete_matrix");
}
