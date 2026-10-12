#include <stdbool.h>
#include <stdint.h>
#include "esp_attr.h"
#include "lwip/memp.h"
#include "lwip/sys.h"
#include "lwip/tcp.h"
#ifdef CONFIG_YORADIO_TCP_PCB_POOL_DIAGNOSTICS
#include "esp_log.h"
// Retain bounded metadata without serial output on ordinary allocation/free.
// Dump only after an ownership failure, outside the critical section.
typedef struct { uint32_t event; uintptr_t caller; } pool_event_t;
static pool_event_t s_history[128];
static uint32_t s_history_sequence;
static void pool_trace(unsigned action, unsigned slot, unsigned state,
                       bool owned, uintptr_t caller) {
    SYS_ARCH_DECL_PROTECT(level);
    SYS_ARCH_PROTECT(level);
    uint32_t sequence = s_history_sequence++;
    s_history[sequence % 128] = (pool_event_t){
        (slot & 255U) | ((state & 255U) << 8) | ((uint32_t)owned << 16) | (action << 17), caller};
    SYS_ARCH_UNPROTECT(level);
    if (action != 2) return;
    // On firmware, lwIP's core lock serializes all PCB lifetimes. This path
    // terminates in the existing assertion; history is diagnostic, not recovery.
    uint32_t first = sequence < 127 ? 0 : sequence-127;
    unsigned count = sequence < 127 ? (unsigned)sequence+1 : 128;
    for (unsigned offset = 0; offset < count; ++offset) {
        uint32_t n = first+offset;
        pool_event_t entry = s_history[n % 128];
        unsigned kind = entry.event >> 17;
        ESP_LOGI("tcp_pool", "PERF TCP_POOL: sequence=%lu action=%s slot=%u state=%u owned=%u caller=%p",
                 (unsigned long)n, kind == 0 ? "alloc" : kind == 1 ? "free" : "invalid-free",
                 (unsigned)(entry.event & 255U), (unsigned)((entry.event >> 8) & 255U),
                 (unsigned)((entry.event >> 16) & 1U), (void *)entry.caller);
    }
}
#define POOL_TRACE(action, p, slot, state, owned) \
    pool_trace(action, (unsigned)(slot), (unsigned)(state), owned, (uintptr_t)__builtin_return_address(0))
#else
#define POOL_TRACE(action, p, slot, state, owned) ((void)0)
#endif

// IDF's heap-backed lwIP already limits all active/TIME_WAIT PCBs together to
// MEMP_NUM_TCP_PCB. Reserve exactly that capacity, without changing TCP timers,
// states, listen PCBs, packet buffers or the allocation-failure recovery in TCP.
_Static_assert(MEMP_MEM_MALLOC == 1 && MEMP_OVERFLOW_CHECK == 0,
               "TCP pool requires the audited IDF heap-backed memp configuration");
// C3's RTC RAM is byte-addressable and is already a last-priority heap region.
// Keep these small, long-lived nodes out of the large ordinary SRAM regions.
// Ownership flags stay in normal BSS and reset at a full/deep-sleep boot; TCP's
// existing initialization overwrites a reused PCB before it is published.
_Alignas(MEM_ALIGNMENT) static RTC_DATA_ATTR struct tcp_pcb s_pcbs[MEMP_NUM_TCP_PCB];
static bool s_used[MEMP_NUM_TCP_PCB];

void *__real_memp_malloc(memp_t type);
void __real_memp_free(memp_t type, void *p);

void *__wrap_memp_malloc(memp_t type) {
    if (type != MEMP_TCP_PCB) return __real_memp_malloc(type);
    SYS_ARCH_DECL_PROTECT(level);
    SYS_ARCH_PROTECT(level);
    void *result = NULL;
    for (unsigned i = 0; i < MEMP_NUM_TCP_PCB; ++i) {
        if (!s_used[i]) {
            s_used[i] = true;
            result = &s_pcbs[i];
            break;
        }
    }
#if MEMP_STATS
    struct stats_mem *stats = memp_pools[MEMP_TCP_PCB]->stats;
    if (result) {
        if (++stats->used > stats->max) stats->max = stats->used;
    } else {
        ++stats->err;
    }
#endif
    SYS_ARCH_UNPROTECT(level);
    POOL_TRACE(0, result, result ? ((struct tcp_pcb *)result-s_pcbs) : MEMP_NUM_TCP_PCB, 0, result != NULL);
    // Like memp_malloc, return uninitialized storage. tcp_alloc performs the
    // existing full memset and field initialization before publishing a PCB.
    return result;
}

void __wrap_memp_free(memp_t type, void *p) {
    if (type != MEMP_TCP_PCB) { __real_memp_free(type, p); return; }
    if (!p) return;
    uintptr_t address = (uintptr_t)p, base = (uintptr_t)s_pcbs;
    LWIP_ASSERT("TCP PCB belongs to its pool", address >= base &&
                address-base < sizeof(s_pcbs) &&
                (address-base) % sizeof(s_pcbs[0]) == 0);
    unsigned i = (unsigned)((address-base)/sizeof(s_pcbs[0]));
    SYS_ARCH_DECL_PROTECT(level);
    SYS_ARCH_PROTECT(level);
#ifdef CONFIG_YORADIO_TCP_PCB_POOL_DIAGNOSTICS
    unsigned state = ((struct tcp_pcb *)p)->state;
    if (!s_used[i]) {
        SYS_ARCH_UNPROTECT(level);
        POOL_TRACE(2, p, i, state, false);
        LWIP_ASSERT("TCP PCB is allocated", false);
        return;
    }
#endif
    LWIP_ASSERT("TCP PCB is allocated", s_used[i]);
    s_used[i] = false;
#if MEMP_STATS
    --memp_pools[MEMP_TCP_PCB]->stats->used;
#endif
    SYS_ARCH_UNPROTECT(level);
    POOL_TRACE(1, p, i, state, true);
}
