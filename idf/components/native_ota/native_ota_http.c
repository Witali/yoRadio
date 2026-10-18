#include "native_ota_http.h"

#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "json_buffer.h"
#include "lwip/sockets.h"
#include "native_ota_form.h"
#include "native_web_transport.h"

typedef struct {
    httpd_handle_t server;
    int socket;
    uint64_t deadline, last_data, response_deadline;
    bool responding, fatal;
    native_ota_form_t form;
} ota_http_io_t;

static uint64_t ota_now(void) { return (uint64_t)esp_timer_get_time(); }
static uint64_t io_deadline(const ota_http_io_t *io) {
    if (io->responding) return io->response_deadline;
    uint64_t idle = io->last_data + NATIVE_OTA_IDLE_US;
    return idle < io->deadline ? idle : io->deadline;
}
static int io_wait(int socket, bool writable, uint64_t deadline) {
    uint64_t now = ota_now();
    if (now >= deadline || socket < 0 || socket >= FD_SETSIZE) return HTTPD_SOCK_ERR_TIMEOUT;
    uint64_t remaining = deadline - now;
    struct timeval timeout = {.tv_sec = (long)(remaining / 1000000U), .tv_usec = (long)(remaining % 1000000U)};
    fd_set set; FD_ZERO(&set); FD_SET(socket, &set);
    int result = lwip_select(socket + 1, writable ? NULL : &set, writable ? &set : NULL, NULL, &timeout);
    if (!result) return HTTPD_SOCK_ERR_TIMEOUT;
    if (result < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
    vTaskDelay(1); // spurious readiness/EINTR cannot spin the HTTPD task
    return ESP_OK;
}
static ota_http_io_t *request_io(httpd_handle_t server, int socket) {
    ota_http_io_t *io = httpd_sess_get_ctx(server, socket);
    return io && io->server == server && io->socket == socket ? io : NULL;
}
static int ota_receive(httpd_handle_t server, int socket, char *data, size_t size, int flags) {
    ota_http_io_t *io = request_io(server, socket);
    if (!io || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    uint64_t deadline = io_deadline(io);
    while (ota_now() < deadline) {
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket, data, size, flags | MSG_DONTWAIT, &writable);
        if (count >= 0) {
            if ((size_t)count > size) { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
            return ota_now() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)count;
        }
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
            io->fatal = true; return HTTPD_SOCK_ERR_FAIL;
        }
        int result = io_wait(socket, writable, deadline);
        if (result != ESP_OK) return result;
    }
    return HTTPD_SOCK_ERR_TIMEOUT;
}
static int ota_send(httpd_handle_t server, int socket, const char *data, size_t size, int flags) {
    ota_http_io_t *io = request_io(server, socket);
    if (!io || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    size_t offset = 0;
    uint64_t deadline = io_deadline(io);
    while (offset < size && ota_now() < deadline) {
        bool writable;
        ssize_t count = native_web_transport_send(server, socket, data + offset, size - offset,
                                                  flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - offset) { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
            offset += (size_t)count;
        } else if (count < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)) {
            int result = io_wait(socket, writable, deadline);
            if (result != ESP_OK) return result;
        } else { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
    }
    return offset == size && ota_now() < deadline ? (int)offset : HTTPD_SOCK_ERR_TIMEOUT;
}
static void drain_rejection(httpd_req_t *request) {
    uint64_t deadline = ota_now() + 250000U;
    int socket = httpd_req_to_sockfd(request);
    uint8_t discard[256];
    while (ota_now() < deadline) {
        bool writable;
        ssize_t count = native_web_transport_recv(request->handle, socket, discard, sizeof(discard), MSG_DONTWAIT, &writable);
        if (!count) break;
        if (count < 0) {
            if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) break;
            if (io_wait(socket, writable, deadline) != ESP_OK) break;
        } else vTaskDelay(1);
    }
}

esp_err_t native_ota_http_upload(httpd_req_t *request, const native_ota_http_config_t *config) {
    if (!request || !config || !config->admit || !config->finish || !config->policy.before_flash) return ESP_FAIL;
    uint64_t deadline = ota_now() + NATIVE_OTA_OVERALL_US;
    int socket = httpd_req_to_sockfd(request);
    ota_http_io_t *io = NULL;
    bool attached = false, activated = false;
    const char *status = "400 Bad Request", *error = "Expected multipart firmware upload";
    if (httpd_resp_set_type(request, "text/plain; charset=utf-8") != ESP_OK ||
        httpd_resp_set_hdr(request, "Cache-Control", "no-store") != ESP_OK ||
        httpd_resp_set_hdr(request, "Connection", "close") != ESP_OK) {
        status = "500 Internal Server Error"; error = "Cannot prepare OTA response"; goto done;
    }
    char type[192], boundary[71];
    if (!request->content_len ||
        httpd_req_get_hdr_value_str(request, "Content-Type", type, sizeof(type)) != ESP_OK ||
        !mp_form_data_boundary(type, boundary, sizeof(boundary))) goto done;
    if (httpd_sess_get_ctx(request->handle, socket)) {
        status = "503 Service Unavailable"; error = "Session is owned by another service"; goto done;
    }
    io = calloc(1, sizeof(*io));
    if (!io) { status = "503 Service Unavailable"; error = "Not enough memory for OTA"; goto done; }
    io->server = request->handle; io->socket = socket; io->deadline = deadline; io->last_data = ota_now();
    if (!native_ota_form_init(&io->form, boundary, &config->policy)) goto done;
    size_t limit = io->form.image.limit;
    if (limit > SIZE_MAX - NATIVE_OTA_BODY_OVERHEAD) goto done;
    limit += NATIVE_OTA_BODY_OVERHEAD;
    if (config->max_body_bytes && limit > config->max_body_bytes) limit = config->max_body_bytes;
    if (request->content_len > limit) { status = "413 Content Too Large"; error = "Firmware upload exceeds the application limit"; goto done; }
    if (config->admit(config->context, deadline) != ESP_OK) {
        status = "503 Service Unavailable"; error = "OTA unavailable: maintenance or reboot service is busy"; goto done;
    }
    io->last_data = ota_now();
    httpd_sess_set_ctx(request->handle, socket, io, free);
    attached = httpd_sess_get_ctx(request->handle, socket) == io;
    if (!attached || httpd_sess_set_recv_override(request->handle, socket, ota_receive) != ESP_OK ||
        httpd_sess_set_send_override(request->handle, socket, ota_send) != ESP_OK) {
        status = "503 Service Unavailable"; error = "Cannot install OTA transport"; goto done;
    }
    uint8_t chunk[1024];
    size_t remaining = request->content_len;
    while (remaining) {
        if (ota_now() >= io_deadline(io)) { status = "408 Request Timeout"; error = "Firmware upload timed out"; goto done; }
        size_t count = remaining < sizeof(chunk) ? remaining : sizeof(chunk);
        int received = httpd_req_recv(request, (char *)chunk, count);
        if (received == HTTPD_SOCK_ERR_TIMEOUT) { vTaskDelay(1); continue; }
        if (received <= 0 || (size_t)received > count) { error = "Firmware connection interrupted"; goto done; }
        if (ota_now() >= io_deadline(io)) { status = "408 Request Timeout"; error = "Firmware upload timed out"; goto done; }
        if (!native_ota_form_feed(&io->form, chunk, (size_t)received)) goto done;
        // Synchronous maintenance/flash processing is not a silent sender.
        // It resets only the idle clock; it cannot extend the overall budget.
        io->last_data = ota_now();
        if (io->last_data >= deadline) { status = "408 Request Timeout"; error = "Firmware upload timed out"; goto done; }
        remaining -= (size_t)received;
        vTaskDelay(1);
    }
    if (!native_ota_form_finish(&io->form)) goto done;
    if (ota_now() >= deadline) { status = "408 Request Timeout"; error = "Firmware verification timed out"; goto done; }
    if (!native_ota_form_activate(&io->form)) goto done;
    activated = true;
done:
    if (io && !activated) {
        if (io->form.error) error = io->form.error;
        native_ota_form_abort(&io->form);
    }
    if (!activated) (void)httpd_resp_set_status(request, status);
    if (io) { io->responding = true; io->response_deadline = ota_now() + 1000000U; }
    esp_err_t response = httpd_resp_sendstr(request, activated ? "OK" : error);
    bool graceful = response == ESP_OK && (!io || !io->fatal);
    if (!activated && graceful) drain_rejection(request);
    native_web_transport_shutdown(request->handle, socket, graceful);
    if (attached) httpd_sess_set_ctx(request->handle, socket, NULL, NULL); // SDK frees the request workspace
    else free(io);
    config->finish(config->context, activated);
    return ESP_FAIL;
}

esp_err_t native_ota_http_info(httpd_req_t *request, size_t image_limit) {
    const esp_partition_t *running = esp_ota_get_running_partition();
    const esp_partition_t *next = running ? esp_ota_get_next_update_partition(running) : NULL;
    const esp_app_desc_t *app = esp_app_get_description();
    size_t maximum = next ? next->size : 0;
    if (maximum > image_limit) maximum = image_limit;
    char version[sizeof(app->version) + 1], label[sizeof(running->label) + 1], hash[65], body[512], number[32];
    memcpy(version, app->version, sizeof(app->version)); version[sizeof(app->version)] = 0;
    memset(label, 0, sizeof(label)); if (running) memcpy(label, running->label, sizeof(running->label));
    for (size_t i = 0; i < sizeof(app->app_elf_sha256); ++i) snprintf(hash + 2U*i, 3, "%02x", app->app_elf_sha256[i]);
    json_buffer_t output; json_buffer_init(&output, body, sizeof(body));
    json_buffer_raw(&output, "{\"version\":"); json_buffer_string(&output, version);
    json_buffer_raw(&output, ",\"partition\":"); json_buffer_string(&output, label);
    snprintf(number, sizeof(number), "%lu", (unsigned long)maximum);
    json_buffer_raw(&output, ",\"max_size\":"); json_buffer_raw(&output, number);
    size_t body_limit = maximum && maximum <= SIZE_MAX - NATIVE_OTA_BODY_OVERHEAD ? maximum + NATIVE_OTA_BODY_OVERHEAD : 0;
    snprintf(number, sizeof(number), "%lu", (unsigned long)body_limit);
    json_buffer_raw(&output, ",\"max_body_size\":"); json_buffer_raw(&output, number);
    json_buffer_raw(&output, ",\"app_elf_sha256\":"); json_buffer_string(&output, hash); json_buffer_raw(&output, "}");
    if (output.failed) return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR, "OTA metadata unavailable");
    httpd_resp_set_type(request, "application/json"); httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}
