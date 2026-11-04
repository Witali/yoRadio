// Diagnostic pressure uses only public allocations. Every targeted production
// call still reaches its real allocator unchanged. No pressure block is read.
#include "esp_cpu.h"
#if CONFIG_HEAP_ABORT_WHEN_ALLOCATION_FAILS
#error "Real NULL controls require the released non-aborting heap policy"
#endif

enum runtime_mode_t { RC_NONE, RC_BYTE_FALLBACK, RC_DUAL_OOM, RC_SCRATCH_OOM };
enum runtime_scope_t { RC_OTHER, RC_PRESSURE8, RC_PRESSURE32, RC_TARGET_BYTE, RC_TARGET_WORD, RC_TARGET_SCRATCH, RC_ORDINARY };
struct pressure_block_t { void *pointer; };
struct callback_event_t { unsigned epoch,scope,bytes,caps,decoder; };
struct allocation_event_t { unsigned epoch,scope,bytes,caps,old_present,returned_null,callbacks_before,callbacks_after,held_blocks,held_bytes; };
static_assert(std::atomic<TaskHandle_t>::is_always_lock_free && std::atomic<unsigned>::is_always_lock_free && std::atomic<uintptr_t>::is_always_lock_free && std::atomic<esp_alloc_failed_hook_t>::is_always_lock_free,"IRAM callback uses only native atomic loads");
static constexpr unsigned RC_PRESSURE_LIMIT=128,RC_CALLBACK_LIMIT=12,RC_ALLOCATION_LIMIT=12;
static pressure_block_t pressure_blocks[RC_PRESSURE_LIMIT];
static DRAM_ATTR callback_event_t callback_events[RC_CALLBACK_LIMIT];
static allocation_event_t allocation_events[RC_ALLOCATION_LIMIT];
static_assert(sizeof(pressure_blocks)+sizeof(callback_events)+sizeof(allocation_events)==1232,"strict32-bit principal static observer footprint");
static unsigned pressure_count,pressure_peak,pressure_bytes,pressure_peak_bytes,allocation_event_count;
static unsigned pressure_allocations,pressure_frees,pressure_probe_nulls;
static DRAM_ATTR portMUX_TYPE callback_mux=portMUX_INITIALIZER_UNLOCKED;
static DRAM_ATTR unsigned callback_count,callback_buffer_start,allocation_buffer_start;
static DRAM_ATTR std::atomic<unsigned> runtime_epoch;
static DRAM_ATTR bool callback_overflow,allocation_overflow;
static DRAM_ATTR std::atomic<esp_alloc_failed_hook_t> production_failed_alloc;
static DRAM_ATTR std::atomic<TaskHandle_t> runtime_owner;
static DRAM_ATTR std::atomic<uintptr_t> runtime_stack_low,runtime_stack_high;
static DRAM_ATTR std::atomic<unsigned> runtime_scope;
static runtime_mode_t runtime_mode;
static unsigned runtime_target_link,runtime_prefix_links;
static bool runtime_armed,runtime_triggered,runtime_unexpected_success;
static unsigned runtime_word_successes,runtime_target_byte_nulls,runtime_target_word_nulls,runtime_target_scratch_nulls;
static bool runtime_raw_growth_observed;
static unsigned runtime_sdk_depth;

extern "C" void *__real_realloc(void *,size_t);
extern "C" void *__real_heap_caps_malloc(size_t,uint32_t);
extern "C" void __real_heap_caps_free(void *);
extern "C" esp_err_t __real_heap_caps_register_failed_alloc_callback(esp_alloc_failed_hook_t);

// This callback never logs, allocates, dereferences function_name or calls a
// heap getter. It preserves the actual production callback on every event.
FORCE_INLINE_ATTR bool runtime_in_decoder_stack() {
    const uintptr_t low=runtime_stack_low.load(std::memory_order_acquire);
    const uintptr_t sp=(uintptr_t)esp_cpu_get_sp();
    return low && !xPortInIsrContext() && esp_cpu_get_core_id()==1 && sp>=low &&
        sp<runtime_stack_high.load(std::memory_order_relaxed);
}
static void IRAM_ATTR runtime_failed_alloc(size_t bytes,uint32_t caps,const char *function_name) {
    const bool decoder=runtime_in_decoder_stack();
    const unsigned scope=decoder?runtime_scope.load(std::memory_order_relaxed):static_cast<unsigned>(RC_OTHER);
    portENTER_CRITICAL_ISR(&callback_mux);
    const unsigned slot=callback_count-callback_buffer_start;
    if(slot<RC_CALLBACK_LIMIT)callback_events[slot]={runtime_epoch.load(std::memory_order_relaxed),scope,(unsigned)bytes,(unsigned)caps,(unsigned)decoder};
    else callback_overflow=true;
    ++callback_count;
    portEXIT_CRITICAL_ISR(&callback_mux);
    auto original=production_failed_alloc.load(std::memory_order_acquire);
    if(original)original(bytes,caps,function_name);
}
extern "C" esp_err_t __wrap_heap_caps_register_failed_alloc_callback(esp_alloc_failed_hook_t callback) {
    if(!callback)return __real_heap_caps_register_failed_alloc_callback(callback);
    check(!production_failed_alloc.load(),"one_original_health_failed_allocation_callback");
    production_failed_alloc.store(callback,std::memory_order_release);
    return __real_heap_caps_register_failed_alloc_callback(runtime_failed_alloc);
}
static unsigned runtime_callback_count() {
    portENTER_CRITICAL(&callback_mux);const unsigned count=callback_count;portEXIT_CRITICAL(&callback_mux);return count;
}
static bool runtime_callback_overflowed() {
    portENTER_CRITICAL(&callback_mux);const bool overflow=callback_overflow;portEXIT_CRITICAL(&callback_mux);return overflow;
}
FORCE_INLINE_ATTR bool runtime_is_owner() {return runtime_in_decoder_stack();}
static void runtime_set_owner(TaskHandle_t owner_task) {
    check(owner_task && owner_task==decode_task_handle && stream_task_handle && output_task_handle &&
        owner_task!=stream_task_handle && owner_task!=output_task_handle && stream_task_handle!=output_task_handle && !runtime_owner.load(),
        "publish_one_distinct_actual_decoder_owner");
    // Public SDK contract: xTaskGetStackStart is the lowest stack address,
    // independent of growth direction. ESP-IDF task creation sizes are bytes.
    static_assert(sizeof(StackType_t)==1 && portSTACK_GROWTH==-1,"released ESP32 byte stack ABI");
    uintptr_t low=(uintptr_t)xTaskGetStackStart(owner_task),stream=(uintptr_t)xTaskGetStackStart(stream_task_handle),
        output=(uintptr_t)xTaskGetStackStart(output_task_handle);
    constexpr uintptr_t decode_bytes=16384,stream_bytes=6144,output_bytes=4096;
    check(low && stream && output && low<=UINTPTR_MAX-decode_bytes && stream<=UINTPTR_MAX-stream_bytes && output<=UINTPTR_MAX-output_bytes,
        "nonoverflowing_public_original_stack_extents");
    check((low+decode_bytes<=stream || stream+stream_bytes<=low) && (low+decode_bytes<=output || output+output_bytes<=low) &&
        (stream+stream_bytes<=output || output+output_bytes<=stream),"public_pipeline_stack_extents_are_disjoint");
    runtime_stack_high.store(low+decode_bytes,std::memory_order_relaxed);runtime_stack_low.store(low,std::memory_order_release);
    runtime_owner.store(owner_task,std::memory_order_release);
    printf("CYD_RC_OWNER stack_low=%llu stack_high=%llu stack_bytes=16384 stream_low=%llu stream_high=%llu output_low=%llu output_high=%llu public_bounds=1 disjoint=1 callback_task_lookup=0 stack_dereferenced=0 core=1 priority=5\n",
        (unsigned long long)low,(unsigned long long)(low+decode_bytes),(unsigned long long)stream,(unsigned long long)(stream+stream_bytes),
        (unsigned long long)output,(unsigned long long)(output+output_bytes));
}
static void runtime_allocation(unsigned scope,size_t bytes,uint32_t caps,bool old_present,void *result,unsigned before) {
    if(scope==RC_ORDINARY && result)return;
    const unsigned slot=allocation_event_count-allocation_buffer_start;
    if(slot<RC_ALLOCATION_LIMIT)allocation_events[slot]={runtime_epoch.load(),scope,(unsigned)bytes,caps,(unsigned)old_present,(unsigned)(result==nullptr),before,runtime_callback_count(),pressure_count,pressure_bytes};
    else allocation_overflow=true;
    ++allocation_event_count;
}
static void runtime_release_pressure() {
    while(pressure_count) {auto &block=pressure_blocks[--pressure_count];__real_heap_caps_free(block.pointer);block={};++pressure_frees;}
    pressure_bytes=0;runtime_scope=RC_ORDINARY;
}
static void runtime_fill_pressure(uint32_t caps,size_t request,unsigned scope) {
    // The loop terminates on public largest-block observations or an actual
    // pressure-helper NULL, and has a fixed bound. Neither proves target NULL.
    runtime_scope=scope;
    for(unsigned step=0;step<RC_PRESSURE_LIMIT && pressure_count<RC_PRESSURE_LIMIT;++step) {
        size_t largest=heap_caps_get_largest_free_block(caps);
        if(largest<request)break;
        size_t bytes=std::min<size_t>(4096,largest>128?largest-128:largest);
        unsigned before=runtime_callback_count();void *pointer=__real_heap_caps_malloc(bytes,caps);
        if(!pointer){++pressure_probe_nulls;runtime_allocation(scope,bytes,caps,false,pointer,before);break;}
        pressure_blocks[pressure_count++]={pointer};pressure_bytes+=bytes;++pressure_allocations;
        pressure_peak=std::max(pressure_peak,pressure_count);pressure_peak_bytes=std::max(pressure_peak_bytes,pressure_bytes);
    }
}
static void runtime_prefix_barrier() {
    const int64_t deadline=esp_timer_get_time()+30000000;
    // Completed source writes are a published observer fence. The renderer's
    // final DMA tail is intentionally left for the real error-terminal flush.
    while(source_complete_links.load(std::memory_order_acquire)<runtime_prefix_links) {
        check(esp_timer_get_time()<deadline,"fixed_completed_prefix_drain_barrier");vTaskDelay(1);
    }
}
extern "C" void *__wrap_realloc(void *pointer,size_t bytes) {
    if(!runtime_is_owner())return __real_realloc(pointer,bytes);
    const bool target=runtime_armed && !runtime_sdk_depth && decode_link_index==runtime_target_link &&
        ((runtime_mode!=RC_SCRATCH_OOM && !pointer && bytes==15360) ||
         (runtime_mode==RC_SCRATCH_OOM && pointer && bytes==23040 && runtime_raw_growth_observed));
    unsigned scope=RC_ORDINARY;
    if(target) {
        runtime_prefix_barrier();runtime_armed=false;runtime_triggered=true;
        runtime_fill_pressure(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT,bytes,RC_PRESSURE8);
        if(runtime_mode==RC_DUAL_OOM)runtime_fill_pressure(MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT,1920,RC_PRESSURE32);
        scope=runtime_mode==RC_SCRATCH_OOM?RC_TARGET_SCRATCH:RC_TARGET_BYTE;
    }
    runtime_scope=scope;unsigned before=runtime_callback_count();const bool old_present=pointer!=nullptr;void *result=__real_realloc(pointer,bytes);
    // Old-pointer presence was captured before realloc; do not inspect an
    // invalidated old pointer after the real allocator returns.
    runtime_allocation(scope,bytes,0,old_present,result,before);
    if(target) {
        if(result){runtime_unexpected_success=true;runtime_release_pressure();}
        else if(scope==RC_TARGET_SCRATCH){++runtime_target_scratch_nulls;runtime_release_pressure();}
        else ++runtime_target_byte_nulls; // Keep pressure through the word decision.
    }
    runtime_scope=RC_ORDINARY;return result;
}
static void *runtime_real_word_alloc(size_t bytes,uint32_t caps) {
    const bool target=!runtime_sdk_depth && runtime_triggered && pressure_count && runtime_target_byte_nulls &&
        (runtime_mode==RC_BYTE_FALLBACK || runtime_mode==RC_DUAL_OOM);
    runtime_scope=target?RC_TARGET_WORD:RC_ORDINARY;
    unsigned before=runtime_callback_count();void *result=__real_heap_caps_malloc(bytes,caps);
    runtime_allocation(runtime_scope.load(),bytes,caps,false,result,before);
    if(target) {
        if(result)++runtime_word_successes;else ++runtime_target_word_nulls;
        if(!result || runtime_word_successes==8)runtime_release_pressure();
    }
    runtime_scope=RC_ORDINARY;return result;
}
static void runtime_arm(runtime_mode_t mode,unsigned link,unsigned prefix) {
    check(!pressure_count && !runtime_armed,"pressure_between_instances_only");
    runtime_mode=mode;runtime_target_link=link;runtime_prefix_links=prefix;runtime_armed=mode!=RC_NONE;
    runtime_triggered=runtime_unexpected_success=runtime_raw_growth_observed=false;
    runtime_word_successes=runtime_target_byte_nulls=runtime_target_word_nulls=runtime_target_scratch_nulls=0;
}
static void runtime_pressure_witness() {
    check(!pressure_count && !pressure_bytes && !runtime_armed && !runtime_unexpected_success,"pressure_withdrawn_after_genuine_target_outcome");
    if(runtime_mode==RC_BYTE_FALLBACK)check(runtime_triggered && runtime_target_byte_nulls==1 && runtime_word_successes==8 && !runtime_target_word_nulls,"real_byte_NULL_then_all_eight_real_word_planes");
    if(runtime_mode==RC_DUAL_OOM)check(runtime_triggered && runtime_target_byte_nulls==1 && runtime_target_word_nulls==1 && !runtime_word_successes,"both_production_backends_really_refused");
    if(runtime_mode==RC_SCRATCH_OOM)check(runtime_triggered && runtime_raw_growth_observed && runtime_target_scratch_nulls==1,"real_public_resize_then_real_scratch_NULL");
    printf("CYD_RC_PRESSURE mode=%u triggered=%u target_byte_nulls=%u target_word_nulls=%u target_scratch_nulls=%u target_word_successes=%u raw_growth=%u pressure_live=%u pressure_bytes=%u pressure_allocations=%u pressure_frees=%u pressure_probe_nulls=%u fabricated_return=0\n",
        (unsigned)runtime_mode,(unsigned)runtime_triggered,runtime_target_byte_nulls,runtime_target_word_nulls,runtime_target_scratch_nulls,runtime_word_successes,(unsigned)runtime_raw_growth_observed,pressure_count,pressure_bytes,pressure_allocations,pressure_frees,pressure_probe_nulls);
}

// Serialize each quiet leg completely, with global ordinals retained, before
// reusing small fixed buffers. Overflow never creates a passing partial trace.
static void runtime_trace_drain() {
    const unsigned callbacks=runtime_callback_count(),callback_first=callback_buffer_start,allocation_first=allocation_buffer_start;
    const unsigned callback_pending=callbacks-callback_first,allocation_pending=allocation_event_count-allocation_first;
    if(runtime_callback_overflowed() || allocation_overflow || callback_pending>RC_CALLBACK_LIMIT || allocation_pending>RC_ALLOCATION_LIMIT)
        printf("CYD_RC_TRACE_OVERFLOW callback_pending=%u allocation_pending=%u callback_limit=%u allocation_limit=%u\n",
            callback_pending,allocation_pending,RC_CALLBACK_LIMIT,RC_ALLOCATION_LIMIT);
    for(unsigned i=0;i<std::min(callback_pending,RC_CALLBACK_LIMIT);++i) {
        const auto &e=callback_events[i];
        printf("CYD_RC_CALLBACK ordinal=%u epoch=%u scope=%u bytes=%u caps=%u decoder=%u forwarded=1\n",callback_first+i+1,e.epoch,e.scope,e.bytes,e.caps,e.decoder);
    }
    for(unsigned i=0;i<std::min(allocation_pending,RC_ALLOCATION_LIMIT);++i) {
        const auto &e=allocation_events[i];
        printf("CYD_RC_ALLOC ordinal=%u epoch=%u scope=%u bytes=%u caps=%u old_present=%u returned_null=%u callbacks_before=%u callbacks_after=%u held_blocks=%u held_bytes=%u real_call=1 fabricated_return=0\n",
            allocation_first+i+1,e.epoch,e.scope,e.bytes,e.caps,e.old_present,e.returned_null,e.callbacks_before,e.callbacks_after,e.held_blocks,e.held_bytes);
    }
    check(!runtime_callback_overflowed() && !allocation_overflow && callback_pending<=RC_CALLBACK_LIMIT && allocation_pending<=RC_ALLOCATION_LIMIT,
        "static_trace_capacity_overflow_is_NONPASS");
    portENTER_CRITICAL(&callback_mux);const bool stable=callback_count==callbacks;
    if(stable) {
        callback_buffer_start=callbacks;
    }
    portEXIT_CRITICAL(&callback_mux);
    check(stable,"no_unattributed_callback_during_quiet_trace_serialization");allocation_buffer_start=allocation_event_count;
}
