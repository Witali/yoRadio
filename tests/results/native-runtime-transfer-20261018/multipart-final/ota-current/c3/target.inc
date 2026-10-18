
typedef struct {
    websocket_reboot_lease_t reboot;
    audio_maintenance_token_t audio;
    uint64_t deadline;
    bool activity;
} c3_ota_context_t;

static esp_err_t ota_admit(void *opaque, uint64_t deadline) {
    c3_ota_context_t *context = opaque;
    context->deadline = deadline;
    if (!deep_sleep_clock_begin_activity()) return ESP_ERR_INVALID_STATE;
    context->activity = true;
    display_settings_note_activity();
    return websocket_service_reboot_reserve(&context->reboot);
}
static esp_err_t ota_before_flash(void *opaque) {
    c3_ota_context_t *context = opaque;
    uint64_t now = (uint64_t)esp_timer_get_time();
    if (now >= context->deadline) return ESP_ERR_TIMEOUT;
    uint64_t timeout_ms = (context->deadline - now) / 1000U;
    if (timeout_ms > 30000U) timeout_ms = 30000U;
    if (!timeout_ms) return ESP_ERR_TIMEOUT;
    esp_err_t result = audio_service_maintenance_begin((uint32_t)timeout_ms, &context->audio);
    return result == ESP_OK && (uint64_t)esp_timer_get_time() >= context->deadline
               ? ESP_ERR_TIMEOUT : result;
}
static void ota_finished(void *opaque, bool activated) {
    c3_ota_context_t *context = opaque;
    if (activated) {
        // Both audio and activity stay held until the preallocated status task
        // restarts. A failed response cannot cancel the selected application.
        (void)websocket_service_reboot_commit(&context->reboot, 1000);
    } else {
        if (context->audio.epoch) (void)audio_service_maintenance_end(&context->audio, true);
        if (context->reboot.epoch) (void)websocket_service_reboot_cancel(&context->reboot);
        if (context->activity) deep_sleep_clock_end_activity();
    }
}

esp_err_t web_ota_handler(httpd_req_t *request) {
    c3_ota_context_t context = {0};
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *next = running ? esp_ota_get_next_update_partition(running) : NULL;
    native_ota_http_config_t config = {
        .policy = {.expected_chip = ESP_CHIP_ID_ESP32C3, .image_limit = next ? next->size : 1,
            .before_flash = ota_before_flash, .context = &context},
        .admit = ota_admit, .finish = ota_finished, .context = &context,
    };
    memcpy(config.policy.expected_project, esp_app_get_description()->project_name, sizeof(config.policy.expected_project));
    return native_ota_http_upload(request, &config);
}
esp_err_t web_ota_info_handler(httpd_req_t *request) {
    if (!deep_sleep_clock_begin_activity()) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Wake the radio with BOOT");
    }
    display_settings_note_activity();
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *next = running ? esp_ota_get_next_update_partition(running) : NULL;
    esp_err_t result = native_ota_http_info(request, next ? next->size : 0);
    deep_sleep_clock_end_activity();
    return result;
}
