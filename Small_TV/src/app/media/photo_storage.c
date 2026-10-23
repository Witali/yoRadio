#include "photo_storage.h"
#include "jpeg_espidf.h"
#include "jpeg_layout.h"
#include "settings.h"
#include "esp_heap_caps.h"

static jpeg_espidf_t storage;

bool photo_storage_service_memory(size_t *required,size_t *available)
{
    /* Other tasks may consume RAM after a successful codec allocation. Keep
     * checking the service floor during buffered work, not only at malloc. */
    *required=16u*1024u;*available=heap_caps_get_free_size(MALLOC_CAP_8BIT);
    return *available>=*required;
}

size_t photo_storage_allocation_available(void)
{
    /* FIXED_RECONSTRUCTION: a successful codec malloc must not consume the RAM
     * needed by Wi-Fi/HTTP. The integrated C2 failure left only1392minimum bytes.
     * This16KiB policy is service headroom, not a promise that every JPEG fits.
     * Observe both total free8bit RAM and the largest contiguous block; later
     * allocator failure is still possible because other tasks can allocate. */
    size_t reserve,free;photo_storage_service_memory(&reserve,&free);
    size_t largest=heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    size_t available=free>reserve ? free-reserve:0;
    return available<largest ? available:largest;
}

esp_err_t photo_storage_authorize(const jpeg_guard_layout_t *layout,
                                 jpeg_transport_t **transport,jpeg_guard_sha256_t *hash)
{
    /* REQUESTED_CHANGE: verify partitions/assets before granting capabilities.
     * A matching legacy layout may receive only its canonical stamp (32+8bytes),
     * after full vacant-candidate checks, with no erases/photos/settings writes. */
    esp_err_t error=jpeg_espidf_init(&storage);
    if(error!=ESP_OK)return error;
    /* REQUESTED_CHANGE: a persisted zero also forbids adopting an unstamped
     * legacy image. Startup precedes HTTP, so the loaded policy is stable here.
     * Complete matching stamps authorize reads without any program/erase. */
    bool readonly=settings_jpeg_write_limit_kib()==0;
    const jpeg_transport_limits_t limits={30000,0x800000,readonly ? 0:JPEG_PROVISION_PROGRAM_BYTES,0,60000000};
    jpeg_transport_result_t authorized;
    if(readonly)authorized=jpeg_espidf_authorize(&storage,layout,&limits);
    else {
        jpeg_provision_diagnostic_t diagnostic;
        authorized=jpeg_espidf_provision(&storage,layout,&jpeg_layout_stamp,&diagnostic,&limits);
    }
    if(authorized!=JPEG_TRANSPORT_OK)
        return ESP_ERR_INVALID_STATE;
    *transport=&storage.transport;*hash=jpeg_espidf_hash_provider(&storage);return ESP_OK;
}
