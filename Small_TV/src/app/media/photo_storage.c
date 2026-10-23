#include "photo_storage.h"
#include "jpeg_espidf.h"
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
    /* REQUESTED_CHANGE: verify exact partitions, immutable assets and stamp once
     * before allowing the worker to use cache/scratch capabilities. No erases. */
    esp_err_t error=jpeg_espidf_init(&storage);
    if(error!=ESP_OK)return error;
    const jpeg_transport_limits_t limits={10000,0x400000,0,0,30000000};
    if(jpeg_espidf_authorize(&storage,layout,&limits)!=JPEG_TRANSPORT_OK)return ESP_ERR_INVALID_STATE;
    *transport=&storage.transport;*hash=jpeg_espidf_hash_provider(&storage);return ESP_OK;
}
