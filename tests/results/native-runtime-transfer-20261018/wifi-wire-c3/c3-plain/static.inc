static void *s_static_request_queue=(void *)1;
static FILE *open_nonempty_file(const char *path) {return web_upload_open_file(path);}
const uint8_t embedded_script_stub_start[1] asm("_binary_native_script_js_gz_start")={0};
const uint8_t embedded_script_stub_end[1] asm("_binary_native_script_js_gz_end")={0};
static const char *content_type(const char *path) {
    if (strstr(path, ".html")) return "text/html; charset=utf-8";
    if (strstr(path, ".css")) return "text/css; charset=utf-8";
    if (strstr(path, ".js")) return "application/javascript; charset=utf-8";
    if (strstr(path, ".svg")) return "image/svg+xml";
    if (strstr(path, ".png")) return "image/png";
    if (strstr(path, ".ico")) return "image/x-icon";
    return "application/octet-stream";
}
static esp_err_t finish_static_response(httpd_req_t *request,
                                        esp_err_t result) {
    // The async request still owns its session. A queued session close may run
    // before async_handler_complete and recycle that slot underneath the worker.
    // Shutdown wakes HTTPD; it reaps the socket after completion releases it.
    (void)shutdown(httpd_req_to_sockfd(request), SHUT_RDWR);
    return result;
}
static bool embedded_script_size(const uint8_t *start, const uint8_t *end, ssize_t *length) {
    uintptr_t first = (uintptr_t)start, last = (uintptr_t)end;
    if (last < first || last - first > INT_MAX) return false;
    *length = (ssize_t)(last - first);
    return true;
}
static esp_err_t send_static_file(httpd_req_t *request, FILE *file) {
    char chunk[CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES];
    bool failed = false;
    for (;;) {
        size_t count = fread(chunk, 1, sizeof(chunk), file);
        if (count && httpd_resp_send_chunk(request, chunk, (ssize_t)count) != ESP_OK) {
            failed = true;
            break;
        }
        // A positive short read can already set EOF or a read error. Do not
        // issue another read while the stream position may be indeterminate.
        if (ferror(file)) { failed = true; break; }
        if (feof(file)) break;
        if (count < sizeof(chunk)) { failed = true; break; }
    }
    if (fclose(file) != 0) failed = true;
    if (failed) {
        // The request still owns its fd here; avoid a successful zero chunk or
        // a delayed fd-only close that could affect a later reused session.
        (void)shutdown(httpd_req_to_sockfd(request), SHUT_RDWR);
        return ESP_FAIL;
    }
    return finish_static_response(request, httpd_resp_send_chunk(request, NULL, 0));
}
static esp_err_t serve_static_request(httpd_req_t *request) {
    if (!native_wifi_public_static_uri(request->uri, request->method == HTTP_GET))
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND, "Public file not found");
    char uri[160];
    const char *query = strchr(request->uri, '?');
    size_t uri_len = query ? (size_t)(query - request->uri)
                           : strlen(request->uri);
    if (uri_len >= sizeof(uri) || strstr(request->uri, "..")) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Invalid path");
    }
    memcpy(uri, request->uri, uri_len);
    uri[uri_len] = '\0';
    if (strcmp(uri, "/script.js") == 0 || strcmp(uri, "/script.js.gz") == 0) {
        extern const uint8_t script_start[] asm("_binary_native_script_js_gz_start");
        extern const uint8_t script_end[] asm("_binary_native_script_js_gz_end");
        ssize_t script_bytes;
        if (!embedded_script_size(script_start, script_end, &script_bytes))
            return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Invalid embedded script span");
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
        httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
        httpd_resp_set_hdr(request, "Connection", "close");
        return finish_static_response(request, httpd_resp_send(request,
            (const char *)script_start, script_bytes));
    }
    if (strcmp(uri, "/") == 0 || strcmp(uri, "/index.html") == 0 ||
        strcmp(uri, "/settings.html") == 0 ||
        strcmp(uri, "/update.html") == 0 || strcmp(uri, "/ir.html") == 0) {
        if (strcmp(uri, "/") == 0 && !web_ui_available()) {
            return send_recovery_page(request);
        }
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_hdr(request, "Connection", "close");
        return finish_static_response(
            request, httpd_resp_sendstr(request, yoradio_index_html()));
    }
    if (strcmp(uri, "/variables.js") == 0) {
        native_state_t state;
        native_state_snapshot(s_state, &state);
        char variables[512];
        snprintf(variables, sizeof(variables),
                 "var yoVersion='idf-%s';\n"
                 "var webUiRevision='native06-wifi';\n"
                 "var formAction='%s';\n"
                 "var playMode='%s';\n"
                 "var equalizerEnabled=false;\n"
                 "var nativeFirmwareOnly=true;\n"
                 "var nativeFirmwareName='ESP32-C3 OLED native';\n"
                 "var nativeFirmwareInfo='/api/native/ota';\n"
                 "var nativeWiFiApi='/api/native/wifi';\n"
                 "var nativeWiFiMaxProfiles=5;\n"
                 "var nativeWiFiPrivateExport=false;\n",
                 esp_get_idf_version(),
                 state.network_mode == NATIVE_NETWORK_CLIENT &&
                         web_ui_available()
                     ? "webboard"
                     : "",
                 state.network_mode == NATIVE_NETWORK_CLIENT ? "player"
                                                              : "ap");
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_hdr(request, "Connection", "close");
        return finish_static_response(request,
                                      httpd_resp_sendstr(request, variables));
    }

    char path[224];
    bool gzip = false;
    if (strncmp(uri, "/data/", 6) == 0) {
        snprintf(path, sizeof(path), "/spiffs%s", uri);
    } else {
        if (strlen(uri) > 3 && strcmp(uri + strlen(uri) - 3, ".gz") == 0) {
            snprintf(path, sizeof(path), "/spiffs/www%s", uri);
        } else {
            snprintf(path, sizeof(path), "/spiffs/www%s.gz", uri);
        }
        gzip = true;
    }
    FILE *file = open_nonempty_file(path);
    if (!file) {
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND,
                                   "WebUI file not found");
    }
    httpd_resp_set_type(request, content_type(uri));
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    httpd_resp_set_hdr(request, "Connection", "close");
    if (gzip) httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
    return send_static_file(request, file);
}
static esp_err_t static_handler(httpd_req_t *request) {
    if (!native_wifi_public_static_uri(request->uri, request->method == HTTP_GET))
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND, "Public file not found");
    httpd_req_t *async_request = NULL;
    esp_err_t result =
        httpd_req_async_handler_begin(request, &async_request);
    if (result != ESP_OK) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        httpd_resp_set_hdr(request, "Connection", "close");
        return httpd_resp_sendstr(request, "Static worker unavailable");
    }
    if (xQueueSend(s_static_request_queue, &async_request, 0) != pdTRUE) {
        httpd_resp_set_status(async_request, "503 Service Unavailable");
        httpd_resp_set_hdr(async_request, "Connection", "close");
        httpd_resp_sendstr(async_request, "Static worker queue full");
        httpd_req_async_handler_complete(async_request);
    }
    return ESP_OK;
}
static esp_err_t with_awake_request(httpd_req_t *request,
                                     esp_err_t (*handler)(httpd_req_t *)) {
    if (!deep_sleep_clock_begin_activity()) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Clock is entering sleep");
    }
    display_settings_note_activity();
    esp_err_t result = handler(request);
    display_settings_note_activity();
    deep_sleep_clock_end_activity();
    return result;
}
static esp_err_t sleep_guarded_upload_handler(httpd_req_t *request) {
    return with_awake_request(request, web_upload_handler);
}
static esp_err_t sleep_guarded_webboard_upload_handler(httpd_req_t *request) {
    return with_awake_request(request, web_board_upload_handler);
}
static esp_err_t sleep_guarded_recovery_wifi_handler(httpd_req_t *request) {
    return with_awake_request(request, web_wifi_upload_handler);
}

static esp_err_t serve_static_boundary(httpd_req_t *r) {return serve_static_request(r);}
static esp_err_t static_admission_boundary(httpd_req_t *r) {return static_handler(r);}
static void static_activate_boundary(void) {}
