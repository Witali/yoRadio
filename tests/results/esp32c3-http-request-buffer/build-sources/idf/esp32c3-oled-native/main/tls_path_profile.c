#include "tls_path_profile.h"
#include <inttypes.h>
#include <string.h>
#include "aes/esp_aes.h"
#include "aes/esp_aes_gcm.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_transport.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static portMUX_TYPE s_lock = portMUX_INITIALIZER_UNLOCKED;
static tls_path_sample_t s_samples[TLS_PATH_STAGE_COUNT];

int64_t tls_path_profile_begin(void) {
    return strcmp(pcTaskGetName(NULL), "radio_stream") == 0 ? esp_timer_get_time() : -1;
}

void tls_path_profile_end(tls_path_stage_t stage, int64_t start,
                          size_t requested, size_t completed,
                          tls_path_outcome_t outcome) {
    if (start < 0) return;
    uint64_t elapsed = (uint64_t)(esp_timer_get_time() - start);
    portENTER_CRITICAL(&s_lock);
    tls_path_sample_t *s = &s_samples[stage];
    ++s->calls;
    s->elapsed_us += elapsed;
    s->requested_bytes += requested;
    s->completed_bytes += completed;
    uint32_t bounded = elapsed > UINT32_MAX ? UINT32_MAX : (uint32_t)elapsed;
    if (bounded > s->max_us) s->max_us = bounded;
    switch (outcome) {
        case TLS_PATH_OK: ++s->ok; break;
        case TLS_PATH_ZERO: ++s->zero; break;
        case TLS_PATH_RETRY: ++s->retry; break;
        case TLS_PATH_ERROR: ++s->errors; break;
    }
    if (requested <= 1024) ++s->size_le_1024;
    else if (requested <= 4096) ++s->size_le_4096;
    else if (requested <= 16384) ++s->size_le_16384;
    else ++s->size_larger;
    portEXIT_CRITICAL(&s_lock);
}

void tls_path_profile_snapshot(tls_path_sample_t samples[TLS_PATH_STAGE_COUNT]) {
    portENTER_CRITICAL(&s_lock);
    memcpy(samples, s_samples, sizeof(s_samples));
    portEXIT_CRITICAL(&s_lock);
}

void tls_path_profile_poll(void) {
    static uint32_t sequence;
    static const char *const names[TLS_PATH_STAGE_COUNT] = {
        "http", "tls", "poll", "gcm", "ctr"
    };
    tls_path_sample_t samples[TLS_PATH_STAGE_COUNT];
    int64_t sampled_us = esp_timer_get_time();
    tls_path_profile_snapshot(samples);
    ++sequence;
    for (unsigned i = 0; i < TLS_PATH_STAGE_COUNT; ++i) {
        const tls_path_sample_t *s = &samples[i];
        ESP_LOGI("tls_path", "PERF TLS_PATH: seq=%" PRIu32 " at_us=%" PRIi64
            " stage=%s calls=%" PRIu32 " elapsed_us=%" PRIu64 " max_us=%" PRIu32
            " requested=%" PRIu64 " completed=%" PRIu64
            " ok=%" PRIu32 " zero=%" PRIu32 " retry=%" PRIu32 " errors=%" PRIu32
            " le1024=%" PRIu32 " le4096=%" PRIu32 " le16384=%" PRIu32 " larger=%" PRIu32,
            sequence, sampled_us, names[i], s->calls, s->elapsed_us, s->max_us,
            s->requested_bytes, s->completed_bytes, s->ok, s->zero, s->retry, s->errors,
            s->size_le_1024, s->size_le_4096, s->size_le_16384, s->size_larger);
    }
}

int __real_esp_transport_poll_read(esp_transport_handle_t transport, int timeout_ms);
int __wrap_esp_transport_poll_read(esp_transport_handle_t transport, int timeout_ms) {
    int64_t start = tls_path_profile_begin();
    int result = __real_esp_transport_poll_read(transport, timeout_ms);
    // Poll has no byte request. Zero means no socket readiness before timeout.
    tls_path_profile_end(TLS_PATH_POLL_READ, start, 0, 0,
        result > 0 ? TLS_PATH_OK : result == 0 ? TLS_PATH_ZERO : TLS_PATH_ERROR);
    return result;
}

int __real_esp_aes_gcm_auth_decrypt(esp_gcm_context *ctx, size_t length,
    const unsigned char *iv, size_t iv_len, const unsigned char *aad, size_t aad_len,
    const unsigned char *tag, size_t tag_len, const unsigned char *input, unsigned char *output);
int __wrap_esp_aes_gcm_auth_decrypt(esp_gcm_context *ctx, size_t length,
    const unsigned char *iv, size_t iv_len, const unsigned char *aad, size_t aad_len,
    const unsigned char *tag, size_t tag_len, const unsigned char *input, unsigned char *output) {
    int64_t start = tls_path_profile_begin();
    int result = __real_esp_aes_gcm_auth_decrypt(ctx, length, iv, iv_len, aad, aad_len,
                                             tag, tag_len, input, output);
    tls_path_profile_end(TLS_PATH_GCM_DECRYPT, start, length, result == 0 ? length : 0,
                         result == 0 ? TLS_PATH_OK : TLS_PATH_ERROR);
    return result;
}

int __real_esp_aes_crypt_ctr(esp_aes_context *ctx, size_t length, size_t *nc_off,
    unsigned char nonce_counter[16], unsigned char stream_block[16],
    const unsigned char *input, unsigned char *output);
int __wrap_esp_aes_crypt_ctr(esp_aes_context *ctx, size_t length, size_t *nc_off,
    unsigned char nonce_counter[16], unsigned char stream_block[16],
    const unsigned char *input, unsigned char *output) {
    int64_t start = tls_path_profile_begin();
    int result = __real_esp_aes_crypt_ctr(ctx, length, nc_off, nonce_counter,
                                      stream_block, input, output);
    tls_path_profile_end(TLS_PATH_AES_CTR, start, length, result == 0 ? length : 0,
                         result == 0 ? TLS_PATH_OK : TLS_PATH_ERROR);
    return result;
}
