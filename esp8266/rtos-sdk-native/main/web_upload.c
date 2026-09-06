#include "web_upload.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "esp_system.h"
#include "esp_ota_ops.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "file_replace.h"
#include "playlist_service.h"
#include "radio_control.h"
#include "native_state.h"
#include "web_multipart.h"
#include "web_service.h"

#define UPLOAD_MAX (96U * 1024U)
#define UPLOAD_TEMP "/spiffs/upload.tmp"
static uint8_t s_receive[512]; /* HTTP task only */
static volatile TickType_t s_reboot_at;
static const char *TAG = "upload";

void web_upload_request_reboot(void) {
    s_reboot_at = xTaskGetTickCount() + pdMS_TO_TICKS(2000);
}
void web_upload_poll(void) {
    if (s_reboot_at && (int32_t)(xTaskGetTickCount() - s_reboot_at) >= 0)
        esp_restart();
}

typedef struct {
    FILE *file;
    char destination[80];
    size_t bytes;
    unsigned saved;
    bool ready, wifi, playlist;
    bool wifi_saved, playlist_saved;
    bool board, ignore, credentials;
    char ssid[33], password[64];
    size_t text_length;
    char *text;
    size_t text_capacity;
    unsigned fields;
} upload_t;

static bool valid_wifi(const char *path) {
    FILE *file = fopen(path, "rb");
    if (!file) return false;
    char line[128];
    unsigned count = 0;
    bool valid = true;
    while (fgets(line, sizeof(line), file)) {
        size_t n = strlen(line);
        if (!n || (line[n-1] != '\n' && !feof(file))) { valid = false; break; }
        line[strcspn(line, "\r\n")] = 0;
        if (!line[0]) continue;
        char *tab = strchr(line, '\t');
        if (!tab) { valid = false; break; }
        *tab++ = 0;
        size_t ssid = strlen(line), password = strlen(tab);
        if (!ssid || ssid > 32 || password > 63 || strchr(tab, '\t') ||
            ++count > 5) { valid = false; break; }
    }
    valid = valid && !ferror(file) && count > 0;
    fclose(file);
    return valid;
}

static bool publish_file(upload_t *u) {
    if (!u->ready) return true;
    bool changed = false;
    bool ok = u->playlist ? playlist_service_install(UPLOAD_TEMP, &changed) == ESP_OK
                         : file_replace(UPLOAD_TEMP, u->destination);
    if (!ok) return false;
    ++u->saved;
    u->wifi_saved |= u->wifi;
    u->playlist_saved |= u->playlist && changed;
    u->ready = false;
    return true;
}

static bool upload_part(mp_event_t event, const uint8_t *data, size_t length,
                         void *context) {
    upload_t *u = context;
    if (event == MP_BEGIN) {
        if (!publish_file(u)) return false;
        char field[24], name[64] = "";
        if (!mp_parameter((const char *)data, "name", field, sizeof(field)))
            return false;
        (void)mp_parameter((const char *)data, "filename", name, sizeof(name));
        u->ignore = strcmp(field, "submit") == 0;
        if (u->board && !name[0] &&
            (strcmp(field, "www") == 0 || strcmp(field, "data") == 0))
            u->ignore = true; /* Unselected optional file input. */
        u->text = NULL; u->text_length = 0;
        if (u->ignore) return true;
        if (strcmp(field, "ssid") == 0 || strcmp(field, "pass") == 0) {
            unsigned flag = strcmp(field, "ssid") == 0 ? 1U : 2U;
            if (u->fields & flag || u->saved) return false;
            u->fields |= flag;
            u->credentials = true;
            u->text = flag == 1U ? u->ssid : u->password;
            u->text_capacity = flag == 1U ? sizeof(u->ssid) : sizeof(u->password);
            return true;
        }
        if (u->credentials) return false;
        u->wifi = strcmp(field, "wifile") == 0 ||
            (u->board && strcmp(field, "data") == 0 && strcmp(name, "wifi.csv") == 0);
        u->playlist = strcmp(field, "plfile") == 0 ||
            (u->board && strcmp(field, "data") == 0 && strcmp(name, "playlist.csv") == 0);
        if (u->wifi) strcpy(u->destination, "/spiffs/data/wifi.csv");
        else if (u->playlist) strcpy(u->destination, PLAYLIST_PATH);
        else if (u->board && strcmp(field, "www") == 0) {
            static const char *allowed[] = {"theme.css.gz", "style.css.gz",
                "script.js.gz", "dragpl.js.gz", "player.html.gz", "options.html.gz",
                "logo.svg.gz", "updform.html.gz", "ir.css.gz", "ir.js.gz", "irrecord.html.gz"};
            bool found = false;
            for (unsigned i = 0; i < sizeof(allowed)/sizeof(allowed[0]); ++i)
                found |= strcmp(name, allowed[i]) == 0;
            if (!found) return false;
            snprintf(u->destination, sizeof(u->destination), "/spiffs/www/%s", name);
        } else return false;
        if (!u->board && u->saved) return false;
        u->bytes = 0;
        u->file = fopen(UPLOAD_TEMP, "wb");
        return u->file != NULL;
    }
    if (u->ignore) return true;
    if (u->text) {
        if (event == MP_DATA) {
            if (u->text_length + length >= u->text_capacity ||
                memchr(data, 0, length) || memchr(data, '\t', length) ||
                memchr(data, '\r', length) || memchr(data, '\n', length)) return false;
            memcpy(u->text + u->text_length, data, length);
            u->text_length += length;
            u->text[u->text_length] = 0;
        }
        return true;
    }
    if (!u->file) return false;
    if (event == MP_DATA) {
        if (u->bytes + length > (u->wifi ? 640U : UPLOAD_MAX)) return false;
        if (u->wifi && memchr(data, 0, length)) return false;
        u->bytes += length;
        return fwrite(data, 1, length, u->file) == length;
    }
    bool ok = u->bytes > 0 && fflush(u->file) == 0;
    if (fclose(u->file) != 0) ok = false;
    u->file = NULL;
    if (u->wifi) ok = ok && valid_wifi(UPLOAD_TEMP);
    if (u->playlist) ok = ok && playlist_service_validate(UPLOAD_TEMP);
    if (!u->wifi && !u->playlist) {
        FILE *file = fopen(UPLOAD_TEMP, "rb");
        ok = ok && file && fgetc(file) == 0x1f && fgetc(file) == 0x8b;
        if (file) fclose(file);
    }
    u->ready = ok;
    return ok;
}

static bool receive_form(httpd_req_t *request, size_t maximum,
                          mp_handler_t handler, void *context) {
    char type[160];
    if (!request->content_len || request->content_len > maximum ||
        httpd_req_get_hdr_value_str(request, "Content-Type", type, sizeof(type)) != ESP_OK)
        return false;
    if (strncmp(type, "multipart/form-data;", 20) != 0) return false;
    char *boundary = strstr(type, "boundary=");
    if (!boundary) return false;
    boundary += 9;
    if (*boundary == '"') ++boundary;
    boundary[strcspn(boundary, "\";")] = 0;
    web_multipart_t parser;
    if (!mp_init(&parser, boundary, handler, context)) return false;
    size_t left = request->content_len;
    TickType_t start = xTaskGetTickCount();
    while (left) {
        if (xTaskGetTickCount() - start > pdMS_TO_TICKS(120000)) return false;
        size_t n = left > sizeof(s_receive) ? sizeof(s_receive) : left;
        int received = httpd_req_recv(request, (char *)s_receive, n);
        if (received <= 0) return false;
        if (!mp_feed(&parser, s_receive, (size_t)received)) return false;
        left -= (size_t)received;
        vTaskDelay(1);
    }
    return mp_complete(&parser);
}

esp_err_t web_upload_handler(httpd_req_t *request) {
    upload_t upload = {.board = strncmp(request->uri, "/webboard", 9) == 0};
    /* File maintenance pauses radio explicitly; no decoder competes for RAM
     * with flash writes. Commands arriving over WS resume after this request. */
    (void)radio_control_stop();
    bool ok = receive_form(request, UPLOAD_MAX, upload_part, &upload);
    if (upload.file) fclose(upload.file);
    if (ok && upload.credentials) {
        ok = upload.fields == 3U && upload.ssid[0];
        FILE *file = ok ? fopen(UPLOAD_TEMP, "wb") : NULL;
        if (file) {
            ok = fprintf(file, "%s\t%s\n", upload.ssid, upload.password) > 0;
            if (fclose(file) != 0) ok = false;
            ok = ok && valid_wifi(UPLOAD_TEMP);
            strcpy(upload.destination, "/spiffs/data/wifi.csv");
            upload.ready = ok; upload.wifi = true; upload.playlist = false;
        } else ok = false;
    }
    ok = ok && publish_file(&upload) && upload.saved;
    if (!ok) (void)remove(UPLOAD_TEMP);
    if (upload.playlist_saved) {
        native_state_set_station_count(playlist_service_count());
        web_service_notify_playlist_changed();
    }
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    httpd_resp_set_hdr(request, "Connection", "close");
    httpd_resp_set_type(request, "text/plain; charset=utf-8");
    if (!ok) {
        ESP_LOGW(TAG, "Upload rejected or storage failure (%u files saved)", upload.saved);
        httpd_resp_set_status(request, "400 Bad Request");
    } else if (upload.board || upload.credentials) {
        httpd_resp_set_status(request, "303 See Other");
        httpd_resp_set_hdr(request, "Location", "/");
    }
    const char *body = ok ? "OK" : "Upload failed: invalid, incomplete, oversized file or storage full";
    esp_err_t result = httpd_resp_send(request, body, strlen(body));
    if (ok && upload.wifi_saved) web_upload_request_reboot();
    if (result == ESP_OK) shutdown(httpd_req_to_sockfd(request), SHUT_WR);
    /* Do not ask the SDK to drain an untrusted unbounded rejected body. */
    return ok ? result : ESP_FAIL;
}

typedef struct {
    const esp_partition_t *partition;
    esp_ota_handle_t handle;
    bool started, verified, image_part, target_part, target_seen, image_seen;
    size_t written, target_length;
    char target[16];
} ota_upload_t;

static bool ota_part(mp_event_t event, const uint8_t *data, size_t length, void *context) {
    ota_upload_t *u = context;
    if (event == MP_BEGIN) {
        char field[24];
        if (!mp_parameter((const char *)data, "name", field, sizeof(field))) return false;
        u->target_part = strcmp(field, "updatetarget") == 0;
        u->image_part = strcmp(field, "update") == 0;
        if (u->target_part) {
            if (u->target_seen || u->image_seen) return false;
            u->target_seen = true;
            return true;
        }
        /* The original shared YoRadio form and emergency page send "fw". */
        if (!u->image_part || u->image_seen ||
            (strcmp(u->target, "fw") != 0 && strcmp(u->target, "firmware") != 0))
            return false;
        u->image_seen = true;
        return true;
    }
    if (u->target_part) {
        if (event == MP_DATA) {
            if (u->target_length + length >= sizeof(u->target) ||
                memchr(data, 0, length)) return false;
            memcpy(u->target + u->target_length, data, length);
            u->target_length += length;
            u->target[u->target_length] = 0;
        }
        return true;
    }
    if (!u->image_part) return false;
    if (event == MP_DATA) {
        if (u->written + length > u->partition->size) return false;
        if (!u->started) {
            if (!length || data[0] != 0xe9) return false;
            if (esp_ota_begin(u->partition, OTA_SIZE_UNKNOWN, &u->handle) != ESP_OK)
                return false;
            u->started = true;
        }
        if (esp_ota_write(u->handle, data, length) != ESP_OK) return false;
        u->written += length;
        return true;
    }
    if (!u->started || !u->written) return false;
    u->verified = esp_ota_end(u->handle) == ESP_OK;
    u->started = false; /* SDK frees the handle even on validation failure. */
    return u->verified;
}

esp_err_t web_ota_handler(httpd_req_t *request) {
    ota_upload_t upload = {.partition = esp_ota_get_next_update_partition(NULL)};
    bool ok = upload.partition &&
              upload.partition != esp_ota_get_running_partition();
    if (ok) {
        (void)radio_control_stop();
        ok = receive_form(request, upload.partition->size + 4096U, ota_part, &upload);
    }
    if (upload.started) (void)esp_ota_end(upload.handle);
    /* Select boot slot only after complete reception AND image validation. */
    ok = ok && upload.verified &&
         esp_ota_set_boot_partition(upload.partition) == ESP_OK;
    httpd_resp_set_hdr(request, "Connection", "close");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    httpd_resp_set_type(request, "text/plain; charset=utf-8");
    if (!ok) httpd_resp_set_status(request, "400 Bad Request");
    const char *body = ok ? "OK" :
        "OTA rejected: use an ESP8266 native app.bin. SPIFFS images are not supported; use Board file upload.";
    esp_err_t result = httpd_resp_send(request, body, strlen(body));
    if (result == ESP_OK) shutdown(httpd_req_to_sockfd(request), SHUT_WR);
    if (ok) web_upload_request_reboot();
    return ok ? result : ESP_FAIL;
}
