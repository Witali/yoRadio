#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <pthread.h>
#include <sanitizer/asan_interface.h>

#define CONFIG_LWIP_L2_TO_L3_COPY 1
#define MEM_LIBC_MALLOC 1
#define LWIP_STATS 0
#define MEM_STATS 0
#define LWIP_SUPPORT_CUSTOM_PBUF 1
#define _Static_assert(condition, message) /* RV32 layout checked by target build. */
typedef uint8_t u8_t;
typedef uint16_t u16_t;
typedef uint16_t LWIP_PBUF_REF_T;
typedef int esp_err_t;
typedef int err_t;
typedef int pbuf_layer;
typedef int pbuf_type;
typedef int esp_netif_t;
enum { PBUF_RAW, PBUF_RAW_TX, PBUF_RAM, PBUF_REF };
enum { ESP_OK=0, ESP_FAIL=-1, ESP_ERR_NO_MEM=0x101, ERR_OK=0, ERR_MEM=-1 };
enum { PBUF_TYPE_ALLOC_SRC_MASK_STD_HEAP, PBUF_TYPE_ALLOC_SRC_MASK_STD_MEMP_PBUF,
       PBUF_TYPE_ALLOC_SRC_MASK_STD_MEMP_PBUF_POOL, MEMP_PBUF_POOL, MEMP_PBUF };
#define PBUF_FLAG_IS_CUSTOM 1
struct pbuf { struct pbuf *next; void *payload; u16_t len,tot_len,ref; u8_t flags; };
struct pbuf_custom { struct pbuf pbuf; void (*custom_free_function)(struct pbuf *); };
struct netif { void *state; bool up; err_t (*input)(struct pbuf *,struct netif *); };
#define unlikely(x) (x)
#define netif_is_up(n) ((n)->up)
#define pbuf_get_allocsrc(p) ((void)(p),PBUF_TYPE_ALLOC_SRC_MASK_STD_HEAP)
#define LWIP_ASSERT(message, condition) assert(condition)
#define LWIP_DEBUGF(...) ((void)0)
#define LWIP_MEM_ALIGN(p) ((void *)(((uintptr_t)(p)+3u)&~(uintptr_t)3u))
#define PERF_START ((void)0)
#define PERF_STOP(x) ((void)(x))

typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
static pthread_mutex_t critical_mutex=PTHREAD_MUTEX_INITIALIZER;
static _Thread_local unsigned critical_depth;
static void enter(void) { assert(!critical_depth); assert(!pthread_mutex_lock(&critical_mutex)); ++critical_depth; }
static void leave(void) { assert(critical_depth==1); --critical_depth; assert(!pthread_mutex_unlock(&critical_mutex)); }
#define portENTER_CRITICAL(m) do { (void)(m); enter(); } while(0)
#define portEXIT_CRITICAL(m) do { (void)(m); leave(); } while(0)
#define SYS_ARCH_DECL_PROTECT(v) unsigned v=0
#define SYS_ARCH_PROTECT(v) do { (void)(v); enter(); } while(0)
#define SYS_ARCH_UNPROTECT(v) do { (void)(v); leave(); } while(0)
static int64_t now;
static int64_t esp_timer_get_time(void) { return now; }
#define MALLOC_CAP_8BIT 1
typedef struct { int unused; } walker_heap_into_t;
typedef struct { void *ptr; size_t size; bool used; } walker_block_info_t;
typedef struct { size_t total_free_bytes,largest_free_block; } multi_heap_info_t;
static void heap_caps_walk(unsigned, bool (*)(walker_heap_into_t,walker_block_info_t,void *),void *);
static void heap_caps_get_info(multi_heap_info_t *,unsigned);
static void test_log(const char *tag,const char *format,...) {
    (void)tag; assert(!critical_depth);
    va_list ap; va_start(ap,format); vprintf(format,ap); va_end(ap); putchar('\n');
}
#define ESP_LOGI test_log
static uint32_t esp_rom_crc32_le(uint32_t crc,const uint8_t *bytes,uint32_t size) {
    crc=~crc;
    while(size--) { crc^=*bytes++; for(unsigned b=0;b<8;++b) crc=(crc>>1)^((crc&1)?UINT32_C(0xedb88320):0); }
    return ~crc;
}
static void test_free(void *);
#define mem_clib_free test_free
u8_t pbuf_free(struct pbuf *);
static void memp_free(int pool,void *p) { (void)pool; (void)p; assert(!"Unexpected pool release"); }
static unsigned driver_frees;
static void esp_netif_free_rx_buffer(void *netif,void *buffer) {
    (void)netif; assert(buffer && !critical_depth); ++driver_frees;
}

/* PRODUCTION_SOURCE */

// The runner inserts the pinned SDK bodies. Host call-name redirection models
// --wrap; the separate target ELF check verifies real interposition.
/* SDK_FUNCTIONS */

enum { HEAP_SLOTS=64, HEAP_SLOT_BYTES=256 };
enum { MODE_QUEUE, MODE_DROP, MODE_CONSUME, MODE_NESTED, MODE_THREAD };
static _Alignas(16) uint8_t arena[HEAP_SLOTS][HEAP_SLOT_BYTES];
static struct { size_t size; bool used,requires_locked_free; } blocks[HEAP_SLOTS];
static _Thread_local bool expected_owned;
static bool fail_alloc;
static unsigned actual_frees,mode,nesting,queued_count;
static struct pbuf *queued[8];
static uint8_t input_bytes[31];

struct pbuf *__real_pbuf_alloc(pbuf_layer layer,u16_t len,pbuf_type type) {
    (void)layer; assert(type==PBUF_RAM && !critical_depth);
    if(fail_alloc) return NULL;
    size_t bytes=sizeof(struct pbuf)+len; assert(bytes<=HEAP_SLOT_BYTES);
    enter(); unsigned i=0; while(i<HEAP_SLOTS && blocks[i].used) ++i; assert(i<HEAP_SLOTS);
    blocks[i].size=bytes; blocks[i].used=true; blocks[i].requires_locked_free=expected_owned;
    __asan_unpoison_memory_region(arena[i],bytes); memset(arena[i],0,bytes);
    struct pbuf *p=(void *)arena[i]; p->payload=arena[i]+sizeof(*p); p->len=p->tot_len=len; p->ref=1;
    leave(); return p;
}
static void test_free(void *p) {
    unsigned i=0; while(i<HEAP_SLOTS && p!=arena[i]) ++i; assert(i<HEAP_SLOTS && blocks[i].used);
    if(blocks[i].requires_locked_free) assert(critical_depth==1);
    bool acquired=!critical_depth; if(acquired) enter();
    for(unsigned n=0;n<RX_TRACK_SLOTS;++n) assert(!owners[n].metadata || owners[n].release_key!=p);
    blocks[i].used=false; ++actual_frees;
    __asan_poison_memory_region(arena[i],HEAP_SLOT_BYTES);
    if(acquired) leave();
}
static void heap_caps_walk(unsigned caps,bool (*fn)(walker_heap_into_t,walker_block_info_t,void *),void *ctx) {
    assert(caps==MALLOC_CAP_8BIT && critical_depth==1);
    for(unsigned i=0;i<HEAP_SLOTS;++i) if(blocks[i].used)
        assert(fn((walker_heap_into_t){0},(walker_block_info_t){arena[i],blocks[i].size,true},ctx));
}
static void heap_caps_get_info(multi_heap_info_t *info,unsigned caps) {
    assert(caps==MALLOC_CAP_8BIT && critical_depth==1); size_t used=0;
    for(unsigned i=0;i<HEAP_SLOTS;++i) if(blocks[i].used) used+=blocks[i].size;
    *info=(multi_heap_info_t){200000-used,65536};
}
static void snapshot(void) { now+=5000000; rx_buffer_diagnostic_poll(); }
static void *other_thread(void *unused) {
    (void)unused; assert(!expected_owned);
    struct pbuf *p=__wrap_pbuf_alloc(PBUF_RAW,17,PBUF_RAM); assert(p);
    assert(pbuf_free(p)==1); return NULL;
}
static err_t receive(struct pbuf *p,struct netif *netif) {
    assert(!critical_depth && p && p->len==sizeof(input_bytes));
    assert(!memcmp(p->payload,input_bytes,sizeof(input_bytes)));
    if(mode==MODE_DROP) return ERR_MEM;
    if(mode==MODE_CONSUME) { assert(pbuf_free(p)==1); return ERR_OK; }
    queued[queued_count++]=p;
    if(!nesting && mode==MODE_NESTED) {
        ++nesting;
        assert(__wrap_wlanif_input(netif,input_bytes,sizeof(input_bytes),input_bytes)==ESP_OK);
        --nesting;
        unsigned before=live; expected_owned=false;
        struct pbuf *other=__wrap_pbuf_alloc(PBUF_RAW,17,PBUF_RAM);
        assert(live==before); assert(pbuf_free(other)==1); expected_owned=true;
    }
    if(mode==MODE_THREAD) {
        unsigned before=live; pthread_t thread;
        assert(!pthread_create(&thread,NULL,other_thread,NULL)); assert(!pthread_join(thread,NULL));
        assert(live==before);
    }
    return ERR_OK;
}
static void enqueue(struct netif *netif) {
    expected_owned=true;
    assert(__wrap_wlanif_input(netif,input_bytes,sizeof(input_bytes),input_bytes)==ESP_OK);
    expected_owned=false;
}
int main(void) {
    memset(input_bytes,0x5a,sizeof(input_bytes)); __asan_poison_memory_region(arena,sizeof(arena));
    struct netif netif={.up=true,.input=receive}; snapshot();
    expected_owned=true; fail_alloc=true;
    assert(__wrap_wlanif_input(&netif,input_bytes,sizeof(input_bytes),input_bytes)==ESP_ERR_NO_MEM);
    fail_alloc=false; netif.up=false;
    assert(__wrap_wlanif_input(&netif,input_bytes,sizeof(input_bytes),input_bytes)==ESP_FAIL);
    netif.up=true;
    assert(__wrap_wlanif_input(&netif,NULL,sizeof(input_bytes),input_bytes)==ESP_FAIL);
    expected_owned=false; assert(!live && !allocations && driver_frees==3);
    mode=MODE_DROP; expected_owned=true;
    assert(__wrap_wlanif_input(&netif,input_bytes,sizeof(input_bytes),input_bytes)==ESP_FAIL);
    expected_owned=false; assert(!live && allocations==1 && releases==1);
    mode=MODE_CONSUME; enqueue(&netif); assert(!live && allocations==2 && releases==2);
    mode=MODE_QUEUE; enqueue(&netif); enqueue(&netif); assert(live==2); snapshot();
    queued[0]->next=queued[1]; queued[0]->ref=2;
    assert(pbuf_free(queued[0])==0 && live==2);
    assert(pbuf_free(queued[0])==2 && !live); queued_count=0;
    enqueue(&netif); enqueue(&netif); queued[0]->next=queued[1]; queued[1]->ref=2;
    assert(pbuf_free(queued[0])==1 && live==1); snapshot();
    assert(pbuf_free(queued[1])==1 && !live); queued_count=0;
    mode=MODE_NESTED; enqueue(&netif); assert(live==2 && queued_count==2);
    assert(pbuf_free(queued[0])==1 && pbuf_free(queued[1])==1); queued_count=0;
    mode=MODE_THREAD; enqueue(&netif); assert(live==1 && queued_count==1);
    assert(pbuf_free(queued[0])==1); queued_count=0;
    struct pbuf *other=__wrap_pbuf_alloc(PBUF_RAW,17,PBUF_RAM);
    assert(!live && pbuf_free(other)==1); snapshot();
    assert(!lost && !untracked_releases && !live && allocations==releases);
    for(unsigned i=0;i<HEAP_SLOTS;++i) assert(!blocks[i].used);
    assert(actual_frees>releases);
    puts("PASS copied RX ownership, SDK input/free, failure, chain/refcount, nesting, task isolation, paired heap and poisoned lifetime checks");
}
