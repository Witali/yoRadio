#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include "web_audio_pause_config.h"
typedef uint32_t TickType_t;
typedef int esp_err_t;
typedef int helix_codec_t;
typedef int helix_codec_kind_t;
typedef struct { int socket; } http_stream_t;
typedef struct { uint32_t generation; bool play; } audio_command_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_INVALID_STATE -2
#define ESP_ERR_TIMEOUT -3
#define portMAX_DELAY UINT32_MAX
#define pdMS_TO_TICKS(ms) ((TickType_t)(ms))
static int depth, closed, released, silenced, connecting, queued;
static uint32_t s_generation = 7;
static void *s_commands = (void *)1;
static audio_command_t queued_command;
static TickType_t now;
static void (*on_delay)(void);
static TickType_t xTaskGetTickCount(void) { return now; }
#define taskENTER_CRITICAL() (++depth)
#define taskEXIT_CRITICAL() (--depth)
static void vTaskDelay(TickType_t ticks) {
    assert(depth == 0); now += ticks;
    if (on_delay) on_delay();
}
static int close(int fd) { assert(depth == 0 && fd >= 0); ++closed; return 0; }
static void native_audio_output_silence(void) { assert(depth == 0); ++silenced; }
static void release_codec(helix_codec_t **codec, helix_codec_kind_t *kind,
                          const char *reason) {
    assert(depth == 0 && reason); if (*codec) ++released;
    *codec = NULL; *kind = 0;
}
static void native_state_set_audio(bool playing, bool starting, const char *error) {
    assert(!playing && starting && !error); ++connecting;
}
static bool generation_current(uint32_t generation) { return s_generation == generation; }
static void xQueueOverwrite(void *queue, const audio_command_t *command) {
    assert(queue == s_commands && depth); queued_command = *command; ++queued;
}
/* REQUEUE_IMPLEMENTATION */
#include "audio_web_pause.inc"

typedef int httpd_req_t;
static int served, unavailable, finished, prepared, serve_result;
static void prepare_short_response(httpd_req_t *request) { assert(request); ++prepared; }
static int finish_short_response(httpd_req_t *request, int result) {
    assert(request); ++finished; return result;
}
static void httpd_resp_set_status(httpd_req_t *request, const char *status) {
    assert(request && status[0] == '5'); ++unavailable;
}
static void httpd_resp_set_hdr(httpd_req_t *request, const char *key, const char *value) {
    assert(request && key[0] == 'R' && value[0] == '1');
}
static int httpd_resp_send(httpd_req_t *request, const char *body, int length) {
    assert(request && body && length == sizeof("Audio pause timed out") - 1);
    return ESP_OK;
}
static int serve_static_request(httpd_req_t *request) {
    assert(request); ++served; return serve_result;
}
/* STATIC_HANDLER */

static void test_http(void) {
    httpd_req_t request = 1;
#if YORADIO_ESP8266_WEB_AUDIO_PAUSE == 2
    s_web_pause_ack = false;
    assert(static_handler(&request) == ESP_OK);
    assert(unavailable == 1 && prepared == 1 && finished == 1 && !served);
    assert(!audio_web_pause_requested());
    s_web_pause_ack = true; /* Owner is already in the resource-free hold. */
#endif
    serve_result = ESP_FAIL;
    assert(static_handler(&request) == ESP_FAIL);
    assert(served == 1);
#if YORADIO_ESP8266_WEB_AUDIO_PAUSE == 2
    assert(!s_web_pause_request && s_web_pause_hold);
    now += WEB_AUDIO_PAUSE_HOLD_MS;
    assert(!audio_web_pause_requested());
#endif
}

#if YORADIO_ESP8266_WEB_AUDIO_PAUSE == 2
static helix_codec_t *gate_codec;
static helix_codec_kind_t gate_kind;
static unsigned gate_stage;
static void gate_http(void) {
    assert(!gate_codec && gate_kind == 0 && s_web_pause_ack);
    if (gate_stage == 0) {
        assert(audio_service_web_pause_begin() == ESP_OK);
        audio_service_web_pause_end();
        ++gate_stage;
    } else if (gate_stage == 1 && now - s_web_pause_ended == 200) {
        /* Another file in the same page extends the hold, without reallocating. */
        assert(audio_service_web_pause_begin() == ESP_OK);
        audio_service_web_pause_end();
        ++gate_stage;
        ++s_generation; /* New Stop/Next while paused cancels the old resume. */
    }
}
static void acknowledge(void) { s_web_pause_ack = true; on_delay = NULL; }

static void test_long(void) {
    s_commands = NULL;
    assert(audio_service_web_pause_begin() == ESP_ERR_INVALID_STATE);
    s_commands = (void *)1;
    assert(audio_service_web_pause_begin() == ESP_ERR_TIMEOUT);
    assert(now == WEB_AUDIO_PAUSE_ACK_MS && !audio_web_pause_requested());
    assert(!s_web_pause_ack && !closed && !released);

    on_delay = acknowledge;
    assert(audio_service_web_pause_begin() == ESP_OK);
    audio_service_web_pause_end();
    assert(audio_web_pause_requested());
    now += WEB_AUDIO_PAUSE_HOLD_MS;
    assert(!audio_web_pause_requested());
    s_web_pause_ack = false;

    http_stream_t stream = { 3 };
    audio_command_t command = { s_generation, true };
    assert(!audio_web_pause_checkpoint(&stream, &command) && stream.socket == 3);
    s_web_pause_request = true;
    assert(audio_web_pause_checkpoint(&stream, &command));
    assert(stream.socket == -1 && closed == 1 && queued == 1);
    assert(queued_command.generation == command.generation && connecting == 1);
    assert(!s_web_pause_ack); /* Closing alone does not acknowledge RAM release. */
    assert(audio_web_pause_checkpoint(&stream, &command) && closed == 1);

    helix_codec_t codec = 1;
    gate_codec = &codec; gate_kind = 1; on_delay = gate_http;
    TickType_t before = now;
    audio_web_pause_gate(&gate_codec, &gate_kind);
    on_delay = NULL;
    assert(released == 1 && !s_web_pause_ack && gate_stage == 2);
    assert(now - before == 451 && !audio_web_pause_requested());
    s_web_pause_request = true;
    int queued_before = queued, connecting_before = connecting;
    assert(audio_web_pause_checkpoint(&stream, &command));
    assert(queued == queued_before && connecting == connecting_before);

    /* Unsigned elapsed ticks remain correct across wraparound. */
    now = UINT32_MAX - 10;
    audio_service_web_pause_end();
    now += 249;
    assert(audio_web_pause_requested());
    ++now;
    assert(!audio_web_pause_requested());
    assert(depth == 0 && AUDIO_WEB_QUEUE_WAIT == 20);
}
#endif
int main(void) {
#if YORADIO_ESP8266_WEB_AUDIO_PAUSE == 2
    test_long();
#else
    assert(audio_service_web_pause_begin() == ESP_OK);
    audio_service_web_pause_end();
    assert(!audio_web_pause_requested());
    assert(AUDIO_WEB_QUEUE_WAIT == portMAX_DELAY);
    assert(!closed && !released && !silenced && !queued);
#endif
    test_http();
    puts("Web audio pause tests passed");
    return 0;
}
