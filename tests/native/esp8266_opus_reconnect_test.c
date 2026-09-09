/* Production audio_task branches are injected by the JS driver, not copied.
 * The real codec bridge/arena allocation semantics have a separate lifecycle
 * harness; these stubs expose and check the caller's ownership/order. */
#include "codec_bridge.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define YORADIO_ESP8266_AUDIO_PROFILE 0
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
#define audio_transport_phase(phase) ((void)0)
#define pdMS_TO_TICKS(ms) (ms)
#define taskENTER_CRITICAL() ((void)0)
#define taskEXIT_CRITICAL() ((void)0)
/* DEFINES */
typedef struct { uint32_t generation; bool play; char url[64]; } audio_command_t;
typedef struct { int socket; } http_stream_t;
struct helix_codec { helix_codec_kind_t kind; };
enum { CLOSE, SILENCE, DESTROY, WARM_OPEN, COLD_OPEN, RESET, OLD_FREE,
       NEW_ALLOC, REQUEUE_EVENT, DELAY, BENCHMARK };
static unsigned events[128], event_count;
static unsigned allocations, frees, opens, delays, requeues, switches, resets;
static int open_results[2], open_errors[2];
static bool sockets[16], pause_requested, close_fails, reset_fails, create_fails;
static bool change_on_close, change_on_open, change_on_delay;
static uint32_t generation;
#define s_generation generation
static helix_codec_t *held;
static helix_codec_kind_t held_kind;
static audio_command_t queued;
static int s_commands;

static void event(unsigned value) { assert(event_count < 128); events[event_count++] = value; }
static unsigned position(unsigned value) {
    for (unsigned i = 0; i < event_count; ++i) if (events[i] == value) return i;
    return 128;
}
static bool generation_current(uint32_t value) { return generation == value; }
static void newer_command(void) { ++generation; queued.generation = generation; queued.play = false; }
static bool audio_web_pause_requested(void) { return pause_requested; }
static bool audio_web_pause_checkpoint(http_stream_t *stream, const audio_command_t *command) {
    (void)stream; (void)command; return pause_requested;
}
static void native_audio_output_silence(void) { event(SILENCE); }
static void native_state_set_audio(bool playing, bool connecting, const char *error) {
    (void)playing; (void)connecting; (void)error;
}
static void network_service_set_streaming(bool streaming) { (void)streaming; }
static void log_audio_stack(const char *reason) { (void)reason; }
static void opus_benchmark_run_pending(uint32_t value, bool (*current)(uint32_t)) {
    assert(current(value)); event(BENCHMARK);
}
static void xQueueOverwrite(int queue, const audio_command_t *command) {
    (void)queue; queued = *command; ++requeues; event(REQUEUE_EVENT);
}
static void vTaskDelay(unsigned ticks) {
    assert(ticks == 250); ++delays; event(DELAY);
    if (change_on_delay) newer_command();
}
static int mock_close(int socket) {
    assert(socket >= 3 && socket < 16 && sockets[socket]);
    event(CLOSE);
    if (change_on_close) newer_command();
    if (close_fails) { errno = EIO; return -1; }
    sockets[socket] = false;
    return 0;
}
#define close mock_close
static int open_http_stream(char *url, http_stream_t *stream) {
    assert(url[0] && opens < HTTP_OPEN_ATTEMPTS);
    event(held ? WARM_OPEN : COLD_OPEN);
    const unsigned attempt = opens++;
    if (change_on_open) newer_command();
    if (open_results[attempt]) {
        errno = open_errors[attempt]; return open_results[attempt];
    }
    const int socket = 4 + (int)attempt;
    assert(!sockets[socket]); sockets[socket] = true; stream->socket = socket;
    return 0;
}
helix_codec_t *helix_codec_create(helix_codec_kind_t kind, size_t reserve) {
    assert(!held && reserve == CODEC_HEAP_RESERVE_BYTES);
    if (create_fails) return NULL;
    helix_codec_t *codec = malloc(sizeof(*codec)); assert(codec);
    codec->kind = kind; held = codec; ++allocations; event(NEW_ALLOC); return codec;
}
void helix_codec_destroy(helix_codec_t *codec) {
    assert(codec && codec == held); event(DESTROY); free(codec); held = NULL; ++frees;
}
int helix_codec_switch(helix_codec_t *codec, helix_codec_kind_t kind) {
    assert(codec == held && sockets[4]); ++switches;
    if (codec->kind == kind) {
        ++resets; event(RESET); return reset_fails ? -2 : 0;
    }
    event(OLD_FREE); ++frees;
    codec->kind = kind; event(NEW_ALLOC); ++allocations;
    return 0;
}
const char *helix_codec_error_message(helix_codec_kind_t kind, int error) {
    (void)kind; (void)error; return "decoder error";
}
/* RELEASE */
/* REQUEUE */

static audio_command_t command(void) {
    audio_command_t result = {generation, true, "http://test.invalid/opus"};
    return result;
}
static void finish_transport(int feed) {
    audio_command_t command = {generation, true, "http://test.invalid/opus"};
    http_stream_t stream = {3};
    helix_codec_t *codec = held;
    helix_codec_kind_t codec_kind = held_kind;
    for (unsigned once = 0; once < 1; ++once) {
        /* RECONNECT */
    }
    held = codec; held_kind = codec_kind;
}
static bool open_command(audio_command_t command, http_stream_t *out) {
    http_stream_t stream = {-1};
    helix_codec_t *codec = held;
    helix_codec_kind_t codec_kind = held_kind;
    bool success = false;
    for (unsigned once = 0; once < 1; ++once) {
        /* OPEN */
        success = true;
    }
    held = codec; held_kind = codec_kind; *out = stream;
    return success;
}
static bool after_sniff(helix_codec_kind_t sniffed, http_stream_t stream) {
    helix_codec_t *codec = held;
    helix_codec_kind_t codec_kind = sniffed;
    bool success = false;
    for (unsigned once = 0; once < 1; ++once) {
        /* SNIFF */
        success = true;
    }
    held = codec; held_kind = codec_kind;
    return success;
}
static void stop_command(void) {
    audio_command_t command = {generation, false, ""};
    helix_codec_t *codec = held;
    helix_codec_kind_t codec_kind = held_kind;
    for (unsigned once = 0; once < 1; ++once) {
        /* STOP */
    }
    held = codec; held_kind = codec_kind;
}
static void setup(helix_codec_kind_t kind) {
    assert(!held && allocations == frees);
    memset(sockets, 0, sizeof(sockets)); memset(open_results, 0, sizeof(open_results));
    memset(open_errors, 0, sizeof(open_errors));
    pause_requested = close_fails = reset_fails = create_fails = false;
    change_on_close = change_on_open = change_on_delay = false;
    generation = 100; queued = command();
    held = helix_codec_create(kind, CODEC_HEAP_RESERVE_BYTES); held_kind = kind;
    sockets[3] = true;
    event_count = opens = delays = requeues = switches = resets = 0;
}
static void cleanup(void) {
    if (held) stop_command();
    close_fails = false;
    for (int fd = 3; fd < 16; ++fd) if (sockets[fd]) mock_close(fd);
    assert(!held && allocations == frees);
}
static void retention_and_reset(void) {
    for (unsigned kind = HELIX_CODEC_MP3; kind <= HELIX_CODEC_OPUS; ++kind) {
        setup((helix_codec_kind_t)kind);
        const unsigned before = allocations;
        const bool warm = CONFIG_YORADIO_OGG_OPUS && kind == HELIX_CODEC_OPUS;
        finish_transport(0);
        assert(!sockets[3] && requeues == 1 && delays == 1);
        assert(!!held == warm && position(CLOSE) < position(SILENCE));
        if (!warm) assert(position(SILENCE) < position(DESTROY));
        http_stream_t stream;
        assert(open_command(queued, &stream) && opens == 1);
        assert(position(CLOSE) < position(warm ? WARM_OPEN : COLD_OPEN));
        assert(after_sniff((helix_codec_kind_t)kind, stream));
        assert(resets == (unsigned)warm && allocations == before + !warm);
        if (warm) assert(position(WARM_OPEN) < position(RESET) && position(DESTROY) == 128);
        else assert(position(DESTROY) < position(COLD_OPEN));
        cleanup();
    }
}
static void failed_open_falls_back_once(void) {
    for (unsigned failed = 0; failed < 3; ++failed) {
        setup(HELIX_CODEC_OPUS); finish_transport(0);
        open_results[0] = -2; open_errors[0] = failed == 0 ? ENOMEM : failed == 1 ? ETIMEDOUT : EPROTO;
        http_stream_t stream;
        assert(open_command(queued, &stream) && opens == 2);
        assert(!held && delays == 2); /* Existing 250ms recovery + retry. */
        assert(position(DESTROY) < position(COLD_OPEN));
        if (CONFIG_YORADIO_OGG_OPUS) assert(position(WARM_OPEN) < position(DESTROY));
        assert(after_sniff(HELIX_CODEC_OPUS, stream) && held && !resets);
        cleanup();
    }
    setup(HELIX_CODEC_OPUS); finish_transport(0);
    open_results[0] = open_results[1] = -2;
    open_errors[0] = open_errors[1] = ENOMEM;
    http_stream_t stream;
    assert(!open_command(queued, &stream) && opens == 2 && !held);
    assert(requeues == 1); /* No third attempt or automatic allocation loop. */
    cleanup();
}
static void switches_errors_and_stop(void) {
    setup(HELIX_CODEC_OPUS); finish_transport(0);
    http_stream_t stream; assert(open_command(queued, &stream));
    assert(after_sniff(HELIX_CODEC_MP3, stream));
    if (CONFIG_YORADIO_OGG_OPUS) assert(position(OLD_FREE) < position(NEW_ALLOC));
    assert(held->kind == HELIX_CODEC_MP3); cleanup();
    setup(HELIX_CODEC_OPUS); finish_transport(-109);
    assert(!held && !requeues && position(CLOSE) < position(DESTROY)); cleanup();
    setup(HELIX_CODEC_OPUS); close_fails = true; finish_transport(0);
    assert(!held && requeues == 1); cleanup();
    setup(HELIX_CODEC_OPUS); finish_transport(0);
    assert(open_command(queued, &stream)); reset_fails = true; create_fails = true;
    assert(!after_sniff(HELIX_CODEC_OPUS, stream) && !held && !sockets[4]); cleanup();
    setup(HELIX_CODEC_OPUS); finish_transport(0);
    stop_command(); assert(!held && position(DESTROY) < position(BENCHMARK)); cleanup();
}
static void newer_generation_wins(void) {
    for (unsigned when = 0; when < 2; ++when) {
        setup(HELIX_CODEC_OPUS);
        change_on_close = when == 0; change_on_delay = when == 1;
        finish_transport(0);
        assert(!requeues && !queued.play && !sockets[3]);
        change_on_close = change_on_delay = false;
        stop_command(); assert(!held); cleanup();
    }
    setup(HELIX_CODEC_OPUS); finish_transport(0);
    const audio_command_t stale = queued;
    newer_command();
    queued.play = true;
    strcpy(queued.url, "http://test.invalid/new-station");
    http_stream_t stream;
    assert(!open_command(stale, &stream) && !opens);
    assert(queued.play && strcmp(queued.url, "http://test.invalid/new-station") == 0);
    stop_command(); cleanup();
    for (unsigned failed = 0; failed < 2; ++failed) {
        setup(HELIX_CODEC_OPUS); finish_transport(0);
        change_on_open = true;
        if (failed) { open_results[0] = -2; open_errors[0] = ENOMEM; }
        assert(!open_command(queued, &stream) && opens == 1 && !sockets[4]);
        assert(!queued.play && requeues == 1); /* Never overwrite the newer Stop. */
        change_on_open = false; stop_command(); cleanup();
    }
    setup(HELIX_CODEC_OPUS); finish_transport(0); pause_requested = true;
    assert(!open_command(queued, &stream) && !opens);
    pause_requested = false; stop_command(); cleanup();
}
int main(void) {
    assert(HTTP_OPEN_ATTEMPTS == 2);
    retention_and_reset(); failed_open_falls_back_once();
    switches_errors_and_stop(); newer_generation_wins();
    assert(allocations == frees && !held);
    printf("actual reconnect control-flow PASS: Opus=%d, %u paired allocations/frees\n",
           CONFIG_YORADIO_OGG_OPUS, allocations);
    return 0;
}
