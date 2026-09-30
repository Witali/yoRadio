#include "web_ota.h"

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include "audio_service.h"
#include "deep_sleep_clock.h"
#include "display_settings.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "ota_upload.h"
#include "lwip/sockets.h"
#include "lwip/tcp.h"

static bool s_reboot_pending;

static void finish_rejection(httpd_req_t *request) {
    /* A close with unread upload bytes can reset TCP and discard our error in
     * the browser. Send FIN first, then briefly drain the peer. Never let an
     * oversized body or a silent sender keep the HTTP task occupied forever. */
    int fd = httpd_req_to_sockfd(request);
    if (shutdown(fd, SHUT_WR) != 0) return;
    int64_t deadline = esp_timer_get_time() + 250000;
    char discard[256];
    while (esp_timer_get_time() < deadline) {
        int n = recv(fd, discard, sizeof(discard), MSG_DONTWAIT);
        if (n == 0 || (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK &&
                      errno != EINTR)) break;
        vTaskDelay(1);
    }
}

static void ota_reboot(void *argument) {
    (void)argument;
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    vTaskDelay(pdMS_TO_TICKS(1000));
    esp_restart();
}

static bool boundary_from_request(httpd_req_t *request, char *boundary,
                                  size_t capacity) {
    char type[192];
    if (httpd_req_get_hdr_value_str(request, "Content-Type", type,
                                    sizeof(type)) != ESP_OK ||
        strncmp(type, "multipart/form-data;", 20)) return false;
    const char *start = strstr(type + 20, "boundary=");
    if (!start) return false;
    start += 9;
    bool quoted = *start == '"';
    if (quoted) ++start;
    const char *end = quoted ? strchr(start, '"') : strpbrk(start, "; \t");
    if (!end) {
        if (quoted) return false;
        end = start + strlen(start);
    }
    size_t size = end - start;
    if (!size || size > 70 || size >= capacity) return false;
    memcpy(boundary, start, size);
    boundary[size] = 0;
    return !strpbrk(boundary, "\r\n");
}

esp_err_t web_ota_handler(httpd_req_t *request) {
    int no_delay = 1;
    (void)setsockopt(httpd_req_to_sockfd(request), IPPROTO_TCP, TCP_NODELAY,
                     &no_delay, sizeof(no_delay));
    httpd_resp_set_type(request, "text/plain; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    httpd_resp_set_hdr(request, "Connection", "close");
    if (s_reboot_pending || !deep_sleep_clock_begin_activity()) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        httpd_resp_sendstr(request, "Radio is sleeping or rebooting; wake it and retry");
        finish_rejection(request);
        return ESP_FAIL;
    }
    display_settings_note_activity();
    ota_upload_t *upload = calloc(1, sizeof(*upload));
    TaskHandle_t reboot = NULL;
    const char *error = "Not enough memory for OTA";
    bool ok = false;
    char boundary[71];
    if (!upload) goto done;
    error = "Expected multipart firmware upload";
    if (!boundary_from_request(request, boundary, sizeof(boundary))) goto done;
    if (!ota_upload_init(upload, boundary)) goto done;
    error = "Empty or oversized firmware upload";
    if (!request->content_len ||
        request->content_len > upload->partition->size + 2048U) goto done;

    // Keep saved station, Smart Start and all settings intact.
    audio_service_stop();
    size_t remaining = request->content_len;
    uint8_t chunk[1024];
    int64_t start = esp_timer_get_time(), last_data = start;
    while (remaining) {
        int64_t now = esp_timer_get_time();
        error = "Upload timed out; retry with a stable connection";
        if (now - start >= 180000000 || now - last_data >= 10000000) goto done;
        size_t count = remaining < sizeof(chunk) ? remaining : sizeof(chunk);
        int received = httpd_req_recv(request, (char *)chunk, count);
        if (received == HTTPD_SOCK_ERR_TIMEOUT) continue;
        error = "Upload connection interrupted";
        if (received <= 0) goto done;
        now = esp_timer_get_time();
        error = "Upload timed out; retry with a stable connection";
        if (now - start >= 180000000 || now - last_data >= 10000000) goto done;
        last_data = now;
        if (!ota_upload_feed(upload, chunk, (size_t)received)) goto done;
        remaining -= (size_t)received;
        vTaskDelay(1);
    }
    if (!ota_upload_finish(upload)) goto done;
    // Allocate the reboot task before changing the boot selector. It cannot
    // run until the response has been queued, even if sending it fails.
    error = "Not enough memory to schedule reboot";
    if (xTaskCreate(ota_reboot, "ota_reboot", 2048, NULL, 3, &reboot) != pdPASS)
        goto done;
    if (!ota_upload_activate(upload)) goto done;
    s_reboot_pending = true;
    ok = true;
done:
    if (!ok) {
        if (upload && upload->error) error = upload->error;
        if (reboot) vTaskDelete(reboot);
        if (upload) ota_upload_abort(upload);
        httpd_resp_set_status(request, "400 Bad Request");
    }
    esp_err_t result = httpd_resp_sendstr(request, ok ? "OK" : error);
    free(upload);
    if (ok) {
        // Retain the activity lease until restart: there must be no deep sleep
        // between changing otadata and booting the new application.
        xTaskNotifyGive(reboot);
    } else {
        finish_rejection(request);
        display_settings_note_activity();
        deep_sleep_clock_end_activity();
    }
    // Close rejected uploads rather than draining an untrusted request body.
    return ok ? result : ESP_FAIL;
}

esp_err_t web_ota_info_handler(httpd_req_t *request) {
    if (!deep_sleep_clock_begin_activity()) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Wake the radio with BOOT");
    }
    display_settings_note_activity();
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *next = esp_ota_get_next_update_partition(NULL);
    const esp_app_desc_t *app = esp_app_get_description();
    // Escape the fixed-size version field even for custom build versions.
    char version[sizeof(app->version) * 6 + 1];
    size_t used = 0;
    for (size_t i = 0; i < sizeof(app->version) && app->version[i]; ++i) {
        unsigned char ch = app->version[i];
        if (ch < 32 || ch == '"' || ch == '\\') {
            used += (size_t)snprintf(version + used, sizeof(version) - used,
                                     "\\u%04x", ch);
        } else version[used++] = ch;
    }
    version[used] = 0;
    char hash[65], body[448];
    // esp_app_get_elf_sha256() may use a shortened CONFIG_APP_RETRIEVE_LEN_ELF_SHA.
    for (size_t i = 0; i < sizeof(app->app_elf_sha256); ++i)
        snprintf(hash + i * 2, 3, "%02x", app->app_elf_sha256[i]);
    snprintf(body, sizeof(body),
             "{\"version\":\"%s\",\"partition\":\"%s\",\"max_size\":%lu,"
             "\"app_elf_sha256\":\"%s\"}", version,
             running ? running->label : "", (unsigned long)(next ? next->size : 0), hash);
    httpd_resp_set_type(request, "application/json");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    esp_err_t result = httpd_resp_sendstr(request, body);
    deep_sleep_clock_end_activity();
    return result;
}
