#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <setjmp.h>

typedef int esp_err_t;
typedef int native_codec_t;
enum { ESP_OK, ESP_FAIL, ESP_ERR_HTTP_CONNECT, ESP_ERR_HTTP_WRITE_DATA,
       ESP_ERR_HTTP_EAGAIN, ESP_ERR_TIMEOUT, ESP_ERR_HTTP_FETCH_HEADER,
       ESP_ERR_HTTP_MAX_REDIRECT, ESP_ERR_HTTP_INVALID_TRANSPORT,
       NATIVE_CODEC_AUTO, NATIVE_CODEC_AAC, AUDIO_END_EOF,
       AUDIO_END_BUFFER_STALLED, AUDIO_END_READ_FAILED };
enum { STREAM_CHUNK_SIZE = 2048, STREAM_READ_TIMEOUT_MS = 250,
       MAX_HTTP_REDIRECTS = 5, ICY_METADATA_MAX = 4080,
       STREAM_STALL_TIMEOUT_US = 10000000 };
typedef uint32_t TickType_t;
#define portMAX_DELAY UINT32_MAX
#define pdTRUE 1
#define pdMS_TO_TICKS(n) (n)
#define ESP_LOGE(tag, ...) do { if (0) printf(__VA_ARGS__); } while (0)
#define ESP_LOGW(tag, ...) ESP_LOGE(tag, __VA_ARGS__)
#define ESP_LOGI(tag, ...) ESP_LOGE(tag, __VA_ARGS__)
static atomic_uint s_generation, s_decoder_released_generation;
static void *s_commands, *s_state;
static char s_icy_metadata[ICY_METADATA_MAX + 1];
typedef struct { int64_t started_us; uint64_t audio_bytes; } stream_bitrate_meter_t;

/* PRODUCTION_COMMAND_TYPES */
/* PRODUCTION_RETRY_CONSTANTS */

typedef struct {
    const char *url, *user_agent;
    unsigned timeout_ms, buffer_size, buffer_size_tx, max_redirection_count;
    bool disable_auto_redirect, keep_alive_enable;
    void *crt_bundle_attach;
} esp_http_client_config_t;
#define esp_crt_bundle_attach NULL
typedef struct { bool live; } fake_client_t;
typedef fake_client_t *esp_http_client_handle_t;
typedef struct { int result, status; bool bad_headers; } attempt_t;
static fake_client_t client;
static attempt_t attempts[16];
static unsigned attempt_count, attempt_limit, eos_count, eof_reason, close_count;
static int64_t now_us, attempt_times[16], event_us;
static unsigned event_kind, stop_after_attempt;
static bool watchdog, queued, init_oom, cancel_in_open;
static play_command_t queued_command;
static jmp_buf finished;
static void *input_buffer;
static int read_result;
static bool send_ok;
static char last_url[512], last_state[64];

static void *stream_malloc(size_t size) { assert(!input_buffer); return input_buffer = malloc(size); }
static int64_t esp_timer_get_time(void) { return now_us; }
static bool runtime_settings_get_watchdog(void) { return watchdog; }
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
static void parse_icy_metadata(uint32_t gen, char *data, size_t size) { (void)gen; (void)data; (void)size; }
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
    if (init_oom) return NULL;
    assert(attempt_count < attempt_limit);
    attempt_times[attempt_count++] = now_us;
    snprintf(last_url, sizeof(last_url), "%s", config->url);
    client.live = true;
    if (stop_after_attempt == attempt_count) { event_kind = 1; event_us = now_us + 50000; }
    return &client;
}
static void esp_http_client_set_header(esp_http_client_handle_t c, const char *key, const char *value) {
    (void)c; (void)key; (void)value;
}
static int esp_http_client_open(esp_http_client_handle_t c, int size) {
    (void)c; (void)size;
    if (cancel_in_open) atomic_fetch_add(&s_generation, 1);
    return attempts[attempt_count-1].result;
}
static int64_t esp_http_client_fetch_headers(esp_http_client_handle_t c) {
    (void)c; return attempts[attempt_count-1].bad_headers ? -1 : 100;
}
static int esp_http_client_get_status_code(esp_http_client_handle_t c) { (void)c; return attempts[attempt_count-1].status; }
static int esp_http_client_get_errno(esp_http_client_handle_t c) { (void)c; return 0; }
static int esp_http_client_set_redirection(esp_http_client_handle_t c) { (void)c; return ESP_OK; }
static void esp_http_client_close(esp_http_client_handle_t c) { assert(c->live); ++close_count; }
static void dispose_http_client(esp_http_client_handle_t c) { assert(c->live); c->live = false; }
static void esp_http_client_set_timeout_ms(esp_http_client_handle_t c, int timeout) { (void)c; (void)timeout; }
static int esp_http_client_get_response_header(esp_http_client_handle_t c, const char *key, char **value) {
    (void)c; (void)key; (void)value; return ESP_FAIL;
}
static int esp_http_client_read(esp_http_client_handle_t c, char *data, size_t size) {
    (void)c; (void)data; (void)size; return read_result;
}
static bool esp_http_client_is_complete_data_received(esp_http_client_handle_t c) { (void)c; return true; }

/* PRODUCTION_OPEN_STREAM */
#define malloc stream_malloc
/* PRODUCTION_STREAM_TASK */
#undef malloc

static void reset(unsigned count) {
    memset(attempts, 0, sizeof(attempts));
    memset(attempt_times, 0, sizeof(attempt_times));
    atomic_store(&s_generation, 0); atomic_store(&s_decoder_released_generation, 0);
    attempt_count = eos_count = close_count = event_kind = stop_after_attempt = 0;
    now_us = event_us = 0; attempt_limit = count;
    watchdog = send_ok = true; init_oom = cancel_in_open = queued = false;
    input_buffer = NULL; read_result = 0; client.live = false;
    last_state[0] = last_url[0] = 0;
    for (unsigned i=0; i<count; ++i) attempts[i].status = 503;
    queue_play("http://fixture/first");
}
static void execute(void) {
    if (!setjmp(finished)) stream_task(NULL);
    assert(!client.live);
    free(input_buffer); input_buffer = NULL;
}
int main(void) {
    unsigned cases = 0;
    reset(3); attempts[2].status = 200; execute();
    assert(attempt_count == 3 && eos_count == 1 && eof_reason == AUDIO_END_EOF);
    assert(attempt_times[1] == 1000000 && attempt_times[2] == 3000000); ++cases;
    reset(7); stop_after_attempt = 7; execute();
    const int64_t schedule[] = {0, 1, 3, 7, 15, 31, 61};
    for (unsigned i=0; i<7; ++i) assert(attempt_times[i] == schedule[i]*1000000);
    assert(eos_count == 0); ++cases;
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
    printf("PASS stream retry cases=%u; HTTP ownership, cancellation, EOF and error gates\n", cases);
}
