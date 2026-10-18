#include "native_wifi_http.h"

#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_wifi_json.h"
#include "native_wifi_request_io.h"

#define WIFI_IDLE_US UINT64_C(10000000)
#define WIFI_TOTAL_US UINT64_C(30000000)

typedef struct {
    native_wifi_edit_t edit;
    uint8_t body[NATIVE_WIFI_BODY_BYTES];
} wifi_http_payload_t;

// The request I/O context owns this callback, including abnormal SDK teardown.
static void wifi_http_free(void *opaque) {
    if (opaque) { native_wifi_erase(opaque, sizeof(wifi_http_payload_t)); free(opaque); }
}

esp_err_t native_wifi_http_edit(httpd_req_t *request,
                               const native_wifi_http_config_t *config) {
    if (!request || !config || !config->edit || !config->admit || !config->finish) return ESP_FAIL;
    native_wifi_request_io_t *io = NULL;
    wifi_http_payload_t *payload = NULL;
    bool committed = false;
    const char *status = "400 Bad Request", *body = "{\"error\":\"Invalid Wi-Fi update\"}";
    if (httpd_resp_set_type(request, "application/json; charset=utf-8") != ESP_OK ||
        httpd_resp_set_hdr(request, "Cache-Control", "no-store") != ESP_OK ||
        httpd_resp_set_hdr(request, "Connection", "close") != ESP_OK) {
        status = "500 Internal Server Error"; body = "{\"error\":\"Response unavailable\"}"; goto done;
    }
    if (request->method != HTTP_POST || !request->content_len) goto done;
    if (request->content_len > NATIVE_WIFI_BODY_BYTES) {
        status = "413 Content Too Large"; body = "{\"error\":\"Wi-Fi update exceeds limit\"}"; goto done;
    }
    char type[64];
    if (httpd_req_get_hdr_value_str(request, "Content-Type", type, sizeof(type)) != ESP_OK ||
        strcasecmp(type, "application/json")) goto done;
    if (request->sess_ctx) {
        status = "503 Service Unavailable"; body = "{\"error\":\"Session unavailable\"}"; goto done;
    }
    payload = calloc(1, sizeof(*payload));
    if (!payload) { status = "503 Service Unavailable"; body = "{\"error\":\"Memory unavailable\"}"; goto done; }
    // open ALWAYS consumes payload, even when attachment/overrides fail.
    io = native_wifi_request_io_open(request, WIFI_IDLE_US, WIFI_TOTAL_US, payload, wifi_http_free);
    if (!io) {
        payload = NULL;
        status = "503 Service Unavailable"; body = "{\"error\":\"Transport unavailable\"}"; goto done;
    }
    if (config->admit(config->context) != ESP_OK) {
        status = "503 Service Unavailable"; body = "{\"error\":\"Reboot service busy\"}"; goto done;
    }
    size_t offset = 0;
    while (offset < request->content_len) {
        if (native_wifi_request_io_expired(io)) goto timeout;
        int count = httpd_req_recv(request, (char *)payload->body + offset, request->content_len - offset);
        if (count == HTTPD_SOCK_ERR_TIMEOUT) { vTaskDelay(1); continue; }
        if (count <= 0 || (size_t)count > request->content_len - offset) goto done;
        if (native_wifi_request_io_expired(io)) goto timeout;
        offset += (size_t)count;
        if (!native_wifi_request_io_progress(request)) goto timeout;
        vTaskDelay(1);
    }
    if (native_wifi_json_decode(payload->body, offset, &payload->edit) != NATIVE_WIFI_OK) goto done;
    if (native_wifi_request_io_expired(io)) goto timeout;
    native_wifi_result_t result = config->edit(&payload->edit);
    // Publication is irreversible. A late deadline/response error cannot cancel
    // the reserved reboot or falsely report that the desired store is unchanged.
    if (result == NATIVE_WIFI_OK) { committed = true; goto done; }
    if (result == NATIVE_WIFI_CONFLICT) {
        status = "409 Conflict"; body = "{\"error\":\"Wi-Fi settings changed; reload\"}";
    } else if (result == NATIVE_WIFI_BUSY || result == NATIVE_WIFI_NOT_READY ||
               result == NATIVE_WIFI_INVALID_STORAGE || result == NATIVE_WIFI_NO_MEMORY) {
        status = "503 Service Unavailable"; body = "{\"error\":\"Wi-Fi store unavailable\"}";
    } else if (result != NATIVE_WIFI_INVALID) {
        status = "500 Internal Server Error"; body = "{\"error\":\"Wi-Fi storage failed\"}";
    }
    goto done;
timeout:
    status = "408 Request Timeout"; body = "{\"error\":\"Wi-Fi upload timed out\"}";
done:
    if (!committed) (void)httpd_resp_set_status(request, status);
    native_wifi_request_io_response(io);
    esp_err_t response = httpd_resp_sendstr(request, committed ? "{\"saved\":true,\"rebooting\":true}" : body);
    native_wifi_request_io_close(request, io, response == ESP_OK, !committed);
    config->finish(config->context, committed && response == ESP_OK);
    return ESP_FAIL;
}

esp_err_t native_wifi_http_info(httpd_req_t *request,
    native_wifi_result_t (*metadata)(native_wifi_metadata_t *out)) {
    native_wifi_metadata_t value;
    char body[1536]; size_t size;
    if (!request || !metadata) return ESP_FAIL;
    if (request->method != HTTP_GET || request->content_len) {
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_hdr(request, "Connection", "close");
        httpd_resp_set_status(request, "400 Bad Request");
        esp_err_t sent = httpd_resp_sendstr(request, "Metadata requests must not contain a body");
        native_wifi_request_io_close(request, NULL, sent == ESP_OK, false);
        return ESP_FAIL;
    }
    native_wifi_result_t result = metadata(&value);
    if (result != NATIVE_WIFI_OK) {
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Wi-Fi metadata unavailable");
    }
    if (!native_wifi_json_metadata(&value, body, sizeof(body), &size))
        return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Wi-Fi metadata unavailable");
    if (httpd_resp_set_type(request, "application/json; charset=utf-8") != ESP_OK ||
        httpd_resp_set_hdr(request, "Cache-Control", "no-store") != ESP_OK) return ESP_FAIL;
    return httpd_resp_send(request, body, (ssize_t)size);
}
