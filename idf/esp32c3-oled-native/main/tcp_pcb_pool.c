#include <stdbool.h>
#include <stdint.h>
#include "esp_attr.h"
#include "lwip/memp.h"
#include "lwip/sys.h"
#include "lwip/tcp.h"
#ifdef CONFIG_YORADIO_TCP_PCB_POOL_DIAGNOSTICS
#include "esp_log.h"
#define POOL_TRACE(action, p, slot, state, owned) \
    ESP_LOGI("tcp_pool", "PERF TCP_POOL: action=%s address=%p slot=%u state=%u owned=%u", \
             action, p, (unsigned)(slot), (unsigned)(state), (unsigned)(owned))
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
    POOL_TRACE("alloc", result, result ? ((struct tcp_pcb *)result-s_pcbs) : MEMP_NUM_TCP_PCB, 0, result != NULL);
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
        POOL_TRACE("invalid-free", p, i, state, false);
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
    POOL_TRACE("free", p, i, state, true);
}
