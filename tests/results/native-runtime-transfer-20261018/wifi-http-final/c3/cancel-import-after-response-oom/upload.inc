
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

bool web_upload_publish_playlist(const char *csv_temporary,
                                 const char *index_temporary) {
    if (!s_storage_lock ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return false;
    bool replaced = native_file_replace_pair(
        csv_temporary, "/spiffs/data/playlist.csv", "/spiffs/data/playlist.csv.bak",
        index_temporary, "/spiffs/data/index.dat", "/spiffs/data/index.dat.bak");
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
    char type[192], boundary[71];
    size_t limit = form->mode == WEB_FORM_CREDENTIALS ? 4096U : WEB_UPLOAD_MAX;
    if (!request->content_len || request->content_len > limit ||
        httpd_req_get_hdr_value_str(request, "Content-Type", type, sizeof(type)) != ESP_OK ||
        !mp_form_data_boundary(type, boundary, sizeof(boundary))) return false;
    web_multipart_t parser;
    if (!mp_init(&parser, boundary, web_file_form_part, form)) return false;
    uint8_t chunk[WEB_UPLOAD_RECEIVE_BYTES] = {0};
    bool complete = false;
    size_t remaining = request->content_len;
    int64_t started = esp_timer_get_time(), last_data = started;
    while (remaining) {
        int64_t now = esp_timer_get_time();
        if (now - started >= WEB_UPLOAD_TIMEOUT_US || now - last_data >= WEB_UPLOAD_IDLE_US)
            goto done;
        size_t count = remaining < sizeof(chunk) ? remaining : sizeof(chunk);
        int received = httpd_req_recv(request, (char *)chunk, count);
        if (received == HTTPD_SOCK_ERR_TIMEOUT) { vTaskDelay(1); continue; }
        if (received <= 0 || (size_t)received > count) goto done;
        now = esp_timer_get_time();
        if (now - started >= WEB_UPLOAD_TIMEOUT_US || now - last_data >= WEB_UPLOAD_IDLE_US)
            goto done;
        if (!mp_feed(&parser, chunk, (size_t)received)) goto done;
        // Staging may synchronously write/flush flash. Exclude that controlled
        // work only from idle time; never extend the absolute receive budget.
        last_data = esp_timer_get_time();
        if (last_data - started >= WEB_UPLOAD_TIMEOUT_US ||
            !native_wifi_request_io_progress(request)) goto done;
        native_wifi_erase(chunk, sizeof(chunk));
        remaining -= (size_t)received;
        vTaskDelay(1);
    }
    complete = mp_complete(&parser);
done:
    native_wifi_erase(chunk, sizeof(chunk));
    return complete;
}

static bool upload_destination(const char *name, bool playlist,
                               char *destination, size_t capacity) {
    char checked[WEB_FILE_FORM_NAME_BYTES];
    if (!name || !web_form_name(name, checked, sizeof(checked)) ||
        strcmp(checked, name)) return false;
    int length = snprintf(destination, capacity, "/spiffs/%s/%s",
                          playlist ? "data" : "www", name);
    if (length <= 0 || (size_t)length >= capacity) return false;
    size_t backup_bytes = (size_t)length - strlen("/spiffs") + sizeof(".bak");
    if (backup_bytes > WEB_FILE_FORM_NAME_BYTES) return false;
    if (!playlist && (length <= 3 || strcmp(destination + length - 3, ".gz") != 0)) return false;
    if (!playlist) {
        size_t raw = strlen(name) - 3U;
        if ((raw >= 3U && !memcmp(name + raw - 3U, ".gz", 3)) ||
            (raw >= 4U && (!memcmp(name + raw - 4U, ".bak", 4) ||
                           !memcmp(name + raw - 4U, ".tmp", 4)))) return false;
    }
    return !playlist || !strcmp(name, "playlist.csv");
}

static bool publish_file(unsigned slot, const char *name, bool playlist) {
    char temporary[64], destination[128];
    temporary_path(slot, temporary, sizeof(temporary));
    if (!upload_destination(name, playlist, destination, sizeof(destination))) return false;
    // Retain the previous file until the validated replacement has its live
    // name. Boot/read recovery can restore a retained backup after interruption.
    if (playlist) return web_upload_publish_file(temporary, destination);
    char backup[256];
    if (!s_storage_lock || !backup_name(destination, backup, sizeof(backup)) ||
        xSemaphoreTake(s_storage_lock, pdMS_TO_TICKS(1000)) != pdTRUE) return false;
    bool replaced = native_file_replace(temporary, destination, backup);
    if (replaced) {
        destination[strlen(destination) - 3] = 0;
        if (remove(destination) != 0 && errno != ENOENT) replaced = false;
    }
    xSemaphoreGive(s_storage_lock);
    return replaced;
}

static bool credentials_valid(const web_file_form_t *form) {
    if (!form->ssid_seen || !form->password_seen) return false;
    size_t ssid = strnlen(form->ssid, sizeof(form->ssid));
    size_t password = strnlen(form->password, sizeof(form->password));
    return ssid && ssid < NATIVE_WIFI_SSID_BYTES && password < NATIVE_WIFI_PASSWORD_BYTES &&
           !strpbrk(form->ssid, "\t\r\n") && !strpbrk(form->password, "\t\r\n");
}

static esp_err_t handle_upload(httpd_req_t *request, web_form_mode_t mode) {
    if (!websocket_service_reboot_ready()) {
        httpd_resp_set_hdr(request, "Connection", "close");
        httpd_resp_set_status(request, "503 Service Unavailable");
        esp_err_t sent = httpd_resp_sendstr(request, "Upload service is starting");
        native_wifi_request_io_close(request, NULL, sent == ESP_OK, false);
        return ESP_FAIL;
    }
    native_wifi_request_io_t *io = native_wifi_request_io_open(request,
        WEB_UPLOAD_IDLE_US, WEB_UPLOAD_TIMEOUT_US, NULL, NULL);
    if (!io) {
        httpd_resp_set_hdr(request, "Connection", "close");
        httpd_resp_set_status(request, "503 Service Unavailable");
        esp_err_t sent = httpd_resp_sendstr(request, "Upload transport unavailable");
        native_wifi_request_io_close(request, NULL, sent == ESP_OK, false);
        return ESP_FAIL;
    }
    upload_sink_t sink = {.fd = -1};
    web_file_form_t form = {
        .mode = mode, .sink = {begin_file, write_file, end_file, &sink},
    };
    bool ok = receive_form(request, &form);
    if (sink.fd >= 0) close(sink.fd);
    free(sink.buffer);
    bool wifi_saved = false, playlist_saved = false, reboot_busy = false;
    websocket_reboot_lease_t reboot = {0};
    bool has_wifi = mode == WEB_FORM_CREDENTIALS || form.wifi_seen;
    if (ok && mode == WEB_FORM_CREDENTIALS) ok = credentials_valid(&form);
    else if (ok) {
        ok = form.files || form.wifi_seen;
        if (ok && form.wifi_seen)
            ok = network_service_validate_credentials_file(
                (const uint8_t *)form.wifi, form.wifi_bytes) == ESP_OK;
        for (unsigned i = 0; ok && i < form.files; ++i) {
            char destination[128];
            ok = upload_destination(form.names[i], form.playlist[i],
                                    destination, sizeof(destination));
        }
    }
    // Temporary staging above is allowed before admission. No live asset,
    // playlist or credential publication may precede this atomic reservation.
    if (ok && has_wifi) {
        ok = websocket_service_reboot_reserve(&reboot) == ESP_OK;
        reboot_busy = !ok;
    }
    for (unsigned i = 0; ok && i < form.files; ++i) {
        if (form.playlist[i]) {
            char temporary[64];
            temporary_path(i, temporary, sizeof(temporary));
            ok = radio_control_publish_playlist(temporary,
                    web_upload_publish_playlist) == ESP_OK;
            playlist_saved = ok;
        } else ok = publish_file(i, form.names[i], false);
    }
    if (ok && has_wifi) {
        ok = mode == WEB_FORM_CREDENTIALS ?
            network_service_save_credentials(form.ssid, form.password) == ESP_OK :
            network_service_save_credentials_file((const uint8_t *)form.wifi, form.wifi_bytes) == ESP_OK;
        wifi_saved = ok;
    }
    for (unsigned i = 0; i < WEB_FILE_FORM_MAX_FILES; ++i) {
        char path[64];
        temporary_path(i, path, sizeof(path));
        remove(path);
    }
    native_wifi_erase(&form, sizeof(form));
    if (playlist_saved) websocket_service_notify_playlist_changed();
    httpd_resp_set_type(request, "text/plain; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    httpd_resp_set_hdr(request, "Connection", "close");
    if (!ok) httpd_resp_set_status(request, reboot_busy ? "503 Service Unavailable" : "400 Bad Request");
    else if (mode != WEB_FORM_UPLOAD) {
        httpd_resp_set_status(request, "303 See Other");
        httpd_resp_set_hdr(request, "Location", "/");
    }
    native_wifi_request_io_response(io);
    esp_err_t response = httpd_resp_sendstr(request, ok ? "OK" :
        reboot_busy ? "Reboot service is busy; no files were published" :
        "Upload failed: invalid, incomplete, oversized file or storage full");
    native_wifi_request_io_close(request, io, response == ESP_OK, !ok);
    if (wifi_saved && response == ESP_OK) (void)websocket_service_reboot_commit(&reboot, 750);
    else if (reboot.epoch) (void)websocket_service_reboot_cancel(&reboot);
    // Success remains HTTP 200/303. Every terminal upload closes via SDK
    // deletion, never its unread-body purge or stale request overrides.
    return ESP_FAIL;
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
