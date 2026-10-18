
static atomic_bool s_ota_active;
typedef struct {
    web_reboot_lease_t reboot;
    audio_maintenance_token_t audio;
    uint64_t deadline;
} cyd_ota_context_t;

void web_ota_activate(void) { atomic_store(&s_ota_active, true); }
void web_ota_deactivate(void) { atomic_store(&s_ota_active, false); }
static esp_err_t ota_admit(void *opaque, uint64_t deadline) {
    cyd_ota_context_t *context = opaque;
    context->deadline = deadline;
    if (!atomic_load(&s_ota_active)) return ESP_ERR_INVALID_STATE;
    return web_reboot_reserve(&context->reboot);
}
static esp_err_t ota_before_flash(void *opaque) {
    cyd_ota_context_t *context = opaque;
    uint64_t now = (uint64_t)esp_timer_get_time();
    if (now >= context->deadline) return ESP_ERR_TIMEOUT;
    uint64_t timeout_ms = (context->deadline - now) / 1000U;
    if (timeout_ms > 30000U) timeout_ms = 30000U;
    if (!timeout_ms) return ESP_ERR_TIMEOUT;
    esp_err_t result = audio_service_maintenance_begin((uint32_t)timeout_ms, &context->audio);
    // An acknowledgement at/after the absolute deadline cannot authorize an
    // erase. The held token is handed back by the common failure cleanup.
    return result == ESP_OK && (uint64_t)esp_timer_get_time() >= context->deadline
               ? ESP_ERR_TIMEOUT : result;
}
static void ota_finished(void *opaque, bool activated) {
    cyd_ota_context_t *context = opaque;
    if (activated) {
        // Valid reservation pins the preallocated task. Sending/OOM cannot
        // cancel a boot selection; maintenance stays held through restart.
        (void)web_reboot_commit(&context->reboot, 1000);
    } else {
        if (context->audio.epoch) (void)audio_service_maintenance_end(&context->audio, true);
        if (context->reboot.epoch) (void)web_reboot_cancel(&context->reboot);
    }
}
esp_err_t web_ota_handler(httpd_req_t *request) {
    cyd_ota_context_t context = {0};
    native_ota_http_config_t config = {
        .policy = {.expected_chip = ESP_CHIP_ID_ESP32, .image_limit = WEB_OTA_MAX_IMAGE_BYTES,
            .before_flash = ota_before_flash, .context = &context},
        .max_body_bytes = WEB_OTA_MAX_BODY_BYTES,
        .admit = ota_admit, .finish = ota_finished, .context = &context,
    };
    memcpy(config.policy.expected_project, esp_app_get_description()->project_name, sizeof(config.policy.expected_project));
    return native_ota_http_upload(request, &config);
}
esp_err_t web_ota_info_handler(httpd_req_t *request) {
    return native_ota_http_info(request, WEB_OTA_MAX_IMAGE_BYTES);
}
