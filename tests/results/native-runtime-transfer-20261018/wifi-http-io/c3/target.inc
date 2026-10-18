
typedef struct {
    websocket_reboot_lease_t reboot;
    bool activity;
} wifi_edit_context_t;

static esp_err_t wifi_admit(void *opaque) {
    wifi_edit_context_t *context = opaque;
    if (!deep_sleep_clock_begin_activity()) return ESP_ERR_INVALID_STATE;
    context->activity = true;
    display_settings_note_activity();
    return websocket_service_reboot_reserve(&context->reboot);
}
static void wifi_finished(void *opaque, bool committed) {
    wifi_edit_context_t *context = opaque;
    if (committed) {
        // Activity and reservation remain held through response failure/restart.
        (void)websocket_service_reboot_commit(&context->reboot, 750);
    } else {
        if (context->reboot.epoch) (void)websocket_service_reboot_cancel(&context->reboot);
        if (context->activity) deep_sleep_clock_end_activity();
    }
}
esp_err_t web_wifi_edit_handler(httpd_req_t *request) {
    wifi_edit_context_t context = {0};
    const native_wifi_http_config_t config = {
        .edit = network_service_wifi_edit, .admit = wifi_admit,
        .finish = wifi_finished, .context = &context,
    };
    return native_wifi_http_edit(request, &config);
}
esp_err_t web_wifi_info_handler(httpd_req_t *request) {
    if (!deep_sleep_clock_begin_activity()) {
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_hdr(request, "Connection", "close");
        httpd_resp_set_status(request, "503 Service Unavailable");
        esp_err_t sent = httpd_resp_sendstr(request, "Clock is entering sleep");
        native_wifi_request_io_close(request, NULL, sent == ESP_OK, false);
        return ESP_FAIL;
    }
    display_settings_note_activity();
    esp_err_t result = native_wifi_http_info(request, network_service_wifi_metadata);
    deep_sleep_clock_end_activity();
    return result;
}
