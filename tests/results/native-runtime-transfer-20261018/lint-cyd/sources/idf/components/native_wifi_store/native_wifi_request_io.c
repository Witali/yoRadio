#include "native_wifi_request_io.h"

#include <errno.h>
#include <limits.h>
#include <stdlib.h>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "native_web_transport.h"
#include "native_wifi_store.h"

struct native_wifi_request_io {
    httpd_handle_t server;
    int socket;
    uint64_t started, last_data, idle_us, overall_us, response_deadline;
    bool responding, fatal;
    void *payload;
    void (*dispose)(void *);
};

static uint64_t io_now(void) { return (uint64_t)esp_timer_get_time(); }
static uint64_t io_deadline(const native_wifi_request_io_t *io) {
    if (io->responding) return io->response_deadline;
    uint64_t idle = io->last_data + io->idle_us, total = io->started + io->overall_us;
    return idle < total ? idle : total;
}
static void io_free(void *opaque) {
    native_wifi_request_io_t *io = opaque;
    if (!io) return;
    if (io->dispose) io->dispose(io->payload);
    native_wifi_erase(io, sizeof(*io)); free(io);
}
static int io_wait(int socket, bool writable, uint64_t until) {
    uint64_t now = io_now();
    if (now >= until || socket < 0 || socket >= FD_SETSIZE) return HTTPD_SOCK_ERR_TIMEOUT;
    uint64_t remaining = until - now;
    struct timeval timeout = {.tv_sec=(long)(remaining / 1000000U), .tv_usec=(long)(remaining % 1000000U)};
    fd_set set; FD_ZERO(&set); FD_SET(socket, &set);
    int result = lwip_select(socket + 1, writable ? NULL : &set, writable ? &set : NULL, NULL, &timeout);
    if (!result) return HTTPD_SOCK_ERR_TIMEOUT;
    if (result < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
    vTaskDelay(1); return ESP_OK;
}
static native_wifi_request_io_t *owned_io(httpd_handle_t server, int socket) {
    native_wifi_request_io_t *io = httpd_sess_get_ctx(server, socket);
    return io && io->server == server && io->socket == socket ? io : NULL;
}
static int io_receive(httpd_handle_t server, int socket, char *data, size_t size, int flags) {
    native_wifi_request_io_t *io = owned_io(server, socket);
    if (!io || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    uint64_t until = io_deadline(io);
    while (io_now() < until) {
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket, data, size, flags | MSG_DONTWAIT, &writable);
        if (count >= 0) {
            if ((size_t)count > size) { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
            return io_now() >= until ? HTTPD_SOCK_ERR_TIMEOUT : (int)count;
        }
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
            io->fatal = true; return HTTPD_SOCK_ERR_FAIL;
        }
        int result = io_wait(socket, writable, until);
        if (result != ESP_OK) return result;
    }
    return HTTPD_SOCK_ERR_TIMEOUT;
}
static int io_send(httpd_handle_t server, int socket, const char *data, size_t size, int flags) {
    native_wifi_request_io_t *io = owned_io(server, socket);
    if (!io || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    size_t offset = 0;
    uint64_t until = io_deadline(io);
    while (offset < size && io_now() < until) {
        bool writable;
        ssize_t count = native_web_transport_send(server, socket, data + offset, size - offset,
                                                  flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - offset) { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
            offset += (size_t)count;
        } else if (count < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)) {
            int result = io_wait(socket, writable, until);
            if (result != ESP_OK) return result;
        } else { io->fatal = true; return HTTPD_SOCK_ERR_FAIL; }
    }
    return offset == size && io_now() < until ? (int)offset : HTTPD_SOCK_ERR_TIMEOUT;
}
static void io_drain(httpd_req_t *request) {
    uint64_t until = io_now() + 250000U;
    int socket = httpd_req_to_sockfd(request);
    uint8_t discard[256];
    while (io_now() < until) {
        bool writable;
        ssize_t count = native_web_transport_recv(request->handle, socket, discard, sizeof(discard), MSG_DONTWAIT, &writable);
        if (!count) break;
        if (count < 0) {
            if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) break;
            if (io_wait(socket, writable, until) != ESP_OK) break;
        } else vTaskDelay(1);
    }
    native_wifi_erase(discard, sizeof(discard));
}
native_wifi_request_io_t *native_wifi_request_io_open(httpd_req_t *request,
    uint64_t idle_us, uint64_t overall_us, void *payload, void (*dispose)(void *)) {
    uint64_t now = io_now();
    if (!request || request->sess_ctx || !idle_us || !overall_us ||
        now > UINT64_MAX - idle_us || now > UINT64_MAX - overall_us) {
        if (dispose) dispose(payload);
        return NULL;
    }
    native_wifi_request_io_t *io = calloc(1, sizeof(*io));
    if (!io) { if (dispose) dispose(payload); return NULL; }
    *io = (native_wifi_request_io_t){.server=request->handle, .socket=httpd_req_to_sockfd(request),
        .started=now, .last_data=now, .idle_us=idle_us, .overall_us=overall_us, .payload=payload, .dispose=dispose};
    httpd_sess_set_ctx(request->handle, io->socket, io, io_free);
    // sess_ctx/free_ctx are PUBLIC request fields. Within this active handler,
    // set_ctx writes them; a transient failed lookup must not cause a double free.
    if (request->sess_ctx != io) { io_free(io); return NULL; }
    if (httpd_sess_set_recv_override(request->handle, io->socket, io_receive) != ESP_OK ||
        httpd_sess_set_send_override(request->handle, io->socket, io_send) != ESP_OK) {
        httpd_sess_set_ctx(request->handle, io->socket, NULL, NULL);
        // If detach itself cannot find the session, SDK still owns io+payload
        // through public sess_ctx and will free them on terminal session cleanup.
        return NULL;
    }
    return io;
}
bool native_wifi_request_io_expired(const native_wifi_request_io_t *io) {
    return !io || io_now() >= io_deadline(io);
}
bool native_wifi_request_io_progress(httpd_req_t *request) {
    native_wifi_request_io_t *io = request ? owned_io(request->handle, httpd_req_to_sockfd(request)) : NULL;
    if (!io || io_now() - io->started >= io->overall_us) return false;
    io->last_data = io_now(); return true;
}
void native_wifi_request_io_response(native_wifi_request_io_t *io) {
    if (io) { io->responding = true; io->response_deadline = io_now() + 1000000U; }
}
void native_wifi_request_io_close(httpd_req_t *request,
    native_wifi_request_io_t *io, bool response_ok, bool drain_rejected) {
    bool graceful = response_ok && (!io || !io->fatal);
    if (drain_rejected && graceful) io_drain(request);
    int socket = httpd_req_to_sockfd(request);
    native_web_transport_prepare_close(request->handle, socket, graceful);
    if (io && request->sess_ctx == io) httpd_sess_set_ctx(request->handle, socket, NULL, NULL);
}
