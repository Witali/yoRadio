#include "rx_buffer_diagnostic.h"
#include <inttypes.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_netif_net_stack.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "lwip/esp_pbuf_ref.h"

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
