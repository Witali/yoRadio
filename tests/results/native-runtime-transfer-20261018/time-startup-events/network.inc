static void station_lost_ip(void) {
    time_service_notify_network(false);
    xEventGroupClearBits(s_wifi_events, WIFI_CONNECTED_BIT);
    wifi_mode_t mode = WIFI_MODE_NULL;
    bool access_point = esp_wifi_get_mode(&mode) == ESP_OK &&
                        (mode == WIFI_MODE_AP || mode == WIFI_MODE_APSTA);
    native_state_set_network(s_state, access_point ? NATIVE_NETWORK_ACCESS_POINT
                                                   : NATIVE_NETWORK_STARTING, 0);
}
static void event_handler(void *arg, esp_event_base_t base, int32_t id,
                          void *event_data) {
    (void)arg;
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        if (s_have_credentials) esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        station_lost_ip();
        if (s_have_credentials && s_retries++ < WIFI_MAX_RETRIES) {
            ESP_LOGW(TAG, "Wi-Fi disconnected, retry %d/%d", s_retries,
                     WIFI_MAX_RETRIES);
            esp_wifi_connect();
        } else {
            xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        s_retries = 0;
        native_state_set_network(s_state, NATIVE_NETWORK_CLIENT,
                                 event->ip_info.ip.addr);
        time_service_notify_network(true);
        xEventGroupClearBits(s_wifi_events, WIFI_FAILED_BIT);
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: " IPSTR, IP2STR(&event->ip_info.ip));
    } else if (base == IP_EVENT && id == IP_EVENT_STA_LOST_IP) {
        station_lost_ip();
    }
}
esp_err_t network_service_start(native_state_t *state) {
    ESP_RETURN_ON_ERROR(network_service_storage_init(), TAG,
                        "Wi-Fi file storage initialization failed");
    s_state = state;
    s_wifi_events = xEventGroupCreate();
    ESP_RETURN_ON_FALSE(s_wifi_events, ESP_ERR_NO_MEM, TAG,
                        "Wi-Fi event group allocation failed");
    ESP_RETURN_ON_ERROR(esp_netif_init(), TAG, "TCP/IP stack failed");
    ESP_RETURN_ON_ERROR(esp_event_loop_create_default(), TAG,
                        "Default event loop failed");
    s_station_netif = esp_netif_create_default_wifi_sta();
    ESP_RETURN_ON_FALSE(s_station_netif, ESP_ERR_NO_MEM, TAG,
                        "Station network interface allocation failed");
    wifi_init_config_t init = WIFI_INIT_CONFIG_DEFAULT();
    ESP_RETURN_ON_ERROR(esp_wifi_init(&init), TAG, "Wi-Fi init failed");
    // The desired file owns persistence; never create another driver NVS copy.
    ESP_RETURN_ON_ERROR(esp_wifi_set_storage(WIFI_STORAGE_RAM), TAG,
                        "Wi-Fi RAM storage selection failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            WIFI_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL),
                        TAG, "Wi-Fi event registration failed");
    ESP_RETURN_ON_ERROR(esp_event_handler_register(
                            IP_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL),
                        TAG, "IP event registration failed");

    memset(&s_station_config, 0, sizeof(s_station_config));
    s_have_credentials = read_credentials(&s_station_config);
    if (s_have_credentials) {
        s_station_config.sta.threshold.authmode = WIFI_AUTH_OPEN;
        s_station_config.sta.pmf_cfg.capable = true;
        s_station_config.sta.pmf_cfg.required = false;
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
        ESP_RETURN_ON_ERROR(
            esp_wifi_set_config(WIFI_IF_STA, &s_station_config), TAG,
            "Station configuration failed");
    } else {
        ESP_RETURN_ON_ERROR(esp_wifi_set_mode(WIFI_MODE_STA), TAG,
                            "Station mode failed");
    }
    ESP_RETURN_ON_ERROR(esp_wifi_start(), TAG, "Wi-Fi start failed");

    if (s_have_credentials) {
        EventBits_t bits = xEventGroupWaitBits(
            s_wifi_events, WIFI_CONNECTED_BIT | WIFI_FAILED_BIT, pdTRUE,
            pdFALSE, pdMS_TO_TICKS(20000));
        if (bits & WIFI_CONNECTED_BIT) return ESP_OK;
    }
    return start_access_point();
}
