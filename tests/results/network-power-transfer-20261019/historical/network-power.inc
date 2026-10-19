esp_err_t network_service_set_streaming(bool active) {
    const wifi_ps_type_t mode = active ? WIFI_PS_NONE : WIFI_PS_MIN_MODEM;
    esp_err_t result = esp_wifi_set_ps(mode);
    if (result == ESP_OK) {
        ESP_LOGI(TAG, "Wi-Fi power save: %s",
                 active ? "disabled for audio" : "modem sleep");
    } else {
        ESP_LOGW(TAG, "Wi-Fi power save update failed: %s",
                 esp_err_to_name(result));
    }
    return result;
}
