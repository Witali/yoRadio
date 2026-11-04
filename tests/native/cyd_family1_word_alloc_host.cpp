// HOST public-API seams for the actual diagnostic observer. Numeric ESP32
// addresses are labels only: no heap payload or alias is ever dereferenced.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <thread>
#include <utility>
#include <vector>
using TaskHandle_t=void *;
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
static TaskHandle_t decoder=reinterpret_cast<void *>(1);
static thread_local TaskHandle_t current=reinterpret_cast<void *>(2);
static thread_local bool in_isr;
static thread_local unsigned task_lookups;
static std::atomic<unsigned> real_allocations,real_frees,checked_groups;
static std::atomic<unsigned> live_decoders{5},session_generation{1};
struct fixture_t {const char *name;};
static fixture_t fixture{"old_plus_candidate"};
static fixture_t *active=&fixture;
static void check(bool value,const char *reason){if(!value)std::fprintf(stderr,"HOST_FAILURE %s\n",reason);assert(value);}
static int xPortGetCoreID(){return current==decoder?1:0;}
static unsigned uxTaskPriorityGet(void *){return current==decoder?5:1;}
static bool xPortInIsrContext(){return in_isr;}
static TaskHandle_t xTaskGetCurrentTaskHandle(){++task_lookups;return current;}
static void owner(int core,unsigned priority){check(!in_isr && current==decoder && xPortGetCoreID()==core && uxTaskPriorityGet(nullptr)==priority,"actual_observer_owner_filter");}
static uint64_t esp_timer_get_time(){static std::atomic<uint64_t> ticks;return ++ticks;}
static size_t heap_caps_get_free_size(uint32_t caps){return caps&MALLOC_CAP_8BIT?100:300;}
static size_t heap_caps_get_largest_free_block(uint32_t caps){return caps&MALLOC_CAP_8BIT?200:400;}
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
static std::vector<uintptr_t> returns;
static size_t return_at;
extern "C" void *__real_heap_caps_malloc(size_t bytes,uint32_t caps) {
    ++real_allocations;
    if(current!=decoder || in_isr || !bytes || bytes>11520 || caps!=2050)return reinterpret_cast<void *>(0x3ffd0000);
    check(return_at<returns.size(),"complete_explicit_HOST_return_schedule");return reinterpret_cast<void *>(returns[return_at++]);
}
extern "C" void __real_heap_caps_free(void *){++real_frees;}
#include "word_alloc_observer.inc"
static void planned(std::vector<uintptr_t> values){check(return_at==returns.size(),"all_planned_calls_forwarded");returns=std::move(values);return_at=0;}
static std::vector<uintptr_t> addresses(uintptr_t base,unsigned count,size_t step){std::vector<uintptr_t> result;for(unsigned i=0;i<count;++i)result.push_back(base+i*step);return result;}
static std::vector<void *> allocate(unsigned count,size_t bytes){std::vector<void *> result;for(unsigned i=0;i<count;++i){auto p=__wrap_heap_caps_malloc(bytes,2050);check(p,"planned_success_return");result.push_back(p);}return result;}
static void release(const std::vector<void *> &values){for(void *p:values)__wrap_heap_caps_free(p);}
int main() {
    // Before publishing the owner and on byte/C1/C2 requests, no task lookup or
    // watch state is needed; the exact public call still reaches the seam.
    unsigned lookup=task_lookups,real=real_allocations.load();
    check(__wrap_heap_caps_malloc(16,2050)==reinterpret_cast<void *>(0x3ffd0000),"unpublished_owner_preserves_real_return");
    __wrap_heap_caps_malloc(64,2052);__wrap_heap_caps_malloc(0,2050);__wrap_heap_caps_malloc(11524,2050);__wrap_heap_caps_free(nullptr);
    check(task_lookups==lookup && real_allocations==real+4 && !word_alloc_sequence,"unselected_fast_paths_do_not_observe");
    word_alloc_set_owner(decoder);current=decoder;
    lookup=task_lookups;__wrap_heap_caps_malloc(64,2052);
    check(task_lookups==lookup && !word_alloc_sequence,"cap_check_precedes_task_lookup");++checked_groups;
    std::atomic<bool> running{true};std::atomic<unsigned> foreign_calls{0};
    std::thread foreign([&]{current=reinterpret_cast<void *>(2);while(running){__wrap_heap_caps_malloc(3840,2050);__wrap_heap_caps_free(reinterpret_cast<void *>(0x3ffd0000));++foreign_calls;}});
    auto old_addresses=addresses(0x3ffb0000,8,0x1000),new_addresses=addresses(0x40081000,8,0x3000);
    auto all=old_addresses;all.insert(all.end(),new_addresses.begin(),new_addresses.end());planned(all);
    auto old=allocate(8,3840);unsigned frees=word_alloc_frees.load();
    // Match a live watched pointer in a foreign task and ISR. The public seam
    // deliberately has no payload side effect; this tests observer forwarding,
    // not the validity of freeing production storage from those contexts.
    current=reinterpret_cast<void *>(2);__wrap_heap_caps_free(old[0]);current=decoder;
    in_isr=true;__wrap_heap_caps_free(old[0]);lookup=task_lookups;__wrap_heap_caps_malloc(3840,2050);in_isr=false;
    check(task_lookups==lookup && word_alloc_frees==frees && word_alloc_live==8,"foreign_and_ISR_calls_never_touch_watch_state");++checked_groups;
    auto replacement=allocate(8,11520);check(word_alloc_live==16 && word_alloc_peak==16,"all_old_and_candidate_planes_tracked");
    release(old);release(replacement);check(!word_alloc_live && !word_alloc_live_bytes,"growth_storage_freed_exactly");++checked_groups;
    const unsigned refusal_slots[]={0,3,7};
    for(unsigned failed:refusal_slots) {
        fixture.name=failed==0?"refuse_first":failed==3?"refuse_middle":"refuse_last";++session_generation;
        all=old_addresses;all.insert(all.end(),new_addresses.begin(),new_addresses.begin()+failed);all.push_back(0);planned(all);
        old=allocate(8,3840);replacement=allocate(failed,11520);
        check(!__wrap_heap_caps_malloc(11520,2050),"real_NULL_not_relabelled_success");release(replacement);
        check(word_alloc_live==8 && word_alloc_live_bytes==8*3840,"old_storage_still_observed_after_partial_candidate_cleanup");
        release(old);check(!word_alloc_live,"old_storage_closed_after_failure");++checked_groups;
    }
    fixture.name="shared_aliases";++session_generation;planned({0x400bc000,0x3ffe1300});
    auto p=__wrap_heap_caps_malloc(11520,2050);check(p,"shared_IRAM_alias_return");__wrap_heap_caps_free(p);
    p=__wrap_heap_caps_malloc(11520,2050);check(p,"same_physical_DRAM_after_prior_free");__wrap_heap_caps_free(p);++checked_groups;
    running=false;foreign.join();check(foreign_calls>0 && return_at==returns.size(),"foreign_thread_ran_and_all_returns_forwarded");
    current=reinterpret_cast<void *>(2);record_word_alloc_complete();
    std::printf("HOST_WORD_RESULT groups=%u attempts=%u successes=%u refusals=%u frees=%u foreign_calls=%u hardware=0 native_heap=0\n",
        checked_groups.load(),word_alloc_sequence.load(),word_alloc_successes.load(),word_alloc_refusals.load(),word_alloc_frees.load(),foreign_calls.load());
}
