static esp_err_t reconnect_handler(httpd_req_t *request) {
    if (request->content_len) {
        (void)httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST, "Reconnect does not accept a body");
        return ESP_FAIL;
    }
    esp_err_t result = network_service_retry_client();
    if (result != ESP_OK) {
        httpd_resp_set_status(request, result == ESP_ERR_NOT_FOUND ? "400 Bad Request" :
            result == ESP_ERR_TIMEOUT ? "409 Conflict" : "503 Service Unavailable");
        httpd_resp_set_type(request, "application/json");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_sendstr(request, result == ESP_ERR_NOT_FOUND ?
            "{\"error\":\"no_active_profiles\"}" : result == ESP_ERR_TIMEOUT ?
            "{\"error\":\"retry_pending\"}" : "{\"error\":\"network_unavailable\"}");
    }
    httpd_resp_set_type(request, "application/json");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, "{\"reconnecting\":true,\"accepted\":true}");
}
static esp_err_t network_handler(httpd_req_t *request) {
    if (request->content_len) {
        (void)httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST, "Network status does not accept a body");
        return ESP_FAIL;
    }
    network_snapshot_t view;
    if (network_service_snapshot(&view, 100) != ESP_OK) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        httpd_resp_set_type(request, "application/json; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_sendstr(request, "{\"error\":\"network_unavailable\"}");
    }
    static const char *const phases[] = {"wait_start", "disconnecting", "retry_wait",
                                         "connecting", "online", "ap_idle"};
    const char *phase = (unsigned)view.phase < sizeof(phases)/sizeof(phases[0]) ? phases[view.phase] : "unknown";
    char body[768];
    int size = snprintf(body, sizeof(body),
        "{\"phase\":\"%s\",\"epoch\":%lu,\"online\":%s,\"ap_enabled\":%s,"
        "\"reconciling\":%s,\"active_profiles\":%u,\"profile_index\":%u,\"target_profile\":%u,"
        "\"attempt\":%u,\"profiles_tried\":%u,\"ipv4\":%lu,\"rssi_valid\":%s,\"rssi\":%d,"
        "\"rssi_age_ms\":%llu,\"event_overflows\":%lu,\"last_error\":%ld,\"disconnect_reason\":%u}",
        phase, (unsigned long)view.epoch, view.online ? "true" : "false",
        view.ap_enabled ? "true" : "false", view.reconciling ? "true" : "false",
        view.profile_count, view.profile_index, view.target_profile, view.attempt, view.profiles_tried,
        (unsigned long)view.ipv4, view.rssi_valid ? "true" : "false", view.rssi,
        (unsigned long long)view.rssi_age_ms, (unsigned long)view.event_overflows,
        (long)view.last_error, view.disconnect_reason);
    if (size < 0 || (size_t)size >= sizeof(body))
        return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Network status exhausted");
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}
