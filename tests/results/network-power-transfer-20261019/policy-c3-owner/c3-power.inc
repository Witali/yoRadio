static esp_err_t apply_power(void *context, bool active) {
    (void)context;
    return esp_wifi_set_ps(active ? WIFI_PS_NONE : WIFI_PS_MIN_MODEM);
}

static void rssi_task(void *argument) {
    (void)argument;
    int64_t rssi_next = 0;
    while (true) {
        int64_t now = esp_timer_get_time();
        if (!atomic_load(&s_stopping_for_sleep)) {
            native_network_power_poll(now, apply_power, NULL);
            if (now >= rssi_next) {
                wifi_ap_record_t access_point = {0};
                if (esp_wifi_sta_get_ap_info(&access_point) == ESP_OK)
                    native_state_set_wifi_rssi(s_state, access_point.rssi);
                rssi_next = now > INT64_MAX - (int64_t)WIFI_RSSI_INTERVAL_MS * 1000
                    ? INT64_MAX : now + (int64_t)WIFI_RSSI_INTERVAL_MS * 1000;
            }
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void network_service_audio_accept(uint32_t generation, bool active) {
    native_network_power_accept(generation, active);
}

void network_service_audio_receive(uint32_t generation) {
    native_network_power_receive(generation);
}

void network_service_audio_finish(uint32_t generation) {
    native_network_power_finish(generation);
}

esp_err_t network_service_prepare_sleep(void) {
    atomic_store(&s_stopping_for_sleep, true);
    esp_err_t result = esp_wifi_stop();
    if (result != ESP_OK) atomic_store(&s_stopping_for_sleep, false);
    return result;
}
