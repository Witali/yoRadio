static esp_err_t wifi_driver_start(esp_netif_t * esp_netif, void * args)
{
    wifi_netif_driver_t driver = args;
    driver->base.netif = esp_netif;
    esp_netif_driver_ifconfig_t driver_ifconfig = {
        .handle =  driver,
        .transmit = wifi_transmit,
        .transmit_wrap = wifi_transmit_wrap,
        .driver_free_rx_buffer = wifi_free
    };

    return esp_netif_set_driver_config(esp_netif, &driver_ifconfig);
}
void esp_wifi_destroy_if_driver(wifi_netif_driver_t h)
{
    if (h) {
        esp_wifi_internal_reg_rxcb(h->wifi_if, NULL);  // ignore the potential error
        // as the wifi might have been already uninitialized
        s_wifi_netifs[h->wifi_if] = NULL;
    }
    free(h);
}
wifi_netif_driver_t esp_wifi_create_if_driver(wifi_interface_t wifi_if)
{
    wifi_netif_driver_t driver = calloc(1, sizeof(struct wifi_netif_driver));
    if (driver == NULL) {
        ESP_LOGE(TAG, "No memory to create a wifi interface handle");
        return NULL;
    }
    driver->wifi_if = wifi_if;
    driver->base.post_attach = wifi_driver_start;
    return driver;
}
