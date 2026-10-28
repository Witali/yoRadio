#pragma once
#include "jpeg_transport.h"
#include "esp_err.h"

/* Keep platform heap policy out of the JPEG library, HTTP and LCD modules.
 * Available excludes the service reserve and respects contiguous allocations. */
size_t photo_storage_allocation_available(void);
bool photo_storage_service_memory(size_t *required,size_t *available);
/* Implemented by ESP-IDF; host tests bind the same transport to strict NOR/OS SHA.
 * Only initialization touches platform discovery. Jobs reuse one authorized boot. */
esp_err_t photo_storage_authorize(const jpeg_guard_layout_t *layout,
                                 jpeg_transport_t **transport,jpeg_guard_sha256_t *hash);
