#include "web_static.h"

#include <stdatomic.h>
#include <stdio.h>
#include <string.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "web_pages.h"
#include "web_upload.h"
#include "native_wifi_public.h"

#define STATIC_QUEUE_DEPTH 2
#define STATIC_STACK_BYTES (3072 + CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES)

static QueueHandle_t s_requests;
static TaskHandle_t s_workers[CONFIG_YORADIO_WEB_STATIC_WORKERS];
static atomic_bool s_active;

static const char *content_type(const char *path) {
    const char *extension = strrchr(path, '.');
    if (!extension) return "application/octet-stream";
    if (!strcmp(extension, ".html")) return "text/html; charset=utf-8";
    if (!strcmp(extension, ".css")) return "text/css; charset=utf-8";
    if (!strcmp(extension, ".js")) return "application/javascript; charset=utf-8";
    if (!strcmp(extension, ".svg")) return "image/svg+xml";
    if (!strcmp(extension, ".png")) return "image/png";
    if (!strcmp(extension, ".ico")) return "image/x-icon";
    return "application/octet-stream";
}

static FILE *open_nonempty(const char *path) {
    FILE *file = web_upload_open_file(path);
    if (file && (fgetc(file) == EOF || fseek(file, 0, SEEK_SET))) {
        fclose(file);
        file = NULL;
    }
    return file;
}

static esp_err_t serve_static(httpd_req_t *request) {
    if (!native_wifi_public_static_uri(request->uri, request->method == HTTP_GET))
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND, "File not found");
    char uri[160];
    size_t length = strcspn(request->uri, "?");
    if (!length || length >= sizeof(uri))
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST, "Invalid path");
    memcpy(uri, request->uri, length);
    uri[length] = '\0';
    // Paths are literal SPIFFS names. No decoding or alternate separators.
    if (uri[0] != '/' || strstr(uri, "..") || strstr(uri, "//"))
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST, "Invalid path");
    for (const unsigned char *p = (const unsigned char *)uri; *p; ++p) {
        if (!((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') ||
              (*p >= '0' && *p <= '9') || strchr("/._-", *p)))
            return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST, "Invalid path");
    }
    httpd_resp_set_hdr(request, "Connection", "close");
    if (!strcmp(uri, "/variables.js")) {
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_sendstr(request,
            "var webUiRevision='native06-wifi';\n"
            "var nativeFirmwareOnly=true;\n"
            "var nativeFirmwareName='ESP32 CYD native';\n"
            "var nativeFirmwareInfo='/api/native/ota';\n"
            "var nativeWiFiApi='/api/native/wifi';\n"
            "var nativeWiFiMaxProfiles=5;\n"
            "var nativeWiFiPrivateExport=false;\n"
            "var nativeTimeApi='/api/native/time';\n");
    }
    if (!strcmp(uri, "/") || !strcmp(uri, "/index.html") ||
        !strcmp(uri, "/settings.html") || !strcmp(uri, "/webboard") ||
        !strcmp(uri, "/emergency")) {
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return httpd_resp_sendstr(request, web_native_page());
    }
    // Only the public playlist is downloadable from the data directory.
    if (!strncmp(uri, "/data/", 6) && strcmp(uri, "/data/playlist.csv") != 0)
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND, "File not found");
    char path[224];
    bool gzip = false;
    if (!strncmp(uri, "/data/", 6)) snprintf(path, sizeof(path), "/spiffs%s", uri);
    else snprintf(path, sizeof(path), "/spiffs/www%s", uri);
    FILE *file = open_nonempty(path);
    if (!file && strncmp(uri, "/data/", 6) != 0) {
        size_t used = strlen(path);
        memcpy(path + used, ".gz", 4);
        file = open_nonempty(path);
        gzip = file != NULL;
    } else if (file && length > 3 && !strcmp(uri + length - 3, ".gz")) {
        gzip = true;
        uri[length - 3] = '\0';
    }
    if (!file) return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND, "File not found");
    httpd_resp_set_type(request, content_type(uri));
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    if (gzip) httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
    char chunk[CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES];
    esp_err_t result = ESP_OK;
    for (;;) {
        size_t count = fread(chunk, 1, sizeof(chunk), file);
        if (count) {
            result = httpd_resp_send_chunk(request, chunk, (ssize_t)count);
            if (result != ESP_OK) break;
        }
        // A positive short read may already have set EOF or an error. Its
        // position can be indeterminate after error; never read it again.
        if (ferror(file)) { result = ESP_FAIL; break; }
        if (feof(file)) break;
        if (count < sizeof(chunk)) { result = ESP_FAIL; break; }
    }
    if (fclose(file) != 0) result = ESP_FAIL;
    // Never terminate a failed/truncated response as a successful body.
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
    return result;
}

static void complete_static(httpd_req_t *request) {
    // The async request still owns the session here, so its descriptor cannot
    // be purged/reused. Shutdown, then complete and wake HTTPD to reap it.
    // A queued close by fd after completion could close a reused descriptor.
    shutdown(httpd_req_to_sockfd(request), SHUT_RDWR);
    if (httpd_req_async_handler_complete(request) != ESP_OK)
        ESP_LOGW("web", "Static request completion failed");
}

static void static_worker(void *argument) {
    (void)argument;
    // During startup rollback these tasks own no queue or session resources.
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    while (true) {
        httpd_req_t *request;
        if (xQueueReceive(s_requests, (void *)&request, portMAX_DELAY) != pdTRUE) continue;
        serve_static(request);
        complete_static(request);
    }
}

void web_static_abort(void) {
    // Startup rollback only: no route has been activated or queued work.
    for (unsigned i = 0; i < CONFIG_YORADIO_WEB_STATIC_WORKERS; ++i) {
        if (s_workers[i]) vTaskDelete(s_workers[i]);
        s_workers[i] = NULL;
    }
    if (s_requests) vQueueDelete(s_requests);
    s_requests = NULL;
}

esp_err_t web_static_start(void) {
    if (s_requests) return ESP_ERR_INVALID_STATE;
    atomic_store(&s_active, false);
    s_requests = xQueueCreate(STATIC_QUEUE_DEPTH, sizeof(httpd_req_t *));
    if (!s_requests) return ESP_ERR_NO_MEM;
    for (unsigned i = 0; i < CONFIG_YORADIO_WEB_STATIC_WORKERS; ++i) {
        if (xTaskCreate(static_worker, "web_static", STATIC_STACK_BYTES, NULL, 2,
                        &s_workers[i]) != pdPASS) {
            web_static_abort();
            return ESP_ERR_NO_MEM;
        }
    }
    return ESP_OK;
}

void web_static_activate(void) {
    atomic_store(&s_active, true);
    for (unsigned i = 0; i < CONFIG_YORADIO_WEB_STATIC_WORKERS; ++i)
        xTaskNotifyGive(s_workers[i]);
}

esp_err_t web_static_handler(httpd_req_t *request) {
    httpd_resp_set_hdr(request, "Connection", "close");
    if (!native_wifi_public_static_uri(request->uri, request->method == HTTP_GET))
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND, "File not found");
    if (!atomic_load(&s_active)) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Web service is starting");
    }
    httpd_req_t *async_request = NULL;
    if (httpd_req_async_handler_begin(request, &async_request) != ESP_OK) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Static worker unavailable");
    }
    if (xQueueSend(s_requests, (const void *)&async_request, 0) != pdTRUE) {
        httpd_resp_set_status(async_request, "503 Service Unavailable");
        httpd_resp_sendstr(async_request, "Static queue full");
        complete_static(async_request);
    }
    return ESP_OK;
}
