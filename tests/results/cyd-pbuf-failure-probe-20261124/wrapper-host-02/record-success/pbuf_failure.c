/* Opt-in diagnostic only. Preserve the public lwIP call and its return value.
 * A bounded record is written only after a NULL return; no heap, heap query,
 * task discovery or logging runs in that path. GNU wrapping does not cover
 * calls that the linker resolves locally inside pbuf.c. */
#include <stdint.h>

#include "esp_attr.h"
#include "esp_cpu_utils.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "lwip/mem.h"
#include "lwip/pbuf.h"
#include "pbuf_failure_record.h"

static DRAM_ATTR portMUX_TYPE s_pbuf_failure_lock = portMUX_INITIALIZER_UNLOCKED;
static DRAM_ATTR pbuf_failure_record_t s_pbuf_failures;

_Static_assert(sizeof(s_pbuf_failures) <= 128, "Keep the diagnostic table bounded");

struct pbuf *__real_pbuf_alloc(pbuf_layer layer, u16_t length, pbuf_type type);
struct pbuf *__wrap_pbuf_alloc(pbuf_layer layer, u16_t length, pbuf_type type);
void cyd_openeth_pbuf_failure_dump(void);

/* Reproduce pbuf_alloc's PBUF_RAM size formula and overflow guards. This is a
 * derived size, not an observed malloc argument. Zero means unavailable for
 * this type/overflow branch. Preserve the SDK's u16_t layer conversion. */
static uint32_t derived_allocation_bytes(pbuf_layer layer, u16_t length, pbuf_type type) {
    if (type != PBUF_RAM) return 0;
    u16_t offset = (u16_t)layer;
    mem_size_t payload_len = (mem_size_t)(LWIP_MEM_ALIGN_SIZE(offset) + LWIP_MEM_ALIGN_SIZE(length));
    mem_size_t alloc_len = (mem_size_t)(LWIP_MEM_ALIGN_SIZE(sizeof(struct pbuf)) + payload_len);
    if (payload_len < LWIP_MEM_ALIGN_SIZE(length) || alloc_len < LWIP_MEM_ALIGN_SIZE(length)) return 0;
    return (uint32_t)alloc_len;
}

__attribute__((noinline))
struct pbuf *__wrap_pbuf_alloc(pbuf_layer layer, u16_t length, pbuf_type type) {
    struct pbuf *result = __real_pbuf_alloc(layer, length, type);
    if (result) {
        pbuf_failure_key_t key = {
            .layer = (uint32_t)layer, .type = (uint32_t)type, .length = length,
            .allocation_bytes = derived_allocation_bytes(layer, length, type),
            .caller_pc = esp_cpu_process_stack_pc((uint32_t)(uintptr_t)__builtin_return_address(0)),
        };
        // The allocator has returned before this separate critical section.
        // Match the existing health callback's task/ISR-compatible lock form.
        portENTER_CRITICAL_ISR(&s_pbuf_failure_lock);
        pbuf_failure_record_add(&s_pbuf_failures, &key);
        portEXIT_CRITICAL_ISR(&s_pbuf_failure_lock);
    }
    return result;
}

/* Called by the existing diagnostic PCM EOF owner. Copy while locked, then
 * print outside the lock, after the real audio flush has returned. Counters
 * are cumulative and are not cleared or substituted for global heap faults. */
void cyd_openeth_pbuf_failure_dump(void) {
    pbuf_failure_record_t snapshot;
    portENTER_CRITICAL_ISR(&s_pbuf_failure_lock);
    pbuf_failure_record_snapshot(&s_pbuf_failures, &snapshot);
    portEXIT_CRITICAL_ISR(&s_pbuf_failure_lock);
    esp_rom_printf("CYD_OPENETH_PBUF_FAILURE_SUMMARY total=%u overflow=%u used=%u saturated=%u table_bytes=%u lock_bytes=%u\n",
        (unsigned)snapshot.total, (unsigned)snapshot.overflow, (unsigned)snapshot.used,
        (unsigned)snapshot.saturated, (unsigned)sizeof(s_pbuf_failures), (unsigned)sizeof(s_pbuf_failure_lock));
    for (uint32_t i = 0; i < snapshot.used; ++i) {
        const pbuf_failure_entry_t *entry = &snapshot.entries[i];
        esp_rom_printf("CYD_OPENETH_PBUF_FAILURE index=%u layer=%u type=%u length=%u derived_allocation_bytes=%u caller_pc=0x%08x count=%u saturated=%u\n",
            (unsigned)i, (unsigned)entry->key.layer, (unsigned)entry->key.type,
            (unsigned)entry->key.length, (unsigned)entry->key.allocation_bytes,
            (unsigned)entry->key.caller_pc, (unsigned)entry->count, (unsigned)entry->saturated);
    }
}
