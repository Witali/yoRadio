#include "network_netif.h"

#include <stddef.h>

#include "esp_wifi_default.h"

esp_err_t network_netif_release(network_netif_t *owner) {
    if (!owner) return ESP_ERR_INVALID_ARG;
    if (owner->cleanup_failed) return ESP_ERR_INVALID_STATE;
    if (!owner->handle) return ESP_OK;
    esp_err_t result = esp_wifi_clear_default_wifi_driver_and_handlers(owner->handle);
    if (result != ESP_OK) {
        owner->cleanup_failed = true;
        return result;
    }
    esp_netif_destroy(owner->handle);
    owner->handle = NULL;
    return ESP_OK;
}

esp_err_t network_netif_create(network_netif_t *out, bool ap) {
    if (!out) return ESP_ERR_INVALID_ARG;
    if (out->handle || out->cleanup_failed) return ESP_ERR_INVALID_STATE;
    esp_netif_config_t config = !ap ? (esp_netif_config_t)ESP_NETIF_DEFAULT_WIFI_AP()
                                   : (esp_netif_config_t)ESP_NETIF_DEFAULT_WIFI_STA();
    out->handle = esp_netif_new(&config);
    if (!out->handle) return ESP_ERR_NO_MEM;
    esp_err_t result = ap ? esp_netif_attach_wifi_ap(out->handle)
                          : esp_netif_attach_wifi_station(out->handle);
    if (result == ESP_OK) result = ap ? esp_wifi_set_default_wifi_ap_handlers()
                                     : esp_wifi_set_default_wifi_sta_handlers();
    if (result != ESP_OK) (void)network_netif_release(out);
    return result;
}
