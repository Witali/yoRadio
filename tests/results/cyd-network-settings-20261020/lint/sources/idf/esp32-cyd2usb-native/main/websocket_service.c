#include "websocket_service.h"

#include <stdatomic.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>

#include "sdkconfig.h"
#include "audio_service.h"
#include "esp_timer.h"
#include "freertos/task.h"
#include "json_buffer.h"
#include "lwip/sockets.h"
#include "native_audio_output.h"
#include "native_audio_settings.h"
#include "radio_control.h"
#include "network_status.h"
#include "websocket_message.h"
#include "native_web_transport.h"

#if !CONFIG_HTTPD_WS_SUPPORT
#error "CYD WebSocket service requires CONFIG_HTTPD_WS_SUPPORT=y"
#endif
#if !CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT
#error "CYD WebSocket transport requires the public post-handshake callback"
#endif
#if !CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT
#error "CYD WebSocket service requires the pre-handshake callback"
#endif
#if CONFIG_HTTPD_QUEUE_WORK_BLOCKING
#error "CYD WebSocket producer requires CONFIG_HTTPD_QUEUE_WORK_BLOCKING=n"
#endif

#define WS_CLIENT_LIMIT 2U
#define WS_COMMAND_LIMIT 96U
#define WS_STATUS_BYTES 5120U
#define WS_POLL_MS 100U
#define WS_HEARTBEAT_US 2000000LL
#define WS_TASK_STACK 2048U
#define WS_FRAME_BUDGET_US 1000000LL
#define WS_MESSAGE_BUDGET_US 5000000ULL

typedef struct {
    bool used, closing, initialized;
    int socket;
    uint32_t status_revision, playlist_revision;
    uint16_t item;
    int64_t sent_us;
    int64_t frame_deadline_us;
    int64_t receive_deadline_us;
    websocket_message_t message;
    uint8_t command[WS_COMMAND_LIMIT + 1U];
} ws_client_t;

typedef struct {
    uint32_t generation, bitrate;
    uint16_t item, count;
    uint8_t volume, fill;
    int8_t balance, rssi;
    bool running, pending, smartstart, normalization;
    bool rssi_valid, network_online, ap_enabled;
    uint8_t normgain;
    int8_t normtarget;
    uint16_t normtime;
    char station[96], name[144], title[192], format[48];
} ws_status_key_t;

static httpd_handle_t s_server;
static native_state_t *s_state;
static atomic_bool s_running, s_task_alive, s_work_pending;
static atomic_uint s_playlist_revision;
// Only the HTTPD task touches these objects. Queued work contains no payload or
// captured fd, and every send completes before this workspace is reused.
static ws_client_t s_clients[WS_CLIENT_LIMIT];
static ws_status_key_t s_previous, s_current;
static bool s_have_previous;
static uint32_t s_status_revision;
static char s_status[WS_STATUS_BYTES];
static int s_sockets[CONFIG_LWIP_MAX_SOCKETS];

static void session_free(void *context) {
    ws_client_t *client = context;
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) {
        if (client == &s_clients[i]) {
            memset(client, 0, sizeof(*client));
            break;
        }
    }
}

static bool current_client(const ws_client_t *client) {
    return client && client->used && !client->closing &&
        httpd_sess_get_ctx(s_server, client->socket) == client;
}

static int send_complete_frame_bytes(httpd_handle_t server, int socket, const char *data, size_t size, int flags) {
    ws_client_t *client = NULL;
    void *context = httpd_sess_get_ctx(server, socket);
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) if (context == &s_clients[i]) client = &s_clients[i];
    if (!client || !current_client(client)) return HTTPD_SOCK_ERR_FAIL;
    // Application frames share one deadline across IDF's header and payload
    // writes. SDK-generated PONG/CLOSE writes each get a finite fallback budget.
    int64_t deadline = client->frame_deadline_us ? client->frame_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t written = 0;
    while (written < size) {
        if (!atomic_load(&s_running)) return HTTPD_SOCK_ERR_FAIL;
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t sent = native_web_transport_send(server, socket,
            data + written, size - written, flags | MSG_DONTWAIT, &writable);
        if (sent > 0) {
            if ((size_t)sent > size - written) return HTTPD_SOCK_ERR_FAIL;
            written += (size_t)sent;
            continue;
        }
        if (!sent || (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR)) return HTTPD_SOCK_ERR_FAIL;
        int64_t remaining = deadline - esp_timer_get_time();
        if (remaining <= 0) return HTTPD_SOCK_ERR_TIMEOUT;
        struct timeval wait = {.tv_sec = (long)(remaining / 1000000LL), .tv_usec = (long)(remaining % 1000000LL)};
        fd_set writable_set;
        FD_ZERO(&writable_set); FD_SET(socket, &writable_set);
        // Use lwIP directly: CYD intentionally has CONFIG_VFS_SUPPORT_SELECT=n.
        int ready = lwip_select(socket + 1, writable ? NULL : &writable_set,
                               writable ? &writable_set : NULL, NULL, &wait);
        if (!ready) return HTTPD_SOCK_ERR_TIMEOUT;
        if (ready < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
        // Yield after no progress, including spurious readiness/EINTR, so a slow
        // peer cannot turn the HTTPD task into a one-second CPU spin.
        vTaskDelay(1);
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)written;
}

static int receive_complete_frame_bytes(httpd_handle_t server, int socket, char *data, size_t size, int flags) {
    ws_client_t *client = NULL;
    void *context = httpd_sess_get_ctx(server, socket);
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) if (context == &s_clients[i]) client = &s_clients[i];
    if (!client || !current_client(client)) return HTTPD_SOCK_ERR_FAIL;
    int64_t deadline = client->receive_deadline_us ? client->receive_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t received = 0;
    while (received < size) {
        if (!atomic_load(&s_running)) return HTTPD_SOCK_ERR_FAIL;
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket,
            data + received, size - received, flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - received) return HTTPD_SOCK_ERR_FAIL;
            received += (size_t)count;
            // A peek never consumes bytes: appending another peek would duplicate
            // the same prefix. Return the available prefix without reading again.
            if (flags & MSG_PEEK) break;
            continue;
        }
        if (!count) return 0;
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
        int64_t remaining = deadline - esp_timer_get_time();
        if (remaining <= 0) return HTTPD_SOCK_ERR_TIMEOUT;
        struct timeval wait = {.tv_sec = (long)(remaining / 1000000LL), .tv_usec = (long)(remaining % 1000000LL)};
        fd_set readable;
        FD_ZERO(&readable); FD_SET(socket, &readable);
        int ready = lwip_select(socket + 1, writable ? NULL : &readable,
                               writable ? &readable : NULL, NULL, &wait);
        if (!ready) return HTTPD_SOCK_ERR_TIMEOUT;
        if (ready < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
        vTaskDelay(1);
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)received;
}

static void fail_client(ws_client_t *client) {
    if (!current_client(client)) return;
    client->closing = true;
    // HTTPD owns close(). Immediate shutdown wakes its receive loop without a
    // queued fd/session-pointer close that could hit a subsequently reused fd.
    native_web_transport_shutdown(s_server, client->socket, false);
}

static ws_client_t *find_client(int socket) {
    void *context = httpd_sess_get_ctx(s_server, socket);
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) {
        if (context == &s_clients[i]) return &s_clients[i];
    }
    if (context) return NULL; // Do not replace another service's session owner.
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) {
        if (!s_clients[i].used) {
            s_clients[i] = (ws_client_t){.used = true, .socket = socket,
                .playlist_revision = atomic_load(&s_playlist_revision)};
            websocket_message_init(&s_clients[i].message, s_clients[i].command,
                sizeof(s_clients[i].command), WS_MESSAGE_BUDGET_US);
            httpd_sess_set_ctx(s_server, socket, &s_clients[i], session_free);
            if (httpd_sess_get_ctx(s_server, socket) == &s_clients[i]) {
                if (httpd_sess_set_send_override(s_server, socket, send_complete_frame_bytes) == ESP_OK &&
                    httpd_sess_set_recv_override(s_server, socket, receive_complete_frame_bytes) == ESP_OK)
                    return &s_clients[i];
                httpd_sess_set_ctx(s_server, socket, NULL, NULL);
            }
            memset(&s_clients[i], 0, sizeof(s_clients[i]));
            return NULL;
        }
    }
    return NULL;
}

static esp_err_t send_text(ws_client_t *client, const char *text) {
    if (!current_client(client) || client->message.close_sent ||
        client->message.close_received) return ESP_ERR_INVALID_STATE;
    httpd_ws_frame_t frame = {.final = true, .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text, .len = strlen(text)};
    client->frame_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame_async(s_server, client->socket, &frame);
    client->frame_deadline_us = 0;
    if (result != ESP_OK) fail_client(client);
    return result;
}

static esp_err_t send_control(ws_client_t *client, httpd_ws_type_t type,
                               const uint8_t *payload, size_t size) {
    if (!current_client(client)) return ESP_ERR_INVALID_STATE;
    // A received Close is already marked ws_close by SDK. Its session context
    // still owns this fd; ws_get_fd_info is therefore not an ownership test.
    httpd_ws_frame_t frame = {.final = true, .type = type,
        .payload = (uint8_t *)payload, .len = size};
    client->frame_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame_async(s_server, client->socket, &frame);
    client->frame_deadline_us = 0;
    if (result == ESP_OK && type == HTTPD_WS_TYPE_CLOSE)
        websocket_message_mark_close_sent(&client->message);
    if (result != ESP_OK) fail_client(client);
    return result;
}

static esp_err_t close_with_code(ws_client_t *client, uint16_t code) {
    uint8_t payload[2] = {(uint8_t)(code >> 8U), (uint8_t)code};
    if (!client->message.close_sent)
        (void)send_control(client, HTTPD_WS_TYPE_CLOSE, payload, sizeof(payload));
    fail_client(client);
    return ESP_FAIL;
}

static bool same_radio(const radio_control_snapshot_t *left, const radio_control_snapshot_t *right) {
    return left->item == right->item && left->count == right->count &&
        left->smartstart == right->smartstart && !strcmp(left->name, right->name);
}

static bool capture_status(ws_status_key_t *key) {
    radio_control_snapshot_t before, after;
    native_state_t state, latest;
    for (unsigned attempt = 0; attempt < 3U; ++attempt) {
        if (!radio_control_snapshot(&before)) return false;
        native_state_snapshot(s_state, &state);
        if (!radio_control_snapshot(&after)) return false;
        native_state_snapshot(s_state, &latest);
        network_snapshot_t network;
        if (network_service_snapshot(&network, 20) != ESP_OK) return false;
        if (!same_radio(&before, &after) || state.audio_generation != latest.audio_generation ||
            strcmp(state.station, latest.station) != 0) continue;
        memset(key, 0, sizeof(*key));
        key->generation = state.audio_generation;
        key->bitrate = state.bitrate_kbps;
        key->running = state.audio_running;
        key->pending = state.audio_pending;
        key->rssi_valid = network.online && network.rssi_valid;
        key->rssi = key->rssi_valid ? network.rssi : 0;
        key->network_online = network.online;
        key->ap_enabled = network.ap_enabled;
        key->item = after.item;
        key->count = after.count;
        key->smartstart = after.smartstart;
        key->volume = native_audio_output_get_volume();
        key->balance = native_audio_output_get_balance();
        native_input_health_t input = audio_service_input_health();
        key->fill = state.audio_running && input.available && input.target ?
            (uint8_t)(input.ready > input.target ? 100U : (uint64_t)input.ready * 100U / input.target) : 0U;
        key->normalization = native_audio_settings_get_normalization();
        key->normgain = native_audio_settings_get_normalization_gain_db();
        key->normtarget = native_audio_settings_get_normalization_target_dbfs();
        key->normtime = native_audio_settings_get_normalization_time_ms();
        strlcpy(key->station, state.station, sizeof(key->station));
        strlcpy(key->name, after.name, sizeof(key->name));
        strlcpy(key->title, state.title, sizeof(key->title));
        strlcpy(key->format, state.stream_format, sizeof(key->format));
        return true;
    }
    return false;
}

static void payload_string(json_buffer_t *out, const char *id, const char *value) {
    json_buffer_raw(out, "{\"id\":"); json_buffer_string(out, id);
    json_buffer_raw(out, ",\"value\":"); json_buffer_string(out, value); json_buffer_raw(out, "}");
}

static void payload_number(json_buffer_t *out, const char *id, long value) {
    char text[32];
    snprintf(text, sizeof(text), "%ld", value);
    json_buffer_raw(out, "{\"id\":"); json_buffer_string(out, id);
    json_buffer_raw(out, ",\"value\":"); json_buffer_raw(out, text); json_buffer_raw(out, "}");
}

static void payload_unsigned(json_buffer_t *out, const char *id, uint32_t value) {
    char text[32];
    snprintf(text, sizeof(text), "%lu", (unsigned long)value);
    json_buffer_raw(out, "{\"id\":"); json_buffer_string(out, id);
    json_buffer_raw(out, ",\"value\":"); json_buffer_raw(out, text); json_buffer_raw(out, "}");
}

static bool format_status(const ws_status_key_t *key) {
    json_buffer_t out;
    json_buffer_init(&out, s_status, sizeof(s_status));
    json_buffer_raw(&out, "{\"status\":{\"station\":"); json_buffer_string(&out, key->station);
    json_buffer_raw(&out, ",\"title\":"); json_buffer_string(&out, key->title);
    json_buffer_raw(&out, ",\"format\":"); json_buffer_string(&out, key->format);
    char values[512];
    snprintf(values, sizeof(values), ",\"bitrate\":%lu,\"connecting\":%s,\"audio\":%s,\"generation\":%lu,\"volume\":%u,\"balance\":%d,\"current\":%u,\"count\":%u,\"smartstart\":%s,\"normalization\":%s,\"normgain\":%u,\"normtarget\":%d,\"normtime\":%u,\"network_online\":%s,\"ap_enabled\":%s,\"rssi_valid\":%s,\"rssi\":%d},\"payload\":[",
        (unsigned long)key->bitrate, key->pending ? "true" : "false", key->running ? "true" : "false",
        (unsigned long)key->generation, key->volume, key->balance, key->item, key->count,
        key->smartstart ? "true" : "false", key->normalization ? "true" : "false", key->normgain, key->normtarget, key->normtime,
        key->network_online ? "true" : "false", key->ap_enabled ? "true" : "false",
        key->rssi_valid ? "true" : "false", key->rssi);
    json_buffer_raw(&out, values);
    payload_string(&out, "nameset", key->name); json_buffer_raw(&out, ",");
    payload_string(&out, "meta", key->title); json_buffer_raw(&out, ",");
    payload_number(&out, "volume", key->volume); json_buffer_raw(&out, ",");
    payload_number(&out, "balance", key->balance); json_buffer_raw(&out, ",");
    payload_number(&out, "rssi", key->rssi); json_buffer_raw(&out, ",");
    payload_number(&out, "heap", key->fill); json_buffer_raw(&out, ",");
    payload_unsigned(&out, "bitrate", key->bitrate); json_buffer_raw(&out, ",");
    payload_string(&out, "fmt", key->format); json_buffer_raw(&out, ",");
    payload_string(&out, "playerwrap", key->running ? "playing" : "stopped");
    json_buffer_raw(&out, "]}");
    return !out.failed;
}

static bool prepare_status(void) {
    if (!capture_status(&s_current)) return false;
    if (!s_have_previous || memcmp(&s_current, &s_previous, sizeof(s_current)) != 0) {
        if (!format_status(&s_current)) return false;
        ++s_status_revision;
        s_previous = s_current;
        s_have_previous = true;
    }
    return true;
}

static esp_err_t send_status(ws_client_t *client, bool force) {
    int64_t now = esp_timer_get_time();
    bool initial = !client->initialized;
    if (force || initial || client->status_revision != s_status_revision ||
        now - client->sent_us >= WS_HEARTBEAT_US) {
        esp_err_t result = send_text(client, s_status);
        if (result != ESP_OK) return result;
        if (initial || client->item != s_current.item) {
            char current[32];
            snprintf(current, sizeof(current), "{\"current\":%u}", s_current.item);
            result = send_text(client, current);
            if (result != ESP_OK) return result;
        }
        if (initial) {
            result = send_text(client, "{\"playermode\":\"modeweb\"}");
            if (result != ESP_OK) return result;
        }
        client->initialized = true;
        client->item = s_current.item;
        client->status_revision = s_status_revision;
        client->sent_us = now;
    }
    unsigned playlist = atomic_load(&s_playlist_revision);
    if (client->playlist_revision != playlist) {
        esp_err_t result = send_text(client, "{\"file\":\"/data/playlist.csv\"}");
        if (result != ESP_OK) return result;
        client->playlist_revision = playlist;
    }
    return ESP_OK;
}

static void status_work(void *argument) {
    (void)argument;
    if (atomic_load(&s_running)) {
        size_t count = CONFIG_LWIP_MAX_SOCKETS;
        if (httpd_get_client_list(s_server, &count, s_sockets) == ESP_OK) {
            bool prepared = false;
            for (size_t i = 0; i < count; ++i) {
                if (httpd_ws_get_fd_info(s_server, s_sockets[i]) != HTTPD_WS_CLIENT_WEBSOCKET) continue;
                if (!prepared) {
                    if (!prepare_status()) break;
                    prepared = true;
                }
                ws_client_t *client = find_client(s_sockets[i]);
                if (client) {
                    websocket_message_result_t expired = websocket_message_expire(
                        &client->message, (uint64_t)esp_timer_get_time());
                    if (expired.event == WEBSOCKET_MESSAGE_ERROR)
                        (void)close_with_code(client, expired.close_code);
                    else (void)send_status(client, false);
                }
                else (void)shutdown(s_sockets[i], SHUT_RDWR);
            }
        }
    }
    atomic_store(&s_work_pending, false);
}

static void poll_status(void) {
    bool expected = false;
    if (!atomic_load(&s_running) || !atomic_compare_exchange_strong(&s_work_pending, &expected, true)) return;
    if (httpd_queue_work(s_server, status_work, NULL) != ESP_OK) atomic_store(&s_work_pending, false);
}

static void status_task(void *argument) {
    (void)argument;
    while (atomic_load(&s_running)) {
        poll_status();
        vTaskDelay(pdMS_TO_TICKS(WS_POLL_MS));
    }
    atomic_store(&s_task_alive, false);
    vTaskDelete(NULL);
}

static bool number(const char *text, int minimum, int maximum, int *result) {
    bool negative = *text == '-';
    if (negative && minimum >= 0) return false;
    if (negative) ++text;
    if (!*text) return false;
    unsigned value = 0;
    for (; *text; ++text) {
        if (*text < '0' || *text > '9') return false;
        value = value * 10U + (unsigned)(*text - '0');
        if (value > 65535U) return false;
    }
    int signed_value = negative ? -(int)value : (int)value;
    if (signed_value < minimum || signed_value > maximum) return false;
    *result = signed_value;
    return true;
}

static esp_err_t command_error(ws_client_t *client, const char *message) {
    // Messages here are fixed literals; no command text is reflected into JSON.
    return send_text(client, message);
}

static esp_err_t handle_command(ws_client_t *client, char *command) {
    char *separator = strchr(command, '=');
    const char *value = separator ? separator + 1 : "";
    if (separator) *separator = '\0';
    bool flag = !*value || !strcmp(value, "1");
    int parsed;
    esp_err_t result = ESP_ERR_INVALID_ARG;
    if (!strcmp(command, "ping") && flag) return send_text(client, "{\"pong\":1}");
    if (!strcmp(command, "getactive") && flag)
        return send_text(client, "{\"capabilities\":{\"radio\":true,\"audio_settings\":true,\"playlist_events\":true,\"display_controls\":false,\"sd\":false,\"eq\":false}}");
    if (!strcmp(command, "getsystem") && flag) {
        if (!prepare_status()) return send_text(client, "{\"commandError\":\"Snapshot unavailable\"}");
        char settings[256];
        snprintf(settings, sizeof(settings), "{\"sst\":%u,\"normalize\":%u,\"normgain\":%u,\"normtarget\":%d,\"normtime\":%u}",
            s_current.smartstart, s_current.normalization, s_current.normgain, s_current.normtarget, s_current.normtime);
        return send_text(client, settings);
    }
    if (!strcmp(command, "getindex") && flag) result = ESP_OK;
    else if (!strcmp(command, "play") && number(value, 1, UINT16_MAX, &parsed)) result = radio_control_play((uint16_t)parsed);
    else if (!strcmp(command, "stop") && flag) result = radio_control_stop();
    else if (!strcmp(command, "toggle") && flag) result = radio_control_toggle();
    else if (!strcmp(command, "prev") && flag) result = radio_control_previous();
    else if (!strcmp(command, "next") && flag) result = radio_control_next();
    else if (!strcmp(command, "smartstart") && number(value, 0, 1, &parsed)) result = radio_control_set_smartstart_enabled(parsed != 0);
    else if (!strcmp(command, "volume") && number(value, 0, 254, &parsed)) result = native_audio_settings_set_volume((uint8_t)parsed);
    else if (!strcmp(command, "balance") && number(value, -16, 16, &parsed)) result = native_audio_settings_set_balance((int8_t)parsed);
    else if (!strcmp(command, "normalization") && number(value, 0, 1, &parsed)) result = native_audio_settings_set_normalization(parsed != 0);
    else if (!strcmp(command, "normgain") && number(value, 0, 20, &parsed)) result = native_audio_settings_set_normalization_gain_db((uint8_t)parsed);
    else if (!strcmp(command, "normtarget") && number(value, -20, 0, &parsed)) result = native_audio_settings_set_normalization_target_dbfs((int8_t)parsed);
    else if (!strcmp(command, "normtime") && number(value, 100, 10000, &parsed)) result = native_audio_settings_set_normalization_time_ms((uint16_t)parsed);
    else if ((!strcmp(command, "submitplaylist") || !strcmp(command, "submitplaylistdone")) && flag) return ESP_OK;
    if (result != ESP_OK) return command_error(client, result == ESP_ERR_INVALID_ARG ?
        "{\"commandError\":\"Unsupported command or invalid value\"}" : "{\"commandError\":\"Operation failed\"}");
    if (!prepare_status()) return send_text(client, "{\"commandError\":\"Snapshot unavailable\"}");
    if (!strcmp(command, "getindex")) client->initialized = false;
    return send_status(client, true);
}

static esp_err_t receive_and_handle(httpd_req_t *request, ws_client_t *client) {
    httpd_ws_frame_t frame = {0};
    esp_err_t result = httpd_ws_recv_frame(request, &frame, 0);
    if (result != ESP_OK) return result;
    bool control = (unsigned)frame.type >= 8U;
    if (frame.len > (control ? 125U : WS_COMMAND_LIMIT))
        return close_with_code(client, control ? 1002U : 1009U);
    uint8_t payload[125];
    if (frame.len) {
        frame.payload = payload;
        result = httpd_ws_recv_frame(request, &frame, sizeof(payload));
        if (result != ESP_OK) return result;
    }
    websocket_message_result_t message = websocket_message_feed(&client->message,
        (uint8_t)frame.type, frame.final, payload, frame.len,
        (uint64_t)esp_timer_get_time());
    switch (message.event) {
    case WEBSOCKET_MESSAGE_ERROR: return close_with_code(client, message.close_code);
    case WEBSOCKET_MESSAGE_NONE:
    case WEBSOCKET_MESSAGE_PONG: return ESP_OK;
    case WEBSOCKET_MESSAGE_PING:
        return send_control(client, HTTPD_WS_TYPE_PONG, message.data, message.size);
    case WEBSOCKET_MESSAGE_CLOSE:
        if (client->message.close_sent) return ESP_OK;
        return send_control(client, HTTPD_WS_TYPE_CLOSE, message.data, message.size);
    case WEBSOCKET_MESSAGE_BINARY:
        // Radio commands use text; RFC 6455 permits closing unsupported data.
        return close_with_code(client, 1003U);
    case WEBSOCKET_MESSAGE_TEXT:
        if (!message.size) return send_text(client, "{\"commandError\":\"Empty command\"}");
        if (memchr(message.data, 0, message.size))
            return send_text(client, "{\"commandError\":\"Invalid command\"}");
        return handle_command(client, (char *)client->command);
    }
    return ESP_FAIL;
}

static esp_err_t websocket_handler(httpd_req_t *request) {
    // Pinned HTTPD consumes valid upgrades itself. An ordinary GET reached
    // this handler without an upgrade and must remain an HTTP error response.
    if (request->method == HTTP_GET)
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "WebSocket upgrade required");
    if (!atomic_load(&s_running)) return ESP_ERR_INVALID_STATE;
    ws_client_t *client = find_client(httpd_req_to_sockfd(request));
    if (!client) return ESP_ERR_NO_MEM;
    // The first opcode byte was read by HTTPD before dispatch. Header length,
    // mask and payload reads made by the handler share this single deadline.
    client->receive_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = receive_and_handle(request, client);
    client->receive_deadline_us = 0;
    return result;
}

void websocket_service_notify_playlist_changed(void) {
    atomic_fetch_add(&s_playlist_revision, 1U);
}

static esp_err_t websocket_handshake_transport(httpd_req_t *request) {
    if (!atomic_load(&s_running)) return ESP_ERR_INVALID_STATE;
    // IDF consumes the upgrade GET without invoking websocket_handler. Install
    // both overrides before SDK reads any opcode/control bytes on this session.
    return find_client(httpd_req_to_sockfd(request)) ? ESP_OK : ESP_ERR_NO_MEM;
}

esp_err_t websocket_service_register(httpd_handle_t server, native_state_t *state) {
    if (!server || !state) return ESP_ERR_INVALID_ARG;
    if (s_server) return ESP_ERR_INVALID_STATE;
    httpd_uri_t route = {.uri = "/ws", .method = HTTP_GET, .handler = websocket_handler,
        .is_websocket = true, .handle_ws_control_frames = true,
        .ws_pre_handshake_cb = websocket_handshake_transport,
        .ws_post_handshake_cb = websocket_handshake_transport};
    esp_err_t result = httpd_register_uri_handler(server, &route);
    if (result == ESP_OK) { s_server = server; s_state = state; }
    return result;
}

esp_err_t websocket_service_start(void) {
    if (!s_server || atomic_load(&s_running) || atomic_load(&s_task_alive)) return ESP_ERR_INVALID_STATE;
    atomic_store(&s_running, true);
    atomic_store(&s_task_alive, true);
    if (xTaskCreate(status_task, "websocket_status", WS_TASK_STACK, NULL, 2, NULL) != pdPASS) {
        atomic_store(&s_running, false); atomic_store(&s_task_alive, false);
        return ESP_ERR_NO_MEM;
    }
    return ESP_OK;
}

esp_err_t websocket_service_stop(void) {
    atomic_store(&s_running, false);
    for (unsigned attempt = 0; attempt < 50U && atomic_load(&s_task_alive); ++attempt)
        vTaskDelay(pdMS_TO_TICKS(10));
    return atomic_load(&s_task_alive) ? ESP_ERR_TIMEOUT : ESP_OK;
}

esp_err_t websocket_service_server_stopped(httpd_handle_t server) {
    if (atomic_load(&s_task_alive) || atomic_load(&s_running)) return ESP_ERR_INVALID_STATE;
    if (s_server && s_server != server) return ESP_ERR_INVALID_ARG;
    s_server = NULL; s_state = NULL;
    memset(s_clients, 0, sizeof(s_clients));
    s_have_previous = false; s_status_revision = 0;
    atomic_store(&s_work_pending, false); atomic_store(&s_playlist_revision, 0);
    return ESP_OK;
}
