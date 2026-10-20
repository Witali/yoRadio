static void event_handler(void *arg, esp_event_base_t base, int32_t id,
                          void *event_data) {
    (void)arg;
    if (atomic_load(&s_stopping_for_sleep)) return;
    if (!((base == WIFI_EVENT && (id == WIFI_EVENT_STA_START ||
            id == WIFI_EVENT_STA_CONNECTED || id == WIFI_EVENT_STA_DISCONNECTED)) ||
          (base == IP_EVENT && (id == IP_EVENT_STA_GOT_IP || id == IP_EVENT_STA_LOST_IP)))) return;
    softap_operation(true);
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        if (s_have_credentials) connect_station();
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_CONNECTED) {
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_CONNECTED, 0);
#endif
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        softap_link(false, false);
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
        const wifi_event_sta_disconnected_t *event = event_data;
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_DISCONNECTED,
                                  event ? event->reason : 0);
#endif
        if (s_have_credentials &&
            s_retries++ < WIFI_RETRIES_PER_CREDENTIAL) {
            ESP_LOGW(TAG, "Wi-Fi network %u/%u retry %d/%d",
                     (unsigned)(s_credential_index + 1U),
                     (unsigned)s_credential_count, s_retries,
                     WIFI_RETRIES_PER_CREDENTIAL);
            connect_station();
        } else if (s_have_credentials &&
                   s_credential_index + 1U < s_credential_count) {
            ++s_credential_index;
            s_retries = 0;
            if (select_credential(s_credential_index) == ESP_OK) {
                ESP_LOGI(TAG, "Trying saved Wi-Fi network %u/%u",
                         (unsigned)(s_credential_index + 1U),
                         (unsigned)s_credential_count);
                connect_station();
            } else {
                xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
            }
        } else {
            xEventGroupSetBits(s_wifi_events, WIFI_FAILED_BIT);
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        softap_link(true, false);
#ifdef CONFIG_YORADIO_WEB_TCP_PROBE
        web_tcp_probe_record_wifi(WEB_TCP_WIFI_GOT_IP, 0);
#endif
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        wifi_ap_record_t access_point = {0};
        s_retries = 0;
        native_state_set_network(s_state, NATIVE_NETWORK_CLIENT,
                                 event->ip_info.ip.addr);
        if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK) {
            native_state_set_wifi_rssi(s_state, access_point.rssi);
        }
        time_service_notify_network_ready();
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG, "Client address: " IPSTR, IP2STR(&event->ip_info.ip));
    } else if (base == IP_EVENT && id == IP_EVENT_STA_LOST_IP) {
        softap_link(false, false);
    }
    softap_operation(false);
}
