#include "native_wifi_http.h"

#include <errno.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "native_web_transport.h"
#include "native_wifi_json.h"

#define WIFI_IDLE_US UINT64_C(10000000)
#define WIFI_TOTAL_US UINT64_C(30000000)

typedef struct {
    httpd_handle_t server;
    int socket;
    uint64_t started, last_data, response_deadline;
    bool responding, fatal;
    native_wifi_edit_t edit;
    uint8_t body[NATIVE_WIFI_BODY_BYTES];
} wifi_http_io_t;

// Also used by abnormal HTTPD session teardown: no raw-free path may retain a
// partially received password or decoded request in a released heap block.
static void wifi_http_free(void *opaque) {
    if (opaque) { native_wifi_erase(opaque, sizeof(wifi_http_io_t)); free(opaque); }
}

static uint64_t now_us(void) { return (uint64_t)esp_timer_get_time(); }
static uint64_t deadline(const wifi_http_io_t *io) {
    if (io->responding) return io->response_deadline;
    uint64_t idle = io->last_data + WIFI_IDLE_US, total = io->started + WIFI_TOTAL_US;
    return idle < total ? idle : total;
}
static int wait_ready(int socket, bool writable, uint64_t until) {
    uint64_t now = now_us();
    if (now >= until || socket < 0 || socket >= FD_SETSIZE) return HTTPD_SOCK_ERR_TIMEOUT;
    uint64_t remaining = until - now;
    struct timeval timeout = {.tv_sec=(long)(remaining / 1000000U), .tv_usec=(long)(remaining % 1000000U)};
    fd_set set; FD_ZERO(&set); FD_SET(socket, &set);
    int result = lwip_select(socket + 1, writable ? NULL : &set, writable ? &set : NULL, NULL, &timeout);
    if (!result) return HTTPD_SOCK_ERR_TIMEOUT;
    if (result < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
    vTaskDelay(1);
    return ESP_OK;
}
static wifi_http_io_t *request_io(httpd_handle_t server, int socket) {
    wifi_http_io_t *io = httpd_sess_get_ctx(server, socket);
    return io && io->server == server && io->socket == socket ? io : NULL;
}
static int wifi_receive(httpd_handle_t server, int socket, char *data, size_t size, int flags) {
    wifi_http_io_t *io = request_io(server, socket);
    if (!io || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    uint64_t until = deadline(io);
    while (now_us() < until) {
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket, data, size, flags | MSG_DONTWAIT, &writable);
        if (count >= 0) {
            if ((size_t)count > size) { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
            return now_us() >= until ? HTTPD_SOCK_ERR_TIMEOUT : (int)count;
        }
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
            io->fatal = true; return HTTPD_SOCK_ERR_FAIL;
        }
        int result = wait_ready(socket, writable, until);
        if (result != ESP_OK) return result;
    }
    return HTTPD_SOCK_ERR_TIMEOUT;
}
static int wifi_send(httpd_handle_t server, int socket, const char *data, size_t size, int flags) {
    wifi_http_io_t *io = request_io(server, socket);
    if (!io || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    size_t offset = 0;
    uint64_t until = deadline(io);
    while (offset < size && now_us() < until) {
        bool writable;
        ssize_t count = native_web_transport_send(server, socket, data + offset, size - offset,
                                                  flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - offset) { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
            offset += (size_t)count;
        } else if (count < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)) {
            int result = wait_ready(socket, writable, until);
            if (result != ESP_OK) return result;
        } else { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
    }
    return offset == size && now_us() < until ? (int)offset : HTTPD_SOCK_ERR_TIMEOUT;
}
static void drain_rejection(httpd_req_t *request) {
    uint64_t until = now_us() + 250000U;
    int socket = httpd_req_to_sockfd(request);
    uint8_t discard[256];
    while (now_us() < until) {
        bool writable;
        ssize_t count = native_web_transport_recv(request->handle, socket, discard, sizeof(discard), MSG_DONTWAIT, &writable);
        if (!count) break;
        if (count < 0) {
            if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) break;
            if (wait_ready(socket, writable, until) != ESP_OK) break;
        } else vTaskDelay(1);
    }
    native_wifi_erase(discard, sizeof(discard));
}

esp_err_t native_wifi_http_edit(httpd_req_t *request,
                               const native_wifi_http_config_t *config) {
    if (!request || !config || !config->edit || !config->admit || !config->finish) return ESP_FAIL;
    int socket = httpd_req_to_sockfd(request);
    wifi_http_io_t *io = NULL;
    bool attached = false, committed = false;
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
    if (httpd_sess_get_ctx(request->handle, socket)) {
        status = "503 Service Unavailable"; body = "{\"error\":\"Session unavailable\"}"; goto done;
    }
    io = calloc(1, sizeof(*io));
    if (!io) { status = "503 Service Unavailable"; body = "{\"error\":\"Memory unavailable\"}"; goto done; }
    io->server = request->handle; io->socket = socket; io->started = io->last_data = now_us();
    httpd_sess_set_ctx(request->handle, socket, io, wifi_http_free);
    attached = httpd_sess_get_ctx(request->handle, socket) == io;
    if (!attached || httpd_sess_set_recv_override(request->handle, socket, wifi_receive) != ESP_OK ||
        httpd_sess_set_send_override(request->handle, socket, wifi_send) != ESP_OK) {
        status = "503 Service Unavailable"; body = "{\"error\":\"Transport unavailable\"}"; goto done;
    }
    if (config->admit(config->context) != ESP_OK) {
        status = "503 Service Unavailable"; body = "{\"error\":\"Reboot service busy\"}"; goto done;
    }
    size_t offset = 0;
    while (offset < request->content_len) {
        if (now_us() >= deadline(io)) goto timeout;
        int count = httpd_req_recv(request, (char *)io->body + offset, request->content_len - offset);
        if (count == HTTPD_SOCK_ERR_TIMEOUT) { vTaskDelay(1); continue; }
        if (count <= 0 || (size_t)count > request->content_len - offset) goto done;
        if (now_us() >= deadline(io)) goto timeout;
        offset += (size_t)count; io->last_data = now_us(); vTaskDelay(1);
    }
    if (native_wifi_json_decode(io->body, offset, &io->edit) != NATIVE_WIFI_OK) goto done;
    if (now_us() >= deadline(io)) goto timeout;
    native_wifi_result_t result = config->edit(&io->edit);
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
    if (io) { io->responding = true; io->response_deadline = now_us() + 1000000U; }
    esp_err_t response = httpd_resp_sendstr(request, committed ? "{\"saved\":true,\"rebooting\":true}" : body);
    bool graceful = response == ESP_OK && (!io || !io->fatal);
    if (!committed && graceful) drain_rejection(request);
    native_web_transport_prepare_close(request->handle, socket, graceful);
    if (attached) httpd_sess_set_ctx(request->handle, socket, NULL, NULL);
    else wifi_http_free(io);
    config->finish(config->context, committed);
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
        native_web_transport_prepare_close(request->handle, httpd_req_to_sockfd(request), sent == ESP_OK);
        return ESP_FAIL; // Do not SDK-purge an untrusted GET request body.
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
