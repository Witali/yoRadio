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
/* PRODUCTION_SOURCE */
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
