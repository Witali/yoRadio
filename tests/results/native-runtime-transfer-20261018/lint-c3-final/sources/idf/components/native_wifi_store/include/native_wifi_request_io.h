#pragma once

#include "esp_http_server.h"
#include <stdbool.h>
#include <stdint.h>

typedef struct native_wifi_request_io native_wifi_request_io_t;

// HTTPD-handler task only. Rejects an existing session owner; never restores or
// retains foreign override pointers. ALWAYS consumes payload using dispose (if
// non-NULL), including allocation/attachment failure. On success SDK teardown
// owns the small I/O context AND payload; dispose must wipe any secret workspace.
// Partial override installation is terminal: call close and return ESP_FAIL.
native_wifi_request_io_t *native_wifi_request_io_open(httpd_req_t *request,
    uint64_t idle_us, uint64_t overall_us, void *payload, void (*dispose)(void *));
bool native_wifi_request_io_expired(const native_wifi_request_io_t *io);
// After bounded application processing, refresh only idle time; overall remains
// absolute. False means overall elapsed or this request does not own the I/O.
bool native_wifi_request_io_progress(httpd_req_t *request);
void native_wifi_request_io_response(native_wifi_request_io_t *io);
// Optional rejection drain <=250ms, TLS close preparation, then detach owned
// context. Overrides remain terminal; the caller MUST return ESP_FAIL so SDK
// performs final socket deletion without body purge. Never calls raw shutdown.
void native_wifi_request_io_close(httpd_req_t *request,
    native_wifi_request_io_t *io, bool response_ok, bool drain_rejected);
