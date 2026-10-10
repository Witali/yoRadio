#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "tls_path_profile.h"
#include "stream_http_reader.h"
#include "mbedtls/ssl.h"
#include "esp_tls_errors.h"
#include "aes/esp_aes.h"
#include "aes/esp_aes_gcm.h"
#include "esp_transport.h"

int __wrap_esp_transport_poll_read(esp_transport_handle_t, int);
int __wrap_esp_aes_gcm_auth_decrypt(esp_gcm_context *, size_t,
    const unsigned char *, size_t, const unsigned char *, size_t,
    const unsigned char *, size_t, const unsigned char *, unsigned char *);
int __wrap_esp_aes_crypt_ctr(esp_aes_context *, size_t, size_t *,
    unsigned char [16], unsigned char [16], const unsigned char *, unsigned char *);

static int64_t clock_us;
static const char *task_name = "radio_stream";
static int critical_depth, closes, rows, tls_result, http_result, poll_result, crypto_result;
static int last_tls_code, last_tls_error;
static esp_gcm_context gcm;
static esp_aes_context aes;
static mbedtls_ssl_context ssl;
static unsigned char iv[16], aad[16], tag[16], input[16], output[16], counter[16], stream[16];
static size_t offset;
static esp_http_client_handle_t client = (esp_http_client_handle_t)&ssl;
static esp_transport_handle_t transport = (esp_transport_handle_t)&ssl;
static unsigned char buffer[32];

int64_t esp_timer_get_time(void) { return clock_us; }
const char *pcTaskGetName(void *task) { assert(task == NULL); return task_name; }
void test_enter(void *lock) { assert(lock); assert(critical_depth++ == 0); }
void test_exit(void *lock) { assert(lock); assert(--critical_depth == 0); }
void test_log(const char *name, const char *format, ...) {
    assert(critical_depth == 0);
    assert(strcmp(name, "tls_path") == 0);
    va_list args;
    va_start(args, format);
    char line[512];
    vsnprintf(line, sizeof(line), format, args);
    va_end(args);
    assert(strstr(line, "PERF TLS_PATH: seq=1 "));
    ++rows;
}

int __real_esp_transport_poll_read(esp_transport_handle_t handle, int timeout) {
    assert(handle == transport); assert(timeout == 17);
    clock_us += 20;
    return poll_result;
}
int __real_esp_aes_crypt_ctr(esp_aes_context *ctx, size_t length, size_t *off,
    unsigned char nc[16], unsigned char sb[16], const unsigned char *in, unsigned char *out) {
    assert(ctx == &aes && length == 16 && off == &offset && nc == counter && sb == stream);
    assert(in == input && out == output);
    *off = 7; nc[0] = 8; sb[0] = 9; out[0] = 10;
    clock_us += 30;
    return crypto_result;
}
int __real_esp_aes_gcm_auth_decrypt(esp_gcm_context *ctx, size_t length,
    const unsigned char *v, size_t vlen, const unsigned char *a, size_t alen,
    const unsigned char *t, size_t tlen, const unsigned char *in, unsigned char *out) {
    assert(ctx == &gcm && length == 16 && v == iv && vlen == 12 && a == aad && alen == 13);
    assert(t == tag && tlen == 16 && in == input && out == output);
    clock_us += 40;
    assert(__wrap_esp_aes_crypt_ctr(&aes, 16, &offset, counter, stream, input, output) == crypto_result);
    // Simulate the real implementation's authenticated-output handling.
    if (crypto_result) memset(out, 0, length);
    return crypto_result;
}
int mbedtls_ssl_read(mbedtls_ssl_context *ctx, unsigned char *buf, size_t length) {
    assert(ctx == &ssl && buf == buffer && (length == 32 || length == 0));
    if (tls_result > 0) {
        assert(__wrap_esp_aes_gcm_auth_decrypt(&gcm, 16, iv, 12, aad, 13, tag, 16, input, output) == 0);
        buf[0] = 42;
    }
    clock_us += 10;
    return tls_result;
}
int esp_http_client_read(esp_http_client_handle_t handle, char *buf, int length) {
    assert(handle == client && (unsigned char *)buf == buffer && length == 32);
    __wrap_esp_transport_poll_read(transport, 17);
    yoradio_mbedtls_ssl_read(&ssl, buffer, 32);
    clock_us += 5;
    return http_result;
}
esp_err_t esp_http_client_close(esp_http_client_handle_t handle) {
    assert(handle == client); ++closes; return ESP_OK;
}
esp_err_t esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t handle, int *tls, int *sys) {
    assert(handle == client && sys == NULL); *tls = last_tls_code; return last_tls_error;
}

static void run_http(int result, int tls, int poll) {
    stream_http_reader_t reader = {0};
    http_result = result; tls_result = tls; poll_result = poll;
    assert(stream_http_read(&reader, client, (char *)buffer, 32) == result);
}
int main(void) {
    tls_path_sample_t s[TLS_PATH_STAGE_COUNT], before[TLS_PATH_STAGE_COUNT];
    run_http(16, 16, 1);
    assert(buffer[0] == 42 && output[0] == 10 && offset == 7 && counter[0] == 8 && stream[0] == 9);
    tls_path_profile_snapshot(s);
    assert(s[TLS_PATH_HTTP_READ].elapsed_us == 105);
    assert(s[TLS_PATH_TLS_READ].elapsed_us == 80);
    assert(s[TLS_PATH_GCM_DECRYPT].elapsed_us == 70);
    assert(s[TLS_PATH_AES_CTR].elapsed_us == 30);
    assert(s[TLS_PATH_POLL_READ].elapsed_us == 20);
    for (unsigned i = 0; i < TLS_PATH_STAGE_COUNT; ++i) {
        assert(s[i].calls == 1 && s[i].ok == 1 && s[i].errors == 0);
        assert(s[i].completed_bytes == (i == TLS_PATH_POLL_READ ? 0 : 16));
    }
    run_http(-ESP_ERR_HTTP_EAGAIN, MBEDTLS_ERR_SSL_WANT_READ, 0);
    run_http(-ESP_ERR_HTTP_EAGAIN, MBEDTLS_ERR_SSL_WANT_WRITE, 0);
    run_http(-ESP_ERR_HTTP_EAGAIN, MBEDTLS_ERR_SSL_TIMEOUT, 0);
    run_http(0, 0, 0);
    tls_result = 0;
    assert(yoradio_mbedtls_ssl_read(&ssl, buffer, 32) == MBEDTLS_ERR_SSL_CONN_EOF);
    assert(yoradio_mbedtls_ssl_read(&ssl, buffer, 0) == 0);
    tls_result = -99;
    assert(yoradio_mbedtls_ssl_read(&ssl, buffer, 32) == -99);
    poll_result = -5;
    assert(__wrap_esp_transport_poll_read(transport, 17) == -5);
    crypto_result = -77;
    assert(__wrap_esp_aes_gcm_auth_decrypt(&gcm, 16, iv, 12, aad, 13, tag, 16, input, output) == -77);
    for (unsigned i = 0; i < 16; ++i) assert(output[i] == 0);
    crypto_result = 0;
    tls_path_profile_snapshot(s);
    assert(s[TLS_PATH_HTTP_READ].retry == 3 && s[TLS_PATH_HTTP_READ].zero == 1);
    assert(s[TLS_PATH_TLS_READ].retry == 3 && s[TLS_PATH_TLS_READ].zero == 3 && s[TLS_PATH_TLS_READ].errors == 1);
    assert(s[TLS_PATH_GCM_DECRYPT].errors == 1 && s[TLS_PATH_GCM_DECRYPT].completed_bytes == 16);
    assert(s[TLS_PATH_AES_CTR].errors == 1 && s[TLS_PATH_AES_CTR].completed_bytes == 16);
    assert(s[TLS_PATH_POLL_READ].zero == 4 && s[TLS_PATH_POLL_READ].errors == 1);
    // Fatal partial bytes remain valid, but further reads cannot reuse the connection.
    stream_http_reader_t reader = {0};
    http_result = 16; tls_result = 16; poll_result = 1;
    last_tls_error = ESP_ERR_MBEDTLS_SSL_READ_FAILED; last_tls_code = 99;
    assert(stream_http_read(&reader, client, (char *)buffer, 32) == 16 && reader.failed && closes == 1);
    tls_path_profile_snapshot(before);
    assert(stream_http_read(&reader, client, (char *)buffer, 32) == ESP_FAIL);
    tls_path_profile_snapshot(s);
    assert(memcmp(s, before, sizeof(s)) == 0);
    last_tls_error = 0;
    // Other tasks call the unchanged APIs but cannot contaminate stream metrics.
    task_name = "httpd";
    run_http(16, 16, 1);
    tls_path_profile_snapshot(s);
    assert(memcmp(s, before, sizeof(s)) == 0);
    task_name = "radio_stream";
    const size_t sizes[] = {0, 1024, 1025, 4096, 4097, 16384, 16385};
    tls_path_profile_snapshot(before);
    for (unsigned i = 0; i < sizeof(sizes)/sizeof(sizes[0]); ++i) {
        int64_t start = tls_path_profile_begin();
        clock_us += 11;
        tls_path_profile_end(TLS_PATH_AES_CTR, start, sizes[i], sizes[i], TLS_PATH_OK);
    }
    tls_path_profile_snapshot(s);
    assert(s[TLS_PATH_AES_CTR].size_le_1024 - before[TLS_PATH_AES_CTR].size_le_1024 == 2);
    assert(s[TLS_PATH_AES_CTR].size_le_4096 == 2 && s[TLS_PATH_AES_CTR].size_le_16384 == 2 && s[TLS_PATH_AES_CTR].size_larger == 1);
    // 64-bit elapsed counters survive a sample longer than the 32-bit maximum.
    int64_t start = tls_path_profile_begin();
    clock_us += (int64_t)UINT32_MAX + 8;
    tls_path_profile_end(TLS_PATH_POLL_READ, start, 0, 0, TLS_PATH_ZERO);
    tls_path_profile_snapshot(s);
    assert(s[TLS_PATH_POLL_READ].max_us == UINT32_MAX);
    assert(s[TLS_PATH_POLL_READ].elapsed_us > UINT32_MAX);
    for (unsigned i = 0; i < TLS_PATH_STAGE_COUNT; ++i) {
        assert(s[i].calls == s[i].ok + s[i].zero + s[i].retry + s[i].errors);
        assert(s[i].calls == s[i].size_le_1024 + s[i].size_le_4096 + s[i].size_le_16384 + s[i].size_larger);
    }
    tls_path_profile_poll();
    assert(rows == TLS_PATH_STAGE_COUNT && critical_depth == 0);
    puts("TLS_PATH_PROFILE_PASS nested timings, pass-through, failures, EOF/retries, task isolation, bins, 64-bit counters");
}
