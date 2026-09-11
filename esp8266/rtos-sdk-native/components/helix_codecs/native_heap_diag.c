#include "native_heap_diag.h"
#include "esp_heap_caps.h"
#include "esp_heap_port.h"
#include "priv/esp_heap_caps_priv.h"
#ifdef CONFIG_HEAP_TRACING
#error "Diagnostic heap walker requires the untraced ESP8266 allocator"
#endif
extern heap_region_t g_heap_region[];
extern size_t g_heap_region_num;
native_heap_diag_t native_heap_diag_snapshot(void) {
    native_heap_diag_t out = {0, 0};
    bool valid = true;
    _heap_caps_lock(0);
    for (size_t i=0; i<g_heap_region_num; ++i) {
        heap_region_t *region = &g_heap_region[i];
        if (!(region->caps & MALLOC_CAP_8BIT)) continue;
        out.free_dram += region->free_bytes;
        uintptr_t start=(uintptr_t)region->start_addr;
        if (region->total_size < MEM_HEAD_SIZE || region->total_size > UINTPTR_MAX-start) {
            valid=false; continue;
        }
        uintptr_t end=start+region->total_size;
        for (mem_blk_t *block=region->free_blk; block;) {
            uintptr_t address=(uintptr_t)block;
            if (address<start || address>end-MEM_HEAD_SIZE || address%HEAP_ALIGN_SIZE) {
                valid=false; break;
            }
            mem_blk_t *next=mem_blk_next(block);
            if (!next) break; /* terminal sentinel has no allocatable payload */
            if ((uintptr_t)next<=address || (uintptr_t)next>end-MEM_HEAD_SIZE ||
                (uintptr_t)next-address<MEM_HEAD_SIZE ||
                (uintptr_t)next%HEAP_ALIGN_SIZE) { valid=false; break; }
            if (!mem_blk_is_used(block)) {
                size_t span=blk_link_size(block)&~(HEAP_ALIGN_SIZE-1U);
                size_t payload=span>MEM_HEAD_SIZE ? span-MEM_HEAD_SIZE : 0;
                if (payload>out.largest_dram) out.largest_dram=payload;
            }
            block=next;
        }
    }
    _heap_caps_unlock(0);
    if (!valid) out.largest_dram=UINT32_MAX;
    return out;
}
