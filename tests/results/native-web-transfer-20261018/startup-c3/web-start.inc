static void abort_static_startup(void) {
    // No HTTP listener existed, so workers cannot own requests yet.
    for (size_t i = 0; i < CONFIG_YORADIO_WEB_STATIC_WORKERS; ++i) {
        if (s_static_worker_tasks[i]) vTaskDelete(s_static_worker_tasks[i]);
        s_static_worker_tasks[i] = NULL;
    }
    if (s_static_request_queue) vQueueDelete(s_static_request_queue);
    s_static_request_queue = NULL;
}
esp_err_t web_service_start(native_state_t *state) {
    if (!state || !state->lock) return ESP_ERR_INVALID_ARG;
    bool expected = false;
    if (!atomic_compare_exchange_strong(&s_started, &expected, true)) return ESP_ERR_INVALID_STATE;
    s_state = state;
    esp_fill_random(&s_health_boot_id, sizeof(s_health_boot_id));
    esp_err_t result = web_upload_storage_init();
    if (result != ESP_OK) goto unprepared;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 8192; // Upload payload is a bounded, temporary heap buffer.
    // Browsers commonly fetch six assets in parallel. Keep those connections
    // plus the persistent WebSocket alive; with four sockets the LRU purge
    // closed /ws during page startup and the shared UI spinner never stopped.
    config.max_open_sockets = WEB_MAX_OPEN_SOCKETS;
    config.max_uri_handlers = 15; // Includes WebSocket, memory probe and final wildcard.
    config.lru_purge_enable = true;
    config.send_wait_timeout = CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS;
    config.uri_match_fn = httpd_uri_match_wildcard;
    httpd_handle_t server = NULL;
    result = native_web_transport_prepare(&config);
    if (result != ESP_OK) goto unprepared;
    result = start_static_workers();
    if (result != ESP_OK) goto release_transport;
    result = httpd_start(&server, &config);
    if (result != ESP_OK) {
        abort_static_startup();
        goto release_transport;
    }
    // Once HTTPD is live, retain its workers/transport on a route failure.
    // C3's producer lifetime has no stop API; prevent a second partial start.
    httpd_uri_t status = {
        .uri = "/api/native/status",
        .method = HTTP_GET,
        .handler = status_handler,
    };
    httpd_uri_t health = {
        .uri = "/api/native/health", .method = HTTP_GET,
        .handler = health_handler,
    };
    httpd_uri_t ota = {
        .uri = "/update", .method = HTTP_POST, .handler = web_ota_handler,
    };
    httpd_uri_t ota_info = {
        .uri = "/api/native/ota", .method = HTTP_GET,
        .handler = web_ota_info_handler,
    };
    httpd_uri_t reconnect = {
        .uri = "/api/native/reconnect",
        .method = HTTP_POST,
        .handler = sleep_guarded_reconnect_handler,
    };
    httpd_uri_t play = {
        .uri = "/api/native/play*",
        .method = HTTP_POST,
        .handler = sleep_guarded_play_handler,
    };
    httpd_uri_t stop = {
        .uri = "/api/native/stop",
        .method = HTTP_POST,
        .handler = sleep_guarded_stop_handler,
    };
    httpd_uri_t upload = {
        .uri = "/upload",
        .method = HTTP_POST,
        .handler = sleep_guarded_upload_handler,
    };
    httpd_uri_t webboard_page = {
        .uri = "/webboard",
        .method = HTTP_GET,
        .handler = webboard_page_handler,
    };
    httpd_uri_t webboard_upload = {
        .uri = "/webboard",
        .method = HTTP_POST,
        .handler = sleep_guarded_webboard_upload_handler,
    };
    httpd_uri_t emergency = {
        .uri = "/emergency",
        .method = HTTP_GET,
        .handler = sleep_guarded_emergency_handler,
    };
    httpd_uri_t recovery_wifi = {
        .uri = "/",
        .method = HTTP_POST,
        .handler = sleep_guarded_recovery_wifi_handler,
    };
    httpd_uri_t files = {
        .uri = "/*",
        .method = HTTP_GET,
        .handler = static_handler,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &status), TAG,
                        "Status route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &health), TAG,
                        "Health route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &ota), TAG,
                        "OTA route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &ota_info), TAG,
                        "OTA info route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &reconnect), TAG,
                        "Reconnect route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &play), TAG,
                        "Play route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &stop), TAG,
                        "Stop route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &upload), TAG,
                        "Upload route registration failed");
    ESP_RETURN_ON_ERROR(
        httpd_register_uri_handler(server, &webboard_page), TAG,
        "Web board page route registration failed");
    ESP_RETURN_ON_ERROR(
        httpd_register_uri_handler(server, &webboard_upload), TAG,
        "Web board upload route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &emergency), TAG,
                        "Emergency page route registration failed");
    ESP_RETURN_ON_ERROR(
        httpd_register_uri_handler(server, &recovery_wifi), TAG,
        "Recovery Wi-Fi route registration failed");
    httpd_uri_t memory = {
        .uri = "/api/native/web-memory", .method = HTTP_GET,
        .handler = web_memory_handler,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &memory), TAG,
                        "Web memory route registration failed");
    ESP_RETURN_ON_ERROR(websocket_service_register(server, state), TAG,
                        "WebSocket service registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &files), TAG,
                        "Static route registration failed");
    if (state->lock && xSemaphoreTake(state->lock, pdMS_TO_TICKS(100))) {
        state->web_ready = true;
        xSemaphoreGive(state->lock);
    }
    ESP_LOGI(TAG, "Native %s server started", native_web_transport_secure() ? "HTTPS" : "HTTP");
    return ESP_OK;
release_transport:
    if (native_web_transport_release() != ESP_OK) return result;
unprepared:
    atomic_store(&s_started, false);
    return result;
}
