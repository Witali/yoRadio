#pragma once

#include <stdbool.h>

#include "esp_err.h"
#include "esp_netif.h"

typedef struct {
    esp_netif_t *handle;
    bool cleanup_failed;
} network_netif_t;

// Caller serializes this owner's lifecycle. Create requires a zero owner;
// ESP_OK alone makes handle usable. A failed create returns the original SDK
// error and releases partial setup, unless cleanup_failed retains that partial
// owner for the process lifetime. Never use its handle as a working interface.
esp_err_t network_netif_create(network_netif_t *out, bool ap);

// Stop Wi-Fi and exclude application callbacks/users before releasing. An empty
// owner succeeds. A cleanup error permanently retains the object: the pinned
// SDK may already have freed its driver despite returning an error, so another
// clear/destroy attempt is unsafe and returns INVALID_STATE without SDK calls.
esp_err_t network_netif_release(network_netif_t *owner);
