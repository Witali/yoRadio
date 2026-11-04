// Explicit HOST public-API doubles for the actual passive target observers.
// Numeric target addresses are labels, never dereferenced or freed by libc.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <mutex>
#include <thread>
#include <vector>
#include "native_health.h"
using TaskHandle_t=void *;
using esp_alloc_failed_hook_t=void (*)(size_t,uint32_t,const char *);
using portMUX_TYPE=std::mutex;
#define portMUX_INITIALIZER_UNLOCKED {}
#define portENTER_CRITICAL(p) (p)->lock()
#define portEXIT_CRITICAL(p) (p)->unlock()
#define portENTER_CRITICAL_ISR(p) (p)->lock()
#define portEXIT_CRITICAL_ISR(p) (p)->unlock()
#define SOC_IRAM_LOW 0x40080000u
#define SOC_IRAM_HIGH 0x400aa000u
#define SOC_DIRAM_IRAM_LOW 0x400a0000u
#define SOC_DIRAM_IRAM_HIGH 0x400c0000u
#define SOC_DIRAM_DRAM_LOW 0x3ffe0000u
#define SOC_DIRAM_DRAM_HIGH 0x40000000u
#define SOC_DRAM_LOW 0x3ffae000u
#define SOC_DRAM_HIGH 0x40000000u
#define MALLOC_CAP_INTERNAL 2048u
#define MALLOC_CAP_32BIT 2u
#define MALLOC_CAP_8BIT 4u
#define MALLOC_CAP_DEFAULT 4096u
static TaskHandle_t decoder=reinterpret_cast<void *>(1);
static TaskHandle_t decode_task_handle=decoder,stream_task_handle=reinterpret_cast<void *>(3),output_task_handle=reinterpret_cast<void *>(4);
static thread_local TaskHandle_t current=reinterpret_cast<void *>(2);
static thread_local bool in_isr,refuse_realloc;
static thread_local int core_override=-1;
static thread_local unsigned task_lookups;
static std::atomic<unsigned> real_realloc_calls,foreign_calls,real_word_allocs,real_word_frees;
static std::atomic<unsigned> live_decoders{5},session_generation{1},http_generation{1};
static native_health_faults_t health;
static std::mutex health_lock;
static const char *forwarded_function;
struct link_t {unsigned reference;};
struct fixture_t {const char *name;const link_t *links[1];unsigned count;};
static link_t link{0};
static fixture_t fixture{"fallback",{&link},1};
static fixture_t *active=&fixture;
static unsigned decode_link_index;
static void check(bool value,const char *reason){if(!value){std::fprintf(stderr,"HOST_FAILURE %s\n",reason);std::fflush(stdout);}assert(value);}
static int xPortGetCoreID(){return core_override>=0?core_override:current==decoder?1:0;}
static unsigned uxTaskPriorityGet(void *){return current==decoder?5:1;}
static bool xPortInIsrContext(){return in_isr;}
static TaskHandle_t xTaskGetCurrentTaskHandle(){++task_lookups;return current;}
static void *esp_cpu_get_sp(){return reinterpret_cast<void *>(in_isr?0x3fff0000u:current==decoder?0x3ffb1000u:0x3ffe0000u);}
static uint8_t *xTaskGetStackStart(TaskHandle_t task){return reinterpret_cast<uint8_t *>(task==decoder?0x3ffb0000u:task==stream_task_handle?0x3ffae000u:0x3ffd0000u);}
static void owner(int core,unsigned priority){check(!in_isr && current==decoder && xPortGetCoreID()==core && uxTaskPriorityGet(nullptr)==priority,"exact_HOST_owner_dispatch");}
static uint64_t esp_timer_get_time(){static std::atomic<uint64_t> ticks;return ++ticks;}
static size_t heap_caps_get_free_size(uint32_t caps){return caps&MALLOC_CAP_8BIT?40000:120000;}
static size_t heap_caps_get_largest_free_block(uint32_t caps){return caps&MALLOC_CAP_8BIT?10000:100000;}
static bool span(const void *p,uintptr_t low,uintptr_t high){auto a=reinterpret_cast<uintptr_t>(p);return a>=low && a<high;}
static bool esp_ptr_in_iram(const void *p){return span(p,SOC_IRAM_LOW,SOC_IRAM_HIGH);}
static bool esp_ptr_in_dram(const void *p){return span(p,SOC_DRAM_LOW,SOC_DRAM_HIGH);}
static bool esp_ptr_in_diram_iram(const void *p){return span(p,SOC_DIRAM_IRAM_LOW,SOC_DIRAM_IRAM_HIGH);}
static bool esp_ptr_in_diram_dram(const void *p){return span(p,SOC_DIRAM_DRAM_LOW,SOC_DIRAM_DRAM_HIGH);}
static bool esp_ptr_internal(const void *p){return span(p,SOC_DRAM_LOW,SOC_DIRAM_IRAM_HIGH);}
static bool esp_ptr_byte_accessible(const void *p){return esp_ptr_in_dram(p);}
static bool esp_ptr_executable(const void *p){return esp_ptr_in_iram(p);}
static void *esp_ptr_diram_iram_to_dram(const void *p){return reinterpret_cast<void *>(SOC_DIRAM_DRAM_HIGH-(reinterpret_cast<uintptr_t>(p)-SOC_DIRAM_IRAM_LOW)-4);}
static void *esp_ptr_diram_dram_to_iram(const void *p){return reinterpret_cast<void *>(SOC_DIRAM_IRAM_LOW+SOC_DIRAM_DRAM_HIGH-reinterpret_cast<uintptr_t>(p)-4);}
static esp_alloc_failed_hook_t registered_callback;
static unsigned real_registrations;
extern "C" esp_err_t __real_heap_caps_register_failed_alloc_callback(esp_alloc_failed_hook_t callback){++real_registrations;if(!callback)return ESP_ERR_INVALID_ARG;registered_callback=callback;return ESP_OK;}
static void original_health_callback(size_t bytes,uint32_t caps,const char *function){std::lock_guard<std::mutex> lock(health_lock);++health.allocation_failures;health.allocation_size=(uint32_t)bytes;health.allocation_caps=caps;forwarded_function=function;}
extern "C" void *__real_realloc(void *pointer,size_t bytes){
    ++real_realloc_calls;
    if(current!=decoder || in_isr)++foreign_calls;
    if(refuse_realloc && bytes){refuse_realloc=false;check(registered_callback,"real_public_callback_registered");unsigned lookups=task_lookups;registered_callback(bytes,6144,"heap_caps_realloc");check(task_lookups==lookups,"callback_does_not_call_task_getter");return nullptr;}
    return pointer?pointer:reinterpret_cast<void *>(0x3ffd0000);
}
extern "C" void *__real_heap_caps_malloc(size_t,uint32_t){unsigned i=real_word_allocs.fetch_add(1);return reinterpret_cast<void *>(0x40081000u+i*0x1000u);}
extern "C" void __real_heap_caps_free(void *){++real_word_frees;}
#include "allocation_fault_observer.inc"
#include "word_alloc_observer.inc"

int main(int argc,char **argv){
    check(argc==2,"explicit_HOST_vector");const char *mode=argv[1];
    check(__wrap_heap_caps_register_failed_alloc_callback(nullptr)==ESP_ERR_INVALID_ARG && !registered_callback,"NULL_registration_preserves_SDK_contract");
    check(__wrap_heap_caps_register_failed_alloc_callback(original_health_callback)==ESP_OK,"original_health_callback_is_registered");
    auto installed=registered_callback;
    check(__wrap_heap_caps_register_failed_alloc_callback(nullptr)==ESP_ERR_INVALID_ARG && installed==registered_callback && real_registrations==3,"NULL_registration_does_not_replace_original");
    if(!std::strcmp(mode,"unpublished")){
        current=decoder;unsigned lookup=task_lookups;registered_callback(42,6144,"heap_caps_realloc");
        check(task_lookups==lookup && allocation_callbacks.unknown==1 && allocation_callbacks.forwarded==1,"unpublished_stack_callback_forwards_without_task_lookup");
        allocation_fault_set_owner(decoder);record_native_fault_counters(health);record_allocation_fault_complete(health);return 2;
    }
    allocation_fault_set_owner(decoder);word_alloc_set_owner(decoder);
    unsigned lookups=task_lookups;
    in_isr=true;auto pointer=reinterpret_cast<void *>(0x3ffb4000);check(__wrap_realloc(pointer,16)==pointer,"ISR_realloc_is_forwarded_unchanged");in_isr=false;
    check(task_lookups==lookups && allocation_realloc_calls==0,"ISR_does_not_access_decoder_context");
    if(!std::strcmp(mode,"opaque")){
        in_isr=true;core_override=1;lookups=task_lookups;const char *opaque=reinterpret_cast<const char *>(1);registered_callback(123,4,opaque);in_isr=false;
        check(task_lookups==lookups && forwarded_function==opaque && health.allocation_failures==1 && allocation_callbacks.forwarded==1 && allocation_callbacks.unknown==1 && allocation_callbacks.records[0].function==opaque,"callback_never_reads_opaque_function_pointer_or_looks_up_task_and_forwards_once");
        std::puts("HOST_ALLOC_OBSERVER mode=opaque forwarded=1 unknown=1 opaque_dereferenced=0 native_heap=0");return 0;
    }
    if(!std::strcmp(mode,"unknown") || !std::strcmp(mode,"overflow")){
        core_override=1; // Foreign task on the decoder's core, different stack.
        unsigned count=!std::strcmp(mode,"overflow")?9:1;
        lookups=task_lookups;for(unsigned i=0;i<count;++i)registered_callback(42,4,"heap_caps_malloc");
        check(task_lookups==lookups && health.allocation_failures==count && allocation_callbacks.forwarded==count,"all_unknown_callbacks_still_forwarded_once_without_task_lookup");
        record_native_fault_counters(health);record_allocation_fault_complete(health);return 2;
    }
    const bool recovered=!std::strncmp(mode,"recovered",9);
    check(recovered || !std::strcmp(mode,"zero"),"known_HOST_vector");
    std::atomic<bool> running{true},foreign_started{false};
    std::thread foreign([&]{current=reinterpret_cast<void *>(2);while(running){core_override=foreign_calls.load()%2;check(__wrap_realloc(pointer,777)==pointer,"foreign_realloc_result_preserved");foreign_started=true;}});
    while(!foreign_started)std::this_thread::yield();
    current=decoder;
    lookups=task_lookups;check(__wrap_realloc(pointer,0)==pointer && task_lookups==lookups,"zero_size_call_is_forwarded_without_failed_allocation_claim");
    for(unsigned i=0;i<5;++i)std::printf("CYD_F1_OBS_OPEN fixture=fallback link=0 kind=raw instance=%u stream=%u generation=1 result=0 live=%u\n",i+1,i,i+1);
    refuse_realloc=recovered;
    void *old=!std::strcmp(mode,"recovered_initial")?nullptr:pointer;
    void *result=__wrap_realloc(old,15360);check(result==(recovered?nullptr:pointer),"actual_HOST_return_not_rewritten");
    std::vector<void *> planes;
    for(unsigned i=0;i<8;++i){auto p=__wrap_heap_caps_malloc(1920,2050);check(p,"planned_word_plane_public_return");planes.push_back(p);}
    for(unsigned i=0;i<5;++i)std::printf("CYD_F1_OBS_CALL fixture=fallback link=0 kind=raw instance=%u stream=%u call=1 input=20 consumed=20 capacity=3840 decoded=%u needed=0 retry=0 advanced=1 result=0\n",i+1,i,i<3?3840:1920);
    std::puts("CYD_F1_LINK fixture=fallback index=0 reference=0 channels=8 layout=1 gain_q8=0 bytes=15360 sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
    for(unsigned i=0;i<5;++i)std::printf("CYD_F1_OBS_CLOSE fixture=fallback link=0 kind=raw instance=%u stream=%u calls=1 consumed=20 decoded=%u resizes=0 retries=0 pending=0 buffer_pending=0 result=0\n",i+1,i,i<3?3840:1920);
    live_decoders=0;for(auto p:planes)__wrap_heap_caps_free(p);
    running=false;foreign.join();
    check(foreign_calls>0 && allocation_realloc_calls==1 && allocation_realloc_returns==1 && !allocation_realloc_inflight,"concurrent_foreign_calls_do_not_race_decoder_context");
    check(allocation_callbacks.callbacks==health.allocation_failures && allocation_callbacks.forwarded==health.allocation_failures && !allocation_callbacks.unknown && !allocation_callbacks.overflow,"original_health_and_passive_counters_agree");
    current=reinterpret_cast<void *>(2);
    record_native_fault_counters(health);record_word_alloc_complete();record_allocation_fault_complete(health);
    std::printf("HOST_ALLOC_OBSERVER mode=%s forwarded=%u owner_calls=1 foreign_calls=%u word_allocs=%u word_frees=%u native_heap=0\n",mode,health.allocation_failures,foreign_calls.load(),real_word_allocs.load(),real_word_frees.load());
}
