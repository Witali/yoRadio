#include "web_service.h"

#include <ctype.h>
#include <errno.h>
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
#include "web_pages_bridge.h"
#include "websocket_service.h"

#define WEBBOARD_UPLOAD_MAX (96 * 1024)
#define MULTIPART_HEADER_MAX 768

static const char *const TAG = "web";
static native_state_t *s_state;

static void reboot_task(void *argument) {
    (void)argument;
    vTaskDelay(pdMS_TO_TICKS(750));
    esp_restart();
}

static FILE *open_nonempty_file(const char *path) {
    FILE *file = fopen(path, "rb");
    if (!file) return NULL;
    // SPIFFS does not guarantee useful seek/tell results for every damaged
    // directory entry.  Prove that at least one byte can actually be read so
    // a zero-byte raw file cannot shadow its valid .gz counterpart.
    if (fgetc(file) == EOF || fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return NULL;
    }
    return file;
}

static bool web_asset_available(const char *name) {
    char path[224];
    snprintf(path, sizeof(path), "/spiffs/www/%s.gz", name);
    FILE *file = open_nonempty_file(path);
    if (!file) return false;
    fclose(file);
    return true;
}

static bool web_ui_available(void) {
    static const char *const required[] = {
        "theme.css",
        "style.css",
        "script.js",
        "dragpl.js",
        "player.html",
        "options.html",
        "logo.svg",
    };
    for (size_t index = 0; index < sizeof(required) / sizeof(required[0]);
         ++index) {
        if (!web_asset_available(required[index])) return false;
    }
    return true;
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

typedef esp_err_t (*multipart_part_handler_t)(
    const char *field, const char *filename, const uint8_t *data, size_t size,
    void *context);

static bool multipart_parameter(const char *headers, const char *name,
                                char *value, size_t value_size) {
    char prefix[40];
    snprintf(prefix, sizeof(prefix), "%s=\"", name);
    const char *start = strstr(headers, prefix);
    if (!start) return false;
    start += strlen(prefix);
    const char *end = strchr(start, '"');
    if (!end || end == start || (size_t)(end - start) >= value_size) {
        return false;
    }
    memcpy(value, start, (size_t)(end - start));
    value[end - start] = '\0';
    return true;
}

static esp_err_t receive_multipart(httpd_req_t *request, size_t maximum_size,
                                   multipart_part_handler_t handler,
                                   void *context) {
    if (request->content_len <= 0 ||
        (size_t)request->content_len > maximum_size) {
        return ESP_ERR_INVALID_SIZE;
    }
    char content_type[192];
    if (httpd_req_get_hdr_value_str(request, "Content-Type", content_type,
                                    sizeof(content_type)) != ESP_OK) {
        return ESP_ERR_INVALID_ARG;
    }
    const char *boundary_value = strstr(content_type, "boundary=");
    if (!boundary_value) return ESP_ERR_INVALID_ARG;
    boundary_value += strlen("boundary=");
    if (*boundary_value == '"') ++boundary_value;
    size_t boundary_size = strcspn(boundary_value, "\";");
    if (boundary_size == 0 || boundary_size > 70) return ESP_ERR_INVALID_ARG;

    char boundary[76];
    memcpy(boundary, "--", 2);
    memcpy(boundary + 2, boundary_value, boundary_size);
    boundary[boundary_size + 2] = '\0';
    size_t marker_size = boundary_size + 2;
    char next_boundary[80];
    memcpy(next_boundary, "\r\n", 2);
    memcpy(next_boundary + 2, boundary, marker_size + 1);
    size_t next_marker_size = marker_size + 2;

    size_t body_size = (size_t)request->content_len;
    uint8_t *body = malloc(body_size + 1);
    if (!body) return ESP_ERR_NO_MEM;
    size_t total = 0;
    while (total < body_size) {
        int received = httpd_req_recv(request, (char *)body + total,
                                      body_size - total);
        if (received == HTTPD_SOCK_ERR_TIMEOUT) continue;
        if (received <= 0) {
            ESP_LOGE(TAG, "Multipart receive failed: %d after %u/%u bytes",
                     received, (unsigned)total, (unsigned)body_size);
            free(body);
            return ESP_FAIL;
        }
        total += (size_t)received;
    }
    body[body_size] = '\0';

    const uint8_t *body_end = body + body_size;
    const uint8_t *cursor = find_bytes(body, body_end, boundary, marker_size);
    esp_err_t result = cursor ? ESP_OK : ESP_ERR_INVALID_ARG;
    while (result == ESP_OK && cursor && cursor < body_end) {
        cursor += marker_size;
        if (cursor + 2 <= body_end && memcmp(cursor, "--", 2) == 0) break;
        if (cursor + 2 > body_end || memcmp(cursor, "\r\n", 2) != 0) {
            result = ESP_ERR_INVALID_ARG;
            break;
        }
        cursor += 2;
        const uint8_t *headers_end =
            find_bytes(cursor, body_end, "\r\n\r\n", 4);
        if (!headers_end || (size_t)(headers_end - cursor) >=
                                MULTIPART_HEADER_MAX) {
            result = ESP_ERR_INVALID_ARG;
            break;
        }
        char headers[MULTIPART_HEADER_MAX];
        size_t headers_size = (size_t)(headers_end - cursor);
        memcpy(headers, cursor, headers_size);
        headers[headers_size] = '\0';
        char field[32];
        char filename[96] = "";
        if (!multipart_parameter(headers, "name", field, sizeof(field))) {
            result = ESP_ERR_INVALID_ARG;
            break;
        }
        (void)multipart_parameter(headers, "filename", filename,
                                  sizeof(filename));
        const uint8_t *payload = headers_end + 4;
        const uint8_t *next = find_bytes(payload, body_end, next_boundary,
                                         next_marker_size);
        if (!next) {
            result = ESP_ERR_INVALID_ARG;
            break;
        }
        result = handler(field, filename, payload, (size_t)(next - payload),
                         context);
        cursor = next + 2;
    }
    free(body);
    return result;
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

static bool safe_upload_name(const char *filename, char *name,
                             size_t name_size) {
    const char *base = filename;
    for (const char *cursor = filename; *cursor; ++cursor) {
        if (*cursor == '/' || *cursor == '\\') base = cursor + 1;
    }
    size_t length = strlen(base);
    if (length == 0 || length >= name_size || strstr(base, "..")) return false;
    for (size_t index = 0; index < length; ++index) {
        unsigned char value = (unsigned char)base[index];
        if (!isalnum(value) && value != '.' && value != '_' && value != '-') {
            return false;
        }
    }
    memcpy(name, base, length + 1);
    return true;
}

static esp_err_t write_uploaded_file(const char *path, const uint8_t *data,
                                     size_t size) {
    if (!size) return ESP_ERR_INVALID_SIZE;
    FILE *file = fopen(path, "wb");
    if (!file) {
        ESP_LOGE(TAG, "Cannot create %s: errno %d", path, errno);
        return ESP_FAIL;
    }
    bool complete = fwrite(data, 1, size, file) == size && fflush(file) == 0;
    bool closed = fclose(file) == 0;
    if (!complete || !closed) {
        ESP_LOGE(TAG, "Cannot write %u bytes to %s: errno %d",
                 (unsigned)size, path, errno);
    }
    return complete && closed ? ESP_OK : ESP_FAIL;
}

static esp_err_t save_web_asset(const char *filename, const uint8_t *data,
                                size_t size) {
    char name[96];
    if (!safe_upload_name(filename, name, sizeof(name))) {
        return ESP_ERR_INVALID_ARG;
    }
    size_t name_length = strlen(name);
    if (name_length <= 3 || strcmp(name + name_length - 3, ".gz") != 0) {
        ESP_LOGW(TAG, "Rejecting uncompressed WebUI asset: %s", name);
        return ESP_ERR_NOT_SUPPORTED;
    }
    char path[224];
    snprintf(path, sizeof(path), "/spiffs/www/%s", name);
    char obsolete_raw[224];
    memcpy(obsolete_raw, path, strlen(path) - 3);
    obsolete_raw[strlen(path) - 3] = '\0';
    // Remove legacy raw copies. Static WebUI resources are stored only as
    // gzip files, just as they are transferred to the browser.
    remove(obsolete_raw);
    remove(path);
    return write_uploaded_file(path, data, size);
}

static void clear_web_assets_for_recovery(void) {
    static const char *const names[] = {
        "theme.css",       "style.css",       "script.js",
        "dragpl.js",       "player.html",     "options.html",
        "logo.svg",        "updform.html",    "ir.css",
        "ir.js",           "irrecord.html",
    };
    char path[224];
    for (size_t index = 0; index < sizeof(names) / sizeof(names[0]); ++index) {
        snprintf(path, sizeof(path), "/spiffs/www/%s", names[index]);
        remove(path);
        strlcat(path, ".gz", sizeof(path));
        remove(path);
    }
}

typedef struct {
    unsigned saved;
    bool wifi_saved;
    bool web_storage_prepared;
} webboard_upload_t;

static esp_err_t webboard_part(const char *field, const char *filename,
                               const uint8_t *data, size_t size,
                               void *context) {
    webboard_upload_t *upload = context;
    if (strcmp(field, "submit") == 0) return ESP_OK;
    if (!filename[0]) return ESP_ERR_INVALID_ARG;
    esp_err_t result = ESP_ERR_INVALID_ARG;
    if (strcmp(field, "www") == 0) {
        if (!upload->web_storage_prepared) {
            clear_web_assets_for_recovery();
            upload->web_storage_prepared = true;
        }
        result = save_web_asset(filename, data, size);
    } else if (strcmp(field, "data") == 0) {
        char name[96];
        if (!safe_upload_name(filename, name, sizeof(name))) {
            return ESP_ERR_INVALID_ARG;
        }
        if (strcmp(name, "playlist.csv") == 0) {
            result = save_playlist(data, size);
        } else if (strcmp(name, "wifi.csv") == 0) {
            result = save_wifi(data, size);
            upload->wifi_saved = result == ESP_OK;
        }
    }
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Import failed for field %s file %s (%u bytes): %s",
                 field, filename, (unsigned)size, esp_err_to_name(result));
    }
    if (result == ESP_OK) ++upload->saved;
    return result;
}

static esp_err_t send_recovery_page(httpd_req_t *request) {
    httpd_resp_set_type(request, "text/html; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, yoradio_emptyfs_html());
}

static esp_err_t webboard_page_handler(httpd_req_t *request) {
    return send_recovery_page(request);
}

static esp_err_t webboard_upload_handler(httpd_req_t *request) {
    webboard_upload_t upload = {0};
    esp_err_t result = receive_multipart(request, WEBBOARD_UPLOAD_MAX,
                                         webboard_part, &upload);
    if (result != ESP_OK || upload.saved == 0) {
        ESP_LOGW(TAG, "Web board upload failed: %s, saved %u file(s)",
                 esp_err_to_name(result), upload.saved);
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Cannot import selected WebUI files");
    }
    ESP_LOGI(TAG, "Web board imported %u file(s); UI is %s", upload.saved,
             web_ui_available() ? "complete" : "still incomplete");
    httpd_resp_set_status(request, "303 See Other");
    httpd_resp_set_hdr(request, "Location", "/");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    ESP_RETURN_ON_ERROR(httpd_resp_sendstr(request, "Files imported"), TAG,
                        "send WebUI import redirect");
    if (upload.wifi_saved) {
        xTaskCreate(reboot_task, "wifi_reboot", 2048, NULL, 3, NULL);
    }
    return ESP_OK;
}

static esp_err_t emergency_handler(httpd_req_t *request) {
    httpd_resp_set_type(request, "text/html; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, yoradio_emergency_form());
}

typedef struct {
    char ssid[33];
    char password[65];
    bool have_ssid;
    bool have_password;
} recovery_wifi_t;

static esp_err_t recovery_wifi_part(const char *field, const char *filename,
                                    const uint8_t *data, size_t size,
                                    void *context) {
    (void)filename;
    recovery_wifi_t *wifi = context;
    char *target = NULL;
    size_t capacity = 0;
    bool *present = NULL;
    if (strcmp(field, "ssid") == 0) {
        target = wifi->ssid;
        capacity = sizeof(wifi->ssid);
        present = &wifi->have_ssid;
    } else if (strcmp(field, "pass") == 0) {
        target = wifi->password;
        capacity = sizeof(wifi->password);
        present = &wifi->have_password;
    } else if (strcmp(field, "submit") == 0) {
        return ESP_OK;
    } else {
        return ESP_ERR_INVALID_ARG;
    }
    if (size >= capacity) return ESP_ERR_INVALID_SIZE;
    memcpy(target, data, size);
    target[size] = '\0';
    *present = true;
    return ESP_OK;
}

static esp_err_t recovery_wifi_handler(httpd_req_t *request) {
    recovery_wifi_t wifi = {0};
    esp_err_t result = receive_multipart(request, 4096, recovery_wifi_part,
                                         &wifi);
    if (result != ESP_OK || !wifi.have_ssid || !wifi.have_password ||
        network_service_save_credentials(wifi.ssid, wifi.password) != ESP_OK) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Cannot save Wi-Fi credentials");
    }
    httpd_resp_set_type(request, "text/html; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    ESP_RETURN_ON_ERROR(
        httpd_resp_sendstr(
            request,
            "<!doctype html><meta charset=utf-8><meta http-equiv=refresh "
            "content='5;url=/'><p>Wi-Fi saved. Rebooting...</p>"),
        TAG, "send Wi-Fi recovery response");
    xTaskCreate(reboot_task, "wifi_reboot", 2048, NULL, 3, NULL);
    return ESP_OK;
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
        if (strcmp(uri, "/") == 0 && !web_ui_available()) {
            return send_recovery_page(request);
        }
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_sendstr(request, yoradio_index_html());
    }
    if (strcmp(uri, "/variables.js") == 0) {
        native_state_t state;
        native_state_snapshot(s_state, &state);
        char variables[256];
        snprintf(variables, sizeof(variables),
                 "var yoVersion='idf-%s';\n"
                 "var webUiRevision='native01';\n"
                 "var formAction='%s';\n"
                 "var playMode='%s';\n"
                 "var equalizerEnabled=false;\n",
                 esp_get_idf_version(),
                 state.network_mode == NATIVE_NETWORK_CLIENT &&
                         web_ui_available()
                     ? "webboard"
                     : "",
                 state.network_mode == NATIVE_NETWORK_CLIENT ? "player"
                                                              : "ap");
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_sendstr(request, variables);
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
    // Browsers commonly fetch six assets in parallel. Keep those connections
    // plus the persistent WebSocket alive; with four sockets the LRU purge
    // closed /ws during page startup and the shared UI spinner never stopped.
    config.max_open_sockets = 7;
    config.max_uri_handlers = 14;
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
    httpd_uri_t webboard_page = {
        .uri = "/webboard",
        .method = HTTP_GET,
        .handler = webboard_page_handler,
    };
    httpd_uri_t webboard_upload = {
        .uri = "/webboard",
        .method = HTTP_POST,
        .handler = webboard_upload_handler,
    };
    httpd_uri_t emergency = {
        .uri = "/emergency",
        .method = HTTP_GET,
        .handler = emergency_handler,
    };
    httpd_uri_t recovery_wifi = {
        .uri = "/",
        .method = HTTP_POST,
        .handler = recovery_wifi_handler,
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
