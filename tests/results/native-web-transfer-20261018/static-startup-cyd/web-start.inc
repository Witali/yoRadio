static esp_err_t capabilities_handler(httpd_req_t *request) {
    char body[896];
    json_buffer_t output;
    json_buffer_init(&output, body, sizeof(body));
    json_buffer_raw(&output, "{\"schema\":1,\"firmware\":\"esp32-cyd2usb-native\",\"audio_output\":");
    json_buffer_string(&output, native_audio_output_name());
    json_buffer_raw(&output, ",\"websocket\":true,\"websocket_clients\":2,\"radio\":true,\"smartstart\":true,\"normalization\":true,\"wifi_reconnect\":true,\"playlist_upload\":true,\"asset_upload\":true,\"wifi_upload\":true,\"upload_max_bytes\":98304,\"upload_max_files\":16,\"upload_name_max_bytes\":22,\"wifi_file_max_bytes\":799,\"wifi_body_max_bytes\":4096,\"wifi_ssid_max_bytes\":31,\"wifi_password_max_bytes\":63,\"wifi_profiles\":false,\"ota\":false,\"equalizer\":false,\"sd\":false,\"display_controls\":false}");
    if (output.failed) return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Capabilities exhausted");
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}
static atomic_bool s_started;
esp_err_t web_service_start(native_state_t *state) {
    if (!state || !state->lock) return ESP_ERR_INVALID_ARG;
    bool expected = false;
    if (!atomic_compare_exchange_strong(&s_started, &expected, true)) return ESP_ERR_INVALID_STATE;
    // Locks and the reboot task must exist before routes can commit files.
    // Permanent storage mutexes are shared with the network startup/retry.
    esp_err_t result = network_service_storage_init();
    if (result != ESP_OK) {
        atomic_store(&s_started, false);
        return result;
    }
    result = web_reboot_start();
    if (result != ESP_OK) {
        atomic_store(&s_started, false);
        return result;
    }
    result = web_static_start();
    if (result != ESP_OK) {
        if (web_reboot_abort() != ESP_OK) return result;
        atomic_store(&s_started, false);
        return result;
    }
    s_state = state;
    esp_fill_random(&s_health_boot_id,sizeof(s_health_boot_id));
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 6144;
    // LWIP has ten descriptors: HTTPD uses three internal sockets, five
    // clients leave two for the stream and network activity. WS admits two.
    config.max_open_sockets = 5;
    config.send_wait_timeout = CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS;
    config.max_uri_handlers = 16;
    config.lru_purge_enable = true;
    config.uri_match_fn = httpd_uri_match_wildcard;
    httpd_handle_t server = NULL;
    result = native_web_transport_prepare(&config);
    if (result != ESP_OK) goto failed;
    result = httpd_start(&server, &config);
    if (result != ESP_OK) goto failed;
    httpd_uri_t status = {
        .uri = "/api/native/status",
        .method = HTTP_GET,
        .handler = status_handler,
    };
    httpd_uri_t health = {
        .uri = "/api/native/health", .method = HTTP_GET, .handler = health_handler,
    };
    httpd_uri_t reconnect = {
        .uri = "/api/native/reconnect",
        .method = HTTP_POST,
        .handler = reconnect_handler,
    };
    httpd_uri_t radio_get = {.uri="/api/native/radio",.method=HTTP_GET,.handler=radio_handler};
    httpd_uri_t radio_post = {.uri="/api/native/radio",.method=HTTP_POST,.handler=radio_handler};
    httpd_uri_t play = {
        .uri = "/api/native/play*",
        .method = HTTP_POST,
        .handler = play_handler,
    };
    httpd_uri_t stop = {
        .uri = "/api/native/stop",
        .method = HTTP_POST,
        .handler = stop_handler,
    };
    httpd_uri_t settings_get = {
        .uri = "/api/native/settings",
        .method = HTTP_GET,
        .handler = settings_handler,
    };
    httpd_uri_t settings_post = {
        .uri = "/api/native/settings*",
        .method = HTTP_POST,
        .handler = settings_handler,
    };
    httpd_uri_t capabilities = {.uri="/api/native/capabilities", .method=HTTP_GET, .handler=capabilities_handler};
    httpd_uri_t upload = {.uri="/upload", .method=HTTP_POST, .handler=web_upload_handler};
    httpd_uri_t board = {.uri="/webboard", .method=HTTP_POST, .handler=web_board_upload_handler};
    httpd_uri_t wifi = {.uri="/", .method=HTTP_POST, .handler=web_wifi_upload_handler};
    httpd_uri_t files = {
        .uri = "/*",
        .method = HTTP_GET,
        .handler = web_static_handler,
    };
    const httpd_uri_t *routes[] = {&status, &health, &radio_get, &radio_post,
        &reconnect, &play, &stop, &settings_get, &settings_post, &capabilities,
        &upload, &board, &wifi};
    for (unsigned i = 0; i < sizeof(routes) / sizeof(routes[0]); ++i) {
        result = httpd_register_uri_handler(server, routes[i]);
        if (result != ESP_OK) goto failed;
    }
    result = websocket_service_register(server, state);
    if (result != ESP_OK) goto failed;
    result = httpd_register_uri_handler(server, &files);
    if (result != ESP_OK) goto failed;
    result = websocket_service_start();
    if (result != ESP_OK) goto failed;
    web_upload_activate();
    web_static_activate();
    if (state->lock && xSemaphoreTake(state->lock, pdMS_TO_TICKS(100))) {
        state->web_ready = true;
        xSemaphoreGive(state->lock);
    }
    ESP_LOGI(TAG, "Native %s server started", native_web_transport_secure() ? "HTTPS" : "HTTP");
    return ESP_OK;
failed:
    web_upload_deactivate();
    // Keep the server/session workspace alive if a producer has not exited.
    // All ordinary startup failures happen before its task is created.
    if (websocket_service_stop() != ESP_OK) {
        ESP_LOGE(TAG, "WebSocket producer did not stop; retaining server resources");
        return result;
    }
    if (server) {
        if (httpd_stop(server) != ESP_OK) {
            ESP_LOGE(TAG, "HTTP server did not stop; retaining server resources");
            return result;
        }
        websocket_service_server_stopped(server);
    }
    if (native_web_transport_release() != ESP_OK) return result;
    web_static_abort();
    if (web_reboot_abort() != ESP_OK) return result;
    atomic_store(&s_started, false);
    return result;
}
