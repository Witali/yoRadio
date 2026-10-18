static void json_escape(const char *source, char *target, size_t target_size) {
    if (!target_size) return;
    json_buffer_t out;
    json_buffer_init(&out, target, target_size);
    json_buffer_string(&out, source);
    // The shared encoder appends whole escapes/UTF-8 sequences atomically.
    // Preserve its bounded valid prefix even when the complete field did not
    // fit, removing the quotes supplied separately by these legacy JSON forms.
    size_t length = out.length ? out.length - 1U : 0U;
    if (!out.failed && length) --length;
    if (length) memmove(target, target + 1, length);
    target[length] = '\0';
}
static esp_err_t send_timezone_settings(httpd_req_t *request) {
    runtime_time_settings_t current;
    esp_err_t result = runtime_settings_get_time_snapshot(&current, 100);
    if (result != ESP_OK) return result;
    char escaped1[208], escaped2[208];
    char settings[640];
    json_escape(current.servers[0], escaped1, sizeof(escaped1));
    json_escape(current.servers[1], escaped2, sizeof(escaped2));
    snprintf(settings, sizeof(settings),
             "{\"tzh\":%d,\"tzm\":%u,\"sntp1\":\"%s\","
             "\"sntp2\":\"%s\",\"timeint\":%u,\"timeintrtc\":24}",
             current.timezone_hour, current.timezone_minute, escaped1, escaped2,
             current.sync_interval_min);
    return ws_send_request(request, settings);
}
