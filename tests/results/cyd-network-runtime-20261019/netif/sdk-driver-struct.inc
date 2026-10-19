struct wifi_netif_driver {
    esp_netif_driver_base_t base;
    wifi_interface_t wifi_if;
};
