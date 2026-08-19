#include "web_service.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "audio_service.h"
#include "esp_check.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "network_service.h"
#include "websocket_service.h"

static const char *const TAG = "web";
static native_state_t *s_state;

static const char INDEX_HTML[] =
    "<!DOCTYPE html><html><head><meta charset=\"UTF-8\">"
    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,"
    "maximum-scale=1,user-scalable=no\">"
    "<meta name=\"theme-color\" content=\"#e3d25f\">"
    "<script src=\"/variables.js\"></script>"
    "<link rel=\"stylesheet\" href=\"/theme.css\">"
    "<link rel=\"stylesheet\" href=\"/style.css\">"
    "<script src=\"/script.js\"></script>"
    "<script src=\"/dragpl.js\"></script></head>"
    "<body><div id=\"content\" class=\"hidden progmem\"></div>"
    "<div id=\"progress\"><span id=\"loader\"></span></div>"
    "<div id=\"heap\"></div></body></html>";

static void reboot_task(void *argument) {
    (void)argument;
    vTaskDelay(pdMS_TO_TICKS(750));
    esp_restart();
}

static esp_err_t status_handler(httpd_req_t *request) {
    native_state_t state;
    native_state_snapshot(s_state, &state);
    const char *mode = "starting";
    if (state.network_mode == NATIVE_NETWORK_CLIENT) mode = "client";
    if (state.network_mode == NATIVE_NETWORK_ACCESS_POINT) mode = "ap";
    if (state.network_mode == NATIVE_NETWORK_ERROR) mode = "error";
    char body[384];
    snprintf(body, sizeof(body),
             "{\"firmware\":\"esp32c3-oled-native\",\"arduino\":false,"
             "\"network\":\"%s\",\"rssi\":%d,\"audio\":%s,\"station\":\"%s\","
             "\"format\":\"%s\"}",
             mode, state.wifi_rssi,
             state.audio_running ? "true" : "false", state.station,
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

static native_codec_t parse_codec(httpd_req_t *request) {
    char query[80];
    char value[16];
    if (httpd_req_get_url_query_str(request, query, sizeof(query)) == ESP_OK &&
        httpd_query_key_value(query, "codec", value, sizeof(value)) == ESP_OK) {
        if (strcasecmp(value, "mp3") == 0) return NATIVE_CODEC_MP3;
        if (strcasecmp(value, "aac") == 0) return NATIVE_CODEC_AAC;
        if (strcasecmp(value, "flac") == 0) return NATIVE_CODEC_FLAC;
        if (strcasecmp(value, "ogg") == 0 ||
            strcasecmp(value, "opus") == 0 ||
            strcasecmp(value, "vorbis") == 0) return NATIVE_CODEC_OGG;
    }
    return NATIVE_CODEC_AUTO;
}

static esp_err_t play_handler(httpd_req_t *request) {
    if (request->content_len <= 0 || request->content_len >= 512) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Body must contain a stream URL");
    }
    char url[512];
    size_t total = 0;
    while (total < (size_t)request->content_len) {
        int received = httpd_req_recv(request, url + total,
                                      request->content_len - total);
        if (received <= 0) return ESP_FAIL;
        total += received;
    }
    url[total] = '\0';
    esp_err_t result = audio_service_play(url, parse_codec(request));
    if (result != ESP_OK) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Invalid stream URL");
    }
    httpd_resp_set_type(request, "application/json");
    return httpd_resp_sendstr(request, "{\"playing\":true}");
}

static esp_err_t stop_handler(httpd_req_t *request) {
    audio_service_stop();
    httpd_resp_set_type(request, "application/json");
    return httpd_resp_sendstr(request, "{\"playing\":false}");
}

static const uint8_t *find_bytes(const uint8_t *start, const uint8_t *end,
                                 const char *needle, size_t needle_size) {
    if (needle_size == 0 || (size_t)(end - start) < needle_size) return NULL;
    for (const uint8_t *cursor = start;
         cursor + needle_size <= end; ++cursor) {
        if (memcmp(cursor, needle, needle_size) == 0) return cursor;
    }
    return NULL;
}

static esp_err_t save_playlist(const uint8_t *data, size_t size) {
    const char *temporary = "/spiffs/data/playlist.csv.tmp";
    const char *destination = "/spiffs/data/playlist.csv";
    FILE *file = fopen(temporary, "wb");
    ESP_RETURN_ON_FALSE(file, ESP_FAIL, TAG, "open playlist upload");
    bool complete = fwrite(data, 1, size, file) == size && fflush(file) == 0;
    bool closed = fclose(file) == 0;
    if (!complete || !closed) {
        remove(temporary);
        return ESP_FAIL;
    }
    remove(destination);
    if (rename(temporary, destination) != 0) {
        remove(temporary);
        return ESP_FAIL;
    }
    return ESP_OK;
}

static esp_err_t save_wifi(const uint8_t *data, size_t size) {
    char line[160];
    if (size >= sizeof(line)) return ESP_ERR_INVALID_SIZE;
    memcpy(line, data, size);
    line[size] = '\0';
    line[strcspn(line, "\r\n")] = '\0';
    char *tab = strchr(line, '\t');
    if (!tab) return ESP_ERR_INVALID_ARG;
    *tab++ = '\0';
    return network_service_save_credentials(line, tab);
}

static esp_err_t upload_handler(httpd_req_t *request) {
    if (request->content_len <= 0 || request->content_len > 96 * 1024) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Upload is empty or too large");
    }
    size_t size = (size_t)request->content_len;
    uint8_t *body = malloc(size + 1);
    if (!body) {
        return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR,
                                   "Not enough memory for upload");
    }
    size_t received_total = 0;
    while (received_total < size) {
        int received = httpd_req_recv(request, (char *)body + received_total,
                                      size - received_total);
        if (received <= 0) {
            free(body);
            return ESP_FAIL;
        }
        received_total += received;
    }
    body[size] = '\0';

    bool is_wifi = strstr((char *)body, "name=\"wifile\"") != NULL;
    bool is_playlist = strstr((char *)body, "name=\"plfile\"") != NULL;
    uint8_t *headers_end = (uint8_t *)strstr((char *)body, "\r\n\r\n");
    if ((!is_wifi && !is_playlist) || !headers_end) {
        free(body);
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Unsupported multipart upload");
    }
    uint8_t *payload = headers_end + 4;
    const uint8_t *payload_end = find_bytes(payload, body + size, "\r\n--", 4);
    if (!payload_end || payload_end <= payload) {
        free(body);
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Malformed multipart upload");
    }

    esp_err_t result = is_wifi
                           ? save_wifi(payload, payload_end - payload)
                           : save_playlist(payload, payload_end - payload);
    free(body);
    if (result != ESP_OK) {
        return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR,
                                   "Cannot store uploaded file");
    }
    httpd_resp_set_type(request, "text/plain");
    ESP_RETURN_ON_ERROR(httpd_resp_sendstr(request, "OK"), TAG,
                        "send upload response");
    if (is_wifi) {
        xTaskCreate(reboot_task, "wifi_reboot", 2048, NULL, 3, NULL);
    }
    return ESP_OK;
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
    if (strcmp(uri, "/") == 0 || strcmp(uri, "/index.html") == 0 ||
        strcmp(uri, "/settings.html") == 0 ||
        strcmp(uri, "/update.html") == 0 || strcmp(uri, "/ir.html") == 0) {
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_send(request, INDEX_HTML, HTTPD_RESP_USE_STRLEN);
    }
    if (strcmp(uri, "/variables.js") == 0) {
        native_state_t state;
        native_state_snapshot(s_state, &state);
        char variables[256];
        snprintf(variables, sizeof(variables),
                 "var yoVersion='idf-%s';\n"
                 "var webUiRevision='native01';\n"
                 "var formAction='';\n"
                 "var playMode='%s';\n"
                 "var equalizerEnabled=false;\n",
                 esp_get_idf_version(),
                 state.network_mode == NATIVE_NETWORK_CLIENT ? "player"
                                                              : "ap");
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_sendstr(request, variables);
    }

    char path[224];
    if (strncmp(uri, "/data/", 6) == 0) {
        snprintf(path, sizeof(path), "/spiffs%s", uri);
    } else {
        snprintf(path, sizeof(path), "/spiffs/www%s", uri);
    }
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
    httpd_uri_t upload = {
        .uri = "/upload",
        .method = HTTP_POST,
        .handler = upload_handler,
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
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &play), TAG,
                        "Play route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &stop), TAG,
                        "Stop route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &upload), TAG,
                        "Upload route registration failed");
    ESP_RETURN_ON_ERROR(websocket_service_register(server, state), TAG,
                        "WebSocket service registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &files), TAG,
                        "Static route registration failed");
    if (state->lock && xSemaphoreTake(state->lock, pdMS_TO_TICKS(100))) {
        state->web_ready = true;
        xSemaphoreGive(state->lock);
    }
    ESP_LOGI(TAG, "Native HTTP server started");
    return ESP_OK;
}
