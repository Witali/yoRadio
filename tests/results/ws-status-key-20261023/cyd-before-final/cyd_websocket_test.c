#define TEST_NETWORK_STATUS 1
#include <assert.h>
#include <pthread.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "network_status.h"
#include "websocket-under-test.c"

typedef struct { bool live, websocket; unsigned incarnation; void *context; httpd_free_ctx_fn_t free_context; httpd_send_func_t send_override; httpd_recv_func_t recv_override; } socket_t;
typedef struct { int socket; unsigned incarnation; httpd_ws_type_t type; size_t size; char text[WS_STATUS_BYTES]; } delivery_t;
static socket_t sockets[16];
static delivery_t deliveries[256];
static unsigned delivery_count, shutdown_count, queue_calls, capture_calls, command_calls, recv_calls;
static unsigned http_errors;
static int failed_socket = -1;
static bool queue_failure, registration_failure, task_failure, radio_unavailable, setting_failure, slow_send;
static bool context_failure;
static bool network_unavailable;
static network_snapshot_t network_view;
static bool send_override_failure;
static bool recv_override_failure;
static int io_script[32], select_script[32];
static size_t io_length, io_position, select_length, select_position;
static unsigned raw_send_calls, select_calls, transport_yields;
static int64_t io_advance_us;
static int receive_script[64];
static size_t receive_length, receive_position, wire_size, wire_position;
static unsigned raw_receive_calls, last_receive_flags;
static int64_t receive_advance_us;
static char wire[256];
static bool change_radio_during_capture;
static unsigned radio_aba_phase;
static bool suspend_task_exit, stop_task_after_delay;
static httpd_uri_t registered_route;
static httpd_work_fn_t queued_work;
static void *queued_argument;
static void (*task_entry)(void *);
static native_state_t state;
static radio_control_snapshot_t radio;
static native_input_health_t input;
static uint8_t volume, gain;
static int8_t balance, target;
static uint16_t normtime;
static bool normalization;
static int64_t now_us;
static unsigned cases;

size_t strlcpy(char *target_text, const char *source, size_t size) {
    size_t length = strlen(source);
    if (size) { size_t copy = length < size - 1 ? length : size - 1; memcpy(target_text, source, copy); target_text[copy] = 0; }
    return length;
}
int64_t esp_timer_get_time(void) { return now_us; }
esp_err_t network_service_snapshot(network_snapshot_t *out, uint32_t timeout_ms) {
    assert(timeout_ms == 20);
    if (network_unavailable) return ESP_ERR_TIMEOUT;
    *out = network_view; return ESP_OK;
}
void native_state_snapshot(native_state_t *source, native_state_t *out) {
    ++capture_calls;
    if (radio_aba_phase == 1) {
        state.audio_generation=2; strcpy(state.station,"between"); strcpy(state.title,"between title"); radio_aba_phase=2;
    }
    *out = *source;
}
bool radio_control_snapshot(radio_control_snapshot_t *out) {
    if (radio_unavailable) return false;
    if (radio_aba_phase == 2) {
        state.audio_generation=3; strcpy(state.station,"first"); strcpy(state.title,"final title"); radio_aba_phase=0;
    }
    if (change_radio_during_capture && capture_calls) {
        change_radio_during_capture = false;
        radio.item = 2; strcpy(radio.name, "second");
        strcpy(state.station, "second"); strcpy(state.title, "new generation"); state.audio_generation = 2;
    }
    *out = radio; return true;
}
native_input_health_t audio_service_input_health(void) { return input; }
uint8_t native_audio_output_get_volume(void) { return volume; }
int8_t native_audio_output_get_balance(void) { return balance; }
esp_err_t native_audio_settings_set_volume(uint8_t value) { ++command_calls; volume = value; return setting_failure ? ESP_FAIL : ESP_OK; }
esp_err_t native_audio_settings_set_balance(int8_t value) { ++command_calls; balance = value; return setting_failure ? ESP_FAIL : ESP_OK; }
bool native_audio_settings_get_normalization(void) { return normalization; }
uint8_t native_audio_settings_get_normalization_gain_db(void) { return gain; }
int8_t native_audio_settings_get_normalization_target_dbfs(void) { return target; }
uint16_t native_audio_settings_get_normalization_time_ms(void) { return normtime; }
esp_err_t native_audio_settings_set_normalization(bool value) { ++command_calls; normalization = value; return setting_failure ? ESP_FAIL : ESP_OK; }
esp_err_t native_audio_settings_set_normalization_gain_db(uint8_t value) { ++command_calls; if (setting_failure) return ESP_FAIL; gain = value; return ESP_OK; }
esp_err_t native_audio_settings_set_normalization_target_dbfs(int8_t value) { ++command_calls; if (setting_failure) return ESP_FAIL; target = value; return ESP_OK; }
esp_err_t native_audio_settings_set_normalization_time_ms(uint16_t value) { ++command_calls; if (setting_failure) return ESP_FAIL; normtime = value; return ESP_OK; }
esp_err_t radio_control_play(uint16_t item) { ++command_calls; radio.item = item; state.audio_pending = true; return setting_failure ? ESP_FAIL : ESP_OK; }
esp_err_t radio_control_stop(void) { ++command_calls; state.audio_running = state.audio_pending = false; return setting_failure ? ESP_FAIL : ESP_OK; }
esp_err_t radio_control_toggle(void) { ++command_calls; state.audio_pending = !state.audio_pending; return setting_failure ? ESP_FAIL : ESP_OK; }
esp_err_t radio_control_next(void) { ++command_calls; ++radio.item; return setting_failure ? ESP_FAIL : ESP_OK; }
esp_err_t radio_control_previous(void) { ++command_calls; --radio.item; return setting_failure ? ESP_FAIL : ESP_OK; }
esp_err_t radio_control_set_smartstart_enabled(bool value) { ++command_calls; if (setting_failure) return ESP_FAIL; radio.smartstart = value; return ESP_OK; }

esp_err_t httpd_register_uri_handler(httpd_handle_t server, const httpd_uri_t *route) {
    assert(server); if (registration_failure) return ESP_FAIL; registered_route = *route; return ESP_OK;
}
esp_err_t httpd_get_client_list(httpd_handle_t server, size_t *count, int *list) {
    assert(server == s_server); size_t capacity = *count; *count = 0;
    for (int i = 0; i < 16; ++i) if (sockets[i].live) { assert(*count < capacity); list[(*count)++] = i; }
    return ESP_OK;
}
httpd_ws_client_info_t httpd_ws_get_fd_info(httpd_handle_t server, int socket) {
    assert(server == s_server); if (!sockets[socket].live) return HTTPD_WS_CLIENT_INVALID;
    return sockets[socket].websocket ? HTTPD_WS_CLIENT_WEBSOCKET : HTTPD_WS_CLIENT_HTTP;
}
void *httpd_sess_get_ctx(httpd_handle_t server, int socket) { assert(server == s_server); return sockets[socket].live ? sockets[socket].context : NULL; }
void httpd_sess_set_ctx(httpd_handle_t server, int socket, void *context, httpd_free_ctx_fn_t free_context) {
    assert(server == s_server && sockets[socket].live);
    if (context_failure) return;
    if (sockets[socket].context && sockets[socket].free_context) sockets[socket].free_context(sockets[socket].context);
    sockets[socket].context = context; sockets[socket].free_context = free_context;
}
esp_err_t httpd_sess_set_send_override(httpd_handle_t server, int socket, httpd_send_func_t callback) {
    assert(server == s_server && sockets[socket].live);
    if (send_override_failure) return ESP_FAIL;
    sockets[socket].send_override = callback; return ESP_OK;
}
esp_err_t httpd_sess_set_recv_override(httpd_handle_t server, int socket, httpd_recv_func_t callback) {
    assert(server == s_server && sockets[socket].live);
    if (recv_override_failure) return ESP_FAIL;
    sockets[socket].recv_override = callback; return ESP_OK;
}
ssize_t lwip_recv(int socket, void *data, size_t size, int flags) {
    assert(sockets[socket].live && data && (flags & MSG_DONTWAIT));
    ++raw_receive_calls; last_receive_flags=(unsigned)flags; now_us += receive_advance_us;
    size_t available=wire_size-wire_position;
    if (receive_position < receive_length) {
        int value=receive_script[receive_position++];
        if (value < 0) { errno=-value; return -1; }
        if (!value) return 0;
        if ((size_t)value < size) size=(size_t)value;
    }
    if (size > available) size=available;
    memcpy(data,wire+wire_position,size);
    if (!(flags & MSG_PEEK)) wire_position += size;
    return (ssize_t)size;
}
ssize_t lwip_send(int socket, const void *data, size_t size, int flags) {
    assert(sockets[socket].live && data && (flags & MSG_DONTWAIT));
    ++raw_send_calls; now_us += io_advance_us;
    if (io_position < io_length) {
        int value = io_script[io_position++];
        if (value < 0) { errno = -value; return -1; }
        return (size_t)value > size ? (ssize_t)size : value;
    }
    return (ssize_t)size;
}
ssize_t native_web_transport_send(httpd_handle_t server, int socket, const void *data, size_t size, int flags, bool *writable) {
    assert(server == s_server); *writable = true;
    return lwip_send(socket, data, size, flags);
}
ssize_t native_web_transport_recv(httpd_handle_t server, int socket, void *data, size_t size, int flags, bool *writable) {
    assert(server == s_server); *writable = false;
    return lwip_recv(socket, data, size, flags);
}
void native_web_transport_shutdown(httpd_handle_t server, int socket, bool graceful) {
    assert(server == s_server); (void)graceful;
    (void)shutdown(socket, SHUT_RDWR);
}
int lwip_select(int highest, fd_set *readable, fd_set *writable, fd_set *exception, struct timeval *wait) {
    assert(highest > 0 && (!!readable != !!writable) && !exception && wait);
    ++select_calls;
    int result = select_position < select_length ? select_script[select_position++] : 1;
    if (result == 0) { now_us += (int64_t)wait->tv_sec * 1000000 + wait->tv_usec; return 0; }
    now_us += 1000;
    if (result < 0) { errno = -result; return -1; }
    return result;
}
esp_err_t httpd_queue_work(httpd_handle_t server, httpd_work_fn_t callback, void *argument) {
    assert(server == s_server); ++queue_calls; if (queue_failure) return ESP_FAIL;
    assert(!queued_work); queued_work = callback; queued_argument = argument; return ESP_OK;
}
int shutdown(int socket, int how) {
    assert(how == SHUT_RDWR && sockets[socket].live); ++shutdown_count;
    // shutdown does not close/release the fd. HTTPD owns subsequent cleanup.
    return 0;
}
esp_err_t httpd_ws_send_frame_async(httpd_handle_t server, int socket, httpd_ws_frame_t *frame) {
    assert(server == s_server && sockets[socket].live && sockets[socket].context);
    assert(frame->final && !frame->fragmented);
    assert(frame->len < WS_STATUS_BYTES);
    if (frame->type == HTTPD_WS_TYPE_TEXT) assert(frame->payload[frame->len] == 0);
    if (slow_send) {
        slow_send = false;
        char copy[WS_STATUS_BYTES]; strcpy(copy, (char *)frame->payload);
        for (unsigned i = 0; i < 10000; ++i) poll_status();
        websocket_service_notify_playlist_changed();
        strcpy(state.title, "changed during slow send");
        assert(!strcmp(copy, (char *)frame->payload));
    }
    if (socket == failed_socket) return ESP_FAIL;
    assert(sockets[socket].send_override);
    char header[4] = {0};
    // Pinned IDF checks only <0. The production override must hide positive
    // short writes by completing them before returning to these two calls.
    if (sockets[socket].send_override(server, socket, header, frame->len > 125 ? 4 : 2, 0) < 0 ||
        sockets[socket].send_override(server, socket, (char *)frame->payload, frame->len, 0) < 0) return ESP_FAIL;
    assert(delivery_count < 256);
    delivery_t *out = &deliveries[delivery_count++]; out->socket = socket; out->incarnation = sockets[socket].incarnation;
    out->type = frame->type; out->size = frame->len;
    if (frame->len) memcpy(out->text, frame->payload, frame->len);
    out->text[frame->len] = 0;
    return ESP_OK;
}
int httpd_req_to_sockfd(httpd_req_t *request) { return request->socket; }
esp_err_t httpd_resp_send_err(httpd_req_t *request, int status, const char *message) {
    assert(status == HTTPD_400_BAD_REQUEST && strstr(message, "upgrade"));
    assert(!sockets[request->socket].context);
    ++http_errors;
    return ESP_OK;
}
esp_err_t httpd_ws_recv_frame(httpd_req_t *request, httpd_ws_frame_t *frame, size_t maximum) {
    ++recv_calls; if (request->receive_error) return ESP_FAIL;
    if (!maximum) {
        frame->len = request->length; frame->type = request->type; frame->final = request->final; frame->fragmented = request->fragmented;
        if (request->transport_reads) {
            char header,mask[4];
            if (sockets[request->socket].recv_override(s_server,request->socket,&header,1,0) != 1 ||
                sockets[request->socket].recv_override(s_server,request->socket,mask,4,0) != 4) return ESP_FAIL;
        }
        return ESP_OK;
    }
    assert(maximum >= request->length);
    if (request->transport_reads) {
        if (sockets[request->socket].recv_override(s_server,request->socket,(char *)frame->payload,request->length,0) != (int)request->length) return ESP_FAIL;
    } else memcpy(frame->payload, request->payload, request->length);
    return ESP_OK;
}
int xTaskCreate(void (*entry)(void *), const char *name, unsigned stack, void *argument, unsigned priority, void *handle) {
    assert(!strcmp(name, "websocket_status") && stack == 2048 && !argument && priority == 2 && !handle);
    if (task_failure) return 0; task_entry = entry; return pdPASS;
}
void vTaskDelay(unsigned ticks) {
    assert(ticks == 1 || ticks == 10 || ticks == 100);
    if (ticks == 1) { ++transport_yields; now_us += 1000; }
    if (ticks == 100 && stop_task_after_delay) atomic_store(&s_running,false);
    if (!atomic_load(&s_running) && task_entry && !suspend_task_exit) { void (*entry)(void *) = task_entry; task_entry = NULL; entry(NULL); }
}
void vTaskDelete(void *task) { assert(!task); }

static void execute_work(void) {
    assert(queued_work);
    httpd_work_fn_t callback = queued_work; void *argument = queued_argument;
    queued_work = NULL; queued_argument = NULL;
    callback(argument);
}
static void cycle(void) { poll_status(); execute_work(); }
static void close_socket(int socket) {
    if (!sockets[socket].live) return;
    if (sockets[socket].free_context) sockets[socket].free_context(sockets[socket].context);
    sockets[socket].live = false; sockets[socket].context = NULL; sockets[socket].free_context = NULL;
    sockets[socket].send_override = NULL;
    sockets[socket].recv_override = NULL;
}
static void open_socket(int socket, bool websocket) {
    assert(!sockets[socket].live); ++sockets[socket].incarnation; sockets[socket].live = true; sockets[socket].websocket = websocket;
}
static void reset(void) {
    assert(websocket_service_stop() == ESP_OK);
    for (int i = 0; i < 16; ++i) close_socket(i);
    queued_work = NULL; // Models httpd_stop joining/discarding queued work.
    assert(websocket_service_server_stopped(s_server) == ESP_OK);
    memset(sockets, 0, sizeof(sockets)); memset(deliveries, 0, sizeof(deliveries)); memset(&state, 0, sizeof(state));
    memset(&radio, 0, sizeof(radio)); memset(&input, 0, sizeof(input));
    delivery_count = shutdown_count = queue_calls = capture_calls = command_calls = recv_calls = http_errors = 0;
    queue_failure = registration_failure = task_failure = radio_unavailable = setting_failure = slow_send = change_radio_during_capture = context_failure = send_override_failure = recv_override_failure = false;
    io_length = io_position = select_length = select_position = 0; raw_send_calls = select_calls = transport_yields = 0; io_advance_us = 0;
    radio_aba_phase=0; suspend_task_exit=stop_task_after_delay=false;
    receive_length=receive_position=wire_size=wire_position=raw_receive_calls=last_receive_flags=0; receive_advance_us=0;
    failed_socket = -1; volume = 192; balance = 0; gain = 20; target = -3; normtime = 5000; normalization = false; now_us = 0;
    radio.item = 1; radio.count = 10; strcpy(radio.name, "first"); strcpy(state.station, "first"); strcpy(state.title, "initial title");
    strcpy(state.stream_format, "MP3 44.1k 2ch"); state.audio_generation = 1; state.audio_running = true; state.bitrate_kbps = 128;
    input.available = true; input.ready = 4; input.target = 8;
    network_unavailable = false;
    network_view = (network_snapshot_t){.online=true,.rssi_valid=true,.rssi=-42};
    ++cases;
}
static void start(void) {
    assert(websocket_service_register((void *)1, &state) == ESP_OK);
    assert(!strcmp(registered_route.uri, "/ws") && registered_route.is_websocket && registered_route.handle_ws_control_frames);
    assert(websocket_service_start() == ESP_OK);
}
static esp_err_t command_bytes(int socket, const char *text, size_t length) {
    httpd_req_t request = {.socket = socket, .method = HTTP_POST, .payload = text, .length = length,
        .type = HTTPD_WS_TYPE_TEXT, .final = true};
    return registered_route.handler(&request);
}
static esp_err_t frame_bytes(int socket, httpd_ws_type_t type, bool final,
                              const void *payload, size_t length) {
    httpd_req_t request = {.socket=socket, .method=HTTP_POST,
        .payload=payload, .length=length, .type=type, .final=final};
    return registered_route.handler(&request);
}
static void command(const char *text) { assert(command_bytes(7, text, strlen(text)) == ESP_OK); }
static esp_err_t transport_command(const char *text) {
    wire[0]=0; memset(wire+1,0,4); memcpy(wire+5,text,strlen(text)); wire_size=5+strlen(text); wire_position=0;
    httpd_req_t request={.socket=7,.method=HTTP_DELETE,.payload=text,.length=strlen(text),.type=HTTPD_WS_TYPE_TEXT,.final=true,.transport_reads=true};
    return registered_route.handler(&request);
}
static const char *last_text(void) { assert(delivery_count); return deliveries[delivery_count - 1].text; }
static bool contains_delivery(unsigned first, int socket, const char *text) {
    for (unsigned i = first; i < delivery_count; ++i) if (deliveries[i].socket == socket && strstr(deliveries[i].text, text)) return true;
    return false;
}
static void *producer(void *argument) {
    (void)argument;
    for (unsigned i = 0; i < 20000; ++i) { poll_status(); websocket_service_notify_playlist_changed(); }
    return NULL;
}

static void status_key_comparison_regressions(void) {
    reset(); start(); open_socket(7, true); cycle();
    unsigned char members[sizeof(ws_status_key_t)] = {0};
#define MARK_MEMBER(member) memset(members + offsetof(ws_status_key_t, member), 1, sizeof(s_previous.member))
    MARK_MEMBER(generation); MARK_MEMBER(bitrate);
    MARK_MEMBER(item); MARK_MEMBER(count);
    MARK_MEMBER(volume); MARK_MEMBER(fill); MARK_MEMBER(balance); MARK_MEMBER(rssi);
    MARK_MEMBER(running); MARK_MEMBER(pending); MARK_MEMBER(smartstart); MARK_MEMBER(normalization);
    MARK_MEMBER(rssi_valid); MARK_MEMBER(network_online); MARK_MEMBER(ap_enabled);
    MARK_MEMBER(normgain); MARK_MEMBER(normtarget); MARK_MEMBER(normtime);
    MARK_MEMBER(station); MARK_MEMBER(name); MARK_MEMBER(title); MARK_MEMBER(format);
#undef MARK_MEMBER
    unsigned padding = 0;
    unsigned char *bytes = (unsigned char *)&s_previous;
    for (size_t i = 0; i < sizeof(members); ++i) {
        if (!members[i]) { bytes[i] ^= 0xffU; ++padding; }
    }
    assert(padding && "fixture must exercise real status-key padding");
    uint32_t revision = s_status_revision;
    unsigned delivered = delivery_count;
    cycle();
    assert(s_status_revision == revision && "padding alone must not publish status");
    assert(delivery_count == delivered && "padding alone must not send status");
#define CHANGE_STRING_TAIL(member) do { \
    size_t end = strlen(s_previous.member); \
    assert(end + 1U < sizeof(s_previous.member)); \
    s_previous.member[end + 1U] = 'x'; \
} while (0)
    CHANGE_STRING_TAIL(station); CHANGE_STRING_TAIL(name);
    CHANGE_STRING_TAIL(title); CHANGE_STRING_TAIL(format);
#undef CHANGE_STRING_TAIL
    cycle();
    assert(s_status_revision == revision && "string tails must not publish status");
    assert(delivery_count == delivered && "string tails must not send status");

#define CHECK_MEMBER(member, value) do { \
    s_previous.member = (value); \
    revision = s_status_revision; \
    assert(prepare_status()); \
    assert(s_status_revision == revision + 1U && "each status-key member must trigger revision"); \
} while (0)
    CHECK_MEMBER(generation, s_previous.generation + 1U);
    CHECK_MEMBER(bitrate, s_previous.bitrate + 1U);
    CHECK_MEMBER(item, s_previous.item + 1U);
    CHECK_MEMBER(count, s_previous.count + 1U);
    CHECK_MEMBER(volume, s_previous.volume + 1U);
    CHECK_MEMBER(fill, s_previous.fill + 1U);
    CHECK_MEMBER(balance, s_previous.balance + 1);
    CHECK_MEMBER(rssi, s_previous.rssi + 1);
    CHECK_MEMBER(running, !s_previous.running);
    CHECK_MEMBER(pending, !s_previous.pending);
    CHECK_MEMBER(smartstart, !s_previous.smartstart);
    CHECK_MEMBER(normalization, !s_previous.normalization);
    CHECK_MEMBER(rssi_valid, !s_previous.rssi_valid);
    CHECK_MEMBER(network_online, !s_previous.network_online);
    CHECK_MEMBER(ap_enabled, !s_previous.ap_enabled);
    CHECK_MEMBER(normgain, s_previous.normgain + 1U);
    CHECK_MEMBER(normtarget, s_previous.normtarget + 1);
    CHECK_MEMBER(normtime, s_previous.normtime + 1U);
#undef CHECK_MEMBER
#define CHECK_STRING(member) do { \
    s_previous.member[0] ^= 1; \
    revision = s_status_revision; \
    assert(prepare_status()); \
    assert(s_status_revision == revision + 1U && "each status-key string must trigger revision"); \
} while (0)
    CHECK_STRING(station); CHECK_STRING(name); CHECK_STRING(title); CHECK_STRING(format);
#undef CHECK_STRING
    printf("PASS status key: %u padding bytes ignored, 18 scalar and 4 string changes detected\n", padding);
}

int main(void) {
    status_key_comparison_regressions();
    reset(); start(); open_socket(7, false);
    httpd_req_t ordinary_get = {.socket = 7, .method = HTTP_GET};
    assert(registered_route.handler(&ordinary_get) == ESP_OK && http_errors == 1);
    assert(!sockets[7].context && !delivery_count && !command_calls);

    // Actual IDF dispatch consumes upgrade GET itself, calls the post-handshake
    // hook, then reads the first opcode before ever invoking the URI handler.
    // Do not run the periodic producer or invoke the URI handler as HTTP_GET.
    reset(); start(); open_socket(7, true);
    assert(registered_route.ws_post_handshake_cb);
    httpd_req_t upgrade = {.socket = 7, .method = HTTP_GET};
    assert(!sockets[7].send_override && !sockets[7].recv_override);
    assert(registered_route.ws_post_handshake_cb(&upgrade) == ESP_OK);
    assert(sockets[7].send_override && sockets[7].recv_override && !delivery_count);
    wire[0] = 0x81; wire_size = 1;
    receive_script[0] = -EAGAIN; receive_script[1] = 1; receive_length = 2;
    select_script[0] = 1; select_length = 1;
    char opcode;
    assert(sockets[7].recv_override(s_server, 7, &opcode, 1, 0) == 1 && opcode == (char)0x81);
    assert(transport_command("volume=3") == ESP_OK && volume == 3);

    reset(); start(); open_socket(7, true); open_socket(8, true); open_socket(9, true);
    upgrade.socket = 7; assert(registered_route.ws_post_handshake_cb(&upgrade) == ESP_OK);
    upgrade.socket = 8; assert(registered_route.ws_post_handshake_cb(&upgrade) == ESP_OK);
    upgrade.socket = 9; assert(registered_route.ws_post_handshake_cb(&upgrade) == ESP_ERR_NO_MEM && !sockets[9].context);

    reset(); assert(websocket_service_register((void *)1, &state) == ESP_OK);
    open_socket(7, true); upgrade.socket = 7;
    assert(registered_route.ws_post_handshake_cb(&upgrade) == ESP_ERR_INVALID_STATE && !sockets[7].context);

    reset(); start(); open_socket(7, false);
    upgrade.socket = 7;
    assert(registered_route.ws_pre_handshake_cb);
    assert(registered_route.ws_pre_handshake_cb(&upgrade) == ESP_OK);
    io_script[0] = 1; io_length = 1;
    assert(sockets[7].send_override(s_server, 7, "HTTP/1.1 101", 12, 0) == 12 && raw_send_calls == 2);
    sockets[7].websocket = true;
    assert(registered_route.ws_post_handshake_cb(&upgrade) == ESP_OK);

    reset(); start(); open_socket(7, true); cycle();
    unsigned commands_before = command_calls;
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, "volume=", 7) == ESP_OK && command_calls == commands_before);
    const uint8_t ping_data[] = {0, 0x81, 0xff};
    assert(frame_bytes(7, HTTPD_WS_TYPE_PING, true, ping_data, sizeof(ping_data)) == ESP_OK);
    assert(deliveries[delivery_count-1].type == HTTPD_WS_TYPE_PONG && deliveries[delivery_count-1].size == sizeof(ping_data));
    assert(!memcmp(deliveries[delivery_count-1].text, ping_data, sizeof(ping_data)));
    assert(frame_bytes(7, HTTPD_WS_TYPE_CONTINUE, true, "3", 1) == ESP_OK && volume == 3 && command_calls == commands_before+1);

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, "\xf0\x9f", 2) == ESP_OK);
    assert(frame_bytes(7, HTTPD_WS_TYPE_CONTINUE, true, "\x98\x80", 2) == ESP_OK && !s_clients[0].closing);

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, true, "\xc0\xaf", 2) == ESP_FAIL);
    assert(deliveries[delivery_count-1].type == HTTPD_WS_TYPE_CLOSE && (uint8_t)deliveries[delivery_count-1].text[1] == 0xef); // 1007

    reset(); start(); open_socket(7, true); cycle();
    // An invalid prefix cannot become valid by adding continuation bytes.
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, "\xf5", 1) == ESP_FAIL);
    assert((uint8_t)deliveries[delivery_count-1].text[1] == 0xef);

    reset(); start(); open_socket(7, true); cycle();
    char bounded[WS_COMMAND_LIMIT]; memset(bounded, 'x', sizeof(bounded));
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, bounded, 48) == ESP_OK);
    assert(frame_bytes(7, HTTPD_WS_TYPE_CONTINUE, true, bounded, 48) == ESP_OK);
    assert(!s_clients[0].closing && strstr(last_text(), "commandError"));

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, bounded, sizeof(bounded)) == ESP_OK);
    assert(frame_bytes(7, HTTPD_WS_TYPE_CONTINUE, true, "x", 1) == ESP_FAIL);
    assert((uint8_t)deliveries[delivery_count-1].text[1] == 0xf1); // 1009

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, "volume=", 7) == ESP_OK);
    close_socket(7); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, true, "ping", 4) == ESP_OK);
    assert(!command_calls && !strcmp(last_text(), "{\"pong\":1}"));

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_CONTINUE, true, "ping", 4) == ESP_FAIL);
    assert((uint8_t)deliveries[delivery_count-1].text[1] == 0xea); // 1002

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, "pi", 2) == ESP_OK);
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, true, "ping", 4) == ESP_FAIL);

    reset(); start(); open_socket(7, true); cycle();
    const uint8_t close_data[] = {3, 0xe8, 'o', 'k'};
    sockets[7].websocket = false; // SDK marks Close before dispatching handler.
    assert(frame_bytes(7, HTTPD_WS_TYPE_CLOSE, true, close_data, sizeof(close_data)) == ESP_OK);
    assert(deliveries[delivery_count-1].type == HTTPD_WS_TYPE_CLOSE && !memcmp(deliveries[delivery_count-1].text, close_data, sizeof(close_data)));
    assert(send_text(&s_clients[0], "after Close") == ESP_ERR_INVALID_STATE);

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_CLOSE, true, "x", 1) == ESP_FAIL);

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_BINARY, true, "binary", 6) == ESP_FAIL);
    assert((uint8_t)deliveries[delivery_count-1].text[1] == 0xeb); // 1003, text-only radio application

    reset(); start(); open_socket(7, true); cycle();
    assert(frame_bytes(7, HTTPD_WS_TYPE_TEXT, false, "pi", 2) == ESP_OK);
    now_us = WS_MESSAGE_BUDGET_US; cycle();
    assert(s_clients[0].closing && deliveries[delivery_count-1].type == HTTPD_WS_TYPE_CLOSE && (uint8_t)deliveries[delivery_count-1].text[1] == 0xf0); // 1008

    reset();
    assert(websocket_service_register(NULL, &state) == ESP_ERR_INVALID_ARG);
    assert(websocket_service_start() == ESP_ERR_INVALID_STATE);
    registration_failure = true;
    assert(websocket_service_register((void *)1, &state) == ESP_FAIL);
    assert(!s_server);

    reset(); start();
    open_socket(7, true); open_socket(8, true); open_socket(9, false);
    cycle(); assert(delivery_count == 6 && !sockets[9].context);
    assert(contains_delivery(0, 7, "\"current\":1") && contains_delivery(0, 8, "\"current\":1"));
    assert(contains_delivery(0, 7, "\"status\":{\"station\":\"first\"") && contains_delivery(0, 7, "\"heap\",\"value\":50"));
    unsigned first = delivery_count; cycle(); assert(delivery_count == first);
    now_us = WS_HEARTBEAT_US - 1; cycle(); assert(delivery_count == first);
    now_us++; cycle(); assert(delivery_count == first + 2);
    first = delivery_count; strcpy(state.title, "new title"); cycle(); assert(delivery_count == first + 2);
    first = delivery_count; radio.item = 4; cycle(); assert(delivery_count == first + 4);
    first = delivery_count; websocket_service_notify_playlist_changed(); cycle();
    assert(delivery_count == first + 2 && contains_delivery(first, 7, "\"file\":\"/data/playlist.csv\""));

    reset(); start(); open_socket(7, true); poll_status();
    strcpy(state.title, "latest before callback");
    for (unsigned i = 0; i < 10000; ++i) poll_status();
    assert(queue_calls == 1); execute_work(); assert(strstr(deliveries[0].text, "latest before callback"));
    first = delivery_count; slow_send = true; now_us = WS_HEARTBEAT_US; cycle();
    assert(queue_calls == 2); cycle(); assert(contains_delivery(first, 7, "changed during slow send"));

    reset(); start(); open_socket(7, true); cycle(); poll_status();
    close_socket(7); open_socket(7, true); strcpy(state.title, "reconnected"); state.audio_generation = 99;
    first = delivery_count; execute_work(); assert(delivery_count == first + 3);
    assert(deliveries[first].incarnation == 2 && strstr(deliveries[first].text, "reconnected") && strstr(deliveries[first].text, "\"generation\":99"));

    reset(); start(); open_socket(7, true); open_socket(8, true); failed_socket = 7; cycle();
    assert(shutdown_count == 1 && contains_delivery(0, 8, "initial title") && !contains_delivery(0, 7, "initial title"));
    failed_socket = -1; close_socket(7); open_socket(7, true); first = delivery_count; cycle();
    assert(shutdown_count == 1 && deliveries[first].incarnation == 2);

    reset(); start(); open_socket(7, true); open_socket(8, true); open_socket(9, true); cycle();
    assert(shutdown_count == 1 && !sockets[9].context && delivery_count == 6);
    close_socket(7); close_socket(9); open_socket(9, true); cycle(); assert(sockets[9].context);

    reset(); assert(websocket_service_register((void *)1, &state) == ESP_OK); open_socket(7, true);
    assert(command_bytes(7, "volume=1", 8) == ESP_ERR_INVALID_STATE && !command_calls);
    task_failure = true; assert(websocket_service_start() == ESP_ERR_NO_MEM); assert(websocket_service_stop() == ESP_OK);
    assert(websocket_service_server_stopped((void *)1) == ESP_OK);

    reset(); start(); open_socket(7, true); poll_status(); assert(websocket_service_stop() == ESP_OK);
    execute_work(); assert(!delivery_count);
    assert(websocket_service_server_stopped((void *)2) == ESP_ERR_INVALID_ARG);
    close_socket(7); assert(websocket_service_server_stopped((void *)1) == ESP_OK);
    start(); open_socket(7, true); cycle(); assert(delivery_count == 3);

    reset(); start(); queue_failure = true; poll_status(); assert(!atomic_load(&s_work_pending) && !queued_work);
    queue_failure = false; open_socket(7, true); cycle(); assert(delivery_count == 3);

    reset(); start(); open_socket(7, true); context_failure = true; cycle();
    assert(!s_clients[0].used && !s_clients[1].used && shutdown_count == 1);
    close_socket(7); context_failure = false; open_socket(8, true); cycle(); assert(delivery_count == 3);

    reset(); start(); open_socket(7, true); send_override_failure = true; cycle();
    assert(!s_clients[0].used && !s_clients[1].used && !sockets[7].context && shutdown_count == 1);
    close_socket(7); send_override_failure = false; open_socket(8, true); cycle(); assert(delivery_count == 3);

    reset(); start(); open_socket(7,true); recv_override_failure=true; cycle();
    assert(!s_clients[0].used && !s_clients[1].used && !sockets[7].context && shutdown_count == 1);
    close_socket(7); recv_override_failure=false; open_socket(8,true); cycle(); assert(delivery_count == 3 && sockets[8].recv_override);

    reset(); start(); open_socket(7, false); cycle(); assert(!capture_calls && !delivery_count);

    reset(); start(); open_socket(7, true); radio_unavailable = true; cycle(); assert(!delivery_count);
    radio_unavailable = false; change_radio_during_capture = true; cycle();
    assert(capture_calls >= 2 && strstr(deliveries[0].text, "new generation") && strstr(deliveries[1].text, "\"current\":2"));

    reset(); start(); open_socket(7,true); radio_aba_phase=1; cycle();
    assert(strstr(deliveries[0].text,"final title") && !strstr(deliveries[0].text,"between title") && strstr(deliveries[1].text,"\"current\":1"));

    reset(); start();
    void (*entry)(void *)=task_entry; task_entry=NULL; stop_task_after_delay=true; entry(NULL);
    assert(!atomic_load(&s_task_alive) && queued_work && websocket_service_stop() == ESP_OK);
    execute_work(); assert(!delivery_count);

    reset(); start(); suspend_task_exit=true;
    assert(websocket_service_stop() == ESP_ERR_TIMEOUT && websocket_service_server_stopped((void *)1) == ESP_ERR_INVALID_STATE);
    suspend_task_exit=false; assert(websocket_service_stop() == ESP_OK);

    reset(); start(); open_socket(7, true); cycle();
    const char *valid[] = {"ping", "getindex=1", "getsystem", "getactive", "play=65535", "stop=1", "toggle", "prev", "next=1",
        "smartstart=1", "volume=254", "balance=-16", "normalization=1", "normgain=20", "normtarget=-20", "normtime=10000",
        "submitplaylist=1", "submitplaylistdone=1"};
    for (size_t i = 0; i < sizeof(valid) / sizeof(valid[0]); ++i) { first = delivery_count; command(valid[i]);
        for (unsigned j = first; j < delivery_count; ++j) assert(!strstr(deliveries[j].text, "commandError")); }
    assert(volume == 254 && balance == -16 && normalization && gain == 20 && target == -20 && normtime == 10000);
    const char *invalid[] = {"play=0", "play=-1", "play=65536", "play=42949672960000000000", "play=1junk", "play=+1",
        "volume=255", "volume=-1", "volume=-0", "volume=1=2", "balance=-17", "smartstart=2", "smartstart=-0", "normalization=2", "normgain=21", "normtarget=1",
        "normtarget=-21", "normtime=99", "normtime=10001", "normtime=", "reboot=1", "brightness=100", "eq=3", "getindex=bad", ""};
    unsigned operations = command_calls;
    for (size_t i = 0; i < sizeof(invalid) / sizeof(invalid[0]); ++i) { command(invalid[i]); assert(strstr(last_text(), "commandError")); }
    assert(command_calls == operations);
    setting_failure = true; command("normalization=0"); assert(strstr(last_text(), "Operation failed") && !normalization);
    command("volume=5"); assert(strstr(last_text(), "Operation failed") && volume == 5);
    command("balance=7"); assert(strstr(last_text(), "Operation failed") && balance == 7);
    unsigned received = recv_calls; command(""); assert(recv_calls == received + 1);
    operations = command_calls;
    assert(command_bytes(7, "ping\0volume=0", 13) == ESP_OK);
    assert(strstr(last_text(), "commandError") && command_calls == operations);
    char oversized[WS_COMMAND_LIMIT + 1]; memset(oversized, 'x', sizeof(oversized));
    assert(command_bytes(7, oversized, sizeof(oversized)) == ESP_FAIL);
    assert(deliveries[delivery_count-1].type == HTTPD_WS_TYPE_CLOSE);
    reset(); start(); open_socket(7, true); cycle();
    httpd_req_t fragmented = {.socket=7,.method=HTTP_POST,.payload="ping",.length=4,.type=HTTPD_WS_TYPE_TEXT,.final=false};
    assert(registered_route.handler(&fragmented) == ESP_OK);
    fragmented.final=true; fragmented.type=HTTPD_WS_TYPE_CONTINUE;
    assert(registered_route.handler(&fragmented) == ESP_OK); // Completed "pingping" is an unknown command.
    fragmented.type=HTTPD_WS_TYPE_PONG;
    unsigned pong_recv = recv_calls; assert(registered_route.handler(&fragmented) == ESP_OK && recv_calls == pong_recv + 2);
    fragmented.length = 0; pong_recv = recv_calls;
    assert(registered_route.handler(&fragmented) == ESP_OK && recv_calls == pong_recv + 1);

    reset(); start(); open_socket(7, true); cycle();
    io_script[0]=1; io_script[1]=1; io_script[2]=2; io_script[3]=3; io_length=4;
    unsigned raw_before = raw_send_calls;
    assert(send_text(&s_clients[0], "short") == ESP_OK && raw_send_calls == raw_before + 4 && io_position == 4);
    io_position=0; io_length=2; io_script[0]=-EAGAIN; io_script[1]=-EINTR;
    select_script[0]=-EINTR; select_script[1]=1; select_length=2;
    assert(send_text(&s_clients[0], "retry") == ESP_OK && select_calls == 2 && transport_yields == 2);
    assert(!s_clients[0].frame_deadline_us);

    reset(); start(); open_socket(7, true); open_socket(8, true); cycle();
    io_script[0]=-EAGAIN; io_length=1; select_script[0]=0; select_length=1;
    first=delivery_count; now_us=0;
    assert(send_text(&s_clients[0], "timeout") == ESP_FAIL && now_us == WS_FRAME_BUDGET_US && shutdown_count == 1);
    assert(delivery_count == first && send_text(&s_clients[1], "healthy") == ESP_OK);

    reset(); start(); open_socket(7, true); cycle();
    io_script[0]=-EPIPE; io_length=1;
    assert(send_text(&s_clients[0], "broken") == ESP_FAIL && !select_calls && shutdown_count == 1);

    reset(); start(); open_socket(7, true); cycle();
    io_script[0]=0; io_length=1;
    assert(send_text(&s_clients[0], "closed") == ESP_FAIL && shutdown_count == 1);

    reset(); start(); open_socket(7, true); cycle();
    io_advance_us = WS_FRAME_BUDGET_US / 2 + 1; raw_before=raw_send_calls;
    assert(send_text(&s_clients[0], "shared deadline") == ESP_FAIL && raw_send_calls == raw_before + 2 && shutdown_count == 1);

    reset(); start(); open_socket(7, true); cycle();
    for (unsigned i=0;i<32;++i) { io_script[i]=-EAGAIN; select_script[i]=1; }
    io_length=select_length=32; io_advance_us=WS_FRAME_BUDGET_US/8;
    assert(send_text(&s_clients[0], "spurious readiness") == ESP_FAIL && transport_yields && raw_send_calls < 40);

    reset(); start(); open_socket(7, true); cycle();
    io_script[0]=-EAGAIN; io_length=1; select_script[0]=-EBADF; select_length=1;
    assert(send_text(&s_clients[0], "select failure") == ESP_FAIL && shutdown_count == 1);

    reset(); start(); open_socket(7, true); cycle();
    io_script[0]=-EAGAIN; io_length=1; select_script[0]=0; select_length=1; now_us=0;
    assert(!s_clients[0].frame_deadline_us);
    assert(sockets[7].send_override(s_server,7,"pong",4,0) == HTTPD_SOCK_ERR_TIMEOUT && now_us == WS_FRAME_BUDGET_US);

    reset(); start(); open_socket(7,true); cycle();
    receive_length=9; for(unsigned i=0;i<receive_length;++i) receive_script[i]=1;
    assert(transport_command("ping") == ESP_OK && raw_receive_calls == 9 && !strcmp(last_text(),"{\"pong\":1}"));
    assert(!s_clients[0].receive_deadline_us);

    reset(); start(); open_socket(7,true); cycle();
    receive_script[0]=-EAGAIN; receive_script[1]=-EINTR; receive_length=2;
    select_script[0]=-EINTR; select_script[1]=1; select_length=2;
    assert(transport_command("volume=3") == ESP_OK && volume == 3 && select_calls == 2 && transport_yields == 2);
    assert(!s_clients[0].receive_deadline_us);

    reset(); start(); open_socket(7,true); open_socket(8,true); cycle();
    receive_script[0]=-EAGAIN; receive_length=1; select_script[0]=0; select_length=1;
    assert(transport_command("volume=3") == ESP_FAIL && now_us == WS_FRAME_BUDGET_US && !command_calls && !s_clients[0].receive_deadline_us);
    close_socket(7); first=delivery_count; strcpy(state.title,"healthy after receive timeout"); cycle();
    assert(contains_delivery(first,8,"healthy after receive timeout"));

    reset(); start(); open_socket(7,true); cycle();
    receive_advance_us=100001; receive_length=64; for(unsigned i=0;i<receive_length;++i) receive_script[i]=1;
    assert(transport_command("volume=000000000000000000000000000000000000000003") == ESP_FAIL &&
        raw_receive_calls == 10 && now_us <= WS_FRAME_BUDGET_US+100001 && !command_calls && !s_clients[0].receive_deadline_us);

    reset(); start(); open_socket(7,true); cycle(); receive_advance_us=400000;
    assert(transport_command("volume=3") == ESP_FAIL && raw_receive_calls == 3 && !command_calls && !s_clients[0].receive_deadline_us);

    reset(); start(); open_socket(7,true); cycle(); receive_script[0]=0; receive_length=1;
    assert(transport_command("volume=3") == ESP_FAIL && !command_calls && !s_clients[0].receive_deadline_us);

    reset(); start(); open_socket(7,true); cycle(); receive_script[0]=-ECONNRESET; receive_length=1;
    assert(transport_command("volume=3") == ESP_FAIL && !select_calls && !command_calls && !s_clients[0].receive_deadline_us);

    reset(); start(); open_socket(7,true); cycle(); receive_script[0]=-EAGAIN; receive_length=1; select_script[0]=-EBADF; select_length=1;
    assert(transport_command("volume=3") == ESP_FAIL && !command_calls && !s_clients[0].receive_deadline_us);

    reset(); start(); open_socket(7,true); cycle();
    memcpy(wire,"abcdef",6); wire_size=6; receive_script[0]=2; receive_length=1;
    char peek[4]={0}; assert(sockets[7].recv_override(s_server,7,peek,4,MSG_PEEK) == 2 && !memcmp(peek,"ab",2) && !wire_position);
    assert(last_receive_flags & MSG_PEEK);
    assert(sockets[7].recv_override(s_server,7,peek,4,0) == 4 && !memcmp(peek,"abcd",4) && wire_position == 4);

    reset(); start(); open_socket(7,true); cycle();
    receive_script[0]=-EAGAIN; receive_length=1; select_script[0]=0; select_length=1;
    assert(!s_clients[0].receive_deadline_us);
    assert(sockets[7].recv_override(s_server,7,peek,1,0) == HTTPD_SOCK_ERR_TIMEOUT && now_us == WS_FRAME_BUDGET_US);

    reset(); start(); open_socket(7, true); cycle();
    pthread_t left, right; assert(!pthread_create(&left, NULL, producer, NULL)); assert(!pthread_create(&right, NULL, producer, NULL));
    pthread_join(left, NULL); pthread_join(right, NULL); assert(queue_calls == 2); execute_work();
    assert(contains_delivery(3, 7, "\"file\":"));

    reset(); start(); open_socket(7, true);
    memset(state.station, '\1', sizeof(state.station) - 1); state.station[sizeof(state.station) - 1] = 0;
    memset(state.title, '\2', sizeof(state.title) - 1); state.title[sizeof(state.title) - 1] = 0;
    memset(state.stream_format, '\3', sizeof(state.stream_format) - 1); state.stream_format[sizeof(state.stream_format) - 1] = 0;
    memset(radio.name, '\4', sizeof(radio.name) - 1); radio.name[sizeof(radio.name) - 1] = 0;
    state.bitrate_kbps = UINT32_MAX; state.audio_generation = UINT32_MAX; state.audio_pending = true;
    network_view.rssi = INT8_MIN;
    state.wifi_rssi = INT8_MIN; volume = UINT8_MAX; balance = INT8_MIN; input.ready = UINT32_MAX - 1; input.target = UINT32_MAX;
    radio.item=radio.count=UINT16_MAX; radio.smartstart=normalization=true; gain=UINT8_MAX; target=INT8_MIN; normtime=UINT16_MAX;
    cycle(); printf("WS_MAX=%s\n", deliveries[0].text); printf("WS_MAX_BYTES=%zu\n", strlen(deliveries[0].text));
    assert(strlen(deliveries[0].text) < WS_STATUS_BYTES);
    memset(state.title, 0, sizeof(state.title)); strcpy(state.title, "broken \xc0\xaf utf8 \xe2\x82");
    cycle(); assert(strstr(deliveries[3].text, "\\ufffd"));
#if TEST_NETWORK_STATUS
    reset(); start(); open_socket(7, true); cycle();
    assert(strstr(s_status, "\"rssi_valid\":true") && strstr(s_status, "\"rssi\":-42"));
    network_view.rssi_valid=false; network_view.rssi=-70; cycle();
    assert(strstr(s_status, "\"rssi_valid\":false") && strstr(s_status, "\"rssi\":0"));
    network_view.ap_enabled=true; network_view.online=false; cycle();
    assert(strstr(s_status, "\"ap_enabled\":true") && strstr(s_status, "\"network_online\":false"));
    unsigned before_network_failure=delivery_count;
    network_unavailable=true; cycle(); assert(delivery_count==before_network_failure);
    network_unavailable=false; network_view.online=true; network_view.rssi_valid=true;
    network_view.rssi=-30; cycle(); assert(delivery_count>before_network_failure);
    assert(strstr(s_status, "\"rssi_valid\":true") && strstr(s_status, "\"rssi\":-30"));
    assert(websocket_service_stop()==ESP_OK);
    for(int i=0;i<16;++i)close_socket(i);
#endif
    printf("PASS CYD WebSocket core: %u fixture groups, two clients, bounded async work, fd reuse, malformed commands, maximum JSON\n", cases);
    reset();
    return 0;
}
