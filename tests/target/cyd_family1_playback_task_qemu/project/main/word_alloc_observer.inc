// Public allocator forwarding only: no replacement, private heap inspection or
// diagnostic delay. Only the published decoder task accesses the watch table.
#include "esp_attr.h"
#include "esp_memory_utils.h"
#include "soc/soc.h"

struct word_alloc_watch_t {void *pointer;size_t bytes;uint32_t caps;unsigned allocation,generation;};
static word_alloc_watch_t word_alloc_watches[16];
static std::atomic<TaskHandle_t> word_alloc_owner;
static std::atomic<unsigned> word_alloc_sequence,word_alloc_successes,word_alloc_live,word_alloc_peak;
static std::atomic<unsigned> word_alloc_frees,word_alloc_refusals,word_alloc_live_bytes,word_alloc_peak_bytes,word_alloc_inflight;
static_assert(std::atomic<TaskHandle_t>::is_always_lock_free && std::atomic<unsigned>::is_always_lock_free,
    "Allocator dispatch must use native lock-free loads");

static void word_alloc_set_owner(TaskHandle_t task) {
    check(task && !word_alloc_owner.load() && !word_alloc_sequence.load(),"publish_actual_decoder_owner_once");
    word_alloc_owner.store(task,std::memory_order_release);
    printf("CYD_F1_WORD_LIMITS iram_low=%u pure_iram_high=%u iram_high=%u diram_iram_low=%u diram_iram_high=%u diram_dram_low=%u diram_dram_high=%u dram_low=%u dram_high=%u cap_internal=%u cap32=%u cap8=%u owner_core=1 owner_priority=5 owner_published=1\n",
        SOC_IRAM_LOW,SOC_DIRAM_IRAM_LOW,SOC_IRAM_HIGH,SOC_DIRAM_IRAM_LOW,SOC_DIRAM_IRAM_HIGH,
        SOC_DIRAM_DRAM_LOW,SOC_DIRAM_DRAM_HIGH,SOC_DRAM_LOW,SOC_DRAM_HIGH,
        MALLOC_CAP_INTERNAL,MALLOC_CAP_32BIT,MALLOC_CAP_8BIT);
}

static void word_heap_record(const char *operation,const char *stage,unsigned allocation,unsigned generation,
                             size_t bytes,uint32_t caps,void *pointer,bool returned) {
    uintptr_t first=(uintptr_t)pointer,last=first+(bytes>=4?bytes-4:0),alias_first=0,alias_last=0;
    bool diram_i=pointer && esp_ptr_in_diram_iram(pointer) && esp_ptr_in_diram_iram((const void *)last);
    bool diram_d=pointer && esp_ptr_in_diram_dram(pointer) && esp_ptr_in_diram_dram((const void *)last);
    if(diram_i){alias_first=(uintptr_t)esp_ptr_diram_iram_to_dram(pointer);alias_last=(uintptr_t)esp_ptr_diram_iram_to_dram((const void *)last);}
    if(diram_d){alias_first=(uintptr_t)esp_ptr_diram_dram_to_iram(pointer);alias_last=(uintptr_t)esp_ptr_diram_dram_to_iram((const void *)last);}
    // Every public getter is its own observation; other tasks may allocate
    // between them. Neither capability totals nor aliases are additive RAM.
    const unsigned free8=heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
    const unsigned largest8=heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
    const unsigned free32=heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT);
    const unsigned largest32=heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT);
    printf("CYD_F1_WORD_HEAP fixture=%s operation=%s stage=%s allocation=%u generation=%u bytes=%u caps=%u pointer=%llu real_returned=%u attempts=%u successes=%u live_planes=%u peak_planes=%u live_bytes=%u peak_bytes=%u frees=%u refusals=%u inflight=%u live_decoders=%u free8=%u largest8=%u free32=%u largest32=%u heap_snapshot_atomic=0 internal=%u byte_accessible=%u executable=%u in_dram=%u in_iram=%u diram_dram=%u diram_iram=%u pure_iram=%u alias_first_word=%llu alias_last_word=%llu alias_dereferenced=0 time_us=%llu core=%u priority=%u\n",
        active->name,operation,stage,allocation,generation,(unsigned)bytes,(unsigned)caps,(unsigned long long)first,(unsigned)returned,
        word_alloc_sequence.load(),word_alloc_successes.load(),word_alloc_live.load(),word_alloc_peak.load(),
        word_alloc_live_bytes.load(),word_alloc_peak_bytes.load(),word_alloc_frees.load(),word_alloc_refusals.load(),word_alloc_inflight.load(),live_decoders.load(),
        free8,largest8,free32,largest32,
        (unsigned)(pointer && esp_ptr_internal(pointer)),(unsigned)(pointer && esp_ptr_byte_accessible(pointer)),
        (unsigned)(pointer && esp_ptr_executable(pointer)),(unsigned)(pointer && esp_ptr_in_dram(pointer)),
        (unsigned)(pointer && esp_ptr_in_iram(pointer)),(unsigned)diram_d,(unsigned)diram_i,
        (unsigned)(pointer && first>=SOC_IRAM_LOW && first+bytes<=SOC_DIRAM_IRAM_LOW),
        (unsigned long long)alias_first,(unsigned long long)alias_last,(unsigned long long)esp_timer_get_time(),
        (unsigned)xPortGetCoreID(),(unsigned)uxTaskPriorityGet(nullptr));
}

extern "C" void *__real_heap_caps_malloc(size_t,uint32_t);
extern "C" void __real_heap_caps_free(void *);

__attribute__((noinline)) static void *observe_word_alloc(size_t bytes,uint32_t caps) {
    owner(1,5);const unsigned allocation=++word_alloc_sequence,generation=session_generation.load();
    word_alloc_inflight=1;word_heap_record("ALLOC","BEFORE",allocation,generation,bytes,caps,nullptr,false);
    void *pointer=__real_heap_caps_malloc(bytes,caps);
    if(pointer) {
        word_alloc_watch_t *slot=nullptr;
        for(auto &item:word_alloc_watches){check(item.pointer!=pointer,"no_duplicate_live_public_pointer");if(!item.pointer && !slot)slot=&item;}
        check(slot,"bounded_observer_old_plus_candidate_word_planes");*slot={pointer,bytes,caps,allocation,generation};
        ++word_alloc_successes;unsigned live=++word_alloc_live,held=word_alloc_live_bytes.fetch_add(bytes)+bytes;
        word_alloc_peak=std::max(word_alloc_peak.load(),live);word_alloc_peak_bytes=std::max(word_alloc_peak_bytes.load(),held);
    } else ++word_alloc_refusals;
    word_alloc_inflight=0;word_heap_record("ALLOC","AFTER",allocation,generation,bytes,caps,pointer,true);return pointer;
}
__attribute__((noinline)) static void observe_word_free(word_alloc_watch_t *slot) {
    owner(1,5);const word_alloc_watch_t saved=*slot;
    word_alloc_inflight=1;word_heap_record("FREE","BEFORE",saved.allocation,saved.generation,saved.bytes,saved.caps,saved.pointer,false);
    __real_heap_caps_free(saved.pointer);*slot={};--word_alloc_live;word_alloc_live_bytes.fetch_sub(saved.bytes);++word_alloc_frees;
    word_alloc_inflight=0;word_heap_record("FREE","AFTER",saved.allocation,saved.generation,saved.bytes,saved.caps,saved.pointer,true);
}

extern "C" void *IRAM_ATTR __wrap_heap_caps_malloc(size_t bytes,uint32_t caps) {
    if(!bytes || bytes>11520 || caps!=(MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT) || xPortInIsrContext())
        return __real_heap_caps_malloc(bytes,caps);
    TaskHandle_t task=word_alloc_owner.load(std::memory_order_acquire);
    if(!task || xTaskGetCurrentTaskHandle()!=task)return __real_heap_caps_malloc(bytes,caps);
    return observe_word_alloc(bytes,caps);
}
extern "C" void IRAM_ATTR __wrap_heap_caps_free(void *pointer) {
    if(!pointer || xPortInIsrContext()){__real_heap_caps_free(pointer);return;}
    TaskHandle_t task=word_alloc_owner.load(std::memory_order_acquire);
    if(!task || xTaskGetCurrentTaskHandle()!=task){__real_heap_caps_free(pointer);return;}
    // Filter ISR and other tasks BEFORE touching even the live count/table.
    if(word_alloc_live.load(std::memory_order_relaxed)) {
        for(auto &item:word_alloc_watches)if(item.pointer==pointer){observe_word_free(&item);return;}
    }
    __real_heap_caps_free(pointer);
}

static void record_word_alloc_complete() {
    // Called only after real final maintenance has quiesced all owners. These
    // are atomic reads; the coordinator never scans the decoder's watch table.
    const unsigned attempts=word_alloc_sequence.load(),successes=word_alloc_successes.load(),frees=word_alloc_frees.load();
    check(attempts && successes && attempts==successes+word_alloc_refusals.load() && frees==successes &&
        !word_alloc_live.load() && !word_alloc_live_bytes.load() && !word_alloc_inflight.load(),"all_public_word_allocations_really_freed");
    printf("CYD_F1_WORD_COMPLETE attempts=%u successes=%u frees=%u refusals=%u live_planes=%u peak_planes=%u live_bytes=%u peak_bytes=%u inflight=%u owner_only_table=1 atomic_counters=1 final_maintenance=1 diagnostic_delays=0 private_heap=0 application_memory_qualified=0 hardware=0\n",
        attempts,successes,frees,word_alloc_refusals.load(),word_alloc_live.load(),word_alloc_peak.load(),word_alloc_live_bytes.load(),word_alloc_peak_bytes.load(),word_alloc_inflight.load());
}
