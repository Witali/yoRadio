#include "websocket_service.h"

#include <stdatomic.h>
#include <errno.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#include "audio_service.h"
#include "deep_sleep_clock.h"
#include "board_config.h"
#include "display_settings.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "web_tcp_probe.h"
#include "native_audio_output.h"
#include "native_audio_settings.h"
#include "network_service.h"
#include "runtime_settings.h"
#include "time_service.h"
#include "radio_control.h"
#include "websocket_message.h"
#include "json_buffer.h"
#include "native_web_transport.h"

#define WS_STATUS_POLL_MS 100
#define WS_STATUS_HEARTBEAT_MS 2000
#define WS_FRAME_BUDGET_US 1000000LL
#define WS_MESSAGE_BUDGET_US 5000000ULL

#if !CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT
#error "Native WebSocket transport requires the public post-handshake callback"
#endif
#if !CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT
#error "Native WebSocket transport requires the public pre-handshake callback"
#endif
#if CONFIG_HTTPD_QUEUE_WORK_BLOCKING
#error "Native WebSocket publication requires non-blocking HTTPD work admission"
#endif

static const char *const TAG = "websocket";
static httpd_handle_t s_server;
static native_state_t *s_state;

typedef struct {
    bool audio_running;
    uint8_t volume;
    int8_t balance;
    uint32_t bitrate_kbps;
    uint32_t sample_rate_hz;
    uint8_t channels;
    uint8_t bits_per_sample;
    uint32_t pcm_sample_rate_hz;
    uint8_t pcm_channels;
    uint16_t current_item;
    bool station_uppercase;
    char station[144];
    char title[192];
    char codec[16];
    char stream_format[48];
} webui_status_key_t;

// Keep persistent broadcast workspace in BSS so the board-configured task
// stack remains headroom for nested HTTP/WebSocket calls.
static char s_broadcast_status[1280];
static char s_broadcast_current[48];
static webui_status_key_t s_previous_status_key;
static webui_status_key_t s_current_status_key;
static atomic_bool s_playlist_changed_pending;
static atomic_uint s_status_send_pending;
static atomic_uint s_current_send_pending;
static atomic_size_t s_last_ws_clients;
static atomic_uint s_completed_deliveries;

typedef struct {
    bool used, closing;
    int socket;
    int64_t send_deadline_us, receive_deadline_us;
    websocket_message_t message;
    uint8_t command[256];
} ws_client_t;

// Only the HTTPD task accesses session storage. The public free callback clears
// it before the fd can be reused; queued broadcasts capture no session or fd.
static ws_client_t s_clients[CONFIG_LWIP_MAX_SOCKETS];
static atomic_uint s_fragmented_clients;
static atomic_bool s_message_poll_pending;

static void ws_update_active(ws_client_t *client, bool was_active) {
    if (was_active && !client->message.active) atomic_fetch_sub(&s_fragmented_clients, 1U);
    else if (!was_active && client->message.active) atomic_fetch_add(&s_fragmented_clients, 1U);
}

static void ws_session_free(void *context) {
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        if (context == &s_clients[i]) {
            if (s_clients[i].message.active) atomic_fetch_sub(&s_fragmented_clients, 1U);
            memset(&s_clients[i], 0, sizeof(s_clients[i]));
            break;
        }
    }
}

static ws_client_t *ws_session(httpd_handle_t server, int socket) {
    if (server != s_server || socket < 0 || socket >= FD_SETSIZE) return NULL;
    void *context = httpd_sess_get_ctx(server, socket);
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        ws_client_t *client = &s_clients[i];
        if (context == client && client->used && !client->closing &&
            client->socket == socket) return client;
    }
    return NULL;
}

static int ws_wait(int socket, bool sending, int64_t deadline) {
    int64_t remaining = deadline - esp_timer_get_time();
    if (remaining <= 0) return HTTPD_SOCK_ERR_TIMEOUT;
    struct timeval wait = {.tv_sec = (long)(remaining / 1000000LL),
        .tv_usec = (long)(remaining % 1000000LL)};
    fd_set ready_set;
    FD_ZERO(&ready_set);
    FD_SET(socket, &ready_set);
    int ready = lwip_select(socket + 1, sending ? NULL : &ready_set,
                           sending ? &ready_set : NULL, NULL, &wait);
    if (!ready) return HTTPD_SOCK_ERR_TIMEOUT;
    if (ready < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
    // Spurious readiness and EINTR must not spin the HTTPD task at full CPU.
    vTaskDelay(1);
    return ESP_OK;
}

static int ws_send_complete(httpd_handle_t server, int socket,
                            const char *data, size_t size, int flags) {
    ws_client_t *client = ws_session(server, socket);
    if (!client || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    // One deadline covers an application frame's header and payload. SDK
    // control replies get a separate finite fallback for each send call.
    int64_t deadline = client->send_deadline_us ? client->send_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t written = 0;
    while (written < size) {
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t count = native_web_transport_send(server, socket,
            data + written, size - written, flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - written) return HTTPD_SOCK_ERR_FAIL;
            written += (size_t)count;
            continue;
        }
        if (!count || (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR))
            return HTTPD_SOCK_ERR_FAIL;
        int result = ws_wait(socket, writable, deadline);
        if (result != ESP_OK) return result;
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)written;
}

static int ws_receive_complete(httpd_handle_t server, int socket,
                               char *data, size_t size, int flags) {
    ws_client_t *client = ws_session(server, socket);
    if (!client || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    int64_t deadline = client->receive_deadline_us ? client->receive_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t received = 0;
    while (received < size) {
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket,
            data + received, size - received, flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - received) return HTTPD_SOCK_ERR_FAIL;
            received += (size_t)count;
            // A repeated peek returns the same prefix rather than advancing.
            if (flags & MSG_PEEK) break;
            continue;
        }
        if (!count) return 0;
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR)
            return HTTPD_SOCK_ERR_FAIL;
        int result = ws_wait(socket, writable, deadline);
        if (result != ESP_OK) return result;
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)received;
}

static void ws_finish_client(ws_client_t *client, bool graceful) {
    if (!client || ws_session(s_server, client->socket) != client) return;
    client->closing = true;
    bool was_active = client->message.active;
    client->message.active = false;
    client->message.used = 0;
    ws_update_active(client, was_active);
    // HTTPD retains ownership of close(). No deferred fd-only close may affect
    // a replacement session that later receives the same descriptor.
    native_web_transport_shutdown(s_server, client->socket, graceful);
}

static void ws_fail_client(ws_client_t *client) {
    ws_finish_client(client, false);
}

static esp_err_t websocket_pre_handshake(httpd_req_t *request) {
    int socket = httpd_req_to_sockfd(request);
    if (socket < 0 || socket >= FD_SETSIZE ||
        httpd_sess_get_ctx(s_server, socket)) return ESP_FAIL;
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        ws_client_t *client = &s_clients[i];
        if (client->used) continue;
        *client = (ws_client_t){.used = true, .socket = socket};
        if (!websocket_message_init(&client->message, client->command,
                                     sizeof(client->command), WS_MESSAGE_BUDGET_US)) {
            memset(client, 0, sizeof(*client));
            return ESP_FAIL;
        }
        httpd_sess_set_ctx(s_server, socket, client, ws_session_free);
        if (httpd_sess_get_ctx(s_server, socket) != client) {
            memset(client, 0, sizeof(*client));
            return ESP_FAIL;
        }
        if (httpd_sess_set_send_override(s_server, socket, ws_send_complete) != ESP_OK ||
            httpd_sess_set_recv_override(s_server, socket, ws_receive_complete) != ESP_OK) {
            ws_fail_client(client);
            return ESP_FAIL;
        }
        return ESP_OK;
    }
    return ESP_ERR_NO_MEM;
}

static esp_err_t websocket_post_handshake(httpd_req_t *request) {
    return ws_session(s_server, httpd_req_to_sockfd(request)) ? ESP_OK : ESP_FAIL;
}

static esp_err_t ws_send_control(ws_client_t *client, httpd_ws_type_t type,
                                 const uint8_t *payload, size_t size) {
    if (!client || ws_session(s_server, client->socket) != client) return ESP_ERR_INVALID_STATE;
    httpd_ws_frame_t frame = {.final = true, .type = type,
        .payload = (uint8_t *)payload, .len = size};
    client->send_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame_async(s_server, client->socket, &frame);
    client->send_deadline_us = 0;
    if (result != ESP_OK) ws_fail_client(client);
    return result;
}

static esp_err_t ws_close_client(ws_client_t *client, uint16_t code) {
    if (!client || ws_session(s_server, client->socket) != client) return ESP_FAIL;
    esp_err_t result = ESP_OK;
    if (!client->message.close_sent) {
        bool was_active = client->message.active;
        uint8_t payload[2] = {(uint8_t)(code >> 8U), (uint8_t)code};
        result = ws_send_control(client, HTTPD_WS_TYPE_CLOSE, payload, sizeof(payload));
        if (result == ESP_OK) {
            websocket_message_mark_close_sent(&client->message);
            ws_update_active(client, was_active);
        }
    }
    ws_fail_client(client);
    return result;
}

static void message_deadline_work(void *argument) {
    (void)argument;
    uint64_t now = (uint64_t)esp_timer_get_time();
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        ws_client_t *client = &s_clients[i];
        if (!client->message.active || ws_session(s_server, client->socket) != client) continue;
        websocket_message_result_t result = websocket_message_expire(&client->message, now);
        ws_update_active(client, true);
        if (result.event == WEBSOCKET_MESSAGE_ERROR) (void)ws_close_client(client, result.close_code);
    }
    atomic_store(&s_message_poll_pending, false);
}

static void poll_message_deadlines(void) {
    bool expected = false;
    if (!atomic_load(&s_fragmented_clients) ||
        !atomic_compare_exchange_strong(&s_message_poll_pending, &expected, true)) return;
    if (httpd_queue_work(s_server, message_deadline_work, NULL) != ESP_OK)
        atomic_store(&s_message_poll_pending, false);
}

static void json_escape(const char *source, char *target, size_t target_size) {
    if (!target_size) return;
    json_buffer_t out;
    json_buffer_init(&out, target, target_size);
    json_buffer_string(&out, source);
    // The shared encoder appends whole escapes/UTF-8 sequences atomically.
    // Preserve its bounded valid prefix even when the complete field did not
    // fit, removing the quotes supplied separately by these legacy JSON forms.
    size_t length = out.length ? out.length - 1U : 0U;
    if (!out.failed && length) --length;
    if (length) memmove(target, target + 1, length);
    target[length] = '\0';
}

static esp_err_t ws_send_request(httpd_req_t *request, const char *text) {
    ws_client_t *client = ws_session(s_server, httpd_req_to_sockfd(request));
    if (!client || client->message.close_sent || client->message.close_received) return ESP_ERR_INVALID_STATE;
    if (!websocket_message_utf8_valid((const uint8_t *)text, strlen(text))) {
        (void)ws_close_client(client, 1011);
        return ESP_FAIL;
    }
    httpd_ws_frame_t frame = {
        .final = true,
        .fragmented = false,
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text,
        .len = strlen(text),
    };
    client->send_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame(request, &frame);
    client->send_deadline_us = 0;
    if (result != ESP_OK) ws_fail_client(client);
    return result;
}

typedef struct {
    atomic_bool busy;
    const char *text;
    atomic_uint *pending;
} ws_broadcast_work_t;

static ws_broadcast_work_t s_status_work, s_current_work, s_playlist_work;

static void broadcast_work(void *argument) {
    ws_broadcast_work_t *work = argument;
    size_t count = CONFIG_LWIP_MAX_SOCKETS;
    int sockets[CONFIG_LWIP_MAX_SOCKETS];
    size_t clients = 0;
    if (httpd_get_client_list(s_server, &count, sockets) == ESP_OK) {
        for (size_t index = 0; index < count; ++index) {
            if (httpd_ws_get_fd_info(s_server, sockets[index]) ==
                HTTPD_WS_CLIENT_WEBSOCKET) {
                ++clients;
                ws_client_t *client = ws_session(s_server, sockets[index]);
                if (client && !client->message.close_sent && !client->message.close_received) {
                    if (!websocket_message_utf8_valid((const uint8_t *)work->text, strlen(work->text))) {
                        (void)ws_close_client(client, 1011);
                        continue;
                    }
                    httpd_ws_frame_t frame = {.final = true,
                        .type = HTTPD_WS_TYPE_TEXT, .payload = (uint8_t *)work->text,
                        .len = strlen(work->text)};
                    client->send_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
                    esp_err_t result = httpd_ws_send_frame_async(s_server, sockets[index], &frame);
                    client->send_deadline_us = 0;
                    if (result != ESP_OK) ws_fail_client(client);
                    else atomic_fetch_add(&s_completed_deliveries, 1U);
                }
            }
        }
    }
    atomic_store(&s_last_ws_clients, clients);
    atomic_fetch_sub(work->pending, 1U);
    atomic_store(&work->busy, false);
}

static bool broadcast_text(const char *text, atomic_uint *pending,
                            ws_broadcast_work_t *work) {
    if (!s_server || !text || !pending) return false;
    bool expected = false;
    if (!atomic_compare_exchange_strong(&work->busy, &expected, true)) return false;
    work->text = text;
    work->pending = pending;
    atomic_fetch_add(pending, 1U);
    if (httpd_queue_work(s_server, broadcast_work, work) == ESP_OK) return true;
    atomic_fetch_sub(pending, 1U);
    atomic_store(&work->busy, false);
    return false;
}

static void format_status(char *output, size_t output_size) {
    native_state_t state;
    native_state_snapshot(s_state, &state);
    char name[300];
    char title[400];
    char format[120];
    char current_name[144];
    radio_control_current_name(current_name, sizeof(current_name));
    json_escape(current_name, name, sizeof(name));
    json_escape(state.title, title, sizeof(title));
    json_escape(state.stream_format, format, sizeof(format));
    snprintf(output, output_size,
             "{\"payload\":[{\"id\":\"nameset\",\"value\":\"%s\"},"
             "{\"id\":\"meta\",\"value\":\"%s\"},"
             "{\"id\":\"volume\",\"value\":%u},"
             "{\"id\":\"balance\",\"value\":%d},"
             "{\"id\":\"rssi\",\"value\":%d},"
             "{\"id\":\"heap\",\"value\":%u},"
             "{\"id\":\"bitrate\",\"value\":%lu},"
             "{\"id\":\"fmt\",\"value\":\"%s\"},"
             "{\"id\":\"upst\",\"value\":%u},"
             "{\"id\":\"playerwrap\",\"value\":\"%s\"}]}",
             name, title, native_audio_output_get_volume(),
             native_audio_output_get_balance(), state.wifi_rssi,
             (unsigned)(state.audio_running
                            ? audio_service_buffer_fill_percent()
                            : 0U),
             (unsigned long)state.bitrate_kbps, format,
             display_settings_get_station_uppercase() ? 1U : 0U,
             state.audio_running ? "playing" : "stopped");
}

static void capture_status_key(webui_status_key_t *key) {
    native_state_t state;
    memset(key, 0, sizeof(*key));
    native_state_snapshot(s_state, &state);
    key->audio_running = state.audio_running;
    key->volume = native_audio_output_get_volume();
    key->balance = native_audio_output_get_balance();
    key->bitrate_kbps = state.bitrate_kbps;
    key->sample_rate_hz = state.sample_rate_hz;
    key->channels = state.channels;
    key->bits_per_sample = state.bits_per_sample;
    key->pcm_sample_rate_hz = state.pcm_sample_rate_hz;
    key->pcm_channels = state.pcm_channels;
    key->current_item = radio_control_current_item();
    key->station_uppercase = display_settings_get_station_uppercase();
    radio_control_current_name(key->station, sizeof(key->station));
    strlcpy(key->title, state.title, sizeof(key->title));
    strlcpy(key->codec, state.codec, sizeof(key->codec));
    strlcpy(key->stream_format, state.stream_format,
            sizeof(key->stream_format));
}

static esp_err_t send_initial_state(httpd_req_t *request) {
    char status[1280];
    char current[48];
    format_status(status, sizeof(status));
    ESP_RETURN_ON_ERROR(ws_send_request(request, status), TAG,
                        "send WebUI status");
    snprintf(current, sizeof(current), "{\"current\":%u}",
             radio_control_current_item());
    ESP_RETURN_ON_ERROR(ws_send_request(request, current), TAG,
                        "send WebUI station index");
    ESP_RETURN_ON_ERROR(ws_send_request(request, "{\"sdinit\":0}"), TAG,
                        "send WebUI storage state");
    ESP_RETURN_ON_ERROR(
        ws_send_request(request, "{\"playermode\":\"modeweb\"}"), TAG,
        "send WebUI player mode");
    return ESP_OK;
}

static esp_err_t send_system_settings(httpd_req_t *request) {
    char mdns[24];
    char mdns_escaped[144];
    runtime_settings_get_mdns_name(mdns, sizeof(mdns));
    json_escape(mdns, mdns_escaped, sizeof(mdns_escaped));
    native_state_t state;
    native_state_snapshot(s_state, &state);
    char address[20] = "192.168.4.1";
    if (state.network_mode == NATIVE_NETWORK_CLIENT && state.ipv4) {
        esp_ip4_addr_t ip = {.addr = state.ipv4};
        snprintf(address, sizeof(address), IPSTR, IP2STR(&ip));
    }
    char settings[512];
    snprintf(settings, sizeof(settings),
             "{\"sst\":%u,\"aif\":%u,\"vu\":0,\"softr\":%u,\"vut\":0,"
             "\"mdns\":\"%s\",\"ipaddr\":\"%s\",\"abuff\":%u,"
             "\"abuffmax\":%u,"
             "\"mp3decoder\":0,\"normalize\":%u,\"normgain\":%u,"
             "\"normtarget\":%d,\"normtime\":%u,\"telnet\":0,"
             "\"watchdog\":%u,\"stationtimeout\":%u}",
             radio_control_smartstart_enabled() ? 1U : 0U,
             runtime_settings_get_audio_info() ? 1U : 0U,
             runtime_settings_get_softap_delay_min(), mdns_escaped, address,
             runtime_settings_get_audio_buffer_blocks(),
             RUNTIME_MAX_AUDIO_BUFFER_BLOCKS,
             native_audio_settings_get_normalization() ? 1U : 0U,
             native_audio_settings_get_normalization_gain_db(),
             native_audio_settings_get_normalization_target_dbfs(),
             native_audio_settings_get_normalization_time_ms(),
             runtime_settings_get_watchdog() ? 1U : 0U,
             runtime_settings_get_station_timeout_sec());
    return ws_send_request(request, settings);
}

static esp_err_t send_screen_settings(httpd_req_t *request) {
    char settings[256];
    unsigned brightness = display_settings_get_brightness();
    snprintf(settings, sizeof(settings),
             "{\"flip\":0,\"inv\":0,\"nump\":%u,\"tsf\":0,"
             "\"tsd\":0,\"upst\":%u,\"dspon\":%u,\"br\":%u,\"con\":55,"
             "\"scre\":%u,\"scrt\":%u,\"scrb\":%u,\"scrpe\":%u,"
             "\"scrpt\":%u,\"scrpb\":%u}",
             display_settings_get_numbered_playlist() ? 1U : 0U,
             display_settings_get_station_uppercase() ? 1U : 0U,
             display_settings_get_screen_on() ? 1U : 0U, brightness,
             display_settings_get_screensaver_enabled() ? 1U : 0U,
             display_settings_get_screensaver_timeout(),
             display_settings_get_screensaver_blank() ? 1U : 0U,
             display_settings_get_screensaver_playing_enabled() ? 1U : 0U,
             display_settings_get_screensaver_playing_timeout(),
             display_settings_get_screensaver_playing_blank() ? 1U : 0U);
    return ws_send_request(request, settings);
}

static esp_err_t send_timezone_settings(httpd_req_t *request) {
    char sntp1[35];
    char sntp2[35];
    char escaped1[208], escaped2[208];
    char settings[640];
    runtime_settings_get_sntp1(sntp1, sizeof(sntp1));
    runtime_settings_get_sntp2(sntp2, sizeof(sntp2));
    json_escape(sntp1, escaped1, sizeof(escaped1));
    json_escape(sntp2, escaped2, sizeof(escaped2));
    snprintf(settings, sizeof(settings),
             "{\"tzh\":%d,\"tzm\":%u,\"sntp1\":\"%s\","
             "\"sntp2\":\"%s\",\"timeint\":%u,\"timeintrtc\":24}",
             runtime_settings_get_timezone_hour(),
             runtime_settings_get_timezone_minute(), escaped1, escaped2,
             runtime_settings_get_time_sync_interval_min());
    return ws_send_request(request, settings);
}

static esp_err_t send_weather_settings(httpd_req_t *request) {
    return ws_send_request(request,
                           "{\"wen\":0,\"wlat\":\"\",\"wlon\":\"\","
                           "\"wkey\":\"\",\"wint\":60}");
}

static esp_err_t send_control_settings(httpd_req_t *request) {
    char settings[96];
    snprintf(settings, sizeof(settings),
             "{\"vols\":%u,\"enca\":%u,\"irtl\":10,\"skipup\":1}",
             runtime_settings_get_volume_steps(),
             runtime_settings_get_encoder_acceleration());
    return ws_send_request(request, settings);
}

static esp_err_t send_active_settings(httpd_req_t *request, bool client_mode) {
    if (!client_mode) {
        return ws_send_request(request, "{\"act\":[\"group_wifi\"]}");
    }
    // Weather is intentionally excluded by the ESP32-C3 OLED build profile.
    ESP_RETURN_ON_ERROR(ws_send_request(
        request,
        "{\"act\":[\"group_wifi\",\"group_system\",\"group_display\","
        "\"group_oled\",\"group_timezone\",\"group_controls\","
#ifdef CONFIG_YORADIO_ROTARY_ENCODER
        "\"group_encoder\","
#endif
        "\"group_buffer\",\"group_wortc\"]}"), TAG,
        "Send active WebUI groups");
    // C3 has neither a telnet console, an on-device station-list cursor, nor
    // the optional ESP-IDF mDNS responder component. Keep the DHCP hostname,
    // but do not expose no-op controls or a misleading .local link.
    return ws_send_request(request,
        "{\"hide\":[\"telnet\",\"skipup\",\"mdnsnamerow\","
        "\"radiolink\"]}");
}

// The status task exists before HTTP routes become available. Reboot requests
// need no late heap allocation; first ordinary request wins. An OTA lease
// defers execution until its owner cancels or commits after the response.
static atomic_bool s_reboot_ready;
static portMUX_TYPE s_reboot_lock = portMUX_INITIALIZER_UNLOCKED;
static uint32_t s_reboot_at;
static bool s_reboot_pending;
static uint64_t s_reboot_reserved_epoch, s_reboot_next_epoch;

bool websocket_service_reboot_ready(void) {
    return atomic_load(&s_reboot_ready);
}
void websocket_service_request_reboot(unsigned delay_ms) {
    if (delay_ms > 60000U) delay_ms = 60000U;
    uint32_t at = (uint32_t)xTaskGetTickCount() + (uint32_t)pdMS_TO_TICKS(delay_ms);
    portENTER_CRITICAL(&s_reboot_lock);
    if (atomic_load(&s_reboot_ready) && !s_reboot_pending) {
        s_reboot_at = at;
        s_reboot_pending = true;
    }
    portEXIT_CRITICAL(&s_reboot_lock);
}
esp_err_t websocket_service_reboot_reserve(websocket_reboot_lease_t *lease) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    if (lease->epoch) return ESP_ERR_INVALID_STATE;
    portENTER_CRITICAL(&s_reboot_lock);
    if (!atomic_load(&s_reboot_ready) || s_reboot_pending || s_reboot_reserved_epoch ||
        s_reboot_next_epoch == UINT64_MAX) {
        portEXIT_CRITICAL(&s_reboot_lock);
        return ESP_ERR_INVALID_STATE;
    }
    lease->epoch = s_reboot_reserved_epoch = ++s_reboot_next_epoch;
    portEXIT_CRITICAL(&s_reboot_lock);
    return ESP_OK;
}
esp_err_t websocket_service_reboot_cancel(websocket_reboot_lease_t *lease) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    portENTER_CRITICAL(&s_reboot_lock);
    if (!lease->epoch || lease->epoch != s_reboot_reserved_epoch) {
        portEXIT_CRITICAL(&s_reboot_lock);
        return ESP_ERR_INVALID_STATE;
    }
    s_reboot_reserved_epoch = lease->epoch = 0;
    portEXIT_CRITICAL(&s_reboot_lock);
    return ESP_OK;
}
esp_err_t websocket_service_reboot_commit(websocket_reboot_lease_t *lease, unsigned delay_ms) {
    if (!lease) return ESP_ERR_INVALID_ARG;
    if (delay_ms > 60000U) delay_ms = 60000U;
    uint32_t at = (uint32_t)xTaskGetTickCount() + (uint32_t)pdMS_TO_TICKS(delay_ms);
    portENTER_CRITICAL(&s_reboot_lock);
    if (!lease->epoch || lease->epoch != s_reboot_reserved_epoch) {
        portEXIT_CRITICAL(&s_reboot_lock);
        return ESP_ERR_INVALID_STATE;
    }
    if (!s_reboot_pending) s_reboot_at = at;
    s_reboot_pending = true;
    s_reboot_reserved_epoch = lease->epoch = 0;
    portEXIT_CRITICAL(&s_reboot_lock);
    return ESP_OK;
}
static void poll_reboot(void) {
    portENTER_CRITICAL(&s_reboot_lock);
    bool pending = s_reboot_pending && !s_reboot_reserved_epoch;
    uint32_t at = s_reboot_at;
    portEXIT_CRITICAL(&s_reboot_lock);
    if (pending && (int32_t)((uint32_t)xTaskGetTickCount() - at) >= 0) esp_restart();
}

static void log_setting_error(const char *name, esp_err_t result) {
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "%s update failed: %s", name, esp_err_to_name(result));
    }
}

static void handle_command(httpd_req_t *request, char *command) {
    char *separator = strchr(command, '=');
    char *value = separator ? separator + 1 : (char *)"";
    if (separator) *separator = '\0';

    if (strcmp(command, "ping") == 0) {
        ws_send_request(request, "{\"pong\":1}");
    } else if (strcmp(command, "getindex") == 0) {
        send_initial_state(request);
    } else if (strcmp(command, "getactive") == 0) {
        native_state_t state;
        native_state_snapshot(s_state, &state);
        bool client_mode = state.network_mode == NATIVE_NETWORK_CLIENT;
        send_active_settings(request, client_mode);
    } else if (strcmp(command, "getsystem") == 0) {
        send_system_settings(request);
    } else if (strcmp(command, "getscreen") == 0) {
        send_screen_settings(request);
    } else if (strcmp(command, "gettimezone") == 0) {
        send_timezone_settings(request);
    } else if (strcmp(command, "getweather") == 0) {
        send_weather_settings(request);
    } else if (strcmp(command, "getcontrols") == 0) {
        send_control_settings(request);
    } else if (strcmp(command, "submitplaylist") == 0) {
        // The HTTP upload handler emits the file event only after the new
        // playlist has been written successfully.
    } else if (strcmp(command, "submitplaylistdone") == 0) {
        // The shared WebUI acknowledges that it has reloaded playlist.csv.
    } else if (strcmp(command, "play") == 0) {
        display_settings_note_activity();
        radio_control_play((uint16_t)strtoul(value, NULL, 10));
        send_initial_state(request);
    } else if (strcmp(command, "stop") == 0) {
        display_settings_note_activity();
        radio_control_stop();
        send_initial_state(request);
    } else if (strcmp(command, "toggle") == 0) {
        display_settings_note_activity();
        radio_control_toggle();
        send_initial_state(request);
    } else if (strcmp(command, "prev") == 0 ||
               strcmp(command, "next") == 0) {
        display_settings_note_activity();
        if (strcmp(command, "prev") == 0) radio_control_previous();
        else radio_control_next();
        send_initial_state(request);
    } else if (strcmp(command, "volume") == 0) {
        display_settings_note_activity();
        unsigned volume = strtoul(value, NULL, 10);
        native_audio_output_set_volume(volume > 254 ? 254 : (uint8_t)volume);
        send_initial_state(request);
    } else if (strcmp(command, "smartstart") == 0) {
        esp_err_t result = radio_control_set_smartstart_enabled(
            strtoul(value, NULL, 10) != 0);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Smart Start update failed: %s",
                     esp_err_to_name(result));
        }

    } else if (strcmp(command, "audioinfo") == 0) {
        log_setting_error("Audio info", runtime_settings_set_audio_info(
                                            strtoul(value, NULL, 10) != 0U));
    } else if (strcmp(command, "softap") == 0) {
        unsigned minutes = strtoul(value, NULL, 10);
        if (minutes > 30U) minutes = 30U;
        log_setting_error("SoftAP delay",
                          runtime_settings_set_softap_delay_min(minutes));
    } else if (strcmp(command, "abuff") == 0) {
        unsigned blocks = strtoul(value, NULL, 10);
        if (blocks < RUNTIME_MIN_AUDIO_BUFFER_BLOCKS) {
            blocks = RUNTIME_MIN_AUDIO_BUFFER_BLOCKS;
        }
        if (blocks > RUNTIME_MAX_AUDIO_BUFFER_BLOCKS) {
            blocks = RUNTIME_MAX_AUDIO_BUFFER_BLOCKS;
        }
        log_setting_error("Audio buffer",
                          runtime_settings_set_audio_buffer_blocks(blocks));
    } else if (strcmp(command, "watchdog") == 0) {
        log_setting_error("Watchdog", runtime_settings_set_watchdog(
                                          strtoul(value, NULL, 10) != 0U));
    } else if (strcmp(command, "stationtimeout") == 0) {
        char *end;
        unsigned long seconds = strtoul(value, &end, 10);
        if (!value[0] || *end || seconds < RUNTIME_MIN_STATION_TIMEOUT_SEC ||
            seconds > RUNTIME_MAX_STATION_TIMEOUT_SEC) {
            ws_send_request(request,
                "{\"commandError\":\"Station timeout must be 1 to 120 seconds.\"}");
        } else {
            log_setting_error("Station timeout",
                runtime_settings_set_station_timeout_sec((uint8_t)seconds));
        }
    } else if (strcmp(command, "mdnsname") == 0) {
        log_setting_error("mDNS", runtime_settings_set_mdns_name(value));
    } else if (strcmp(command, "reboot") == 0 ||
               strcmp(command, "rebootmdns") == 0) {
        ws_send_request(request, "{\"rebooting\":1}");
        websocket_service_request_reboot(300);
    } else if (strcmp(command, "tzh") == 0) {
        long hour = strtol(value, NULL, 10);
        if (hour < -12) hour = -12;
        if (hour > 14) hour = 14;
        esp_err_t result = runtime_settings_set_timezone_hour((int8_t)hour);
        if (result == ESP_OK) result = time_service_apply();
        log_setting_error("Timezone hour", result);
    } else if (strcmp(command, "tzm") == 0) {
        unsigned minute = strtoul(value, NULL, 10);
        if (minute > 45U) minute = 45U;
        minute = (minute / 15U) * 15U;
        esp_err_t result =
            runtime_settings_set_timezone_minute((uint8_t)minute);
        if (result == ESP_OK) result = time_service_apply();
        log_setting_error("Timezone minute", result);
    } else if (strcmp(command, "sntp1") == 0 ||
               strcmp(command, "sntp2") == 0) {
        esp_err_t result = strcmp(command, "sntp1") == 0
                               ? runtime_settings_set_sntp1(value)
                               : runtime_settings_set_sntp2(value);
        if (result == ESP_OK) result = time_service_apply();
        log_setting_error("SNTP server", result);
    } else if (strcmp(command, "timeint") == 0) {
        unsigned interval = strtoul(value, NULL, 10);
        if (interval < 15U) interval = 15U;
        if (interval > 1440U) interval = 1440U;
        esp_err_t result = runtime_settings_set_time_sync_interval_min(
            (uint16_t)interval);
        if (result == ESP_OK) result = time_service_apply();
        log_setting_error("SNTP interval", result);
    } else if (strcmp(command, "volsteps") == 0) {
        unsigned steps = strtoul(value, NULL, 10);
        if (steps < 1U) steps = 1U;
        if (steps > 10U) steps = 10U;
        log_setting_error("Volume steps",
                          runtime_settings_set_volume_steps((uint8_t)steps));
    } else if (strcmp(command, "encacc") == 0) {
        unsigned acceleration = strtoul(value, NULL, 10);
        if (acceleration > RUNTIME_MAX_ENCODER_ACCELERATION) {
            acceleration = RUNTIME_MAX_ENCODER_ACCELERATION;
        }
        log_setting_error(
            "Encoder acceleration",
            runtime_settings_set_encoder_acceleration((uint16_t)acceleration));
    } else if (strcmp(command, "normalization") == 0) {
        esp_err_t result = native_audio_settings_set_normalization(
            strtoul(value, NULL, 10) != 0U);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Normalization update failed: %s",
                     esp_err_to_name(result));
        }
    } else if (strcmp(command, "normgain") == 0) {
        unsigned gain_db = strtoul(value, NULL, 10);
        if (gain_db > 20U) gain_db = 20U;
        esp_err_t result = native_audio_settings_set_normalization_gain_db(
            (uint8_t)gain_db);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Normalization gain update failed: %s",
                     esp_err_to_name(result));
        }
    } else if (strcmp(command, "normtarget") == 0) {
        long target_dbfs = strtol(value, NULL, 10);
        if (target_dbfs < -20) target_dbfs = -20;
        if (target_dbfs > 0) target_dbfs = 0;
        esp_err_t result =
            native_audio_settings_set_normalization_target_dbfs(
                (int8_t)target_dbfs);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Normalization target update failed: %s",
                     esp_err_to_name(result));
        }
    } else if (strcmp(command, "normtime") == 0) {
        unsigned long time_ms = strtoul(value, NULL, 10);
        if (time_ms < 100U) time_ms = 100U;
        if (time_ms > 10000U) time_ms = 10000U;
        esp_err_t result = native_audio_settings_set_normalization_time_ms(
            (uint16_t)time_ms);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Normalization time update failed: %s",
                     esp_err_to_name(result));
        }
    } else if (strcmp(command, "screenon") == 0) {
        log_setting_error("Screen power", display_settings_set_screen_on(
                                              strtoul(value, NULL, 10) != 0U,
                                              true));
    } else if (strcmp(command, "numplaylist") == 0) {
        log_setting_error("Numbered playlist",
                          display_settings_set_numbered_playlist(
                              strtoul(value, NULL, 10) != 0U, true));
    } else if (strcmp(command, "screensaverenabled") == 0) {
        log_setting_error("Stopped screensaver",
                          display_settings_set_screensaver_enabled(
                              strtoul(value, NULL, 10) != 0U));
    } else if (strcmp(command, "screensavertimeout") == 0) {
        unsigned timeout = strtoul(value, NULL, 10);
        if (timeout < 5U) timeout = 5U;
        if (timeout > 65520U) timeout = 65520U;
        log_setting_error("Stopped screensaver timeout",
                          display_settings_set_screensaver_timeout(timeout));
    } else if (strcmp(command, "screensaverblank") == 0) {
        log_setting_error("Stopped screensaver blank",
                          display_settings_set_screensaver_blank(
                              strtoul(value, NULL, 10) != 0U));
    } else if (strcmp(command, "screensaverplayingenabled") == 0) {
        log_setting_error("Playing screensaver",
                          display_settings_set_screensaver_playing_enabled(
                              strtoul(value, NULL, 10) != 0U));
    } else if (strcmp(command, "screensaverplayingtimeout") == 0) {
        unsigned timeout = strtoul(value, NULL, 10);
        if (timeout < 1U) timeout = 1U;
        if (timeout > 1080U) timeout = 1080U;
        log_setting_error(
            "Playing screensaver timeout",
            display_settings_set_screensaver_playing_timeout(timeout));
    } else if (strcmp(command, "screensaverplayingblank") == 0) {
        log_setting_error("Playing screensaver blank",
                          display_settings_set_screensaver_playing_blank(
                              strtoul(value, NULL, 10) != 0U));
    } else if (strcmp(command, "brightness") == 0 ||
               strcmp(command, "dim") == 0) {
        unsigned brightness = strtoul(value, NULL, 10);
        if (brightness > 100) brightness = 100;
        esp_err_t result = display_settings_set_brightness(
            (uint8_t)brightness, true);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Brightness update failed: %s",
                     esp_err_to_name(result));
        }
    } else if (strcmp(command, "stationuppercase") == 0) {
        esp_err_t result = display_settings_set_station_uppercase(
            strtoul(value, NULL, 10) != 0, true);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Station uppercase update failed: %s",
                     esp_err_to_name(result));
        }
    } else if (strcmp(command, "volp") == 0 ||
               strcmp(command, "volm") == 0) {
        display_settings_note_activity();
        int volume = native_audio_output_get_volume();
        int steps = runtime_settings_get_volume_steps();
        volume += strcmp(command, "volp") == 0 ? steps : -steps;
        if (volume < 0) volume = 0;
        if (volume > 254) volume = 254;
        native_audio_output_set_volume((uint8_t)volume);
        send_initial_state(request);
    } else if (strcmp(command, "balance") == 0) {
        display_settings_note_activity();
        int balance = strtol(value, NULL, 10);
        if (balance < -16) balance = -16;
        if (balance > 16) balance = 16;
        native_audio_output_set_balance((int8_t)balance);
        send_initial_state(request);
    }
}

static esp_err_t websocket_handler_awake(httpd_req_t *request) {
    httpd_ws_frame_t frame = {0};
    ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, 0), TAG,
                        "read WebSocket frame size");
    ws_client_t *client = ws_session(s_server, httpd_req_to_sockfd(request));
    if (!client) return ESP_FAIL;
    if (frame.len > 255) {
        (void)ws_close_client(client, 1009);
        return ESP_FAIL;
    }
    char payload[256];
    frame.payload = (uint8_t *)payload;
    // IDF uses len==0 as its header-read sentinel, so an empty frame must not
    // enter the second read or it would consume the next frame's header.
    if (frame.len) {
        ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, sizeof(payload) - 1),
                            TAG, "read WebSocket frame");
    }
    bool was_active = client->message.active;
    websocket_message_result_t message = websocket_message_feed(&client->message,
        (uint8_t)frame.type, frame.final, (const uint8_t *)payload, frame.len,
        (uint64_t)esp_timer_get_time());
    ws_update_active(client, was_active);
    if (message.event == WEBSOCKET_MESSAGE_ERROR) {
        (void)ws_close_client(client, message.close_code);
        return ESP_FAIL;
    }
    if (message.event == WEBSOCKET_MESSAGE_PING)
        return ws_send_control(client, HTTPD_WS_TYPE_PONG, message.data, message.size);
    if (message.event == WEBSOCKET_MESSAGE_CLOSE) {
        esp_err_t result = ESP_OK;
        if (!client->message.close_sent) {
            result = ws_send_control(client, HTTPD_WS_TYPE_CLOSE, message.data, message.size);
            if (result == ESP_OK) websocket_message_mark_close_sent(&client->message);
        }
        ws_finish_client(client, result == ESP_OK);
        return result;
    }
    if (message.event == WEBSOCKET_MESSAGE_BINARY) {
        (void)ws_close_client(client, 1003);
        return ESP_FAIL;
    }
    if (message.event == WEBSOCKET_MESSAGE_TEXT && message.size) {
        if (memchr(message.data, 0, message.size))
            return ws_send_request(request, "{\"commandError\":\"Command contains NUL\"}");
        handle_command(request, (char *)client->command);
    }
    return ESP_OK;
}

static esp_err_t websocket_handler(httpd_req_t *request) {
    // A successful upgrade is handled by pinned HTTPD before dispatch.
    if (request->method == HTTP_GET)
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "WebSocket upgrade required");
    if (!deep_sleep_clock_begin_activity()) return ESP_FAIL;
    ws_client_t *client = ws_session(s_server, httpd_req_to_sockfd(request));
    if (!client) {
        deep_sleep_clock_end_activity();
        return ESP_FAIL;
    }
    client->receive_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = websocket_handler_awake(request);
    client->receive_deadline_us = 0;
    if (result != ESP_OK) ws_fail_client(client);
    deep_sleep_clock_end_activity();
    return result;
}

typedef struct {
    int64_t started_us;
    uint64_t active_us;
    uint32_t polls;
    uint32_t publications;
    uint32_t deliveries;
} ws_profile_t;

static void profile_status_cycle(ws_profile_t *profile, int64_t cycle_started_us,
                                 uint32_t publications,
                                 uint32_t deliveries) {
    int64_t now_us = esp_timer_get_time();
    if (!profile->started_us) profile->started_us = cycle_started_us;
    profile->active_us += (uint64_t)(now_us - cycle_started_us);
    ++profile->polls;
    profile->publications += publications;
    profile->deliveries += deliveries;
    uint64_t window_us = (uint64_t)(now_us - profile->started_us);
    if (window_us < 5000000ULL) return;
    uint64_t tenths = profile->active_us * 1000ULL / window_us;
    ESP_LOGI(TAG,
             "PERF WS: active %llu us (%llu.%llu%%), polls %lu, "
             "publications %lu, deliveries %lu, clients %u",
             (unsigned long long)profile->active_us,
             (unsigned long long)(tenths / 10ULL),
             (unsigned long long)(tenths % 10ULL),
             (unsigned long)profile->polls,
             (unsigned long)profile->publications,
             (unsigned long)profile->deliveries,
             (unsigned)atomic_load(&s_last_ws_clients));
    memset(profile, 0, sizeof(*profile));
    profile->started_us = now_us;
}

static void status_task(void *argument) {
    (void)argument;
    bool have_previous = false;
    TickType_t last_sent = 0;
    ws_profile_t profile = {0};
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(WS_STATUS_POLL_MS));
        int64_t cycle_started_us = esp_timer_get_time();
        poll_reboot();
        web_tcp_probe_poll();
        poll_message_deadlines();
        uint32_t publications = 0;
        uint32_t deliveries = atomic_exchange(&s_completed_deliveries, 0U);
        capture_status_key(&s_current_status_key);
        TickType_t now = xTaskGetTickCount();
        bool changed = !have_previous ||
                       memcmp(&s_current_status_key, &s_previous_status_key,
                              sizeof(s_current_status_key)) != 0;
        bool heartbeat = !last_sent ||
                         now - last_sent >=
                             pdMS_TO_TICKS(WS_STATUS_HEARTBEAT_MS);
        if (atomic_exchange(&s_playlist_changed_pending, false)) {
            ESP_LOGI(TAG, "Broadcasting playlist changed event");
            if (!broadcast_text(
                "{\"file\":\"/data/playlist.csv\"}",
                &s_status_send_pending, &s_playlist_work)) {
                atomic_store(&s_playlist_changed_pending, true);
            } else ++publications;
        }
        if ((changed || heartbeat) &&
            atomic_load(&s_status_send_pending) == 0U) {
            bool station_changed = !have_previous ||
                                   s_current_status_key.current_item !=
                                       s_previous_status_key.current_item;
            format_status(s_broadcast_status, sizeof(s_broadcast_status));
            bool publish_current = station_changed &&
                atomic_load(&s_current_send_pending) == 0U;
            if (publish_current) {
                snprintf(s_broadcast_current, sizeof(s_broadcast_current),
                         "{\"current\":%u}",
                         s_current_status_key.current_item);
            }
            bool status_queued = broadcast_text(
                s_broadcast_status, &s_status_send_pending, &s_status_work);
            if (status_queued) ++publications;
            bool current_queued = !station_changed;
            if (publish_current) {
                current_queued = broadcast_text(
                    s_broadcast_current, &s_current_send_pending, &s_current_work);
                if (current_queued) ++publications;
            }
            if (status_queued && current_queued) {
                s_previous_status_key = s_current_status_key;
                have_previous = true;
                last_sent = now;
            }
        }
        profile_status_cycle(&profile, cycle_started_us, publications,
                             deliveries);
    }
}

void websocket_service_notify_playlist_changed(void) {
    atomic_store(&s_playlist_changed_pending, true);
}

esp_err_t websocket_service_register(httpd_handle_t server,
                                     native_state_t *state) {
    s_server = server;
    s_state = state;
    httpd_uri_t websocket = {
        .uri = "/ws",
        .method = HTTP_GET,
        .handler = websocket_handler,
        .is_websocket = true,
        .handle_ws_control_frames = true,
        .ws_pre_handshake_cb = websocket_pre_handshake,
        .ws_post_handshake_cb = websocket_post_handshake,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &websocket), TAG,
                        "register native WebSocket route");
    ESP_RETURN_ON_FALSE(xTaskCreate(status_task, "websocket_status",
                                    BOARD_TASK_STACK_WEBSOCKET_STATUS,
                                    NULL, 2, NULL) == pdPASS,
                        ESP_ERR_NO_MEM, TAG, "start WebSocket status task");
    atomic_store(&s_reboot_ready, true);
    return ESP_OK;
}
