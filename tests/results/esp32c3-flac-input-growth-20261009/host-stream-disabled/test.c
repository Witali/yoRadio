#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <setjmp.h>
#include "icy_title.h"
#include <stddef.h>
#include <stdint.h>

typedef enum {
    TLS_PATH_HTTP_READ,
    TLS_PATH_TLS_READ,
    TLS_PATH_POLL_READ,
    TLS_PATH_GCM_DECRYPT,
    TLS_PATH_AES_CTR,
    TLS_PATH_STAGE_COUNT
} tls_path_stage_t;

typedef enum {
    TLS_PATH_OK,
    TLS_PATH_ZERO,
    TLS_PATH_RETRY,
    TLS_PATH_ERROR
} tls_path_outcome_t;

typedef struct {
    uint64_t elapsed_us, requested_bytes, completed_bytes;
    uint32_t calls, max_us, ok, zero, retry, errors;
    uint32_t size_le_1024, size_le_4096, size_le_16384, size_larger;
} tls_path_sample_t;

#ifdef CONFIG_YORADIO_TLS_PATH_PROFILE
// Elapsed wall time includes preemption and blocking. Nested stages overlap.
// Only calls made by radio_stream are recorded; no pointers/data are retained.
int64_t tls_path_profile_begin(void);
void tls_path_profile_end(tls_path_stage_t stage, int64_t start,
                          size_t requested, size_t completed,
                          tls_path_outcome_t outcome);
void tls_path_profile_snapshot(tls_path_sample_t samples[TLS_PATH_STAGE_COUNT]);
void tls_path_profile_poll(void);
#else
static inline int64_t tls_path_profile_begin(void) { return -1; }
static inline void tls_path_profile_end(tls_path_stage_t stage, int64_t start,
                                       size_t requested, size_t completed,
                                       tls_path_outcome_t outcome) {
    (void)stage; (void)start; (void)requested; (void)completed; (void)outcome;
}
static inline void tls_path_profile_poll(void) {}
#endif

#define AUDIO_STATUS_STATION_UNAVAILABLE "station unavailable"

typedef int esp_err_t;
typedef int native_codec_t;
enum { ESP_OK=0, ESP_FAIL=-1, ESP_ERR_HTTP_CONNECT=0x7001, ESP_ERR_HTTP_WRITE_DATA,
       ESP_ERR_HTTP_EAGAIN, ESP_ERR_TIMEOUT, ESP_ERR_HTTP_FETCH_HEADER,
       ESP_ERR_HTTP_MAX_REDIRECT, ESP_ERR_HTTP_INVALID_TRANSPORT };
enum { NATIVE_CODEC_AUTO, NATIVE_CODEC_AAC, NATIVE_CODEC_FLAC, AUDIO_END_EOF,
       AUDIO_END_BUFFER_STALLED, AUDIO_END_READ_FAILED, AUDIO_END_UNAVAILABLE };
enum { ESP_ERR_MBEDTLS_SSL_READ_FAILED=0x801d,
       ESP_TLS_ERR_SSL_TIMEOUT=-0x6800, ESP_TLS_ERR_SSL_WANT_READ=-0x6900,
       ESP_TLS_ERR_SSL_WANT_WRITE=-0x6880, TEST_TLS_ALLOCATION_ERROR=141 };
enum { STREAM_CHUNK_SIZE = 2048, STREAM_READ_TIMEOUT_MS = 250,
       MAX_HTTP_REDIRECTS = 5, ICY_METADATA_MAX = 4080 };
typedef uint32_t TickType_t;
#define portMAX_DELAY UINT32_MAX
#define pdTRUE 1
#define pdMS_TO_TICKS(n) (n)
#define ESP_LOGE(tag, ...) do { if (0) printf(__VA_ARGS__); } while (0)
#define ESP_LOGW(tag, ...) ESP_LOGE(tag, __VA_ARGS__)
#define ESP_LOGI(tag, ...) ESP_LOGE(tag, __VA_ARGS__)
static atomic_uint s_generation, s_decoder_released_generation;
static void *s_commands, *s_state;
static icy_title_parser_t s_icy_title;
typedef struct { int64_t started_us; uint64_t audio_bytes; } stream_bitrate_meter_t;

typedef struct {
    uint32_t generation;
    native_codec_t requested_codec;
#ifdef YORADIO_CODEC_BENCHMARK
    uint32_t fixture_size;
#endif
    char url[512];
} play_command_t;

// Owned by stream_task. Reuse its current command/URL between attempts;
// retain no HTTP/TLS allocation while waiting.
typedef struct {
    int64_t due_us;
    int64_t deadline_us;
    uint32_t delay_ms;
    bool pending;
    uint8_t timeout_sec;
} stream_retry_t;
#define STREAM_RETRY_INITIAL_MS 1000U
#define STREAM_RETRY_MAX_MS 30000U
#define STREAM_RETRY_POLL_MS 100U

typedef struct {
    const char *url, *user_agent;
    unsigned timeout_ms, buffer_size, buffer_size_tx, max_redirection_count;
    bool disable_auto_redirect, keep_alive_enable;
    void *crt_bundle_attach;
    unsigned tls_dyn_buf_strategy;
} esp_http_client_config_t;
enum { HTTP_TLS_DYN_BUF_RX_STATIC=1 };
#define esp_crt_bundle_attach NULL
typedef struct { bool live; } fake_client_t;
typedef fake_client_t *esp_http_client_handle_t;
typedef struct {
    bool failed;
} stream_http_reader_t;
typedef struct { int result, status; bool bad_headers; } attempt_t;
static fake_client_t client;
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
static atomic_uint s_flac_input_ready_generation;
static unsigned growth_calls, finish_calls, finite_reads, read_calls, ready_on_read;
static void tls_input_reserve_expand_flac(void) {
    assert(client.live);
    assert(atomic_load(&s_flac_input_ready_generation) == atomic_load(&s_generation));
    ++growth_calls;
}
static void tls_input_reserve_finish_connection(void) {
    assert(client.live);
    ++finish_calls;
}
#endif
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
static bool input_prepared;
static void tls_input_reserve_prepare_connection(void) {
    assert(!client.live && !input_prepared);
    input_prepared = true;
}
#endif
static attempt_t attempts[16];
static unsigned attempt_count, attempt_limit, eos_count, eof_reason, close_count;
static unsigned connection_close_headers;
static int64_t now_us, attempt_times[16], event_us;
static unsigned event_kind, stop_after_attempt;
static bool watchdog, queued, init_oom, cancel_in_open;
static play_command_t queued_command;
static jmp_buf finished;
static void *input_buffer;
static int read_result;
static int read_tls_error;
static bool send_ok;
static uint8_t timeout_sec;
static int64_t open_duration_us, header_duration_us, read_step_us;
static char last_url[512], last_state[64];

static void *stream_malloc(size_t size) { assert(!input_buffer); return input_buffer = malloc(size); }
static int64_t esp_timer_get_time(void) { return now_us; }
static bool runtime_settings_get_watchdog(void) { return watchdog; }
static uint8_t runtime_settings_get_station_timeout_sec(void) { return timeout_sec; }
static const char *esp_err_to_name(int error) { (void)error; return "stub"; }
static void vTaskDelete(void *unused) { (void)unused; assert(false); }
static void vTaskDelay(unsigned ticks) { now_us += (int64_t)ticks * 1000; }
static void network_service_set_streaming(bool active) { (void)active; }
static void state_set_audio(uint32_t gen, bool active, const char *state) {
    (void)active;
    if (gen == atomic_load(&s_generation)) snprintf(last_state, sizeof(last_state), "%s", state);
}
static void log_runtime_memory(const char *stage) { (void)stage; }
static void native_state_set_bitrate(void *state, uint32_t gen, uint32_t rate) {
    (void)state; (void)gen; (void)rate;
}
static native_codec_t codec_from_content_type(const char *type) { (void)type; return NATIVE_CODEC_AAC; }
static void publish_icy_title(uint32_t gen, const char *title) { (void)gen; (void)title; }
static void stream_bitrate_add(uint32_t gen, stream_bitrate_meter_t *meter, size_t size) {
    (void)gen; (void)meter; (void)size;
}
static bool send_stream_audio(uint32_t gen, native_codec_t *codec, const void *data,
                              size_t size, bool *first) {
    (void)gen; (void)codec; (void)data; (void)size; (void)first;
    return send_ok;
}
static bool send_encoded(uint32_t gen, native_codec_t codec, const void *data, size_t size, uint8_t eos) {
    (void)gen; (void)codec; (void)data; (void)size;
    ++eos_count; eof_reason = eos; return true;
}
static void queue_play(const char *url) {
    unsigned gen = atomic_fetch_add(&s_generation, 1) + 1;
    atomic_store(&s_decoder_released_generation, gen);
    queued_command = (play_command_t){.generation=gen, .requested_codec=NATIVE_CODEC_AAC};
    snprintf(queued_command.url, sizeof(queued_command.url), "%s", url);
    queued = true;
}
static int xQueueReceive(void *queue, void *destination, TickType_t wait) {
    (void)queue;
    assert(!client.live); // Every backoff must release HTTP/TLS first.
    if (queued) { *(play_command_t *)destination = queued_command; queued = false; return pdTRUE; }
    if (wait == portMAX_DELAY) longjmp(finished, 1);
    assert(wait > 0 && wait <= STREAM_RETRY_POLL_MS);
    int64_t end = now_us + (int64_t)wait * 1000;
    if (event_kind && event_us <= end) {
        now_us = event_us;
        if (event_kind == 1) atomic_fetch_add(&s_generation, 1); // Stop, no queue item.
        if (event_kind == 2) watchdog = false;
        if (event_kind == 3) queue_play("http://fixture/second");
        event_kind = 0;
        if (queued) { *(play_command_t *)destination=queued_command; queued=false; return pdTRUE; }
    }
    now_us = end;
    return 0;
}
static esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t *config) {
    assert(!client.live);
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    assert(input_prepared);
    input_prepared = false;
#endif
#ifdef CONFIG_YORADIO_TLS_RETAIN_RX_BUFFER
    assert(config->tls_dyn_buf_strategy==HTTP_TLS_DYN_BUF_RX_STATIC);
#else
    assert(config->tls_dyn_buf_strategy==0);
#endif
    if (init_oom) return NULL;
    assert(attempt_count < attempt_limit);
    attempt_times[attempt_count++] = now_us;
    snprintf(last_url, sizeof(last_url), "%s", config->url);
    client.live = true;
    if (stop_after_attempt == attempt_count) { event_kind = 1; event_us = now_us + 50000; }
    return &client;
}
static void esp_http_client_set_header(esp_http_client_handle_t c, const char *key, const char *value) {
    (void)c;
    if (!strcmp(key, "Connection")) {
        assert(!strcmp(value, "close")); ++connection_close_headers;
    }
}
static int esp_http_client_open(esp_http_client_handle_t c, int size) {
    (void)c; (void)size;
    now_us += open_duration_us;
    if (cancel_in_open) atomic_fetch_add(&s_generation, 1);
    return attempts[attempt_count-1].result;
}
static int64_t esp_http_client_fetch_headers(esp_http_client_handle_t c) {
    now_us += header_duration_us;
    (void)c; return attempts[attempt_count-1].bad_headers ? -1 : 100;
}
static int esp_http_client_get_status_code(esp_http_client_handle_t c) { (void)c; return attempts[attempt_count-1].status; }
static int esp_http_client_get_errno(esp_http_client_handle_t c) { (void)c; return 0; }
static int esp_http_client_set_redirection(esp_http_client_handle_t c) { (void)c; return ESP_OK; }
static void esp_http_client_close(esp_http_client_handle_t c) { assert(c->live); ++close_count; }
static void esp_http_client_cleanup(esp_http_client_handle_t c) { assert(c->live); c->live = false; }
static void dispose_http_client(esp_http_client_handle_t client) {
    if (!client) return;
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
    tls_input_reserve_finish_connection();
#endif
    esp_http_client_close(client);
    esp_http_client_cleanup(client);
}
static void esp_http_client_set_timeout_ms(esp_http_client_handle_t c, int timeout) { (void)c; (void)timeout; }
static int esp_http_client_get_response_header(esp_http_client_handle_t c, const char *key, char **value) {
    (void)c; (void)key; (void)value; return ESP_FAIL;
}
static int esp_http_client_read(esp_http_client_handle_t c, char *data, size_t size) {
    now_us += read_step_us;
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
    ++read_calls;
    if (ready_on_read && read_calls == ready_on_read)
        atomic_store(&s_flac_input_ready_generation, atomic_load(&s_generation));
    if (finite_reads) return read_calls <= finite_reads ? 32 : 0;
#endif
    (void)c; (void)data; (void)size; return read_result;
}
static bool esp_http_client_is_complete_data_received(esp_http_client_handle_t c) { (void)c; return true; }
static int esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t c, int *code, int *flags) {
    (void)c; (void)flags; *code=read_tls_error; read_tls_error=0;
    return *code ? ESP_ERR_MBEDTLS_SSL_READ_FAILED : ESP_OK;
}

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


static bool http_status_is_redirect(int status) {
    return status == 301 || status == 302 || status == 303 || status == 307 ||
           status == 308;
}

static bool retryable_transport_error(esp_err_t result) {
    return result == ESP_ERR_HTTP_CONNECT ||
           result == ESP_ERR_HTTP_WRITE_DATA ||
           result == ESP_ERR_HTTP_EAGAIN || result == ESP_ERR_TIMEOUT;
}

static bool retryable_http_status(int status) {
    // Request timeout, rate limit and server errors can be temporary. Client
    // errors (including authentication/not-found) require a corrected request.
    return status == 408 || status == 429 || (status >= 500 && status <= 599);
}

static int connection_remaining_ms(int64_t deadline_us) {
    int64_t remaining_us = deadline_us - esp_timer_get_time();
    return remaining_us > 0 ? (int)((remaining_us + 999) / 1000) : 0;
}

static esp_err_t open_stream(esp_http_client_handle_t client,
                             const char *requested_url, int64_t deadline_us,
                             bool *retryable) {
    *retryable = false;
    for (unsigned redirect = 0; redirect <= MAX_HTTP_REDIRECTS; ++redirect) {
        int remaining_ms = connection_remaining_ms(deadline_us);
        if (!remaining_ms) return ESP_ERR_TIMEOUT;
        esp_http_client_set_timeout_ms(client, remaining_ms);
        ESP_LOGI(TAG, "Opening stream%s: %s",
                 redirect ? " after redirect" : "", requested_url);
        esp_err_t result = esp_http_client_open(client, 0);
        if (result != ESP_OK) {
            *retryable = retryable_transport_error(result);
            ESP_LOGE(TAG, "Stream transport open failed: %s (errno %d)",
                     esp_err_to_name(result), esp_http_client_get_errno(client));
            return result;
        }

        remaining_ms = connection_remaining_ms(deadline_us);
        if (!remaining_ms) return ESP_ERR_TIMEOUT;
        esp_http_client_set_timeout_ms(client, remaining_ms);
        int64_t headers = esp_http_client_fetch_headers(client);
        if (!connection_remaining_ms(deadline_us)) return ESP_ERR_TIMEOUT;
        int status = esp_http_client_get_status_code(client);
        if (headers < 0) {
            *retryable = true;
            ESP_LOGE(TAG,
                     "Stream response headers failed: status %d, errno %d",
                     status, esp_http_client_get_errno(client));
            esp_http_client_close(client);
            return ESP_ERR_HTTP_FETCH_HEADER;
        }
        ESP_LOGI(TAG, "Stream response: HTTP %d, length %lld", status,
                 (long long)headers);

        if (status >= 200 && status < 300) return ESP_OK;
        if (!http_status_is_redirect(status) || redirect == MAX_HTTP_REDIRECTS) {
            *retryable = retryable_http_status(status);
            esp_http_client_close(client);
            return http_status_is_redirect(status) ? ESP_ERR_HTTP_MAX_REDIRECT
                                                   : ESP_FAIL;
        }
        result = esp_http_client_set_redirection(client);
        esp_http_client_close(client);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream redirect failed: %s",
                     esp_err_to_name(result));
            return result;
        }
    }
    return ESP_ERR_HTTP_MAX_REDIRECT;
}


#define malloc stream_malloc
static void begin_stream_deadline(stream_retry_t *retry) {
    uint8_t timeout_sec = runtime_settings_get_station_timeout_sec();
    *retry = (stream_retry_t){
        .deadline_us = esp_timer_get_time() +
            (int64_t)timeout_sec * 1000000,
        .timeout_sec = timeout_sec,
    };
}

static void station_unavailable(uint32_t generation) {
    if (generation != atomic_load(&s_generation)) return;
    state_set_audio(generation, false, AUDIO_STATUS_STATION_UNAVAILABLE);
    network_service_set_streaming(false);
}

static void schedule_stream_retry(stream_retry_t *retry, uint32_t generation) {
    if (generation != atomic_load(&s_generation) ||
        !runtime_settings_get_watchdog()) return;
    if (!connection_remaining_ms(retry->deadline_us)) {
        station_unavailable(generation);
        return;
    }
    uint32_t delay_ms = retry->delay_ms ? retry->delay_ms * 2U
                                      : STREAM_RETRY_INITIAL_MS;
    if (delay_ms > STREAM_RETRY_MAX_MS) delay_ms = STREAM_RETRY_MAX_MS;
    retry->delay_ms = delay_ms;
    retry->due_us = esp_timer_get_time() + (int64_t)delay_ms * 1000;
    if (retry->due_us > retry->deadline_us) retry->due_us = retry->deadline_us;
    retry->pending = true;
    ESP_LOGW(TAG, "Retry stream connection in %lu ms", (unsigned long)delay_ms);
}

static void receive_stream_command(play_command_t *command,
                                   stream_retry_t *retry) {
    for (;;) {
        if (!retry->pending) {
            xQueueReceive(s_commands, command, portMAX_DELAY);
            begin_stream_deadline(retry);
            return;
        }
        if (command->generation != atomic_load(&s_generation) ||
            !runtime_settings_get_watchdog()) {
            *retry = (stream_retry_t){0};
            continue;
        }
        int64_t remaining_us = retry->due_us - esp_timer_get_time();
        if (remaining_us <= 0) {
            retry->pending = false;
            if (!connection_remaining_ms(retry->deadline_us)) {
                station_unavailable(command->generation);
                continue;
            }
            return;
        }
        uint32_t wait_ms = (uint32_t)((remaining_us + 999) / 1000);
        if (wait_ms > STREAM_RETRY_POLL_MS) wait_ms = STREAM_RETRY_POLL_MS;
        // A new Play wakes the queue immediately. Stop/watchdog changes have
        // no queue item, so check them at bounded intervals while backing off.
        if (xQueueReceive(s_commands, command, pdMS_TO_TICKS(wait_ms)) == pdTRUE) {
            begin_stream_deadline(retry);
            return;
        }
    }
}

static void stream_task(void *argument) {
    (void)argument;
    uint8_t *buffer = malloc(STREAM_CHUNK_SIZE);
    if (!buffer) {
        ESP_LOGE(TAG, "No memory for stream input buffer");
        vTaskDelete(NULL);
    }
    play_command_t command;
    stream_retry_t retry = {0};
    while (true) {
        receive_stream_command(&command, &retry);
#ifdef YORADIO_CODEC_BENCHMARK
        if (command.fixture_size) {
            play_flash_fixture(&command, buffer);
            continue;
        }
#endif

        // A decoder can retain considerably more RAM than a TLS session.
        // Wait until the decoder task has released the previous station before
        // allocating the next HTTP/TLS transport.
        while (atomic_load(&s_generation) == command.generation &&
               atomic_load(&s_decoder_released_generation) !=
                   command.generation &&
               connection_remaining_ms(retry.deadline_us)) {
            vTaskDelay(pdMS_TO_TICKS(1));
        }
        if (atomic_load(&s_generation) != command.generation) continue;
        if (!connection_remaining_ms(retry.deadline_us)) {
            station_unavailable(command.generation);
            continue;
        }

#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
        // Previous HTTP/TLS client is closed. Apply the TLS memory budget;
        // queued packets and outstanding leases keep their owners.
        tls_input_reserve_prepare_connection();
#endif
        network_service_set_streaming(true);
        state_set_audio(command.generation, false, "connecting");

        esp_http_client_config_t config = {
            .url = command.url,
            .timeout_ms = connection_remaining_ms(retry.deadline_us),
            .buffer_size = STREAM_CHUNK_SIZE,
            .buffer_size_tx = 4096,
            .crt_bundle_attach = esp_crt_bundle_attach,
#ifdef CONFIG_YORADIO_TLS_RETAIN_RX_BUFFER
            // Allocate the full RX record once after the handshake. TX and
            // handshake allocations still use the SDK's dynamic strategy.
            .tls_dyn_buf_strategy = HTTP_TLS_DYN_BUF_RX_STATIC,
#endif
            .disable_auto_redirect = false,
            .max_redirection_count = MAX_HTTP_REDIRECTS,
            .keep_alive_enable = true,
            .user_agent = "yoRadio-native/1",
        };
        esp_http_client_handle_t client = esp_http_client_init(&config);
        if (!client) {
            if (atomic_load(&s_generation) == command.generation) {
                state_set_audio(command.generation, false, "HTTP allocation failed");
                network_service_set_streaming(false);
            }
            continue;
        }
        esp_http_client_set_header(client, "Icy-MetaData", "1");
        // One response per connection (RFC 9112 section 9.3). TCP keepalive
        // probes above are independent of HTTP connection reuse.
        esp_http_client_set_header(client, "Connection", "close");
        bool retryable;
        esp_err_t result = open_stream(client, command.url, retry.deadline_us,
                                       &retryable);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream connection failed for %s: %s", command.url,
                     esp_err_to_name(result));
            if (atomic_load(&s_generation) == command.generation) {
                state_set_audio(command.generation, false, "connection failed");
                network_service_set_streaming(false);
            }
            dispose_http_client(client);
            if (retryable) schedule_stream_retry(&retry, command.generation);
            if (!retry.pending) station_unavailable(command.generation);
            continue;
        }
        const int64_t availability_timeout_us = (int64_t)retry.timeout_sec * 1000000;
        retry = (stream_retry_t){0};
        if (strncmp(command.url, "https://", 8) == 0) {
            log_runtime_memory("after TLS handshake");
        }
        // Keep the long timeout for TCP/TLS setup, then poll the stream often
        // enough that Stop can be handled without closing an HTTP client from
        // a different task (esp_http_client handles are not thread-safe).
        esp_http_client_set_timeout_ms(client, STREAM_READ_TIMEOUT_MS);
        if (atomic_load(&s_generation) != command.generation) {
            dispose_http_client(client);
            continue;
        }
        // Match the original yoRadio player state: a successfully opened
        // HTTP/ICY stream is playing even before its first PCM frame arrives.
        state_set_audio(command.generation, true, "connected");
        native_codec_t codec = command.requested_codec;
        if (codec == NATIVE_CODEC_AUTO) {
            char *content_type = NULL;
            if (esp_http_client_get_response_header(
                    client, "Content-Type", &content_type) == ESP_OK) {
                codec = codec_from_content_type(content_type);
            }
        }
        size_t metadata_interval = 0;
        char *metadata_interval_text = NULL;
        if (esp_http_client_get_response_header(
                client, "icy-metaint", &metadata_interval_text) == ESP_OK &&
            metadata_interval_text) {
            metadata_interval = strtoul(metadata_interval_text, NULL, 10);
            ESP_LOGI(TAG, "ICY metadata interval: %u",
                     (unsigned)metadata_interval);
        }
        char *icy_bitrate_text = NULL;
        if (esp_http_client_get_response_header(
                client, "icy-br", &icy_bitrate_text) == ESP_OK &&
            icy_bitrate_text) {
            unsigned long icy_bitrate =
                strtoul(icy_bitrate_text, NULL, 10);
            if (icy_bitrate > 0 && icy_bitrate <= UINT32_MAX) {
                native_state_set_bitrate(s_state, command.generation, (uint32_t)icy_bitrate);
                ESP_LOGI(TAG, "ICY bitrate: %lu kbit/s", icy_bitrate);
            }
        }
        size_t audio_until_metadata = metadata_interval;
        size_t metadata_remaining = 0;
        bool first_chunk = true;
        bool stream_stalled = false;
        bool stream_read_failed = false;
        bool stream_unavailable = false;
        int64_t last_stream_data_us = esp_timer_get_time();
        stream_bitrate_meter_t bitrate_meter = {
            .started_us = esp_timer_get_time(),
        };
        stream_http_reader_t reader = {0};
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
        bool input_growth_attempted = false;
#endif
        while (atomic_load(&s_generation) == command.generation) {
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
            if (!input_growth_attempted && codec == NATIVE_CODEC_FLAC &&
                atomic_load(&s_flac_input_ready_generation) == command.generation) {
                input_growth_attempted = true;
                tls_input_reserve_expand_flac();
            }
#endif
            int received = stream_http_read(&reader, client, (char *)buffer,
                                            STREAM_CHUNK_SIZE);
            // Stop/station change may happen while the socket read is blocked.
            // Never pass data returned by that obsolete read to ICY or audio.
            if (atomic_load(&s_generation) != command.generation) break;
            if (received == -ESP_ERR_HTTP_EAGAIN) {
                if (runtime_settings_get_watchdog() &&
                    esp_timer_get_time() - last_stream_data_us >=
                        availability_timeout_us) {
                    stream_unavailable = true;
                    break;
                }
                continue;
            }
            if (received < 0) {
                log_runtime_memory("at stream read failure");
                ESP_LOGW(TAG, "Stream read failed");
                stream_read_failed = true;
                break;
            }
            if (received == 0) {
                if (esp_http_client_is_complete_data_received(client)) break;
                if (runtime_settings_get_watchdog() &&
                    esp_timer_get_time() - last_stream_data_us >=
                        availability_timeout_us) {
                    ESP_LOGW(TAG, "Stream watchdog timeout");
                    stream_unavailable = true;
                    break;
                }
                vTaskDelay(pdMS_TO_TICKS(10));
                continue;
            }
            size_t offset = 0;
            last_stream_data_us = esp_timer_get_time();
            while (offset < (size_t)received) {
                if (!metadata_interval) {
                    if (!send_stream_audio(command.generation, &codec,
                                           buffer + offset,
                                           (size_t)received - offset,
                                           &first_chunk)) {
                        stream_stalled = true;
                        break;
                    }
                    stream_bitrate_add(command.generation, &bitrate_meter,
                                       (size_t)received - offset);
                    offset = (size_t)received;
                } else if (audio_until_metadata) {
                    size_t available = (size_t)received - offset;
                    size_t chunk = available < audio_until_metadata
                                       ? available
                                       : audio_until_metadata;
                    if (!send_stream_audio(command.generation, &codec,
                                           buffer + offset, chunk,
                                           &first_chunk)) {
                        stream_stalled = true;
                        break;
                    }
                    stream_bitrate_add(command.generation, &bitrate_meter,
                                       chunk);
                    offset += chunk;
                    audio_until_metadata -= chunk;
                } else if (!metadata_remaining) {
                    metadata_remaining = (size_t)buffer[offset++] * ICY_METADATA_BLOCK_BYTES;
                    icy_title_begin(&s_icy_title);
                    if (!metadata_remaining) {
                        audio_until_metadata = metadata_interval;
                    }
                } else {
                    size_t available = (size_t)received - offset;
                    size_t chunk = available < metadata_remaining
                                       ? available
                                       : metadata_remaining;
                    icy_title_feed(&s_icy_title, buffer + offset, chunk);
                    metadata_remaining -= chunk;
                    offset += chunk;
                    if (!metadata_remaining) {
                        publish_icy_title(command.generation,
                                          icy_title_finish(&s_icy_title));
                        audio_until_metadata = metadata_interval;
                    }
                }
            }
            if (stream_stalled) {
                ESP_LOGW(TAG, "Compressed audio buffer stalled");
                break;
            }
        }
        uint8_t end_reason = stream_stalled ? AUDIO_END_BUFFER_STALLED
                             : stream_unavailable ? AUDIO_END_UNAVAILABLE
                             : stream_read_failed ? AUDIO_END_READ_FAILED
                                                  : AUDIO_END_EOF;
        send_encoded(command.generation, codec, NULL, 0, end_reason);
        dispose_http_client(client);
        if (atomic_load(&s_generation) == command.generation) {
            // The decoder still owns buffered input. Its last format callback
            // must precede the terminal state, including delayed HE-AAC PCM.
            // output_task publishes completion after the PCM queue drains.
            network_service_set_streaming(false);
        }
    }
}


#undef malloc

static void reset(unsigned count) {
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
    atomic_store(&s_flac_input_ready_generation, 0);
    growth_calls = finish_calls = finite_reads = read_calls = ready_on_read = 0;
#endif
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    input_prepared = false;
#endif
    memset(attempts, 0, sizeof(attempts));
    memset(attempt_times, 0, sizeof(attempt_times));
    atomic_store(&s_generation, 0); atomic_store(&s_decoder_released_generation, 0);
    attempt_count = eos_count = close_count = event_kind = stop_after_attempt = 0;
    connection_close_headers = 0;
    now_us = event_us = 0; attempt_limit = count;
    watchdog = send_ok = true; init_oom = cancel_in_open = queued = false;
    input_buffer = NULL; read_result = read_tls_error = 0; client.live = false;
    timeout_sec = 10; open_duration_us = header_duration_us = read_step_us = 0;
    last_state[0] = last_url[0] = 0;
    for (unsigned i=0; i<count; ++i) attempts[i].status = 503;
    queue_play("http://fixture/first");
}
static void execute(void) {
    if (!setjmp(finished)) stream_task(NULL);
    assert(!client.live);
    assert(connection_close_headers == attempt_count);
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
    assert(finish_calls == attempt_count);
#endif
    free(input_buffer); input_buffer = NULL;
}
int main(void) {
    unsigned cases = 0;
    reset(3); attempts[2].status = 200; execute();
    assert(attempt_count == 3 && eos_count == 1 && eof_reason == AUDIO_END_EOF);
    assert(attempt_times[1] == 1000000 && attempt_times[2] == 3000000); ++cases;
    reset(4); execute();
    const int64_t schedule[] = {0, 1, 3, 7};
    for (unsigned i=0; i<4; ++i) assert(attempt_times[i] == schedule[i]*1000000);
    assert(eos_count == 0 && now_us == 10000000 && !strcmp(last_state, "station unavailable")); ++cases;
    for (unsigned action=1; action<=3; ++action) {
        reset(2); event_kind = action; event_us = 500000; attempts[1].status = 200;
        execute();
        assert(attempt_count == (action == 3 ? 2U : 1U));
        if (action == 3) assert(attempt_times[1] == 500000 && strstr(last_url, "/second"));
        ++cases;
    }
    reset(1); watchdog = false; execute(); assert(attempt_count == 1 && !eos_count); ++cases;
    reset(1); cancel_in_open = true; attempts[0].result = ESP_ERR_HTTP_CONNECT;
    execute(); assert(attempt_count == 1 && !eos_count); ++cases;
    const int permanent[] = {400,401,403,404,410,416};
    for (unsigned i=0; i<sizeof(permanent)/sizeof(permanent[0]); ++i) {
        reset(1); attempts[0].status=permanent[i]; execute(); assert(attempt_count==1); ++cases;
    }
    const int transient[] = {408,429,500,502,503,504};
    for (unsigned i=0; i<sizeof(transient)/sizeof(transient[0]); ++i) {
        reset(2); attempts[0].status=transient[i]; attempts[1].status=200; execute();
        assert(attempt_count==2 && eos_count==1); ++cases;
    }
    const int transport[] = {ESP_ERR_HTTP_CONNECT, ESP_ERR_HTTP_WRITE_DATA, ESP_ERR_HTTP_EAGAIN, ESP_ERR_TIMEOUT};
    for (unsigned i=0; i<sizeof(transport)/sizeof(transport[0]); ++i) {
        reset(2); attempts[0].result=transport[i]; attempts[1].status=200; execute();
        assert(attempt_count==2 && eos_count==1); ++cases;
    }
    reset(2); attempts[0].bad_headers=true; attempts[1].status=200; execute();
    assert(attempt_count==2 && eos_count==1); ++cases;
    reset(1); attempts[0].status=302; execute(); assert(attempt_count==1 && !eos_count); ++cases;
    reset(1); attempts[0].result=ESP_ERR_HTTP_INVALID_TRANSPORT; execute(); assert(attempt_count==1); ++cases;
    reset(1); init_oom=true; execute(); assert(attempt_count==0); ++cases;
    reset(1); attempts[0].status=200; read_result=-1; execute();
    assert(attempt_count==1 && eof_reason==AUDIO_END_READ_FAILED); ++cases;
    reset(1); attempts[0].status=200; read_result=1; send_ok=false; execute();
    assert(attempt_count==1 && eof_reason==AUDIO_END_BUFFER_STALLED); ++cases;
    for (unsigned seconds=1; seconds<=2; ++seconds) {
        reset(seconds); timeout_sec=seconds; execute();
        assert(now_us==(int64_t)seconds*1000000 && !strcmp(last_state,"station unavailable")); ++cases;
    }
    reset(8); timeout_sec=120; execute();
    assert(attempt_count==8 && now_us==120000000 && !strcmp(last_state,"station unavailable")); ++cases;
    reset(1); attempts[0].status=200; open_duration_us=10000000; execute();
    assert(attempt_count==1 && !eos_count && !strcmp(last_state,"station unavailable")); ++cases;
    reset(1); attempts[0].status=200; open_duration_us=9000000; header_duration_us=1000000; execute();
    assert(attempt_count==1 && !eos_count && !strcmp(last_state,"station unavailable")); ++cases;
    reset(1); attempts[0].status=200; timeout_sec=2; read_result=-ESP_ERR_HTTP_EAGAIN;
    read_step_us=1000000; execute();
    assert(eof_reason==AUDIO_END_UNAVAILABLE && now_us==2000000); ++cases;
    reset(1); attempts[0].status=200; read_result=32; read_tls_error=TEST_TLS_ALLOCATION_ERROR;
    execute(); assert(eof_reason==AUDIO_END_READ_FAILED && close_count==2); ++cases;
    reset(1); attempts[0].status=200; read_result=ESP_FAIL;
    execute(); assert(eof_reason==AUDIO_END_READ_FAILED && close_count==2); ++cases;
#if CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS > 0
    // Explicit FLAC grows once, only after this generation produces PCM.
    reset(1); attempts[0].status=200; queued_command.requested_codec=NATIVE_CODEC_FLAC;
    finite_reads=4; ready_on_read=2;
    execute(); assert(growth_calls==1 && read_calls==5); ++cases;
    // An old decoder, an unready decoder and a different codec cannot grow.
    reset(1); attempts[0].status=200; queued_command.requested_codec=NATIVE_CODEC_FLAC;
    finite_reads=4; atomic_store(&s_flac_input_ready_generation, 99);
    execute(); assert(!growth_calls); ++cases;
    reset(1); attempts[0].status=200; queued_command.requested_codec=NATIVE_CODEC_FLAC;
    finite_reads=4;
    execute(); assert(!growth_calls); ++cases;
    reset(1); attempts[0].status=200; finite_reads=4; ready_on_read=1;
    execute(); assert(!growth_calls); ++cases;
    reset(1); attempts[0].status=200; queued_command.requested_codec=NATIVE_CODEC_FLAC;
    atomic_store(&s_flac_input_ready_generation, atomic_load(&s_generation));
    read_result=ESP_FAIL;
    execute(); assert(growth_calls==1 && finish_calls==1 && eof_reason==AUDIO_END_READ_FAILED); ++cases;
#endif
    printf("PASS stream retry cases=%u; HTTP ownership, cancellation, EOF and error gates\n", cases);
}
