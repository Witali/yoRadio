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


// Observe the public netif ownership transfer; never dereference packet data
// or interpret the driver's opaque L2 handle. No changes to packet lifetimes.
enum { RX_TRACK_SLOTS = 32 };
#define RX_SNAPSHOT_INTERVAL_US 5000000LL

// Version 3 owner records append heap measurements from the same critical
// section as the live RX range walk. Block records remain version 2. CRC32
// covers the uint32 fields in order, little endian; no packet contents escape.
typedef struct {
    uint32_t sequence, live, peak, allocations, releases, lost, unmatched;
    uint32_t payload, metadata, missing, walk_us;
    uint32_t heap_free, heap_largest;
} rx_owner_record_t;
typedef struct {
    uint32_t sequence, id, payload, payload_bytes, metadata, metadata_bytes;
} rx_block_record_t;
_Static_assert(sizeof(rx_owner_record_t) == 13 * sizeof(uint32_t), "No wire CRC padding");
_Static_assert(sizeof(rx_block_record_t) == 6 * sizeof(uint32_t), "No wire CRC padding");

static uint32_t record_crc(const void *record, size_t size) {
    return esp_rom_crc32_le(0, record, size);
}
typedef struct {
    void *release_key, *payload;
    struct pbuf *metadata;
    uint32_t id;
} rx_owner_t;
static rx_owner_t owners[RX_TRACK_SLOTS];
static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
static uint32_t allocations, releases, lost, live, peak, untracked_releases;

static void record_owner(void *release_key, void *payload, struct pbuf *metadata) {
    portENTER_CRITICAL(&lock);
    ++allocations;
    unsigned slot = 0;
    while (slot < RX_TRACK_SLOTS && owners[slot].metadata) ++slot;
    for (unsigned i = 0; i < RX_TRACK_SLOTS; ++i)
        if (owners[i].metadata && owners[i].release_key == release_key) slot = RX_TRACK_SLOTS;
    if (slot < RX_TRACK_SLOTS) {
        owners[slot] = (rx_owner_t){release_key, payload, metadata, allocations};
        if (++live > peak) peak = live;
    } else ++lost;
    portEXIT_CRITICAL(&lock);
}

// Caller holds the owner lock. Do not inspect packet data or freed storage.
static bool release_owner_locked(const void *release_key) {
    unsigned slot = 0;
    while (slot < RX_TRACK_SLOTS &&
           (!owners[slot].metadata || owners[slot].release_key != release_key)) ++slot;
    if (slot < RX_TRACK_SLOTS) {
        owners[slot] = (rx_owner_t){0};
        --live;
        ++releases;
        return true;
    }
    return false;
}

#ifdef CONFIG_LWIP_L2_TO_L3_COPY
#if !MEM_LIBC_MALLOC
#error "RX copy diagnostics require the audited libc-backed lwIP allocator"
#endif
// The original wlanif_input allocates one PBUF_RAM copy before handing it to
// lwIP. Scope by task so unrelated TCP/TX allocations never become RX owners.
typedef struct rx_copy_scope {
    struct rx_copy_scope *previous;
    bool allocation_pending;
} rx_copy_scope_t;
static _Thread_local rx_copy_scope_t *copy_scope;
esp_err_t __real_wlanif_input(void *, void *, size_t, void *);
esp_err_t __wrap_wlanif_input(void *netif, void *buffer, size_t len, void *l2) {
    rx_copy_scope_t scope = {.previous = copy_scope, .allocation_pending = true};
    copy_scope = &scope;
    esp_err_t result = __real_wlanif_input(netif, buffer, len, l2);
    copy_scope = scope.previous;
    return result;
}

struct pbuf *__real_pbuf_alloc(pbuf_layer, u16_t, pbuf_type);
struct pbuf *__wrap_pbuf_alloc(pbuf_layer layer, u16_t len, pbuf_type type) {
    const bool receiving = copy_scope && copy_scope->allocation_pending &&
                           layer == PBUF_RAW && type == PBUF_RAM;
    // Consume only the original copy allocation, including its failure. Any
    // allocations from a downstream input callback have independent owners.
    if (receiving) copy_scope->allocation_pending = false;
    struct pbuf *p = __real_pbuf_alloc(layer, len, type);
    if (p && receiving) record_owner(p, p->payload, p);
    return p;
}

void __real_mem_free(void *);
void __wrap_mem_free(void *pointer) {
    // Observe actual deallocation, not pbuf_free entry: referenced buffers and
    // chained tails can remain alive. This also covers internal pbuf.c calls.
    // In the pinned MEM_LIBC_MALLOC path mem_trim does not move allocations.
    portENTER_CRITICAL(&lock);
    if (release_owner_locked(pointer)) {
        // C3 only: keep removal and real free indivisible to the paired heap
        // snapshot. The libc-backed mem_free neither allocates nor logs.
        __real_mem_free(pointer);
        portEXIT_CRITICAL(&lock);
        return;
    }
    portEXIT_CRITICAL(&lock);
    __real_mem_free(pointer);
}
#else
struct pbuf *__real_esp_pbuf_allocate(esp_netif_t *, void *, size_t, void *);
struct pbuf *__wrap_esp_pbuf_allocate(esp_netif_t *netif, void *buffer,
                                     size_t len, void *l2) {
    struct pbuf *p = __real_esp_pbuf_allocate(netif, buffer, len, l2);
    if (p) record_owner(l2, buffer, p);
    return p;
}

void __real_esp_netif_free_rx_buffer(void *, void *);
void __wrap_esp_netif_free_rx_buffer(void *netif, void *l2) {
    portENTER_CRITICAL(&lock);
    if (!release_owner_locked(l2)) ++untracked_releases;
    portEXIT_CRITICAL(&lock);
    __real_esp_netif_free_rx_buffer(netif, l2);
}
#endif

typedef struct {
    rx_owner_t owner;
    uintptr_t payload_allocation, metadata_allocation;
    size_t payload_bytes, metadata_bytes;
} rx_row_t;
typedef struct { rx_row_t rows[RX_TRACK_SLOTS]; size_t count; } rx_snapshot_t;
_Static_assert(sizeof(rx_snapshot_t) <= 1100, "Bound decoder diagnostic stack");

static bool containing_block(walker_heap_into_t heap, walker_block_info_t block,
                              void *context) {
    (void)heap;
    if (!block.used) return true;
    rx_snapshot_t *snapshot = context;
    uintptr_t first = (uintptr_t)block.ptr, end = first + block.size;
    for (size_t i = 0; i < snapshot->count; ++i) {
        rx_row_t *row = &snapshot->rows[i];
        uintptr_t payload = (uintptr_t)row->owner.payload;
        uintptr_t metadata = (uintptr_t)row->owner.metadata;
        if (payload >= first && payload < end) {
            row->payload_allocation = first;
            row->payload_bytes = block.size;
        }
        if (metadata >= first && metadata < end) {
            row->metadata_allocation = first;
            row->metadata_bytes = block.size;
        }
    }
    return true;
}

static bool already_counted(const rx_snapshot_t *snapshot, size_t before,
                            uintptr_t allocation) {
    for (size_t i = 0; i < before; ++i)
        if (snapshot->rows[i].payload_allocation == allocation ||
            snapshot->rows[i].metadata_allocation == allocation) return true;
    return false;
}

void rx_buffer_diagnostic_poll(void) {
    static int64_t previous;
    static uint32_t sequence;
    int64_t now = esp_timer_get_time();
    if (now - previous < RX_SNAPSHOT_INTERVAL_US) return;
    previous = now;
    rx_snapshot_t snapshot = {0};
    multi_heap_info_t heap;
    uint32_t made, freed, dropped, high, unmatched;
    // C3 is single-core. This short critical section prevents a recorded RX
    // pointer from being freed/reused between the owner copy and heap walk.
    // The wrapped allocator has already released heap locks before taking our
    // lock. Copied pbufs are removed and freed under the same owner lock;
    // the legacy L2 wrapper removes its owner before releasing the driver buffer.
    // No logging, allocation or heap API calls occur in containing_block.
    portENTER_CRITICAL(&lock);
    for (unsigned i = 0; i < RX_TRACK_SLOTS; ++i)
        if (owners[i].metadata) snapshot.rows[snapshot.count++].owner = owners[i];
    made = allocations; freed = releases; dropped = lost;
    high = peak; unmatched = untracked_releases;
    heap_caps_walk(MALLOC_CAP_8BIT, containing_block, &snapshot);
    // C3 is single-core: other tasks cannot change these heap regions between
    // the owner walk and this measurement. Counts exclude allocator headers;
    // they still cannot account for allocations owned by other subsystems.
    heap_caps_get_info(&heap, MALLOC_CAP_8BIT);
    portEXIT_CRITICAL(&lock);
    int64_t walked = esp_timer_get_time() - now;
    size_t payload_bytes = 0, metadata_bytes = 0, missing = 0;
    for (size_t i = 0; i < snapshot.count; ++i) {
        const rx_row_t *row = &snapshot.rows[i];
        if (!already_counted(&snapshot, i, row->payload_allocation))
            payload_bytes += row->payload_bytes;
        if (row->metadata_allocation != row->payload_allocation &&
            !already_counted(&snapshot, i, row->metadata_allocation))
            metadata_bytes += row->metadata_bytes;
        if (!row->payload_bytes || !row->metadata_bytes) ++missing;
    }
    const rx_owner_record_t header = {
        .sequence = ++sequence, .live = snapshot.count, .peak = high,
        .allocations = made, .releases = freed, .lost = dropped, .unmatched = unmatched,
        .payload = payload_bytes, .metadata = metadata_bytes, .missing = missing,
        .walk_us = walked > UINT32_MAX ? UINT32_MAX : (uint32_t)walked,
        .heap_free = heap.total_free_bytes, .heap_largest = heap.largest_free_block,
    };
    ESP_LOGI("rx_owner", "PERF RX_OWNER3: %u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%08" PRIx32,
        (unsigned)header.sequence, (unsigned)header.live, (unsigned)header.peak,
        (unsigned)header.allocations, (unsigned)header.releases,
        (unsigned)header.lost, (unsigned)header.unmatched,
        (unsigned)header.payload, (unsigned)header.metadata,
        (unsigned)header.missing, (unsigned)header.walk_us,
        (unsigned)header.heap_free, (unsigned)header.heap_largest,
        record_crc(&header, sizeof(header)));
    for (size_t i = 0; i < snapshot.count; ++i) {
        const rx_row_t *r = &snapshot.rows[i];
        const rx_block_record_t block = {.sequence = sequence, .id = r->owner.id,
            .payload = r->payload_allocation, .payload_bytes = r->payload_bytes,
            .metadata = r->metadata_allocation, .metadata_bytes = r->metadata_bytes};
        ESP_LOGI("rx_owner", "PERF RX_BLOCK2: %u,%u,%08" PRIx32 ",%u,%08" PRIx32 ",%u,%08" PRIx32,
            (unsigned)block.sequence, (unsigned)block.id, block.payload,
            (unsigned)block.payload_bytes, block.metadata, (unsigned)block.metadata_bytes,
            record_crc(&block, sizeof(block)));
    }
}


// The runner inserts the pinned SDK bodies. Host call-name redirection models
// --wrap; the separate target ELF check verifies real interposition.
esp_err_t __real_wlanif_input(void *h, void *buffer, size_t len, void* l2_buff)
{
    struct netif * netif = h;
    esp_netif_t *esp_netif = netif->state;
    struct pbuf *p;

    if(unlikely(!buffer || !netif_is_up(netif))) {
        if (l2_buff) {
            esp_netif_free_rx_buffer(esp_netif, l2_buff);
        }
        return ESP_FAIL;
    }

#ifdef CONFIG_LWIP_L2_TO_L3_COPY
    p = __wrap_pbuf_alloc(PBUF_RAW, len, PBUF_RAM);
    if (p == NULL) {
        esp_netif_free_rx_buffer(esp_netif, l2_buff);
        return ESP_ERR_NO_MEM;
    }
    memcpy(p->payload, buffer, len);
    esp_netif_free_rx_buffer(esp_netif, l2_buff);
#else
    p = esp_pbuf_allocate(esp_netif, buffer, len, l2_buff);
    if (p == NULL) {
        esp_netif_free_rx_buffer(esp_netif, l2_buff);
        return ESP_ERR_NO_MEM;
    }

#endif

    /* full packet send to tcpip_thread to process */
    if (unlikely(netif->input(p, netif) != ERR_OK)) {
        LWIP_DEBUGF(NETIF_DEBUG, ("wlanif_input: IP input error\n"));
        pbuf_free(p);
        return ESP_FAIL;
    }
    return ESP_OK;
}

u8_t
pbuf_free(struct pbuf *p)
{
  u8_t alloc_src;
  struct pbuf *q;
  u8_t count;

  if (p == NULL) {
    LWIP_ASSERT("p != NULL", p != NULL);
    /* if assertions are disabled, proceed with debug output */
    LWIP_DEBUGF(PBUF_DEBUG | LWIP_DBG_LEVEL_SERIOUS,
                ("pbuf_free(p == NULL) was called.\n"));
    return 0;
  }
  LWIP_DEBUGF(PBUF_DEBUG | LWIP_DBG_TRACE, ("pbuf_free(%p)\n", (void *)p));

  PERF_START;

  count = 0;
  /* de-allocate all consecutive pbufs from the head of the chain that
   * obtain a zero reference count after decrementing*/
  while (p != NULL) {
    LWIP_PBUF_REF_T ref;
    SYS_ARCH_DECL_PROTECT(old_level);
    /* Since decrementing ref cannot be guaranteed to be a single machine operation
     * we must protect it. We put the new ref into a local variable to prevent
     * further protection. */
    SYS_ARCH_PROTECT(old_level);
    /* all pbufs in a chain are referenced at least once */
    LWIP_ASSERT("pbuf_free: p->ref > 0", p->ref > 0);
    /* decrease reference count (number of pointers to pbuf) */
    ref = --(p->ref);
    SYS_ARCH_UNPROTECT(old_level);
    /* this pbuf is no longer referenced to? */
    if (ref == 0) {
      /* remember next pbuf in chain for next iteration */
      q = p->next;
      LWIP_DEBUGF( PBUF_DEBUG | LWIP_DBG_TRACE, ("pbuf_free: deallocating %p\n", (void *)p));
      alloc_src = pbuf_get_allocsrc(p);
#if LWIP_SUPPORT_CUSTOM_PBUF
      /* is this a custom pbuf? */
      if ((p->flags & PBUF_FLAG_IS_CUSTOM) != 0) {
        struct pbuf_custom *pc = (struct pbuf_custom *)p;
        LWIP_ASSERT("pc->custom_free_function != NULL", pc->custom_free_function != NULL);
        pc->custom_free_function(p);
      } else
#endif /* LWIP_SUPPORT_CUSTOM_PBUF */
      {
        /* is this a pbuf from the pool? */
        if (alloc_src == PBUF_TYPE_ALLOC_SRC_MASK_STD_MEMP_PBUF_POOL) {
          memp_free(MEMP_PBUF_POOL, p);
          /* is this a ROM or RAM referencing pbuf? */
        } else if (alloc_src == PBUF_TYPE_ALLOC_SRC_MASK_STD_MEMP_PBUF) {
          memp_free(MEMP_PBUF, p);
          /* type == PBUF_RAM */
        } else if (alloc_src == PBUF_TYPE_ALLOC_SRC_MASK_STD_HEAP) {
          __wrap_mem_free(p);
        } else {
          /* @todo: support freeing other types */
          LWIP_ASSERT("invalid pbuf type", 0);
        }
      }
      count++;
      /* proceed to next pbuf */
      p = q;
      /* p->ref > 0, this pbuf is still referenced to */
      /* (and so the remaining pbufs in chain as well) */
    } else {
      LWIP_DEBUGF( PBUF_DEBUG | LWIP_DBG_TRACE, ("pbuf_free: %p has ref %"U16_F", ending here.\n", (void *)p, (u16_t)ref));
      /* stop walking through the chain */
      p = NULL;
    }
  }
  PERF_STOP("pbuf_free");
  /* return number of de-allocated pbufs */
  return count;
}

void
__real_mem_free(void *rmem)
{
  LWIP_ASSERT("rmem != NULL", (rmem != NULL));
  LWIP_ASSERT("rmem == MEM_ALIGN(rmem)", (rmem == LWIP_MEM_ALIGN(rmem)));
#if LWIP_STATS && MEM_STATS
  rmem = (u8_t *)rmem - MEM_LIBC_STATSHELPER_SIZE;
  MEM_STATS_DEC_USED_LOCKED(used, *(mem_size_t *)rmem);
#endif
  mem_clib_free(rmem);
}

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
