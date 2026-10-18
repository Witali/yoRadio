#include "stubs.h"



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

// Terminal HTTP handler path: bounded TLS close_notify/mark only, without a
// socket shutdown or close. Caller must return failure so HTTPD deletes the
// session. This permits committing a reserved reboot before SDK TCP cleanup,
// whose synchronous FIN allocation can wait even on a nonblocking socket.
void native_web_transport_prepare_close(httpd_handle_t server, int socket, bool graceful);

// HTTPD owns final close/free. Clean protocol Close attempts bounded TLS
// close_notify before shutdown; fatal transport errors use graceful=false.
void native_web_transport_shutdown(httpd_handle_t server, int socket, bool graceful);




#if !CONFIG_ESP_TLS_USING_MBEDTLS || !CONFIG_MBEDTLS_TLS_SERVER
#error "Native WSS transport requires the pinned mbedTLS server backend"
#endif

#define TLS_CLIENTS 3U
#define TLS_HANDSHAKE_US 3000000ULL
#define TLS_IO_US 1000000ULL
#define TLS_CLOSE_US 200000ULL
#define TLS_LOOKAHEAD 128U

typedef struct {
    httpd_handle_t server;
    int socket;
    esp_tls_t *tls;
    bool aborted, shutdown_requested, close_alert_sent;
    size_t peek_size;
    uint8_t peek[TLS_LOOKAHEAD];
} tls_session_t;

static _Atomic(tls_session_t *) s_sessions[TLS_CLIENTS];
static atomic_bool s_prepared, s_secure;
static uint8_t *s_bundle;
static size_t s_bundle_size;
static esp_tls_cfg_server_t s_config;

static void wipe(void *data, size_t size) {
    volatile uint8_t *bytes = data;
    while (size--) *bytes++ = 0;
}

static uint32_t get_u32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8U |
        (uint32_t)p[2] << 16U | (uint32_t)p[3] << 24U;
}

static esp_err_t decode_bundle(uint8_t *bundle, size_t size,
                               bool *secure, esp_tls_cfg_server_t *config) {
    if (size < NATIVE_WEB_TLS_BUNDLE_HEADER || memcmp(bundle, "NTLS", 4) ||
        bundle[4] != 1 || bundle[5] || bundle[7] || bundle[6] > 1)
        return ESP_ERR_INVALID_ARG;
    size_t cert_size = get_u32(bundle + 8), key_size = get_u32(bundle + 12);
    if (cert_size > NATIVE_WEB_TLS_CERT_MAX || key_size > NATIVE_WEB_TLS_KEY_MAX ||
        size != NATIVE_WEB_TLS_BUNDLE_HEADER + cert_size + key_size)
        return ESP_ERR_INVALID_SIZE;
    *secure = bundle[6] == 1;
    memset(config, 0, sizeof(*config));
    if (!*secure) return cert_size || key_size ? ESP_ERR_INVALID_ARG : ESP_OK;
    if (!cert_size || !key_size) return ESP_ERR_INVALID_ARG;
    uint8_t *certificate = bundle + NATIVE_WEB_TLS_BUNDLE_HEADER;
    uint8_t *key = certificate + cert_size;
    if (memchr(certificate, 0, cert_size) || memchr(key, 0, key_size))
        return ESP_ERR_INVALID_ARG;
    // The allocation has two extra bytes. Keep one owner while constructing
    // separate NUL-terminated PEM views, without another private-key copy.
    memmove(key + 1, key, key_size);
    certificate[cert_size] = 0;
    key += 1;
    key[key_size] = 0;
    if (psa_crypto_init() != PSA_SUCCESS) return ESP_FAIL;
    mbedtls_x509_crt chain;
    mbedtls_pk_context private_key;
    mbedtls_x509_crt_init(&chain);
    mbedtls_pk_init(&private_key);
    int result = mbedtls_x509_crt_parse(&chain, certificate, cert_size + 1U);
    if (!result) result = mbedtls_pk_parse_key(&private_key, key, key_size + 1U, NULL, 0);
    if (!result) result = mbedtls_pk_check_pair(&chain.pk, &private_key);
    mbedtls_pk_free(&private_key);
    mbedtls_x509_crt_free(&chain);
    if (result) return ESP_ERR_INVALID_ARG;
    config->servercert_buf = certificate;
    config->servercert_bytes = (unsigned)(cert_size + 1U);
    config->serverkey_buf = key;
    config->serverkey_bytes = (unsigned)(key_size + 1U);
    config->tls_version = ESP_TLS_VER_TLS_1_2;
    return ESP_OK;
}

esp_err_t native_web_transport_provision(const void *bundle, size_t size) {
    if (!bundle || size > NATIVE_WEB_TLS_BUNDLE_MAX) return ESP_ERR_INVALID_SIZE;
    uint8_t *copy = malloc(size + 2U);
    if (!copy) return ESP_ERR_NO_MEM;
    memcpy(copy, bundle, size);
    bool secure;
    esp_tls_cfg_server_t config;
    esp_err_t result = decode_bundle(copy, size, &secure, &config);
    wipe(copy, size + 2U);
    free(copy);
    if (result != ESP_OK) return result;
    nvs_handle_t handle;
    result = nvs_open("web_tls", NVS_READWRITE, &handle);
    if (result != ESP_OK) return result;
    result = nvs_set_blob(handle, "bundle", bundle, size);
    if (result == ESP_OK) result = nvs_commit(handle);
    nvs_close(handle);
    return result;
}

static tls_session_t *session(httpd_handle_t server, int socket) {
    if (!atomic_load(&s_secure)) return NULL;
    void *context = httpd_sess_get_transport_ctx(server, socket);
    for (size_t i = 0; i < TLS_CLIENTS; ++i) {
        tls_session_t *current = atomic_load(&s_sessions[i]);
        if (current && context == current && current->server == server && current->socket == socket)
            return current;
    }
    return NULL;
}

static int wait_ready(int socket, bool writable, uint64_t start, uint64_t budget) {
    uint64_t elapsed = (uint64_t)esp_timer_get_time() - start;
    if (elapsed >= budget || socket < 0 || socket >= FD_SETSIZE) return HTTPD_SOCK_ERR_TIMEOUT;
    uint64_t remaining = budget - elapsed;
    struct timeval timeout = {.tv_sec = (long)(remaining / 1000000ULL),
        .tv_usec = (long)(remaining % 1000000ULL)};
    fd_set ready;
    FD_ZERO(&ready);
    FD_SET(socket, &ready);
    int result = lwip_select(socket + 1, writable ? NULL : &ready,
                            writable ? &ready : NULL, NULL, &timeout);
    if (!result) return HTTPD_SOCK_ERR_TIMEOUT;
    if (result < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
    vTaskDelay(1);
    return ESP_OK;
}

static ssize_t tls_result(tls_session_t *context, ssize_t result, bool *writable) {
    if (result >= 0) return result;
    if (result == ESP_TLS_ERR_SSL_WANT_READ || result == ESP_TLS_ERR_SSL_WANT_WRITE) {
        *writable = result == ESP_TLS_ERR_SSL_WANT_WRITE;
        errno = EAGAIN;
    } else {
        context->aborted = true;
        errno = EIO;
    }
    return -1;
}

static int failed_io(httpd_handle_t server, int socket, int result) {
    tls_session_t *context = session(server, socket);
    if (context) context->aborted = true;
    return result;
}

ssize_t native_web_transport_send(httpd_handle_t server, int socket,
        const void *data, size_t size, int flags, bool *wait_write) {
    if (!wait_write || (!data && size)) { errno = EINVAL; return -1; }
    *wait_write = true;
    if (!atomic_load(&s_secure)) return lwip_send(socket, data, size, flags | MSG_DONTWAIT);
    tls_session_t *context = session(server, socket);
    if (!context || !context->tls || context->aborted || context->shutdown_requested ||
        flags & ~MSG_DONTWAIT) { errno = EIO; return -1; }
    if (!size) return 0;
    return tls_result(context, esp_tls_conn_write(context->tls, data, size), wait_write);
}

ssize_t native_web_transport_recv(httpd_handle_t server, int socket,
        void *data, size_t size, int flags, bool *wait_write) {
    if (!wait_write || (!data && size)) { errno = EINVAL; return -1; }
    *wait_write = false;
    if (!atomic_load(&s_secure)) return lwip_recv(socket, data, size, flags | MSG_DONTWAIT);
    tls_session_t *context = session(server, socket);
    if (!context || !context->tls || context->aborted || context->shutdown_requested ||
        flags & ~(MSG_DONTWAIT | MSG_PEEK)) { errno = EIO; return -1; }
    if (!size) return 0;
    if (context->peek_size) {
        size_t available = size < context->peek_size ? size : context->peek_size;
        memcpy(data, context->peek, available);
        if (!(flags & MSG_PEEK)) {
            context->peek_size -= available;
            memmove(context->peek, context->peek + available, context->peek_size);
        }
        return (ssize_t)available;
    }
    if (flags & MSG_PEEK) {
        size_t capacity = size < sizeof(context->peek) ? size : sizeof(context->peek);
        ssize_t count = tls_result(context, esp_tls_conn_read(context->tls, context->peek, capacity), wait_write);
        if (count > 0) {
            if ((size_t)count > capacity) { context->aborted = true; errno = EIO; return -1; }
            context->peek_size = (size_t)count;
            memcpy(data, context->peek, context->peek_size);
        }
        return count;
    }
    return tls_result(context, esp_tls_conn_read(context->tls, data, size), wait_write);
}

static int httpd_send_tls(httpd_handle_t server, int socket,
                           const char *data, size_t size, int flags) {
    if (size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    uint64_t started = (uint64_t)esp_timer_get_time();
    size_t written = 0;
    while (written < size) {
        if ((uint64_t)esp_timer_get_time() - started >= TLS_IO_US)
            return failed_io(server, socket, HTTPD_SOCK_ERR_TIMEOUT);
        bool writable;
        ssize_t count = native_web_transport_send(server, socket, data + written, size - written, flags, &writable);
        if (count > 0) {
            if ((size_t)count > size - written) return failed_io(server, socket, HTTPD_SOCK_ERR_FAIL);
            written += (size_t)count;
        } else if (count < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)) {
            int result = wait_ready(socket, writable, started, TLS_IO_US);
            if (result != ESP_OK) return failed_io(server, socket, result);
        } else return failed_io(server, socket, HTTPD_SOCK_ERR_FAIL);
    }
    return (uint64_t)esp_timer_get_time() - started >= TLS_IO_US ?
        failed_io(server, socket, HTTPD_SOCK_ERR_TIMEOUT) : (int)written;
}

static int httpd_recv_tls(httpd_handle_t server, int socket,
                           char *data, size_t size, int flags) {
    if (size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    uint64_t started = (uint64_t)esp_timer_get_time();
    while ((uint64_t)esp_timer_get_time() - started < TLS_IO_US) {
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket, data, size, flags, &writable);
        if (count >= 0) return (uint64_t)esp_timer_get_time() - started >= TLS_IO_US ?
            failed_io(server, socket, HTTPD_SOCK_ERR_TIMEOUT) : (int)count;
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR)
            return failed_io(server, socket, HTTPD_SOCK_ERR_FAIL);
        int result = wait_ready(socket, writable, started, TLS_IO_US);
        if (result != ESP_OK) return failed_io(server, socket, result);
    }
    return failed_io(server, socket, HTTPD_SOCK_ERR_TIMEOUT);
}

static int httpd_pending_tls(httpd_handle_t server, int socket) {
    tls_session_t *context = session(server, socket);
    if (!context || !context->tls || context->aborted) return -1;
    if (context->peek_size) return (int)context->peek_size;
    ssize_t count = esp_tls_get_bytes_avail(context->tls);
    return count < 0 ? -1 : count > INT_MAX ? INT_MAX : (int)count;
}

static void tls_free(void *opaque) {
    tls_session_t *context = opaque;
    for (size_t i = 0; i < TLS_CLIENTS; ++i) {
        tls_session_t *expected = context;
        (void)atomic_compare_exchange_strong(&s_sessions[i], &expected, NULL);
    }
    if (false) esp_tls_server_session_delete(context->tls);
    wipe(context, sizeof(*context));
    free(context);
}

static void close_alert(tls_session_t *context) {
    if (!context->tls || context->aborted || context->close_alert_sent || context->shutdown_requested) return;
    mbedtls_ssl_context *ssl = esp_tls_get_ssl_context(context->tls);
    if (!ssl) return;
    uint64_t started = (uint64_t)esp_timer_get_time();
    while ((uint64_t)esp_timer_get_time() - started < TLS_CLOSE_US) {
        int result = mbedtls_ssl_close_notify(ssl);
        if (!result) { context->close_alert_sent = true; return; }
        if (result != ESP_TLS_ERR_SSL_WANT_READ && result != ESP_TLS_ERR_SSL_WANT_WRITE) return;
        if (wait_ready(context->socket, result == ESP_TLS_ERR_SSL_WANT_WRITE,
                       started, TLS_CLOSE_US) != ESP_OK) return;
    }
}

void native_web_transport_prepare_close(httpd_handle_t server, int socket, bool graceful) {
    tls_session_t *context = session(server, socket);
    if (context) {
        if (graceful) close_alert(context);
        else context->aborted = true;
        context->shutdown_requested = true;
    }
}

void native_web_transport_shutdown(httpd_handle_t server, int socket, bool graceful) {
    native_web_transport_prepare_close(server, socket, graceful);
    (void)shutdown(socket, SHUT_RDWR);
}

static void httpd_close_tls(httpd_handle_t server, int socket) {
    tls_session_t *context = session(server, socket);
    if (context) close_alert(context);
    (void)lwip_close(socket);
}

static esp_err_t httpd_open_tls(httpd_handle_t server, int socket) {
    if (!atomic_load(&s_prepared) || !atomic_load(&s_secure) || socket < 0 ||
        socket >= FD_SETSIZE || httpd_sess_get_transport_ctx(server, socket)) return ESP_ERR_INVALID_STATE;
    tls_session_t *context = calloc(1, sizeof(*context));
    if (!context) return ESP_ERR_NO_MEM;
    context->server = server;
    context->socket = socket;
    bool reserved = false;
    for (size_t i = 0; i < TLS_CLIENTS; ++i) {
        tls_session_t *expected = NULL;
        if (atomic_compare_exchange_strong(&s_sessions[i], &expected, context)) { reserved = true; break; }
    }
    if (!reserved) { free(context); return ESP_ERR_NO_MEM; }
    httpd_sess_set_transport_ctx(server, socket, context, tls_free);
    if (httpd_sess_get_transport_ctx(server, socket) != context) { tls_free(context); return ESP_FAIL; }
    // HTTPD owns the fd before open_fn and deletes it on every failed return.
    // Register context ownership before anything else can allocate/fail.
    context->aborted = true;
    uint64_t started = (uint64_t)esp_timer_get_time();
    int flags = fcntl(socket, F_GETFL, 0);
    if (flags < 0 || fcntl(socket, F_SETFL, flags | O_NONBLOCK) < 0) return ESP_FAIL;
    context->tls = esp_tls_init();
    if (!context->tls) return ESP_ERR_NO_MEM;
    if (esp_tls_server_session_init(&s_config, socket, context->tls) != ESP_OK) return ESP_FAIL;
    while ((uint64_t)esp_timer_get_time() - started < TLS_HANDSHAKE_US) {
        int result = esp_tls_server_session_continue_async(context->tls);
        if ((uint64_t)esp_timer_get_time() - started >= TLS_HANDSHAKE_US) return ESP_ERR_TIMEOUT;
        if (!result) {
            if (esp_tls_set_conn_state(context->tls, ESP_TLS_DONE) != ESP_OK) return ESP_FAIL;
            context->aborted = false;
            if (httpd_sess_set_send_override(server, socket, httpd_send_tls) != ESP_OK ||
                httpd_sess_set_recv_override(server, socket, httpd_recv_tls) != ESP_OK ||
                httpd_sess_set_pending_override(server, socket, httpd_pending_tls) != ESP_OK) {
                context->aborted = true;
                return ESP_FAIL;
            }
            return ESP_OK;
        }
        if (result != ESP_TLS_ERR_SSL_WANT_READ && result != ESP_TLS_ERR_SSL_WANT_WRITE) return ESP_FAIL;
        int ready = wait_ready(socket, result == ESP_TLS_ERR_SSL_WANT_WRITE, started, TLS_HANDSHAKE_US);
        if (ready != ESP_OK) return ready == HTTPD_SOCK_ERR_TIMEOUT ? ESP_ERR_TIMEOUT : ESP_FAIL;
    }
    return ESP_ERR_TIMEOUT;
}

bool native_web_transport_secure(void) { return atomic_load(&s_secure); }

esp_err_t native_web_transport_release(void) {
    for (size_t i = 0; i < TLS_CLIENTS; ++i)
        if (atomic_load(&s_sessions[i])) return ESP_ERR_INVALID_STATE;
    atomic_store(&s_prepared, false);
    atomic_store(&s_secure, false);
    if (s_bundle) {
        wipe(s_bundle, s_bundle_size + 2U);
        free(s_bundle);
        s_bundle = NULL;
    }
    s_bundle_size = 0;
    memset(&s_config, 0, sizeof(s_config));
    return ESP_OK;
}

static esp_err_t prepare_config(httpd_config_t *config) {
    nvs_handle_t handle;
    esp_err_t result = nvs_open("web_tls", NVS_READONLY, &handle);
    if (result == ESP_ERR_NVS_NOT_FOUND) { atomic_store(&s_prepared, true); return ESP_OK; }
    if (result != ESP_OK) return result;
    size_t size = 0;
    result = nvs_get_blob(handle, "bundle", NULL, &size);
    if (result == ESP_ERR_NVS_NOT_FOUND) { nvs_close(handle); atomic_store(&s_prepared, true); return ESP_OK; }
    if (result != ESP_OK || size > NATIVE_WEB_TLS_BUNDLE_MAX) {
        nvs_close(handle);
        return result != ESP_OK ? result : ESP_ERR_INVALID_SIZE;
    }
    s_bundle = malloc(size + 2U);
    if (!s_bundle) { nvs_close(handle); return ESP_ERR_NO_MEM; }
    s_bundle_size = size;
    result = nvs_get_blob(handle, "bundle", s_bundle, &size);
    nvs_close(handle);
    bool secure = false;
    if (result == ESP_OK && size == s_bundle_size) result = decode_bundle(s_bundle, size, &secure, &s_config);
    else if (result == ESP_OK) result = ESP_ERR_INVALID_SIZE;
    if (result != ESP_OK) { (void)native_web_transport_release(); return result; }
    if (!secure) { (void)native_web_transport_release(); atomic_store(&s_prepared, true); return ESP_OK; }
    config->server_port = 443;
    config->max_open_sockets = TLS_CLIENTS;
    if (config->stack_size < 10240U) config->stack_size = 10240U;
    config->open_fn = httpd_open_tls;
    config->close_fn = httpd_close_tls;
    atomic_store(&s_secure, true);
    atomic_store(&s_prepared, true);
    return ESP_OK;
}

esp_err_t native_web_transport_prepare(httpd_config_t *config) {
    if (!config) return ESP_ERR_INVALID_ARG;
    if (config->open_fn || config->close_fn) return ESP_ERR_INVALID_STATE;
    bool expected = false;
    if (!atomic_compare_exchange_strong(&s_prepared, &expected, true)) return ESP_ERR_INVALID_STATE;
    esp_err_t result = prepare_config(config);
    if (result != ESP_OK) (void)native_web_transport_release();
    return result;
}

#include "faults.c"
