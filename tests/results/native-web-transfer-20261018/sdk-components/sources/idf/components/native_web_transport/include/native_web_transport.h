#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <sys/types.h>

#include "esp_err.h"
#include "esp_http_server.h"

#define NATIVE_WEB_TLS_CERT_MAX 8192U
#define NATIVE_WEB_TLS_KEY_MAX 4096U
#define NATIVE_WEB_TLS_BUNDLE_HEADER 16U
#define NATIVE_WEB_TLS_BUNDLE_MAX (NATIVE_WEB_TLS_BUNDLE_HEADER + NATIVE_WEB_TLS_CERT_MAX + NATIVE_WEB_TLS_KEY_MAX)

// One listener only. Absence of web_tls/bundle selects maintenance HTTP;
// malformed bundles fail closed. NTLS v1 header (little endian): magic[4],
// version16=1, mode16=0(maintenance) or1(TLS), cert_bytes32,key_bytes32;
// followed by exact PEM bytes, without terminators. No keys enter firmware.
// Secure mode preserves task priority/core, selects443,3clients,10240stack.
esp_err_t native_web_transport_prepare(httpd_config_t *config);
bool native_web_transport_secure(void);

// Call only after httpd_stop has joined, or after httpd_start failed. Refuses
// while sessions remain. Wipes credential memory; does not erase provisioning.
esp_err_t native_web_transport_release(void);

// Trusted local provisioning API, not an HTTP endpoint. Validates a complete
// matching cert/key pair before replacing one NVS blob for next startup.
esp_err_t native_web_transport_provision(const void *bundle, size_t size);

// One nonblocking plaintext/TLS operation. Retry returns -1/EAGAIN and reports
// actual readiness direction (a TLS read can require writable and vice versa).
// Never issue raw socket application I/O on a TLS session. MSG_PEEK returns a
// bounded prefix (up to128 plaintext bytes) without consuming it.
ssize_t native_web_transport_send(httpd_handle_t server, int socket,
    const void *data, size_t size, int flags, bool *wait_write);
ssize_t native_web_transport_recv(httpd_handle_t server, int socket,
    void *data, size_t size, int flags, bool *wait_write);

// HTTPD owns final close/free. Clean protocol Close attempts bounded TLS
// close_notify before shutdown; fatal transport errors use graceful=false.
void native_web_transport_shutdown(httpd_handle_t server, int socket, bool graceful);
