#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

// RV32 stack-size assertion is checked by the real firmware compiler. This
// host model has 64-bit pointers and tests range matching/ownership instead.
#define _Static_assert(condition, message)
typedef struct { int unused; } esp_netif_t;
struct pbuf { int unused; };
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
static bool locked, walking;
#define portENTER_CRITICAL(m) do { (void)(m); assert(!locked); locked=true; } while(0)
#define portEXIT_CRITICAL(m) do { (void)(m); assert(locked); locked=false; } while(0)
static int64_t now;
static int64_t esp_timer_get_time(void) { return now; }
#define MALLOC_CAP_8BIT 1
typedef struct { void *start; } walker_heap_into_t;
typedef struct { void *ptr; size_t size; bool used; } walker_block_info_t;
static walker_block_info_t blocks[70];
static size_t block_count;
static void heap_caps_walk(unsigned caps, bool (*visit)(walker_heap_into_t,walker_block_info_t,void *), void *data) {
    assert(caps==1 && locked && !walking); walking=true;
    for(size_t i=0;i<block_count;++i) assert(visit((walker_heap_into_t){0},blocks[i],data));
    walking=false;
}
static void test_log(const char *tag, const char *format, ...) {
    (void)tag; assert(!locked && !walking);
    va_list args; va_start(args,format); vprintf(format,args); va_end(args); putchar('\n');
}
#define ESP_LOGI test_log
static struct pbuf *next_pbuf;
static unsigned real_allocs, real_frees;
struct pbuf *__real_esp_pbuf_allocate(esp_netif_t *n,void *p,size_t s,void *h) {
    (void)n;(void)p;(void)s;(void)h; assert(!locked);++real_allocs;return next_pbuf;
}
void __real_esp_netif_free_rx_buffer(void *n,void *p) {
    (void)n;(void)p;assert(!locked);++real_frees;
}

// The runner inserts the production source here, removing platform includes.

// Observe the public netif ownership transfer; never dereference packet data
// or interpret the driver's opaque L2 handle. No changes to packet lifetimes.
enum { RX_TRACK_SLOTS = 32 };
typedef struct {
    void *l2, *payload;
    struct pbuf *metadata;
    uint32_t id;
} rx_owner_t;
static rx_owner_t owners[RX_TRACK_SLOTS];
static portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
static uint32_t allocations, releases, lost, live, peak, untracked_releases;

struct pbuf *__real_esp_pbuf_allocate(esp_netif_t *, void *, size_t, void *);
struct pbuf *__wrap_esp_pbuf_allocate(esp_netif_t *netif, void *buffer,
                                     size_t len, void *l2) {
    struct pbuf *p = __real_esp_pbuf_allocate(netif, buffer, len, l2);
    if (!p) return p;
    portENTER_CRITICAL(&lock);
    ++allocations;
    unsigned slot = 0;
    while (slot < RX_TRACK_SLOTS && owners[slot].metadata) ++slot;
    for (unsigned i = 0; i < RX_TRACK_SLOTS; ++i)
        if (owners[i].metadata && owners[i].l2 == l2) slot = RX_TRACK_SLOTS;
    if (slot < RX_TRACK_SLOTS) {
        owners[slot] = (rx_owner_t){l2, buffer, p, allocations};
        if (++live > peak) peak = live;
    } else ++lost;
    portEXIT_CRITICAL(&lock);
    return p;
}

void __real_esp_netif_free_rx_buffer(void *, void *);
void __wrap_esp_netif_free_rx_buffer(void *netif, void *l2) {
    portENTER_CRITICAL(&lock);
    unsigned slot = 0;
    while (slot < RX_TRACK_SLOTS &&
           (!owners[slot].metadata || owners[slot].l2 != l2)) ++slot;
    if (slot < RX_TRACK_SLOTS) {
        owners[slot] = (rx_owner_t){0};
        --live;
        ++releases;
    } else ++untracked_releases; // Failed pbuf creation can legitimately do this.
    portEXIT_CRITICAL(&lock);
    __real_esp_netif_free_rx_buffer(netif, l2);
}

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
    if (now - previous < 5000000LL) return;
    previous = now;
    rx_snapshot_t snapshot = {0};
    uint32_t made, freed, dropped, high, unmatched;
    // C3 is single-core. This short critical section prevents a recorded RX
    // pointer from being freed/reused between the owner copy and heap walk.
    // The wrapped allocator has already released heap locks before taking our
    // lock; the free wrapper releases our lock before calling the real free.
    // No logging, allocation or heap API calls occur in containing_block.
    portENTER_CRITICAL(&lock);
    for (unsigned i = 0; i < RX_TRACK_SLOTS; ++i)
        if (owners[i].metadata) snapshot.rows[snapshot.count++].owner = owners[i];
    made = allocations; freed = releases; dropped = lost;
    high = peak; unmatched = untracked_releases;
    heap_caps_walk(MALLOC_CAP_8BIT, containing_block, &snapshot);
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
    ESP_LOGI("rx_owner", "PERF RX_OWNER: seq=%u live=%u peak=%u allocs=%u frees=%u lost=%u unmatched=%u payload=%u metadata=%u missing=%u walk_us=%" PRId64,
        (unsigned)++sequence, (unsigned)snapshot.count, (unsigned)high,
        (unsigned)made, (unsigned)freed, (unsigned)dropped, (unsigned)unmatched,
        (unsigned)payload_bytes, (unsigned)metadata_bytes, (unsigned)missing, walked);
    for (size_t i = 0; i < snapshot.count; ++i) {
        const rx_row_t *r = &snapshot.rows[i];
        ESP_LOGI("rx_owner", "PERF RX_BLOCK: seq=%u id=%u payload=0x%08" PRIxPTR " payload_bytes=%u metadata=0x%08" PRIxPTR " metadata_bytes=%u",
            (unsigned)sequence, (unsigned)r->owner.id, r->payload_allocation,
            (unsigned)r->payload_bytes, r->metadata_allocation, (unsigned)r->metadata_bytes);
    }
}


static uint8_t payloads[34][1800], metadata[34][64], handles[34];
static void add(unsigned index) {
    next_pbuf=(struct pbuf *)metadata[index];
    assert(__wrap_esp_pbuf_allocate(NULL,payloads[index]+44,1280,&handles[index])==next_pbuf);
}
int main(void) {
    now=5000000;rx_buffer_diagnostic_poll();assert(!live);
    add(0);add(1);add(2);
    for(unsigned i=0;i<3;++i) {
        blocks[block_count++]=(walker_block_info_t){payloads[i],1724,true};
        blocks[block_count++]=(walker_block_info_t){metadata[i],32,true};
    }
    now+=5000000;rx_buffer_diagnostic_poll();assert(live==3 && !lost);
    for(unsigned i=0;i<3;++i)__wrap_esp_netif_free_rx_buffer(NULL,&handles[i]);
    assert(!live && releases==3 && real_frees==3);
    next_pbuf=NULL;
    assert(!__wrap_esp_pbuf_allocate(NULL,payloads[0],1280,&handles[0]));
    assert(allocations==3);__wrap_esp_netif_free_rx_buffer(NULL,&handles[0]);
    assert(untracked_releases==1 && real_frees==4);
    for(unsigned i=0;i<33;++i)add(i);
    assert(live==32 && lost==1 && peak==32);
    for(unsigned i=0;i<33;++i)__wrap_esp_netif_free_rx_buffer(NULL,&handles[i]);
    assert(!live && releases==35 && real_frees==37);
    add(0);uint32_t identity=owners[0].id;
    add(0);assert(lost==2 && live==1); // Ambiguous repeated L2 handle is flagged.
    __wrap_esp_netif_free_rx_buffer(NULL,&handles[0]);
    add(0);assert(owners[0].id>identity);
    // A pointer is matched only to an allocated block, never to free storage.
    blocks[0].used=false;
    now+=5000000;rx_buffer_diagnostic_poll();
    __wrap_esp_netif_free_rx_buffer(NULL,&handles[0]);
    rx_snapshot_t shared={.count=2};
    shared.rows[0].payload_allocation=100;shared.rows[0].metadata_allocation=200;
    assert(already_counted(&shared,1,100) && already_counted(&shared,1,200));
    assert(!already_counted(&shared,1,300));
    assert(!live && !locked && !walking);
    puts("PASS range/ownership/free/failure/overflow/identity/log-lock checks");
}
