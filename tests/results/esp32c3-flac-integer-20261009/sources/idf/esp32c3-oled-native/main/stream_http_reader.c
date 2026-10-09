#include "stream_http_reader.h"
#include "tls_path_profile.h"
#include <stddef.h>
#include "esp_tls_errors.h"

int stream_http_read(stream_http_reader_t *reader, esp_http_client_handle_t client,
                     char *buffer, int length) {
    if (reader->failed) return ESP_FAIL;
    int64_t start = tls_path_profile_begin();
    int received = esp_http_client_read(client, buffer, length);
    tls_path_profile_end(TLS_PATH_HTTP_READ, start, length > 0 ? (size_t)length : 0,
        received > 0 ? (size_t)received : 0, received > 0 ? TLS_PATH_OK :
        received == 0 ? TLS_PATH_ZERO : received == -ESP_ERR_HTTP_EAGAIN ? TLS_PATH_RETRY : TLS_PATH_ERROR);
    int tls_code = 0;
    esp_err_t error = esp_http_client_get_and_clear_last_tls_error(client, &tls_code, NULL);
    // ESP-TLS records -ret (a positive mbedTLS error code). Its timeout path
    // also records SSL_READ_FAILED, so checking only the ESP error is wrong.
    bool retryable_tls = tls_code == -ESP_TLS_ERR_SSL_TIMEOUT ||
                         tls_code == -ESP_TLS_ERR_SSL_WANT_READ ||
                         tls_code == -ESP_TLS_ERR_SSL_WANT_WRITE;
    bool fatal_tls = error == ESP_ERR_MBEDTLS_SSL_READ_FAILED && !retryable_tls;
    if (fatal_tls || (received < 0 && received != -ESP_ERR_HTTP_EAGAIN)) {
        reader->failed = true;
        // RFC 5246 section 7.2.2 / RFC 8446 section 6.2: do not read a
        // fatally failed TLS connection again. Close before the caller can
        // block on its audio queue; already authenticated bytes remain valid.
        esp_http_client_close(client);
        if (received <= 0) return ESP_FAIL;
    }
    return received;
}
