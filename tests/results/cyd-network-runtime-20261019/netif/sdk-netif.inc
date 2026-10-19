esp_netif_iodriver_handle esp_netif_get_io_driver(esp_netif_t *esp_netif)
{
    return esp_netif->driver_handle;
}
esp_err_t esp_netif_set_driver_config(esp_netif_t *esp_netif,
                                      const esp_netif_driver_ifconfig_t *driver_config)
{
    if (esp_netif == NULL || driver_config == NULL) {
        return ESP_ERR_ESP_NETIF_INVALID_PARAMS;
    }
    esp_netif->driver_handle = driver_config->handle;
    esp_netif->driver_transmit = driver_config->transmit;
    esp_netif->driver_transmit_wrap = driver_config->transmit_wrap;
    esp_netif->driver_free_rx_buffer = driver_config->driver_free_rx_buffer;
#if (LWIP_IPV4 && LWIP_IGMP) || (LWIP_IPV6 && LWIP_IPV6_MLD)
    esp_netif->driver_set_mac_filter = driver_config->driver_set_mac_filter;
#endif /* LWIP_IPV4 && LWIP_IGMP */
    return ESP_OK;
}
esp_err_t esp_netif_attach(esp_netif_t *esp_netif, esp_netif_iodriver_handle driver_handle)
{
    esp_netif_driver_base_t *base_driver = driver_handle;

    esp_netif->driver_handle = driver_handle;
    if (base_driver->post_attach) {
        esp_err_t ret = base_driver->post_attach(esp_netif, driver_handle);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Post-attach callback of driver(%p) failed with %d", driver_handle, ret);
            return ESP_ERR_ESP_NETIF_DRIVER_ATTACH_FAILED;
        }
    }
    return ESP_OK;
}
