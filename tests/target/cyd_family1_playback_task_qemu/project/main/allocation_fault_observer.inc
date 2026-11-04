// Passive public allocator attribution. The callback may run on either core
// or in an ISR: no heap, printf, string access, or task-owned table scan there.
#include "esp_attr.h"
#include "esp_cpu.h"

struct allocation_callback_record_t {
    unsigned sequence,bytes,caps,attempt,generation,core,isr,decoder_owner,forwarded;
    uintptr_t stack_pointer;
    const char *function;
};
struct allocation_callback_state_t {
    unsigned callbacks,forwarded,unknown,overflow,registrations,registration_errors;
    allocation_callback_record_t records[8];
};
struct allocation_realloc_context_t {unsigned attempt,generation;};
static DRAM_ATTR allocation_callback_state_t allocation_callbacks;
static DRAM_ATTR portMUX_TYPE allocation_callback_lock=portMUX_INITIALIZER_UNLOCKED;
static DRAM_ATTR std::atomic<TaskHandle_t> allocation_decoder_owner;
static DRAM_ATTR std::atomic<uintptr_t> allocation_decoder_stack_low,allocation_decoder_stack_high;
static DRAM_ATTR std::atomic<esp_alloc_failed_hook_t> allocation_original_callback;
static DRAM_ATTR std::atomic<unsigned> allocation_realloc_calls,allocation_realloc_returns;
static DRAM_ATTR std::atomic<unsigned> allocation_realloc_nulls,allocation_realloc_inflight;
// Only the published decoder and its synchronous failed-allocation callback
// access this context. ISR/foreign callbacks never touch it.
static DRAM_ATTR allocation_realloc_context_t allocation_realloc_context;
static_assert(std::atomic<esp_alloc_failed_hook_t>::is_always_lock_free &&
    std::atomic<TaskHandle_t>::is_always_lock_free && std::atomic<unsigned>::is_always_lock_free &&
    std::atomic<uintptr_t>::is_always_lock_free,
    "Callback dispatch must not call an atomic runtime helper");
static_assert(sizeof(allocation_callbacks)+sizeof(allocation_callback_lock)+
    sizeof(allocation_decoder_owner)+sizeof(allocation_original_callback)+
    sizeof(allocation_decoder_stack_low)+sizeof(allocation_decoder_stack_high)+
    sizeof(allocation_realloc_calls)+sizeof(allocation_realloc_returns)+
    sizeof(allocation_realloc_nulls)+sizeof(allocation_realloc_inflight)+
    sizeof(allocation_realloc_context)<=1024,"Bound passive observer DRAM to one KiB");

extern "C" esp_err_t __real_heap_caps_register_failed_alloc_callback(esp_alloc_failed_hook_t);
extern "C" void *__real_realloc(void *,size_t);

static void IRAM_ATTR allocation_failure_callback(size_t bytes,uint32_t caps,const char *function) {
    const bool isr=xPortInIsrContext();
    const unsigned core=(unsigned)xPortGetCoreID();
    const uintptr_t sp=(uintptr_t)esp_cpu_get_sp();
    const uintptr_t low=allocation_decoder_stack_low.load(std::memory_order_acquire);
    const uintptr_t high=allocation_decoder_stack_high.load(std::memory_order_relaxed);
    // Public, once-published bounds and the inline hardware SP identify this
    // finite decoder stack. Do not call the Flash-resident task getter here.
    const bool owner_task=!isr && core==1 && low && sp>=low && sp<high;
    // function is an opaque pointer until final task-context serialization.
    unsigned attempt=0,generation=0;
    if(owner_task){attempt=allocation_realloc_context.attempt;generation=allocation_realloc_context.generation;}
    portENTER_CRITICAL_ISR(&allocation_callback_lock);
    const unsigned sequence=++allocation_callbacks.callbacks;
    const bool retained=sequence<=8;
    if(retained)allocation_callbacks.records[sequence-1]={sequence,(unsigned)bytes,(unsigned)caps,
        attempt,generation,core,(unsigned)isr,(unsigned)owner_task,0,sp,function};
    else ++allocation_callbacks.overflow;
    if(!owner_task || !attempt)++allocation_callbacks.unknown;
    portEXIT_CRITICAL_ISR(&allocation_callback_lock);
    auto original=allocation_original_callback.load(std::memory_order_acquire);
    // The real health callback remains authoritative and is forwarded once.
    if(original)original(bytes,caps,function);
    portENTER_CRITICAL_ISR(&allocation_callback_lock);
    if(original){++allocation_callbacks.forwarded;if(retained)allocation_callbacks.records[sequence-1].forwarded=1;}
    else ++allocation_callbacks.unknown;
    portEXIT_CRITICAL_ISR(&allocation_callback_lock);
}

extern "C" esp_err_t __wrap_heap_caps_register_failed_alloc_callback(esp_alloc_failed_hook_t callback) {
    // Preserve the SDK's NULL-registration error and existing callback.
    if(!callback)return __real_heap_caps_register_failed_alloc_callback(callback);
    allocation_original_callback.store(callback,std::memory_order_release);
    esp_err_t result=__real_heap_caps_register_failed_alloc_callback(allocation_failure_callback);
    portENTER_CRITICAL(&allocation_callback_lock);
    ++allocation_callbacks.registrations;
    if(result!=ESP_OK)++allocation_callbacks.registration_errors;
    portEXIT_CRITICAL(&allocation_callback_lock);
    return result;
}

static void allocation_fault_set_owner(TaskHandle_t task) {
    check(task && task==decode_task_handle && stream_task_handle && output_task_handle &&
        task!=stream_task_handle && task!=output_task_handle && stream_task_handle!=output_task_handle &&
        !allocation_decoder_owner.load(),"publish_allocation_decoder_owner_once");
    const uintptr_t low=(uintptr_t)xTaskGetStackStart(task),stream=(uintptr_t)xTaskGetStackStart(stream_task_handle),
        output=(uintptr_t)xTaskGetStackStart(output_task_handle);
    constexpr uintptr_t bytes=16384,stream_bytes=6144,output_bytes=4096;
    check(low && stream && output && low<=UINTPTR_MAX-bytes && stream<=UINTPTR_MAX-stream_bytes &&
        output<=UINTPTR_MAX-output_bytes,"nonoverflowing_actual_public_task_stack_bounds");
    check((low+bytes<=stream || stream+stream_bytes<=low) &&
        (low+bytes<=output || output+output_bytes<=low) &&
        (stream+stream_bytes<=output || output+output_bytes<=stream),"unique_original_public_task_stack_extents");
    allocation_decoder_stack_high.store(low+bytes,std::memory_order_relaxed);
    allocation_decoder_stack_low.store(low,std::memory_order_release);
    allocation_decoder_owner.store(task,std::memory_order_release);
    printf("CYD_F1_ALLOC_OWNER task_handle=%llu stack_low=%llu stack_high=%llu stack_bytes=16384 stream_stack_low=%llu stream_stack_high=%llu output_stack_low=%llu output_stack_high=%llu public_bounds=1 unique_checked=1 callback_task_lookup=0 stack_dereferenced=0 owner_core=1 owner_priority=5\n",
        (unsigned long long)(uintptr_t)task,(unsigned long long)low,(unsigned long long)(low+bytes),
        (unsigned long long)stream,(unsigned long long)(stream+stream_bytes),
        (unsigned long long)output,(unsigned long long)(output+output_bytes));
}

__attribute__((noinline)) static void *observe_decoder_realloc(void *pointer,size_t bytes) {
    owner(1,5);
    const unsigned attempt=allocation_realloc_calls.fetch_add(1)+1;
    check(!allocation_realloc_context.attempt,"no_recursive_decoder_realloc_observation");
    allocation_realloc_context={attempt,http_generation.load()};
    allocation_realloc_inflight=1;
    void *result=__real_realloc(pointer,bytes);
    allocation_realloc_context={};allocation_realloc_inflight=0;++allocation_realloc_returns;
    if(!result && bytes) {
        ++allocation_realloc_nulls;
        unsigned first=0,count=0;
        portENTER_CRITICAL(&allocation_callback_lock);
        for(const auto &row:allocation_callbacks.records)if(row.sequence && row.attempt==attempt){if(!first)first=row.sequence;++count;}
        portEXIT_CRITICAL(&allocation_callback_lock);
        check(active && decode_link_index<active->count,"failed_realloc_has_current_public_link");
        printf("CYD_F1_REALLOC_NULL fixture=%s link=%u reference=%u generation=%u attempt=%u bytes=%u old_pointer=%llu returned_pointer=0 callback_first=%u callback_count=%u real_returned=1 time_us=%llu core=1 priority=5\n",
            active->name,decode_link_index,active->links[decode_link_index]->reference,
            (unsigned)http_generation.load(),attempt,(unsigned)bytes,(unsigned long long)(uintptr_t)pointer,
            first,count,(unsigned long long)esp_timer_get_time());
    }
    return result;
}

extern "C" void *IRAM_ATTR __wrap_realloc(void *pointer,size_t bytes) {
    if(!bytes || xPortInIsrContext())return __real_realloc(pointer,bytes);
    if(xPortGetCoreID()!=1)return __real_realloc(pointer,bytes);
    const uintptr_t low=allocation_decoder_stack_low.load(std::memory_order_acquire),sp=(uintptr_t)esp_cpu_get_sp();
    if(!low || sp<low || sp>=allocation_decoder_stack_high.load(std::memory_order_relaxed))return __real_realloc(pointer,bytes);
    return observe_decoder_realloc(pointer,bytes);
}

static void record_native_fault_counters(const native_health_faults_t &f) {
    printf("CYD_F1_NATIVE_FAULTS allocation_failures=%u allocation_size=%u allocation_caps=%u decoder_failures=%u decoder_generation=%u decoder_codec=%u decoder_stage=%u decoder_result=%d decoder_completion=%u decoder_input_bytes=%u decoder_allocation_sequence=%u stream_failures=%u stream_generation=%u stream_completion=%u stream_result=%d output_failures=%u output_generation=%u output_stage=%u output_write_errors=%u output_configure_errors=%u output_flush_errors=%u output_result=%d\n",
        (unsigned)f.allocation_failures,(unsigned)f.allocation_size,(unsigned)f.allocation_caps,
        (unsigned)f.decoder_failures,(unsigned)f.decoder_generation,(unsigned)f.decoder_codec,(unsigned)f.decoder_stage,
        (int)f.decoder_result,(unsigned)f.decoder_completion,(unsigned)f.decoder_input_bytes,(unsigned)f.decoder_allocation_sequence,
        (unsigned)f.stream_failures,(unsigned)f.stream_generation,(unsigned)f.stream_completion,(int)f.stream_result,
        (unsigned)f.output_failures,(unsigned)f.output_generation,(unsigned)f.output_stage,(unsigned)f.output_write_errors,
        (unsigned)f.output_configure_errors,(unsigned)f.output_flush_errors,(int)f.output_result);
}

static void record_allocation_fault_complete(const native_health_faults_t &faults) {
    allocation_callback_state_t observed;
    portENTER_CRITICAL(&allocation_callback_lock);observed=allocation_callbacks;portEXIT_CRITICAL(&allocation_callback_lock);
    bool declared=true;
    for(const auto &row:observed.records)if(row.sequence) {
        printf("CYD_F1_ALLOC_CALLBACK sequence=%u bytes=%u caps=%u function=%s attempt=%u generation=%u core=%u isr=%u decoder_owner=%u forwarded=%u stack_pointer=%llu\n",
            row.sequence,row.bytes,row.caps,row.function?row.function:"NULL",row.attempt,row.generation,row.core,row.isr,row.decoder_owner,row.forwarded,(unsigned long long)row.stack_pointer);
        declared=declared && row.bytes && row.attempt && row.generation && row.core==1 && !row.isr &&
            row.decoder_owner && row.forwarded && row.caps==(MALLOC_CAP_DEFAULT|MALLOC_CAP_INTERNAL) &&
            row.stack_pointer>=allocation_decoder_stack_low.load() && row.stack_pointer<allocation_decoder_stack_high.load() &&
            row.function && !strcmp(row.function,"heap_caps_realloc");
    }
    printf("CYD_F1_ALLOC_COMPLETE callbacks=%u forwarded=%u unknown=%u overflow=%u registrations=%u registration_errors=%u realloc_calls=%u realloc_returns=%u realloc_nulls=%u inflight=%u observer_static_bytes=%u callback_capacity=8 final_maintenance=1 diagnostic_delays=0 private_heap=0 hardware=0\n",
        observed.callbacks,observed.forwarded,observed.unknown,observed.overflow,observed.registrations,observed.registration_errors,
        allocation_realloc_calls.load(),allocation_realloc_returns.load(),allocation_realloc_nulls.load(),allocation_realloc_inflight.load(),
        (unsigned)(sizeof(allocation_callbacks)+sizeof(allocation_callback_lock)+sizeof(allocation_decoder_owner)+
            sizeof(allocation_decoder_stack_low)+sizeof(allocation_decoder_stack_high)+
            sizeof(allocation_original_callback)+sizeof(allocation_realloc_calls)+sizeof(allocation_realloc_returns)+
            sizeof(allocation_realloc_nulls)+sizeof(allocation_realloc_inflight)+sizeof(allocation_realloc_context)));
    check(declared && observed.registrations==1 && !observed.registration_errors && !observed.unknown && !observed.overflow &&
        observed.callbacks==observed.forwarded && observed.callbacks==allocation_realloc_nulls.load() &&
        observed.callbacks==faults.allocation_failures && allocation_realloc_calls==allocation_realloc_returns &&
        !allocation_realloc_inflight.load(),"all_real_allocator_callbacks_attributed_and_forwarded");
    // Per-return callback size/caps/function and actual subsequent word-plane
    // groups/complete source PCM are independently checked by the log reader.
    check(!faults.decoder_failures && !faults.stream_failures && !faults.output_failures,
        "no_native_pipeline_faults");
}
