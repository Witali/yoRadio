#include "web_upload.h"

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "file_transaction.h"
#include "network_service.h"
#include "radio_control.h"
#include "web_file_form.h"
#include "websocket_service.h"

#define WEB_UPLOAD_MAX (96U * 1024U)
#define WEB_UPLOAD_RECEIVE_BYTES 256U
#define WEB_UPLOAD_WRITE_BYTES 2048U
#define WEB_UPLOAD_TIMEOUT_US 120000000LL
#define WEB_UPLOAD_IDLE_US 10000000LL

static SemaphoreHandle_t s_storage_lock;

esp_err_t web_upload_storage_init(void) {
    if (!s_storage_lock) s_storage_lock = xSemaphoreCreateMutex();
    return s_storage_lock ? ESP_OK : ESP_ERR_NO_MEM;
}

static bool backup_name(const char *live, char *backup, size_t capacity) {
    if (!live || !*live) return false;
    int length = snprintf(backup, capacity, "%s.bak", live);
    return length > 0 && (size_t)length < capacity;
}

FILE *web_upload_open_file(const char *path) {
    char backup[256];
    if (!s_storage_lock || !backup_name(path, backup, sizeof(backup)) ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return NULL;
    FILE *file = native_file_recover(path, backup) ? fopen(path, "rb") : NULL;
    xSemaphoreGive(s_storage_lock);
    return file;
}

bool web_upload_publish_file(const char *temporary, const char *live) {
    char backup[256];
    if (!s_storage_lock || !backup_name(live, backup, sizeof(backup)) ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return false;
    bool replaced = native_file_replace(temporary, live, backup);
    xSemaphoreGive(s_storage_lock);
    return replaced;
}

// All three routes run synchronously in the same HTTP server task. Its stack
// is reserved at startup. Staging uses flash, never request-sized heap memory.
typedef struct {
    int fd;
    size_t buffered;
    uint8_t *buffer;
} upload_sink_t;

static void temporary_path(unsigned slot, char *path, size_t capacity) {
    snprintf(path, capacity, "/spiffs/data/web-upload-%02u.tmp", slot);
}
static bool begin_file(unsigned slot, void *context) {
    upload_sink_t *sink = context;
    char path[64];
    temporary_path(slot, path, sizeof(path));
    if (!sink->buffer) sink->buffer = malloc(WEB_UPLOAD_WRITE_BYTES);
    if (!sink->buffer) return false; // No live file has been removed.
    sink->buffered = 0;
    sink->fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0666);
    return sink->fd >= 0;
}
static bool flush_buffer(upload_sink_t *sink) {
    size_t offset = 0;
    // POSIX write reaches SPIFFS directly. Do not add a hidden stdio buffer
    // which could allocate heap and split these coalesced 2 KiB writes again.
    while (offset < sink->buffered) {
        ssize_t count = write(sink->fd, sink->buffer + offset, sink->buffered - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return false;
        offset += (size_t)count;
    }
    sink->buffered = 0;
    return true;
}
static bool write_file(const uint8_t *data, size_t size, void *context) {
    upload_sink_t *sink = context;
    if (sink->fd < 0) return false;
    while (size) {
        size_t count = WEB_UPLOAD_WRITE_BYTES - sink->buffered;
        if (count > size) count = size;
        memcpy(sink->buffer + sink->buffered, data, count);
        sink->buffered += count; data += count; size -= count;
        if (sink->buffered == WEB_UPLOAD_WRITE_BYTES) {
            if (!flush_buffer(sink)) return false;
        }
    }
    return true;
}
static bool end_file(void *context) {
    upload_sink_t *sink = context;
    if (sink->fd < 0) return false;
    bool ok = flush_buffer(sink);
    if (fsync(sink->fd) != 0) ok = false;
    if (close(sink->fd) != 0) ok = false;
    sink->fd = -1;
    return ok;
}

static bool receive_form(httpd_req_t *request, web_file_form_t *form) {
    char type[192];
    size_t limit = form->mode == WEB_FORM_CREDENTIALS ? 4096U : WEB_UPLOAD_MAX;
    if (!request->content_len || request->content_len > limit ||
        httpd_req_get_hdr_value_str(request, "Content-Type", type, sizeof(type)) != ESP_OK ||
        strncmp(type, "multipart/form-data;", 20)) return false;
    char *boundary = strstr(type + 20, "boundary=");
    if (!boundary) return false;
    boundary += 9;
    bool quoted = *boundary == '"';
    if (quoted) ++boundary;
    char *end = quoted ? strchr(boundary, '"') : strpbrk(boundary, "; \t");
    if (quoted && !end) return false;
    if (end) *end = 0;
    web_multipart_t parser;
    if (!mp_init(&parser, boundary, web_file_form_part, form)) return false;
    uint8_t chunk[WEB_UPLOAD_RECEIVE_BYTES];
    size_t remaining = request->content_len;
    int64_t started = esp_timer_get_time(), last_data = started;
    while (remaining) {
        int64_t now = esp_timer_get_time();
        if (now - started >= WEB_UPLOAD_TIMEOUT_US || now - last_data >= WEB_UPLOAD_IDLE_US)
            return false;
        size_t count = remaining < sizeof(chunk) ? remaining : sizeof(chunk);
        int received = httpd_req_recv(request, (char *)chunk, count);
        if (received == HTTPD_SOCK_ERR_TIMEOUT) { vTaskDelay(1); continue; }
        if (received <= 0) return false;
        now = esp_timer_get_time();
        if (now - started >= WEB_UPLOAD_TIMEOUT_US || now - last_data >= WEB_UPLOAD_IDLE_US)
            return false;
        last_data = now;
        if (!mp_feed(&parser, chunk, (size_t)received)) return false;
        remaining -= (size_t)received;
        vTaskDelay(1);
    }
    return mp_complete(&parser);
}

static bool publish_file(unsigned slot, const char *name, bool playlist) {
    char temporary[64], destination[128];
    temporary_path(slot, temporary, sizeof(temporary));
    int length = snprintf(destination, sizeof(destination), "/spiffs/%s/%s",
                          playlist ? "data" : "www", name);
    if (length <= 0 || (size_t)length >= sizeof(destination)) return false;
    if (!playlist && (length <= 3 || strcmp(destination + length - 3, ".gz") != 0)) return false;
    // Retain the previous file until the validated replacement has its live
    // name. Boot/read recovery can restore a retained backup after interruption.
    if (!web_upload_publish_file(temporary, destination)) return false;
    if (!playlist) {
        destination[strlen(destination) - 3] = 0; // obsolete uncompressed copy
        remove(destination);
    }
    return true;
}

static esp_err_t handle_upload(httpd_req_t *request, web_form_mode_t mode) {
    upload_sink_t sink = {.fd = -1};
    web_file_form_t form = {
        .mode = mode, .sink = {begin_file, write_file, end_file, &sink},
    };
    bool ok = websocket_service_reboot_ready() && receive_form(request, &form);
    if (sink.fd >= 0) close(sink.fd);
    free(sink.buffer); // Rare file upload only; no permanent payload reserve.
    bool wifi_saved = false, playlist_saved = false;
    if (ok && mode == WEB_FORM_CREDENTIALS) {
        ok = form.ssid_seen && form.password_seen && form.ssid[0] &&
             network_service_save_credentials(form.ssid, form.password) == ESP_OK;
        wifi_saved = ok;
    } else if (ok) {
        ok = form.files || form.wifi_seen;
        if (ok && form.wifi_seen)
            ok = network_service_validate_credentials_file(
                (const uint8_t *)form.wifi, form.wifi_bytes) == ESP_OK;
        for (unsigned i = 0; ok && i < form.files; ++i) {
            ok = publish_file(i, form.names[i], form.playlist[i]);
            if (ok && form.playlist[i]) {
                playlist_saved = true;
                ok = radio_control_reindex_playlist() == ESP_OK;
            }
        }
        if (ok && form.wifi_seen) {
            ok = network_service_save_credentials_file(
                (const uint8_t *)form.wifi, form.wifi_bytes) == ESP_OK;
            wifi_saved = ok;
        }
    }
    // Includes the currently incomplete file, and stale files from an aborted
    // previous boot. No private credentials are logged or retained in RAM.
    for (unsigned i = 0; i < WEB_FILE_FORM_MAX_FILES; ++i) {
        char path[64];
        temporary_path(i, path, sizeof(path));
        remove(path);
    }
    memset(form.wifi, 0, sizeof(form.wifi));
    memset(form.ssid, 0, sizeof(form.ssid));
    memset(form.password, 0, sizeof(form.password));
    if (playlist_saved) websocket_service_notify_playlist_changed();
    httpd_resp_set_type(request, "text/plain; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    httpd_resp_set_hdr(request, "Connection", "close");
    if (!ok) httpd_resp_set_status(request, "400 Bad Request");
    else if (mode != WEB_FORM_UPLOAD) {
        httpd_resp_set_status(request, "303 See Other");
        httpd_resp_set_hdr(request, "Location", "/");
    }
    esp_err_t result = httpd_resp_sendstr(request, ok ? "OK" :
        "Upload failed: invalid, incomplete, oversized file or storage full");
    if (wifi_saved) websocket_service_request_reboot(750);
    // Close rejected requests: do not drain an arbitrarily large unread body.
    return ok ? result : ESP_FAIL;
}

esp_err_t web_upload_handler(httpd_req_t *request) {
    return handle_upload(request, WEB_FORM_UPLOAD);
}
esp_err_t web_board_upload_handler(httpd_req_t *request) {
    return handle_upload(request, WEB_FORM_BOARD);
}
esp_err_t web_wifi_upload_handler(httpd_req_t *request) {
    return handle_upload(request, WEB_FORM_CREDENTIALS);
}
