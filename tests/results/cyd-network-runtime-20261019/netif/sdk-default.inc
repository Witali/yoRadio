static esp_err_t clear_default_wifi_handlers(void)
{
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_STA_START, wifi_default_action_sta_start);
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_STA_STOP, wifi_default_action_sta_stop);
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, wifi_default_action_sta_connected);
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, wifi_default_action_sta_disconnected);
#ifdef CONFIG_ESP_WIFI_SOFTAP_SUPPORT
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_AP_START, wifi_default_action_ap_start);
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_AP_STOP, wifi_default_action_ap_stop);
#endif
    esp_event_handler_unregister(IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_default_action_sta_got_ip);
#ifdef CONFIG_ESP_WIFI_NAN_SYNC_ENABLE
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_NAN_SYNC_STARTED, wifi_default_action_nan_started);
    esp_event_handler_unregister(WIFI_EVENT, WIFI_EVENT_NAN_SYNC_STOPPED, wifi_default_action_nan_stopped);
#endif
    esp_unregister_shutdown_handler((shutdown_handler_t)esp_wifi_stop);
    wifi_default_handlers_set = false;
    return ESP_OK;
}
static esp_err_t set_default_wifi_handlers(void)
{
    if (wifi_default_handlers_set) {
        return ESP_OK;
    }
    esp_err_t err;

    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_STA_START, wifi_default_action_sta_start, NULL);
    if (err != ESP_OK) {
        goto fail;
    }

    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_STA_STOP, wifi_default_action_sta_stop, NULL);
    if (err != ESP_OK) {
        goto fail;
    }

    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_STA_CONNECTED, wifi_default_action_sta_connected, NULL);
    if (err != ESP_OK) {
        goto fail;
    }

    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_STA_DISCONNECTED, wifi_default_action_sta_disconnected, NULL);
    if (err != ESP_OK) {
        goto fail;
    }

#ifdef CONFIG_ESP_WIFI_SOFTAP_SUPPORT
    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_AP_START, wifi_default_action_ap_start, NULL);
    if (err != ESP_OK) {
        goto fail;
    }

    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_AP_STOP, wifi_default_action_ap_stop, NULL);
    if (err != ESP_OK) {
        goto fail;
    }
#endif

    err = esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_default_action_sta_got_ip, NULL);
    if (err != ESP_OK) {
        goto fail;
    }

#ifdef CONFIG_ESP_WIFI_NAN_SYNC_ENABLE
    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_NAN_SYNC_STARTED, wifi_default_action_nan_started, NULL);
    if (err != ESP_OK) {
        goto fail;
    }

    err = esp_event_handler_register(WIFI_EVENT, WIFI_EVENT_NAN_SYNC_STOPPED, wifi_default_action_nan_stopped, NULL);
    if (err != ESP_OK) {
        goto fail;
    }
#endif

    err = esp_register_shutdown_handler((shutdown_handler_t)esp_wifi_stop);
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        goto fail;
    }
    wifi_default_handlers_set = true;
    return ESP_OK;

fail:
    clear_default_wifi_handlers();
    return err;
}
esp_err_t esp_wifi_set_default_wifi_sta_handlers(void)
{
    return set_default_wifi_handlers();
}
esp_err_t esp_wifi_set_default_wifi_ap_handlers(void)
{
    return set_default_wifi_handlers();
}
esp_err_t esp_wifi_clear_default_wifi_driver_and_handlers(void *esp_netif)
{
    int i;
    for (i = 0; i < MAX_WIFI_IFS; ++i) {
        // clear internal static pointers to netifs
        if (s_wifi_netifs[i] == esp_netif) {
            s_wifi_netifs[i] = NULL;
        }
    }
    for (i = 0; i < MAX_WIFI_IFS; ++i) {
        // check if all netifs are cleared to delete default handlers
        if (s_wifi_netifs[i] != NULL) {
            break;
        }
    }

    if (i == MAX_WIFI_IFS) { // if all wifi default netifs are null
        ESP_LOGD(TAG, "Clearing wifi default handlers");
        clear_default_wifi_handlers();
    }
    return disconnect_and_destroy(esp_netif);
}
static esp_err_t disconnect_and_destroy(esp_netif_t* esp_netif)
{
    wifi_netif_driver_t driver = esp_netif_get_io_driver(esp_netif);
    esp_netif_driver_ifconfig_t driver_ifconfig = { };
    esp_err_t  ret = esp_netif_set_driver_config(esp_netif, &driver_ifconfig);
    esp_wifi_destroy_if_driver(driver);
    return ret;
}
static esp_err_t create_and_attach(wifi_interface_t wifi_if, esp_netif_t* esp_netif)
{
    wifi_netif_driver_t driver = esp_wifi_create_if_driver(wifi_if);
    if (driver == NULL) {
        ESP_LOGE(TAG, "Failed to create wifi interface handle");
        return ESP_FAIL;
    }
    return esp_netif_attach(esp_netif, driver);
}
static inline esp_err_t esp_netif_attach_wifi(esp_netif_t *esp_netif, wifi_interface_t wifi_if)
{
    if (esp_netif == NULL || (wifi_if != WIFI_IF_STA
#ifdef CONFIG_ESP_WIFI_SOFTAP_SUPPORT
                              && wifi_if != WIFI_IF_AP
#endif
#ifdef CONFIG_ESP_WIFI_NAN_SYNC_ENABLE
                              && wifi_if != WIFI_IF_NAN
#endif
                             )) {
        return ESP_ERR_INVALID_ARG;
    }
    s_wifi_netifs[wifi_if] = esp_netif;
    return create_and_attach(wifi_if, esp_netif);
}
esp_err_t esp_netif_attach_wifi_station(esp_netif_t *esp_netif)
{
    return esp_netif_attach_wifi(esp_netif, WIFI_IF_STA);
}
esp_err_t esp_netif_attach_wifi_ap(esp_netif_t *esp_netif)
{
    return esp_netif_attach_wifi(esp_netif, WIFI_IF_AP);
}
