#include "web_service.h"

#include <stdio.h>
#include <string.h>

#include "esp_check.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "network_service.h"

static const char *const TAG = "web";
static native_state_t *s_state;

static esp_err_t status_handler(httpd_req_t *request) {
    native_state_t state;
    native_state_snapshot(s_state, &state);
    const char *mode = "starting";
    if (state.network_mode == NATIVE_NETWORK_CLIENT) mode = "client";
    if (state.network_mode == NATIVE_NETWORK_ACCESS_POINT) mode = "ap";
    if (state.network_mode == NATIVE_NETWORK_ERROR) mode = "error";
    char body[384];
    snprintf(body, sizeof(body),
             "{\"firmware\":\"esp-idf-native\",\"arduino\":false,"
             "\"network\":\"%s\",\"audio\":%s,\"station\":\"%s\","
             "\"format\":\"%s\"}",
             mode, state.audio_running ? "true" : "false", state.station,
             state.stream_format);
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}

static esp_err_t reconnect_handler(httpd_req_t *request) {
    esp_err_t result = network_service_retry_client();
    if (result != ESP_OK) {
        httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR,
                            "No saved client configuration");
        return result;
    }
    httpd_resp_set_type(request, "application/json");
    return httpd_resp_sendstr(request, "{\"reconnecting\":true}");
}

static const char *content_type(const char *path) {
    if (strstr(path, ".html")) return "text/html; charset=utf-8";
    if (strstr(path, ".css")) return "text/css; charset=utf-8";
    if (strstr(path, ".js")) return "application/javascript; charset=utf-8";
    if (strstr(path, ".svg")) return "image/svg+xml";
    if (strstr(path, ".png")) return "image/png";
    if (strstr(path, ".ico")) return "image/x-icon";
    return "application/octet-stream";
}

static esp_err_t static_handler(httpd_req_t *request) {
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
    if (strcmp(uri, "/") == 0) strcpy(uri, "/player.html");

    char path[224];
    snprintf(path, sizeof(path), "/spiffs/www%s", uri);
    FILE *file = fopen(path, "rb");
    bool gzip = false;
    if (!file) {
        strlcat(path, ".gz", sizeof(path));
        file = fopen(path, "rb");
        gzip = file != NULL;
    }
    if (!file) {
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND,
                                   "WebUI file not found");
    }
    httpd_resp_set_type(request, content_type(uri));
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    if (gzip) httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
    char chunk[2048];
    size_t count;
    while ((count = fread(chunk, 1, sizeof(chunk), file)) > 0) {
        if (httpd_resp_send_chunk(request, chunk, count) != ESP_OK) {
            fclose(file);
            httpd_resp_sendstr_chunk(request, NULL);
            return ESP_FAIL;
        }
    }
    fclose(file);
    return httpd_resp_send_chunk(request, NULL, 0);
}

esp_err_t web_service_start(native_state_t *state) {
    s_state = state;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 6144;
    config.max_open_sockets = 4;
    config.lru_purge_enable = true;
    config.uri_match_fn = httpd_uri_match_wildcard;
    httpd_handle_t server = NULL;
    ESP_RETURN_ON_ERROR(httpd_start(&server, &config), TAG,
                        "HTTP server start failed");
    httpd_uri_t status = {
        .uri = "/api/native/status",
        .method = HTTP_GET,
        .handler = status_handler,
    };
    httpd_uri_t reconnect = {
        .uri = "/api/native/reconnect",
        .method = HTTP_POST,
        .handler = reconnect_handler,
    };
    httpd_uri_t files = {
        .uri = "/*",
        .method = HTTP_GET,
        .handler = static_handler,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &status), TAG,
                        "Status route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &reconnect), TAG,
                        "Reconnect route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &files), TAG,
                        "Static route registration failed");
    if (state->lock && xSemaphoreTake(state->lock, pdMS_TO_TICKS(100))) {
        state->web_ready = true;
        xSemaphoreGive(state->lock);
    }
    ESP_LOGI(TAG, "Native HTTP server started");
    return ESP_OK;
}
