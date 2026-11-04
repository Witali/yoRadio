// Owner-local public word-plane accounting. No console/heap observer work
// occurs while diagnostic heap pressure is retained.
struct word_alloc_watch_t {void *pointer;size_t bytes;};
static word_alloc_watch_t word_alloc_watches[16];
static std::atomic<TaskHandle_t> word_alloc_owner;
static std::atomic<unsigned> word_alloc_sequence,word_alloc_successes,word_alloc_live,word_alloc_peak;
static std::atomic<unsigned> word_alloc_frees,word_alloc_refusals,word_alloc_live_bytes,word_alloc_peak_bytes;
static void word_alloc_set_owner(TaskHandle_t task) {
    check(task && !word_alloc_owner.load(),"one_public_word_owner");word_alloc_owner=task;
}
extern "C" void *IRAM_ATTR __wrap_heap_caps_malloc(size_t bytes,uint32_t caps) {
    if(!runtime_is_owner() || !bytes || bytes>11520 || caps!=(MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT))return __real_heap_caps_malloc(bytes,caps);
    owner(1,5);++word_alloc_sequence;void *pointer=runtime_real_word_alloc(bytes,caps);
    if(!pointer){++word_alloc_refusals;return pointer;}
    word_alloc_watch_t *slot=nullptr;
    for(auto &row:word_alloc_watches){check(row.pointer!=pointer,"unique_live_word_allocation");if(!row.pointer && !slot)slot=&row;}
    check(slot,"bounded_sixteen_old_plus_candidate_word_planes");*slot={pointer,bytes};++word_alloc_successes;
    unsigned live=++word_alloc_live,total=word_alloc_live_bytes.fetch_add(bytes)+bytes;
    word_alloc_peak=std::max(word_alloc_peak.load(),live);word_alloc_peak_bytes=std::max(word_alloc_peak_bytes.load(),total);return pointer;
}
extern "C" void IRAM_ATTR __wrap_heap_caps_free(void *pointer) {
    if(runtime_is_owner() && pointer && word_alloc_live.load()) {
        for(auto &row:word_alloc_watches)if(row.pointer==pointer) {
            size_t bytes=row.bytes;__real_heap_caps_free(pointer);row={};--word_alloc_live;word_alloc_live_bytes.fetch_sub(bytes);++word_alloc_frees;return;
        }
    }
    __real_heap_caps_free(pointer);
}
static void record_word_alloc_complete() {
    check(word_alloc_sequence==word_alloc_successes+word_alloc_refusals && word_alloc_successes==word_alloc_frees && !word_alloc_live && !word_alloc_live_bytes,"all_real_word_planes_freed");
    printf("CYD_RC_WORD_COMPLETE attempts=%u successes=%u frees=%u refusals=%u live_planes=%u peak_planes=%u live_bytes=%u peak_bytes=%u diagnostic_delays=1 owner_only_table=1 private_heap=0\n",
        word_alloc_sequence.load(),word_alloc_successes.load(),word_alloc_frees.load(),word_alloc_refusals.load(),word_alloc_live.load(),word_alloc_peak.load(),word_alloc_live_bytes.load(),word_alloc_peak_bytes.load());
}
