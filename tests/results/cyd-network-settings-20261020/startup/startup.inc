static esp_err_t mount_spiffs(void) {
    esp_vfs_spiffs_conf_t config = {
        .base_path = "/spiffs",
        .partition_label = "spiffs",
        .max_files = 8,
        // Never format automatically: this preserves Wi-Fi, playlist and UI.
        .format_if_mount_failed = false,
    };
    return esp_vfs_spiffs_register(&config);
}
void app_main(void) {
    ESP_LOGI(TAG, "Starting pure ESP-IDF yoRadio (Arduino-free)");
    if (!native_health_start()) ESP_LOGW(TAG, "Health sampler initialization failed");
    native_state_init(&s_state);

    esp_err_t result = nvs_flash_init();
    if (result != ESP_OK) {
        // Do not erase NVS automatically. Existing settings have priority.
        ESP_LOGE(TAG, "NVS init failed without erase: %s",
                 esp_err_to_name(result));
    }
    ESP_ERROR_CHECK(native_audio_settings_init());
    result = network_settings_init();
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Network settings unavailable: %s", esp_err_to_name(result));
    }
    result = mount_spiffs();
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS mount failed without format: %s",
                 esp_err_to_name(result));
    }
    ESP_ERROR_CHECK(cyd_display_init(&s_display));
    result = time_service_start();
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Time service unavailable: %s", esp_err_to_name(result));
    }

    xTaskCreatePinnedToCore(display_task, "display", BOARD_TASK_STACK_DISPLAY,
                            NULL, 1, NULL, 0);
    xTaskCreatePinnedToCore(network_task, "network", BOARD_TASK_STACK_NETWORK,
                            NULL, 3, NULL, 0);
}
