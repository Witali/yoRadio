#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <inttypes.h>
#include <string.h>
#include <stdarg.h>
#define _Static_assert(c,m) /* RV32 build checks stack bound */
#define RTC_DATA_ATTR
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
static unsigned lock_depth;
#define portENTER_CRITICAL(p) do { (void)(p); ++lock_depth; } while(0)
#define portEXIT_CRITICAL(p) do { (void)(p); assert(lock_depth); --lock_depth; } while(0)
static bool in_isr;
static bool xPortInIsrContext(void) { return in_isr; }
static const char *pcTaskGetName(void *p) { (void)p; return "owner-task-long"; }
static int64_t now;
static int64_t esp_timer_get_time(void) { return now; }
typedef struct { void *start; } walker_heap_into_t;
typedef struct { void *ptr; size_t size; bool used; } walker_block_info_t;
static walker_block_info_t blocks[140];
static unsigned block_count;
#define MALLOC_CAP_8BIT 1
static void heap_caps_walk(unsigned caps, bool (*cb)(walker_heap_into_t,walker_block_info_t,void *), void *ctx) {
    assert(caps==1 && lock_depth);
    for (unsigned i=0;i<block_count;++i) assert(cb((walker_heap_into_t){0},blocks[i],ctx));
}
static void test_log(const char *tag, const char *format, ...) {
    (void)tag; assert(!lock_depth);
    va_list args; va_start(args,format); vprintf(format,args); va_end(args); putchar('\n');
}
#define ESP_LOGI test_log
void esp_heap_trace_alloc_hook(void*,size_t,uint32_t);
void esp_heap_trace_free_hook(void*);
static void *realloc_result;
void __real_heap_caps_free(void *ptr) {
    assert(lock_depth); esp_heap_trace_free_hook(ptr);
}
void *__real_heap_caps_realloc_base(void *ptr,size_t size,uint32_t caps) {
    assert(lock_depth);
    if (!size) { __real_heap_caps_free(ptr); return NULL; }
    if (realloc_result) esp_heap_trace_alloc_hook(realloc_result,size,caps);
    return realloc_result;
}

enum { WATCH_SLOTS = 128, SNAPSHOT_ROWS = 64, OWNER_NAME_BYTES = 12 };
#define WATCH_INTERVAL_US 5000000LL
typedef struct {
    uintptr_t address;
    size_t requested;
    uint32_t id;
    char task[OWNER_NAME_BYTES];
} owner_t;
// Diagnostic storage is outside ordinary SRAM. It still consumes RTC heap
// capacity; the linker checks it fits alongside the existing TCP PCB pool.
static RTC_DATA_ATTR owner_t owners[WATCH_SLOTS];
static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
static RTC_DATA_ATTR uintptr_t first, last;
static RTC_DATA_ATTR uint32_t serial, lost, live, peak, alloc_events, free_events;

static bool overlaps(uintptr_t address, size_t size) {
    return address && address < last &&
           (address >= first || size > first - address);
}

// Hooks run after the allocator releases its heap lock. They copy metadata
// only, never allocate, log or inspect allocated bytes. No stale task handle
// is retained: copy the name while the allocating task is still alive.
void esp_heap_trace_alloc_hook(void *ptr, size_t size, uint32_t caps) {
    (void)caps;
    portENTER_CRITICAL(&lock);
    if (first && overlaps((uintptr_t)ptr, size)) {
        ++alloc_events;
        unsigned slot = WATCH_SLOTS, empty = WATCH_SLOTS;
        for (unsigned i = 0; i < WATCH_SLOTS; ++i) {
            if (owners[i].address == (uintptr_t)ptr) { slot = i; break; }
            if (!owners[i].address) empty = i;
        }
        if (slot == WATCH_SLOTS) slot = empty;
        if (slot == WATCH_SLOTS) ++lost;
        else {
            if (!owners[slot].address && ++live > peak) peak = live;
            owner_t *owner = &owners[slot];
            *owner = (owner_t){.address=(uintptr_t)ptr, .requested=size, .id=++serial};
            const char *name = xPortInIsrContext() ? "ISR" : pcTaskGetName(NULL);
            for (unsigned i = 0; i+1 < OWNER_NAME_BYTES && name[i]; ++i)
                owner->task[i] = name[i];
        }
    }
    portEXIT_CRITICAL(&lock);
}

static void forget(uintptr_t address) {
    for (unsigned i = 0; i < WATCH_SLOTS; ++i) {
        if (address && owners[i].address == address) {
            owners[i] = (owner_t){0};
            --live;
            ++free_events;
            return;
        }
    }
}

void esp_heap_trace_free_hook(void *ptr) {
    portENTER_CRITICAL(&lock);
    if (first) forget((uintptr_t)ptr);
    portEXIT_CRITICAL(&lock);
}

void __real_heap_caps_free(void *ptr);
void *__real_heap_caps_realloc_base(void *ptr, size_t size, uint32_t caps);
void __wrap_heap_caps_free(void *ptr) {
    // C3 only. Prevent address reuse between the real free and IDF's
    // post-free hook. Recursive entry by the same core is supported.
    portENTER_CRITICAL(&lock);
    __real_heap_caps_free(ptr);
    portEXIT_CRITICAL(&lock);
}
void *__wrap_heap_caps_realloc_base(void *ptr, size_t size, uint32_t caps) {
    portENTER_CRITICAL(&lock);
    void *result = __real_heap_caps_realloc_base(ptr, size, caps);
    // In-place resizing is reported by the allocation hook. A successful
    // moving multi_heap_realloc can retire ptr without the public free hook.
    // A failed realloc must preserve the original live allocation.
    if (result && result != ptr) forget((uintptr_t)ptr);
    portEXIT_CRITICAL(&lock);
    return result;
}

typedef struct { uintptr_t address; size_t size; } free_range_t;
static bool largest_free(walker_heap_into_t heap, walker_block_info_t block, void *context) {
    (void)heap;
    free_range_t *range = context;
    if (!block.used && block.size > range->size)
        *range = (free_range_t){(uintptr_t)block.ptr, block.size};
    return true;
}

typedef struct {
    uintptr_t address;
    uint32_t bytes, id, requested;
    char task[OWNER_NAME_BYTES];
} snapshot_row_t;
typedef struct {
    snapshot_row_t rows[SNAPSHOT_ROWS];
    unsigned count, dropped, unknown;
} snapshot_t;
_Static_assert(sizeof(snapshot_t) <= 1900, "Bound decoder probe stack on C3");

static bool capture(walker_heap_into_t heap, walker_block_info_t block, void *context) {
    (void)heap;
    snapshot_t *snapshot = context;
    if (!overlaps((uintptr_t)block.ptr, block.size)) return true;
    if (snapshot->count == SNAPSHOT_ROWS) { ++snapshot->dropped; return true; }
    snapshot_row_t *row = &snapshot->rows[snapshot->count++];
    row->address = (uintptr_t)block.ptr;
    row->bytes = block.size;
    if (!block.used) return true;
    for (unsigned i = 0; i < WATCH_SLOTS; ++i) {
        if (owners[i].address == row->address) {
            row->id = owners[i].id;
            row->requested = owners[i].requested;
            memcpy(row->task, owners[i].task, OWNER_NAME_BYTES);
            return true;
        }
    }
    ++snapshot->unknown;
    memcpy(row->task, "unknown", sizeof("unknown"));
    return true;
}

void heap_fragment_probe_poll(bool idle) {
    static RTC_DATA_ATTR int64_t idle_since, previous;
    static RTC_DATA_ATTR uint32_t sequence;
    const int64_t now = esp_timer_get_time();
    if (!idle) { idle_since = 0; return; }
    if (!idle_since) idle_since = now;
    if (now-idle_since < WATCH_INTERVAL_US || now-previous < WATCH_INTERVAL_US) return;
    previous = now;
    snapshot_t snapshot = {0};
    uint32_t captured_live, captured_peak, captured_lost, made, freed;
    portENTER_CRITICAL(&lock);
    if (!first) {
        free_range_t range = {0};
        heap_caps_walk(MALLOC_CAP_8BIT, largest_free, &range);
        first = range.address;
        last = first + range.size;
        memset(owners, 0, sizeof(owners));
    }
    heap_caps_walk(MALLOC_CAP_8BIT, capture, &snapshot);
    captured_live=live; captured_peak=peak; captured_lost=lost;
    made=alloc_events; freed=free_events;
    portEXIT_CRITICAL(&lock);
    int64_t elapsed = esp_timer_get_time()-now;
    ESP_LOGI("heap_watch", "PERF HEAP_WATCH: seq=%u first=0x%08" PRIxPTR " last=0x%08" PRIxPTR
        " live=%u peak=%u lost=%u alloc_events=%u free_events=%u rows=%u dropped=%u unknown=%u walk_us=%" PRId64,
        (unsigned)++sequence, first, last, (unsigned)captured_live, (unsigned)captured_peak,
        (unsigned)captured_lost, (unsigned)made, (unsigned)freed, snapshot.count,
        snapshot.dropped, snapshot.unknown, elapsed);
    for (unsigned i=0; i<snapshot.count; ++i) {
        snapshot_row_t *row=&snapshot.rows[i];
        ESP_LOGI("heap_watch", "PERF HEAP_OWNER: seq=%u row=%u address=0x%08" PRIxPTR
            " bytes=%u id=%u requested=%u task=%s", (unsigned)sequence, i,
            row->address, (unsigned)row->bytes, (unsigned)row->id,
            (unsigned)row->requested, row->task[0] ? row->task : "free");
    }
}

static unsigned find(uintptr_t ptr) {
    for (unsigned i=0;i<WATCH_SLOTS;++i) if(owners[i].address==ptr)return i;
    return WATCH_SLOTS;
}
int main(void) {
    esp_heap_trace_alloc_hook((void*)0x1100,32,1);assert(!live);
    blocks[0]=(walker_block_info_t){(void*)0x1000,0x10000,false};block_count=1;
    now=1;heap_fragment_probe_poll(true);assert(!first);
    now+=WATCH_INTERVAL_US;heap_fragment_probe_poll(true);assert(first==0x1000 && last==0x11000);
    esp_heap_trace_alloc_hook((void*)0x100,32,1);assert(!live);
    esp_heap_trace_alloc_hook((void*)0x1100,32,1);assert(live==1);
    unsigned slot=find(0x1100);assert(slot<WATCH_SLOTS);
    uint32_t old_id=owners[slot].id;
    assert(strcmp(owners[slot].task,"owner-task-")==0);
    realloc_result=NULL;assert(!__wrap_heap_caps_realloc_base((void*)0x1100,64,1));
    assert(live==1 && owners[slot].id==old_id);
    realloc_result=(void*)0x1100;__wrap_heap_caps_realloc_base((void*)0x1100,64,1);
    assert(live==1 && owners[slot].id>old_id && owners[slot].requested==64);
    realloc_result=(void*)0x1200;__wrap_heap_caps_realloc_base((void*)0x1100,80,1);
    assert(live==1 && find(0x1100)==WATCH_SLOTS && find(0x1200)<WATCH_SLOTS);
    blocks[0]=(walker_block_info_t){(void*)0x1200,80,true};
    now+=WATCH_INTERVAL_US;heap_fragment_probe_poll(true);
    __wrap_heap_caps_realloc_base((void*)0x1200,0,1);assert(!live);
    in_isr=true;esp_heap_trace_alloc_hook((void*)0x1200,16,1);
    assert(strcmp(owners[find(0x1200)].task,"ISR")==0);
    __wrap_heap_caps_free((void*)0x1200);assert(!live);
    snapshot_t snap={0};capture((walker_heap_into_t){0},blocks[0],&snap);assert(snap.unknown==1);
    for(unsigned i=0;i<WATCH_SLOTS+1;++i)esp_heap_trace_alloc_hook((void*)(uintptr_t)(0x2000+i*16),8,1);
    assert(live==WATCH_SLOTS && lost==1);
    for(unsigned i=0;i<WATCH_SLOTS+1;++i)__wrap_heap_caps_free((void*)(uintptr_t)(0x2000+i*16));
    assert(!live && !lock_depth);
    snap=(snapshot_t){0};
    for(unsigned i=0;i<SNAPSHOT_ROWS+2;++i)capture((walker_heap_into_t){0},blocks[0],&snap);
    assert(snap.count==SNAPSHOT_ROWS && snap.dropped==2);
    // A successful move outside the observed region retires its old owner.
    esp_heap_trace_alloc_hook((void*)0x1200,16,1);realloc_result=(void*)0x100;
    __wrap_heap_caps_realloc_base((void*)0x1200,16,1);assert(!live);
    assert(overlaps(0xff0,32) && !overlaps(0xff0,16));
    puts("PASS arm/range/task/ISR/realloc-failure/in-place/moving/zero/free/reuse/overflow/unknown/snapshot/log-lock");
}
