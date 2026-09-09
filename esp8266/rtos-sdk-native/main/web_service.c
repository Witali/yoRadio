#include "web_service.h"
#include "web_audio_pause_config.h"
#include "memory_profile.h"
#include "spiffs_log.h"
#include "json_text.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

#include "board_config.h"
#include "esp_http_server.h"
#include "httpd_trace.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_ota_ops.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "lwip/tcp.h"
#include "native_audio_output.h"
#include "audio_service.h"
#include "opus_benchmark.h"
#include "native_state.h"
#include "persistent_settings.h"
#include "playlist_service.h"
#include "playlist_web_cache.h"
#include "radio_control.h"
#include "time_service.h"
#include "web_pages_bridge.h"
#include "web_upload.h"
#include "web_encoding.h"
#include "web_bundle_generated.h"
#include "network_service.h"
#include "file_replace.h"

#define WS_HEARTBEAT_MS 2000U
#define WS_COMMAND_MAX 255U
#define WEB_STATUS_CAPACITY 1088U
#define WEB_MAX_OPEN_SOCKETS 4U
#define WEB_CONNECTION_BACKLOG 3U
#define WEB_IDLE_TIMEOUT_SECONDS 2U
#define WEB_SEND_CHUNK_SIZE 1024U
#define WEB_STATIC_SCRATCH_SIZE 1024U
#define WEB_WS_CLIENTS 2U
#if !CONFIG_LWIP_SO_LINGER
#error "Native WebUI requires CONFIG_LWIP_SO_LINGER=y for failed-connection cleanup"
#endif

/* This SDK counts the TCP listener and pending accepts in its PCB limit.
 * Exhausting it can silently abandon FIN_WAIT_1 with response data pending. */
_Static_assert(CONFIG_LWIP_MAX_ACTIVE_TCP >=
                   WEB_MAX_OPEN_SOCKETS + WEB_CONNECTION_BACKLOG + 2U,
               "TCP budget must include HTTP sessions, backlog, listener and radio");

extern const unsigned char _binary_script_js_gz_start[];
extern const unsigned char _binary_script_js_gz_end[];

static const char *TAG = "web";
static httpd_handle_t s_server;
#include "web_connection_close.inc"
/* Only the HTTP task owns subscribers and formats/sends this shared buffer.
 * The app task queues a poll, never writes a buffer being transmitted. */
static int s_ws_fds[WEB_WS_CLIENTS] = {-1, -1};
static volatile bool s_poll_queued;
static volatile bool s_playlist_changed;
static char s_async_message[WEB_STATUS_CAPACITY];
/* All static routes run serially on the HTTP task, so one DRAM buffer can
 * replace the former 512/672-byte per-handler stack arrays. */
static char s_static_scratch[WEB_STATIC_SCRATCH_SIZE];
static bool s_bundle_current;

typedef struct {
    bool playing;
    bool connecting;
    uint16_t station_index;
    uint8_t volume;
    uint32_t bitrate_kbps;
    uint32_t sample_rate_hz;
    uint8_t channels;
    codec_type_t codec;
    uint32_t station_hash;
    uint32_t title_hash;
} web_status_key_t;

_Static_assert(sizeof(web_status_key_t) <= 32U,
               "Web status change key must stay compact");

typedef struct {
    char *output;
    size_t capacity;
    size_t length;
    bool valid;
} json_writer_t;

static web_status_key_t s_previous_status;
static bool s_have_previous_status;
static TickType_t s_last_status_tick;

static void copy_text(char *target, size_t capacity, const char *source) {
    if (!capacity) return;
    source = source ? source : "";
    size_t length = strlen(source);
    if (length >= capacity) length = capacity - 1U;
    memcpy(target, source, length);
    target[length] = '\0';
}

static esp_err_t send_string(httpd_req_t *request, const char *text) {
    return httpd_resp_send(request, text, (ssize_t)strlen(text));
}

static esp_err_t send_chunked_string(httpd_req_t *request, const char *text) {
    size_t remaining = strlen(text);
    while (remaining) {
        size_t count = remaining > WEB_SEND_CHUNK_SIZE
                           ? WEB_SEND_CHUNK_SIZE : remaining;
        /* Generated pages are stored in memory-mapped IROM. lwIP on the
         * ESP8266 needs a DRAM-backed source while it queues socket data. */
        memcpy(s_static_scratch, text, count);
        esp_err_t result = httpd_resp_send_chunk(request,
                                                 s_static_scratch, count);
        if (result != ESP_OK) return result;
        text += count;
        remaining -= count;
    }
    return httpd_resp_send_chunk(request, NULL, 0);
}

static void json_escape(const char *source, char *target, size_t capacity) {
    size_t written = 0;
    if (!capacity) return;
    while (source && *source && written + 1U < capacity) {
        char encoded[5];
        size_t count = json_text_unit(&source, encoded);
        if (count >= capacity - written) break;
        memcpy(target + written, encoded, count);
        written += count;
    }
    target[written] = '\0';
}

static uint32_t text_hash(const char *text) {
    uint32_t hash = 2166136261UL;
    while (text && *text) {
        hash ^= (uint8_t)*text++;
        hash *= 16777619UL;
    }
    return hash;
}

static void json_writer_init(json_writer_t *writer, char *output,
                             size_t capacity) {
    writer->output = output;
    writer->capacity = capacity;
    writer->length = 0;
    writer->valid = capacity != 0U;
    if (capacity) output[0] = '\0';
}

static void json_writer_raw(json_writer_t *writer, const char *text) {
    if (!writer->valid) return;
    size_t length = strlen(text);
    if (length >= writer->capacity - writer->length) {
        writer->valid = false;
        return;
    }
    memcpy(writer->output + writer->length, text, length + 1U);
    writer->length += length;
}

static void json_writer_format(json_writer_t *writer, const char *format, ...) {
    if (!writer->valid) return;
    va_list arguments;
    va_start(arguments, format);
    int length = vsnprintf(writer->output + writer->length,
                           writer->capacity - writer->length,
                           format, arguments);
    va_end(arguments);
    if (length < 0 || (size_t)length >= writer->capacity - writer->length) {
        writer->valid = false;
        return;
    }
    writer->length += (size_t)length;
}

static void json_writer_escaped(json_writer_t *writer, const char *text) {
    while (writer->valid && text && *text) {
        char encoded[5];
        if (!json_text_unit(&text, encoded)) continue;
        json_writer_raw(writer, encoded);
    }
}

static void capture_status(web_status_key_t *key, native_state_t *state) {
    native_state_snapshot(state);
    memset(key, 0, sizeof(*key));
    key->playing = state->playing;
    key->connecting = state->connecting;
    key->station_index = state->station_index;
    key->volume = state->volume;
    key->bitrate_kbps = state->bitrate_kbps;
    key->sample_rate_hz = state->sample_rate_hz;
    key->channels = state->channels;
    key->codec = state->codec;
    key->station_hash = text_hash(state->station);
    key->title_hash = text_hash(state->title) ^ text_hash(state->error);
}

static bool status_requires_immediate_send(const web_status_key_t *current,
                                           const web_status_key_t *previous) {
    return current->playing != previous->playing ||
           current->connecting != previous->connecting ||
           current->station_index != previous->station_index ||
           current->volume != previous->volume ||
           current->sample_rate_hz != previous->sample_rate_hz ||
           current->channels != previous->channels ||
           current->codec != previous->codec ||
           current->station_hash != previous->station_hash ||
           current->title_hash != previous->title_hash;
}

static void format_stream(const native_state_t *status, char *output,
                          size_t capacity) {
    const char *codec = native_codec_name(status->codec);
    const char *channels = status->channels == 1U ? "mono" :
                           status->channels == 2U ? "stereo" : "";
    if (!codec[0]) {
        output[0] = '\0';
    } else {
        snprintf(output, capacity, "%s %lu kbps %lu kHz %s", codec,
                 (unsigned long)status->bitrate_kbps,
                 (unsigned long)(status->sample_rate_hz / 1000U), channels);
    }
}

static bool format_status(const native_state_t *status, char *output,
                          size_t capacity) {
    char stream[64];
    format_stream(status, stream, sizeof(stream));
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    persistent_web_settings_t web;
    persistent_settings_get_web(&web);
    json_writer_t writer;
    json_writer_init(&writer, output, capacity);
    json_writer_raw(&writer,
                    "{\"payload\":[{\"id\":\"nameset\",\"value\":\"");
    json_writer_escaped(&writer, status->station);
    json_writer_raw(&writer, "\"},{\"id\":\"meta\",\"value\":\"");
    json_writer_escaped(&writer, status->error[0] && !status->playing
                                    ? status->error : status->title);
    json_writer_format(
        &writer,
        "\"},{\"id\":\"volume\",\"value\":%u},"
        "{\"id\":\"balance\",\"value\":%d},"
        "{\"id\":\"rssi\",\"value\":%d},"
        "{\"id\":\"heap\",\"value\":%u},"
        "{\"id\":\"bitrate\",\"value\":%lu},"
        "{\"id\":\"fmt\",\"value\":\"",
        volume_to_percent(status->volume), settings.balance, status->wifi_rssi,
        status->playing && web.audio_info ? status->buffer_percent : 0U,
        (unsigned long)status->bitrate_kbps);
    json_writer_escaped(&writer, stream);
    json_writer_format(
        &writer,
        "\"},{\"id\":\"upst\",\"value\":%u},"
        "{\"id\":\"playerwrap\",\"value\":\"%s\"},"
        "{\"id\":\"connecting\",\"value\":%s}]}",
        settings.station_uppercase ? 1U : 0U,
        status->playing ? "playing" : "stopped",
        status->connecting ? "true" : "false");
    if (writer.valid) return true;
    copy_text(output, capacity, "{\"error\":\"status overflow\"}");
    return false;
}

static esp_err_t ws_send(httpd_req_t *request, const char *text) {
    httpd_ws_frame_t frame = {
        .final = true,
        .fragmented = false,
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text,
        .len = strlen(text),
    };
    return httpd_ws_send_frame(request, &frame);
}

static bool websocket_socket_active(int socket) {
    return s_server && socket >= 0 &&
           httpd_ws_get_fd_info(s_server, socket) ==
               HTTPD_WS_CLIENT_WEBSOCKET;
}

static bool broadcast_message(const char *message) {
    bool sent = false;
    for (unsigned i = 0; i < WEB_WS_CLIENTS; ++i) {
        int socket = s_ws_fds[i];
        if (!websocket_socket_active(socket)) {
            s_ws_fds[i] = -1;
            continue;
        }
        httpd_ws_frame_t frame = {
            .final = true,
            .fragmented = false,
            .type = HTTPD_WS_TYPE_TEXT,
            .payload = (uint8_t *)message,
            .len = strlen(message),
        };
        if (httpd_ws_send_frame_async(s_server, socket, &frame) != ESP_OK) {
            httpd_sess_trigger_close(s_server, socket);
            s_ws_fds[i] = -1;
        } else {
            httpd_sess_update_lru_counter(s_server, socket);
            sent = true;
        }
    }
    return sent;
}

static bool subscribe_socket(int socket) {
    int available = -1;
    for (unsigned i = 0; i < WEB_WS_CLIENTS; ++i) {
        if (s_ws_fds[i] == socket) return true;
        if (!websocket_socket_active(s_ws_fds[i])) available = (int)i;
    }
    if (available < 0) return false;
    s_ws_fds[available] = socket;
    return true;
}

static void session_closed(httpd_handle_t server, int socket) {
    (void)server;
    web_close_forget(socket);
    for (unsigned i = 0; i < WEB_WS_CLIENTS; ++i)
        if (s_ws_fds[i] == socket) s_ws_fds[i] = -1;
    /* This SDK closes the descriptor after calling close_fn. */
}

static esp_err_t session_opened(httpd_handle_t server, int socket) {
    (void)server;
    web_close_forget(socket);
    /* A failed WebSocket send must not leave retransmission buffers in
     * FIN_WAIT_1 after the session is deleted. Successful HTTP responses
     * still half-close first and receive the bounded grace period. */
    struct linger abort_pending = {.l_onoff = 1, .l_linger = 0};
    if (setsockopt(socket, SOL_SOCKET, SO_LINGER,
                   &abort_pending, sizeof(abort_pending)) != 0) return ESP_FAIL;
    int enabled = 1;
    /* HTTP headers/chunk delimiters and WS headers are short writes. Do not
     * make each one wait for a delayed TCP ACK before sending its payload. */
    return setsockopt(socket, IPPROTO_TCP, TCP_NODELAY,
                      &enabled, sizeof(enabled)) == 0 ? ESP_OK : ESP_FAIL;
}

static esp_err_t send_initial_state(httpd_req_t *request) {
    native_state_t state;
    web_status_key_t status;
    char current[40];
    /* Initial replies and broadcasts execute on the same HTTP task. */
    capture_status(&status, &state);
    if (!format_status(&state, s_async_message, sizeof(s_async_message))) {
        return ESP_ERR_INVALID_SIZE;
    }
    esp_err_t result = ws_send(request, s_async_message);
    if (result != ESP_OK) return result;
    snprintf(current, sizeof(current), "{\"current\":%u}",
             status.station_index);
    if ((result = ws_send(request, current)) != ESP_OK) return result;
    if ((result = ws_send(request, "{\"sdinit\":0}")) != ESP_OK)
        return result;
    return ws_send(request, "{\"playermode\":\"modeweb\"}");
}

static esp_err_t send_current_volume(httpd_req_t *request) {
    /* Match Arduino's VOLUME response. Station/SD/mode did not change;
     * notifying other subscribers remains the normal state-change path. */
    char body[48];
    snprintf(body, sizeof(body),
             "{\"payload\":[{\"id\":\"volume\",\"value\":%u}]}",
             (unsigned)radio_control_volume());
    return ws_send(request, body);
}

static esp_err_t send_active_settings(httpd_req_t *request) {
    native_state_t state;
    native_state_snapshot(&state);
    if (state.network_mode != NETWORK_CLIENT) {
        return ws_send(request, "{\"act\":[\"group_wifi\"]}");
    }
    esp_err_t result = ws_send(
        request,
        "{\"act\":[\"group_wifi\",\"group_system\","
#if CONFIG_YORADIO_OLED
        "\"group_display\",\"group_oled\","
#endif
#if BOARD_ENCODER_A_GPIO >= 0 && BOARD_ENCODER_B_GPIO >= 0
        "\"group_encoder\","
#endif
        "\"group_timezone\",\"group_controls\",\"group_wortc\"]}");
    if (result != ESP_OK) return result;
#if !CONFIG_YORADIO_OLED
    if ((result = ws_send(request, "{\"nativeAppearance\":true}")) != ESP_OK)
        return result;
#endif
    return ws_send(request,
                   "{\"hide\":[\"telnet\",\"skipup\",\"mdnsnamerow\","
                   "\"radiolink\",\"group_weather\",\"group_buffer\","
                   "\"watchdog\",\"dspon\",\"con\",\"scrpe\",\"scrpt\",\"scrpb\"]}");
}

static esp_err_t send_system_settings(httpd_req_t *request) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    persistent_web_settings_t web;
    persistent_settings_get_web(&web);
    native_state_t state;
    native_state_snapshot(&state);
    char body[420];
    snprintf(body, sizeof(body),
             "{\"sst\":%u,\"aif\":%u,\"vu\":0,\"softr\":%u,\"vut\":0,"
             "\"mdns\":\"%s\",\"ipaddr\":\"%s\",\"abuff\":0,"
             "\"abuffmax\":0,\"mp3decoder\":0,\"normalize\":%u,"
             "\"normgain\":%u,\"normtarget\":%d,\"normtime\":%u,"
             "\"telnet\":0,\"watchdog\":0}",
             settings.smart_start, web.audio_info ? 1U : 0U,
             web.softap_delay_min, settings.mdns_name,
             state.ip[0] ? state.ip : "0.0.0.0",
             settings.normalization_enabled ? 1U : 0U,
             settings.normalization_max_gain_db,
             settings.normalization_target_db,
             settings.normalization_time_ms);
    return ws_send(request, body);
}

static esp_err_t send_screen_settings(httpd_req_t *request) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    char body[260];
    snprintf(body, sizeof(body),
             "{\"flip\":0,\"inv\":0,\"nump\":%u,\"tsf\":0,\"tsd\":0,"
             "\"upst\":%u,\"dspon\":1,\"br\":%u,\"con\":55,"
             "\"scre\":%u,\"scrt\":%u,\"scrb\":%u,"
             "\"scrpe\":0,\"scrpt\":5,\"scrpb\":0}",
             settings.numbered_playlist ? 1U : 0U,
             settings.station_uppercase ? 1U : 0U, settings.brightness,
             settings.screensaver_enabled ? 1U : 0U,
             settings.screensaver_timeout_s,
             settings.screensaver_blank ? 1U : 0U);
    return ws_send(request, body);
}

static esp_err_t send_timezone_settings(httpd_req_t *request) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    char server1[SETTINGS_SNTP_CAPACITY * 2U];
    char server2[SETTINGS_SNTP_CAPACITY * 2U];
    char body[260];
    json_escape(settings.sntp1, server1, sizeof(server1));
    json_escape(settings.sntp2, server2, sizeof(server2));
    snprintf(body, sizeof(body),
             "{\"tzh\":%d,\"tzm\":%u,\"sntp1\":\"%s\","
             "\"sntp2\":\"%s\",\"timeint\":%u,\"timeintrtc\":24}",
             settings.timezone_hour, settings.timezone_minute, server1,
             server2, settings.time_sync_interval_min);
    return ws_send(request, body);
}

static esp_err_t send_control_settings(httpd_req_t *request) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    char body[100];
    snprintf(body, sizeof(body),
             "{\"vols\":%u,\"enca\":%u,\"irtl\":10,\"skipup\":1}",
             settings.volume_steps, settings.encoder_acceleration);
    return ws_send(request, body);
}

static bool update_settings(const persistent_settings_t *settings,
                            bool reload_audio) {
    esp_err_t result = persistent_settings_update_runtime(settings);
    if (result != ESP_OK) {
        ESP_LOGW(TAG, "Rejected WebUI settings update: %s",
                 esp_err_to_name(result));
        return false;
    }
    if (reload_audio) native_audio_output_reload_settings();
    radio_control_settings_changed();
    return true;
}

static unsigned parse_unsigned(const char *value, unsigned maximum) {
    unsigned long parsed = strtoul(value, NULL, 10);
    return parsed > maximum ? maximum : (unsigned)parsed;
}

static void handle_command(httpd_req_t *request, char *command) {
    char *separator = strchr(command, '=');
    char *value = separator ? separator + 1 : (char *)"";
    if (separator) *separator = '\0';

    if (strcmp(command, "ping") == 0) {
        ws_send(request, "{\"pong\":1}");
    } else if (strcmp(command, "getindex") == 0) {
        httpd_trace_index_begin();
        esp_err_t index_result = send_initial_state(request);
        httpd_trace_end(index_result);
    } else if (strcmp(command, "getactive") == 0) {
        send_active_settings(request);
    } else if (strcmp(command, "getsystem") == 0) {
        send_system_settings(request);
    } else if (strcmp(command, "getscreen") == 0) {
        send_screen_settings(request);
    } else if (strcmp(command, "gettimezone") == 0) {
        send_timezone_settings(request);
    } else if (strcmp(command, "getweather") == 0) {
        ws_send(request,
                "{\"wen\":0,\"wlat\":\"\",\"wlon\":\"\","
                "\"wkey\":\"\",\"wint\":60}");
    } else if (strcmp(command, "getcontrols") == 0) {
        send_control_settings(request);
    } else if (strcmp(command, "reboot") == 0) {
        ws_send(request, "{\"accepted\":true}");
        web_upload_request_reboot();
    } else if (strcmp(command, "reset") == 0) {
        if (persistent_settings_reset_group(value) != ESP_OK) {
            ws_send(request, "{\"commandError\":\"Unknown settings group\"}");
        } else {
            radio_control_settings_changed();
            native_audio_output_reload_settings();
            time_service_settings_changed();
            if (strcmp(value, "1") == 0) web_upload_request_reboot();
            else {
                send_system_settings(request);
                send_screen_settings(request);
                send_timezone_settings(request);
                send_control_settings(request);
            }
        }
    } else if (strcmp(command, "audioinfo") == 0 ||
               strcmp(command, "softap") == 0) {
        persistent_web_settings_t web;
        persistent_settings_get_web(&web);
        if (strcmp(command, "audioinfo") == 0)
            web.audio_info = parse_unsigned(value, 1U) != 0;
        else web.softap_delay_min = (uint8_t)parse_unsigned(value, 30U);
        if (persistent_settings_update_web(&web) == ESP_OK) {
            radio_control_settings_changed();
            ws_send(request, "{\"accepted\":true}");
        } else ws_send(request, "{\"commandError\":\"Invalid settings\"}");
    } else if (strcmp(command, "play") == 0) {
        radio_control_play((uint16_t)strtoul(value, NULL, 10));
    } else if (strcmp(command, "stop") == 0) {
        radio_control_stop();
    } else if (strcmp(command, "toggle") == 0) {
        radio_control_toggle();
    } else if (strcmp(command, "next") == 0) {
        radio_control_next();
    } else if (strcmp(command, "prev") == 0) {
        radio_control_previous();
    } else if (strcmp(command, "volume") == 0) {
        httpd_trace_volume_begin();
        char *end;
        long target = strtol(value, &end, 10);
        if (end == value || *end != '\0') {
            ws_send(request, "{\"commandError\":\"Invalid volume\"}");
            return;
        }
        if (target < 0) target = 0;
        if (target > RADIO_VOLUME_MAX) target = RADIO_VOLUME_MAX;
        if (radio_control_set_volume((int)target) != ESP_OK) {
            ws_send(request, "{\"commandError\":\"Volume busy\"}");
            return;
        }
        send_current_volume(request);
    } else if (strcmp(command, "volp") == 0 ||
               strcmp(command, "volm") == 0) {
        httpd_trace_volume_begin();
        persistent_settings_t settings;
        persistent_settings_get(&settings);
        int delta = settings.volume_steps;
        radio_control_adjust_volume(strcmp(command, "volp") == 0 ? delta
                                                                  : -delta);
        send_current_volume(request);
    } else {
        persistent_settings_t settings;
        persistent_settings_get(&settings);
        bool changed = true;
        bool reload_audio = false;
        if (strcmp(command, "balance") == 0) {
            long balance = strtol(value, NULL, 10);
            if (balance < -16) balance = -16;
            if (balance > 16) balance = 16;
            settings.balance = (int8_t)balance;
            native_audio_output_set_balance_runtime(settings.balance);
            reload_audio = true;
        } else if (strcmp(command, "smartstart") == 0) {
            settings.smart_start = (uint8_t)parse_unsigned(value, 2U);
        } else if (strcmp(command, "normalization") == 0) {
            settings.normalization_enabled = strtoul(value, NULL, 10) != 0U;
            reload_audio = true;
        } else if (strcmp(command, "normgain") == 0) {
            settings.normalization_max_gain_db =
                (uint8_t)parse_unsigned(value, 24U);
            reload_audio = true;
        } else if (strcmp(command, "normtarget") == 0) {
            long target = strtol(value, NULL, 10);
            if (target < -24) target = -24;
            if (target > 0) target = 0;
            settings.normalization_target_db = (int8_t)target;
            reload_audio = true;
        } else if (strcmp(command, "normtime") == 0) {
            unsigned time_ms = parse_unsigned(value, 30000U);
            if (time_ms < 100U) time_ms = 100U;
            settings.normalization_time_ms = (uint16_t)time_ms;
            reload_audio = true;
        } else if (strcmp(command, "brightness") == 0 ||
                   strcmp(command, "dim") == 0) {
            settings.brightness = (uint8_t)parse_unsigned(value, 100U);
        } else if (strcmp(command, "stationuppercase") == 0) {
            settings.station_uppercase = strtoul(value, NULL, 10) != 0U;
        } else if (strcmp(command, "numplaylist") == 0) {
            settings.numbered_playlist = strtoul(value, NULL, 10) != 0U;
        } else if (strcmp(command, "screensaverenabled") == 0) {
            settings.screensaver_enabled = strtoul(value, NULL, 10) != 0U;
        } else if (strcmp(command, "screensaverblank") == 0) {
            settings.screensaver_blank = strtoul(value, NULL, 10) != 0U;
        } else if (strcmp(command, "screensavertimeout") == 0) {
            unsigned timeout = parse_unsigned(value, 65520U);
            if (timeout < 5U) timeout = 5U;
            settings.screensaver_timeout_s = (uint16_t)timeout;
        } else if (strcmp(command, "tzh") == 0) {
            long hour = strtol(value, NULL, 10);
            if (hour < -12) hour = -12;
            if (hour > 14) hour = 14;
            settings.timezone_hour = (int8_t)hour;
        } else if (strcmp(command, "tzm") == 0) {
            settings.timezone_minute =
                (uint8_t)(parse_unsigned(value, 45U) / 15U * 15U);
        } else if (strcmp(command, "timeint") == 0) {
            unsigned interval = parse_unsigned(value, 1440U);
            if (interval < 15U) interval = 15U;
            settings.time_sync_interval_min = (uint16_t)interval;
        } else if (strcmp(command, "sntp1") == 0) {
            copy_text(settings.sntp1, sizeof(settings.sntp1), value);
        } else if (strcmp(command, "sntp2") == 0) {
            copy_text(settings.sntp2, sizeof(settings.sntp2), value);
        } else if (strcmp(command, "volsteps") == 0) {
            unsigned steps = parse_unsigned(value, 10U);
            settings.volume_steps = (uint8_t)(steps ? steps : 1U);
        } else if (strcmp(command, "encacc") == 0) {
            settings.encoder_acceleration =
                (uint16_t)parse_unsigned(value, 1000U);
        } else {
            changed = false;
        }
        if (changed) {
            bool accepted = update_settings(&settings, reload_audio);
            if (accepted && (strcmp(command, "tzh") == 0 ||
                strcmp(command, "tzm") == 0 || strcmp(command, "timeint") == 0 ||
                strcmp(command, "sntp1") == 0 || strcmp(command, "sntp2") == 0))
                time_service_settings_changed();
            ws_send(request, accepted
                ? "{\"accepted\":true}"
                : "{\"commandError\":\"Settings rejected\"}");
        } else if (strcmp(command, "submitplaylist") != 0 &&
                   strcmp(command, "submitplaylistdone") != 0) {
            ws_send(request, "{\"commandError\":\"Unsupported command in this build\"}");
        }
    }
}

static esp_err_t websocket_handler(httpd_req_t *request) {
    if (request->method == HTTP_GET) {
        char query[32], initial[4];
        if (httpd_req_get_url_query_str(request, query, sizeof(query)) == ESP_OK &&
            httpd_query_key_value(query, "initial", initial, sizeof(initial)) == ESP_OK &&
            strcmp(initial, "1") == 0) {
            if (!subscribe_socket(httpd_req_to_sockfd(request))) return ESP_FAIL;
            return send_initial_state(request);
        }
        /* Legacy clients still explicitly send getindex after installing DOM. */
        return ESP_OK;
    }

    int socket = httpd_req_to_sockfd(request);
    if (!subscribe_socket(socket)) return ESP_FAIL;
    char payload[WS_COMMAND_MAX + 1U];
    httpd_ws_frame_t frame = {
        .payload = (uint8_t *)payload,
    };
    esp_err_t result =
        httpd_ws_recv_frame(request, &frame, sizeof(payload) - 1U);
    if (result != ESP_OK) return result;
    if (frame.type != HTTPD_WS_TYPE_TEXT || frame.len == 0U ||
        frame.len > WS_COMMAND_MAX) {
        return ESP_OK;
    }
    payload[frame.len] = '\0';
    handle_command(request, payload);
    return ESP_OK;
}

static FILE *open_nonempty(const char *path) {
    FILE *file = fopen(path, "rb");
    if (!file) return NULL;
    if (fgetc(file) == EOF || fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return NULL;
    }
    return file;
}

/* Run before HTTP starts: compare actual SPIFFS assets to the build inputs.
 * Only one existing scratch buffer is used. Never serve stale bundled UI
 * after a custom file upload or in place of the empty-filesystem uploader. */
static bool bundle_matches_spiffs(void) {
    for (unsigned i = 0; i < sizeof(web_bundle_files)/sizeof(web_bundle_files[0]); ++i) {
        FILE *file = fopen(web_bundle_files[i].path, "rb");
        if (!file) return false;
        uint32_t hash = 2166136261U;
        size_t n;
        while ((n = fread(s_static_scratch, 1, sizeof(s_static_scratch), file))) {
            for (size_t j = 0; j < n; ++j)
                hash = (hash ^ (uint8_t)s_static_scratch[j]) * 16777619U;
        }
        bool matches = !ferror(file) && hash == web_bundle_files[i].hash;
        fclose(file);
        if (!matches) return false;
    }
    return true;
}

void web_service_notify_assets_changed(void) {
    /* Upload runs on the HTTP task, as do readers of this flag. Revalidate
     * once at next boot; meanwhile use the freshly uploaded original assets. */
    s_bundle_current = false;
}

static size_t request_path_length(const httpd_req_t *request) {
    const char *query = strchr(request->uri, '?');
    return query ? (size_t)(query - request->uri) : strlen(request->uri);
}

static bool request_path_equals(const httpd_req_t *request,
                                const char *path) {
    size_t length = request_path_length(request);
    return strlen(path) == length &&
           memcmp(request->uri, path, length) == 0;
}

static bool web_ui_available(void) {
    static const char *required[] = {
        "theme.css.gz", "style.css.gz", "script.js.gz", "dragpl.js.gz",
        "player.html.gz", "options.html.gz", "logo.svg.gz",
    };
    char path[80];
    for (unsigned index = 0;
         index < sizeof(required) / sizeof(required[0]); ++index) {
        snprintf(path, sizeof(path), "/spiffs/www/%s", required[index]);
        FILE *file = open_nonempty(path);
        if (!file) return false;
        fclose(file);
    }
    return true;
}

static void prepare_short_response(httpd_req_t *request) {
    /* ESP8266's old esp_http_server can leave the final five-byte chunk in
     * lwIP indefinitely on a persistent connection.  Connection: close is
     * standard HTTP/1.1 framing and also keeps static downloads from holding
     * one of the four scarce TCP sessions. */
    httpd_resp_set_hdr(request, "Connection", "close");
}

static esp_err_t finish_short_response(httpd_req_t *request,
                                       esp_err_t result) {
    return web_service_finish_response(request, result);
}

static const char *asset_type(const char *uri) {
    if (strstr(uri, ".css")) return "text/css; charset=utf-8";
    if (strstr(uri, ".js")) return "application/javascript; charset=utf-8";
    if (strstr(uri, ".html")) return "text/html; charset=utf-8";
    if (strstr(uri, ".svg")) return "image/svg+xml";
    return "application/octet-stream";
}

static esp_err_t page_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_hdr(request, "Vary", "Accept-Encoding");
    char encoding[128];
    const char *accept_encoding = NULL;
    esp_err_t header_result = httpd_req_get_hdr_value_str(
        request, "Accept-Encoding", encoding, sizeof(encoding));
    if (header_result == ESP_OK) accept_encoding = encoding;
    else if (httpd_req_get_hdr_value_len(request, "Accept-Encoding") >= sizeof(encoding)) {
        httpd_resp_set_status(request, "431 Request Header Fields Too Large");
        return finish_short_response(request, send_string(request, "Accept-Encoding too long"));
    }
    int gzip_quality = web_encoding_quality(accept_encoding, "gzip");
    int identity_quality = web_encoding_quality(accept_encoding, "identity");
    bool settings_page = request_path_equals(request, "/settings.html");
    if (s_bundle_current && network_service_connected() && gzip_quality > 0 &&
        gzip_quality >= identity_quality &&
        (settings_page || request_path_equals(request, "/") || request_path_equals(request, "/index.html"))) {
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
        /* Its length is known; the HTTP server stages flash data in bounded
         * pieces while preserving a single Content-Length response. */
        const unsigned char *bundle = settings_page ? web_settings_bundle_gzip : web_bundle_gzip;
        size_t bundle_size = settings_page ? sizeof(web_settings_bundle_gzip) : sizeof(web_bundle_gzip);
        esp_err_t result = httpd_resp_send(request, (const char *)bundle, bundle_size);
        return finish_short_response(request, result);
    }
    if (!identity_quality) {
        httpd_resp_set_status(request, "406 Not Acceptable");
        return finish_short_response(request, send_string(request, "No acceptable page encoding"));
    }
    if (request_path_equals(request, "/emergency")) {
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return finish_short_response(
            request, send_chunked_string(request, yoradio_emergency_form()));
    }
    if (request_path_equals(request, "/webboard") ||
        (request_path_equals(request, "/") && !web_ui_available())) {
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        return finish_short_response(
            request, send_chunked_string(request, yoradio_emptyfs_html()));
    }
    httpd_resp_set_type(request, "text/html; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return finish_short_response(
        request, send_chunked_string(request, yoradio_index_html()));
}

static esp_err_t variables_handler(httpd_req_t *request) {
    prepare_short_response(request);
    native_state_t state;
    native_state_snapshot(&state);
    char body[240];
    snprintf(body, sizeof(body),
             "var yoVersion='esp8266-native';\n"
             "var webUiRevision='8266vol100';\n"
             "var formAction='%s';\n"
             "var playMode='%s';\n"
             "var equalizerEnabled=false;\n"
             "var nativeFirmwareOnly=true;\n"
             "var volumeMax=100;\n",
             "",
             state.network_mode == NETWORK_CLIENT ? "player" : "ap");
    httpd_resp_set_type(request, "application/javascript; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return finish_short_response(request, send_string(request, body));
}

static esp_err_t asset_handler(httpd_req_t *request) {
    prepare_short_response(request);
    if (request_path_equals(request, "/script.js") &&
        !file_exists("/spiffs/www/script.js.gz")) {
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
        httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
        const unsigned char *cursor = _binary_script_js_gz_start;
        esp_err_t result = ESP_OK;
        while (cursor < _binary_script_js_gz_end) {
            size_t remaining = (size_t)(_binary_script_js_gz_end - cursor);
            size_t count = remaining > WEB_SEND_CHUNK_SIZE
                               ? WEB_SEND_CHUNK_SIZE : remaining;
            /* ESP8266 socket writes need a DRAM-backed source; the embedded
             * asset lives in memory-mapped IROM. */
            memcpy(s_static_scratch, cursor, count);
            result = httpd_resp_send_chunk(request, s_static_scratch, count);
            if (result != ESP_OK) break;
            cursor += count;
        }
        if (result == ESP_OK)
            result = httpd_resp_send_chunk(request, NULL, 0);
        return finish_short_response(request, result);
    }
    char path[96];
    size_t uri_length = request_path_length(request);
    static const char prefix[] = "/spiffs/www";
    if (uri_length + sizeof(prefix) + 3U > sizeof(path)) {
        return httpd_resp_send_404(request);
    }
    memcpy(path, prefix, sizeof(prefix) - 1U);
    memcpy(path + sizeof(prefix) - 1U, request->uri, uri_length);
    memcpy(path + sizeof(prefix) - 1U + uri_length, ".gz", 4U);
    FILE *file = open_nonempty(path);
    if (!file) {
        return httpd_resp_send_404(request);
    }
    httpd_resp_set_type(request, asset_type(request->uri));
    httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    size_t count;
    esp_err_t result = ESP_OK;
    while ((count = fread(s_static_scratch, 1, WEB_SEND_CHUNK_SIZE, file)) != 0U) {
        result = httpd_resp_send_chunk(request, s_static_scratch, count);
        if (result != ESP_OK) break;
    }
    fclose(file);
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
    return finish_short_response(request, result);
}

static esp_err_t playlist_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_hdr(request, "Vary", "Accept-Encoding");
    char encoding[128];
    const char *accept_encoding = NULL;
    if (httpd_req_get_hdr_value_str(request, "Accept-Encoding", encoding, sizeof(encoding)) == ESP_OK)
        accept_encoding = encoding;
    else if (httpd_req_get_hdr_value_len(request, "Accept-Encoding") >= sizeof(encoding)) {
        httpd_resp_set_status(request, "431 Request Header Fields Too Large");
        return finish_short_response(request, send_string(request, "Accept-Encoding too long"));
    }
    int gzip_quality = web_encoding_quality(accept_encoding, "gzip");
    int identity_quality = web_encoding_quality(accept_encoding, "identity");
    if (gzip_quality > 0 && gzip_quality >= identity_quality) {
        size_t left;
        int file = playlist_web_cache_open(&left);
        if (file >= 0) {
            httpd_resp_set_type(request, "text/csv; charset=utf-8");
            httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
            httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
            esp_err_t result = ESP_OK;
            while (left && result == ESP_OK) {
                size_t n = left < sizeof(s_static_scratch) ? left : sizeof(s_static_scratch);
                uint32_t trace_start = httpd_trace_clock();
                ssize_t count = read(file, s_static_scratch, n);
                httpd_trace_read(trace_start);
                if (count <= 0) { result = ESP_FAIL; break; }
                left -= (size_t)count;
                result = httpd_resp_send_chunk(request, s_static_scratch, (size_t)count);
            }
            close(file);
            if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
            return finish_short_response(request, result);
        }
    }
    if (!identity_quality) {
        httpd_resp_set_status(request, "406 Not Acceptable");
        return finish_short_response(request, send_string(request, "No acceptable playlist encoding"));
    }
#if YORADIO_ESP8266_WEB_PROFILE
    TickType_t profile_start = xTaskGetTickCount(), read_ticks = 0, send_ticks = 0;
#endif
    prepare_short_response(request);
    /* Read blocks into the existing HTTP-task buffer, not one FILE operation
     * per row. Retain only an incomplete tail between reads. Row boundaries
     * match playlist_service's fgets(..., 672), including overlong records.
     * Output uses a bounded independent 1-KiB scratch, never the full list. */
    enum { ROW_BYTES = 672 };
    int file = open(PLAYLIST_PATH, O_RDONLY);
    uint32_t trace_start = httpd_trace_clock();
    ssize_t first = file >= 0 ? read(file, s_async_message,
                                   sizeof(s_async_message) - 1) : -1;
    httpd_trace_read(trace_start);
    if (first <= 0 || !playlist_service_count()) {
        if (file >= 0) close(file);
        return httpd_resp_send_404(request);
    }
    httpd_resp_set_type(request, "text/csv; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    esp_err_t result = ESP_OK;
    size_t used = 0, offset = 0, buffered = (size_t)first;
    bool eof = false, read_failed = false;
    s_async_message[buffered] = '\0';
    for (;;) {
        size_t available = buffered - offset;
        size_t length = available < ROW_BYTES - 1 ? available : ROW_BYTES - 1;
        char *line = s_async_message + offset;
        char *newline = memchr(line, '\n', length);
        if (!newline && available < ROW_BYTES - 1 && !eof) {
            memmove(s_async_message, line, available);
#if YORADIO_ESP8266_WEB_PROFILE
            TickType_t read_start = xTaskGetTickCount();
#endif
            trace_start = httpd_trace_clock();
            ssize_t count = read(file, s_async_message + available,
                                 sizeof(s_async_message) - 1 - available);
            httpd_trace_read(trace_start);
            read_failed = count < 0;
            eof = count <= 0;
            buffered = available + (count > 0 ? (size_t)count : 0);
#if YORADIO_ESP8266_WEB_PROFILE
            read_ticks += xTaskGetTickCount() - read_start;
#endif
            offset = 0;
            s_async_message[buffered] = '\0';
            continue;
        }
        if (!available) break;
        if (newline) length = (size_t)(newline - line) + 1;
        offset += length;
        char saved = line[length];
        line[length] = '\0';
        bool supported = playlist_service_entry_supported(line);
        size_t remaining = supported ? strlen(line) : 0;
        line[length] = saved;
        while (remaining) {
            size_t n = sizeof(s_static_scratch) - used;
            if (n > remaining) n = remaining;
            memcpy(s_static_scratch + used, line, n);
            used += n;
            line += n;
            remaining -= n;
            if (used == sizeof(s_static_scratch)) {
#if YORADIO_ESP8266_WEB_PROFILE
                TickType_t send_start = xTaskGetTickCount();
#endif
                result = httpd_resp_send_chunk(request, s_static_scratch, used);
#if YORADIO_ESP8266_WEB_PROFILE
                send_ticks += xTaskGetTickCount() - send_start;
#endif
                if (result != ESP_OK) break;
                used = 0;
            }
        }
        if (result != ESP_OK) break;
    }
    if (result == ESP_OK && used)
        result = httpd_resp_send_chunk(request, s_static_scratch, used);
    if (read_failed && result == ESP_OK) result = ESP_FAIL;
    close(file);
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
#if YORADIO_ESP8266_WEB_PROFILE
    ESP_LOGI(TAG, "playlist profile: total=%u read=%u send=%u ms",
             (unsigned)((xTaskGetTickCount() - profile_start) * portTICK_PERIOD_MS),
             (unsigned)(read_ticks * portTICK_PERIOD_MS),
             (unsigned)(send_ticks * portTICK_PERIOD_MS));
#endif
    return finish_short_response(request, result);
}

static esp_err_t status_handler(httpd_req_t *request) {
    prepare_short_response(request);
    native_state_t state;
    native_state_snapshot(&state);
    char station[260];
    json_escape(state.station, station, sizeof(station));
    char body[768];
    char error[192];
    json_escape(state.error, error, sizeof(error));
    snprintf(body, sizeof(body),
             "{\"firmware\":\"esp8266-native\",\"port\":80,"
             "\"websocket\":\"/ws\",\"network\":%d,\"rssi\":%d,"
             "\"playing\":%s,\"station\":\"%s\",\"codec\":\"%s\","
             "\"bitrate\":%lu,\"connecting\":%s,\"error\":\"%s\","
             "\"free_heap\":%u,\"min_heap\":%u,\"web_stack_free\":%u,"
             "\"app_address\":%u}",
             state.network_mode, state.wifi_rssi,
             state.playing ? "true" : "false", station,
             native_codec_name(state.codec),
             (unsigned long)state.bitrate_kbps,
             state.connecting ? "true" : "false", error,
             esp_get_free_heap_size(), esp_get_minimum_free_heap_size(),
             (unsigned)uxTaskGetStackHighWaterMark(NULL),
             (unsigned)esp_ota_get_running_partition()->address);
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return finish_short_response(request, send_string(request, body));
}

static esp_err_t favicon_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_type(request, "image/x-icon");
    return finish_short_response(request, httpd_resp_send(request, NULL, 0));
}

static esp_err_t wifi_file_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_type(request, "text/csv; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    FILE *file = fopen("/spiffs/data/wifi.csv", "rb");
    esp_err_t result = ESP_OK;
    if (file) {
        size_t n;
        while ((n = fread(s_static_scratch, 1, sizeof(s_static_scratch), file))) {
            result = httpd_resp_send_chunk(request, s_static_scratch, n);
            if (result != ESP_OK) break;
        }
        if (ferror(file)) result = ESP_FAIL;
        fclose(file);
    }
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
    return finish_short_response(request, result);
}

static esp_err_t audio_health_handler(httpd_req_t *request) {
    prepare_short_response(request);
    audio_service_health_t health;
    native_audio_output_spi_stats_t output;
    audio_service_health(&health);
    native_audio_output_get_spi_stats(&output);
    /* A decode-only build also produces PCM callbacks; it is not physical
     * playback and must never satisfy the continuity acceptance test. */
#if YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY
    const char *output_enabled = "false";
#else
    const char *output_enabled = "true";
#endif
    char body[384];
    snprintf(body, sizeof(body),
        "{\"generation\":%u,\"uptime_ms\":%u,\"rx_bytes\":%u,"
        "\"pcm_frames\":%u,\"sample_rate\":%u,\"rx_age_ms\":%u,"
        "\"pcm_age_ms\":%u,\"underruns\":%u,\"free_heap\":%u,"
        "\"dma_eofs\":%u,\"output_enabled\":%s,\"audio_stack_free\":%u}",
        (unsigned)health.generation, (unsigned)health.uptime_ms,
        (unsigned)health.rx_bytes, (unsigned)health.pcm_frames,
        (unsigned)health.sample_rate, (unsigned)health.rx_age_ms,
        (unsigned)health.pcm_age_ms, (unsigned)output.queue_empty_events,
        (unsigned)esp_get_free_heap_size(),
        (unsigned)output.chained_transfers, output_enabled,
        (unsigned)health.stack_free);
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return finish_short_response(request, send_string(request, body));
}

#if YORADIO_ESP8266_SPIFFS_LOG_HTTP
#include "web_spiffs_log.inc"
#endif

static esp_err_t serve_static_request(httpd_req_t *request) {
    if (request_path_equals(request, "/") ||
        request_path_equals(request, "/index.html") ||
        request_path_equals(request, "/settings.html") ||
        request_path_equals(request, "/update.html")) {
        return page_handler(request);
    }
    if (request_path_equals(request, "/variables.js"))
        return variables_handler(request);
    if (request_path_equals(request, "/data/playlist.csv"))
        return playlist_handler(request);
    if (request_path_equals(request, "/favicon.ico"))
        return favicon_handler(request);
    return asset_handler(request);
}

static esp_err_t static_handler(httpd_req_t *request) {
    if (audio_service_web_pause_begin() != ESP_OK) {
        static const char message[] = "Audio pause timed out";
        prepare_short_response(request);
        httpd_resp_set_status(request, "503 Service Unavailable");
        httpd_resp_set_hdr(request, "Retry-After", "1");
        return finish_short_response(request,
            httpd_resp_send(request, message, sizeof(message) - 1));
    }
    esp_err_t result = serve_static_request(request);
    audio_service_web_pause_end(); /* Includes failed/disconnected sends. */
    return result;
}

#if YORADIO_ESP8266_OPUS_BENCHMARK
static esp_err_t opus_benchmark_start_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_type(request, "application/json");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    if (request->content_len) {
        httpd_resp_set_status(request, "400 Bad Request");
        return finish_short_response(request, send_string(request, "{\"error\":\"empty POST required\"}"));
    }
    if (!opus_benchmark_request()) {
        httpd_resp_set_status(request, "409 Conflict");
        return finish_short_response(request, send_string(request, "{\"error\":\"benchmark busy\"}"));
    }
    if (audio_service_stop() != ESP_OK) {
        opus_benchmark_cancel_pending();
        httpd_resp_set_status(request, "503 Service Unavailable");
        return finish_short_response(request, send_string(request, "{\"error\":\"stop queue failed\"}"));
    }
    httpd_resp_set_status(request, "202 Accepted");
    return finish_short_response(request, send_string(request, "{\"queued\":true}"));
}
static esp_err_t opus_benchmark_status_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_type(request, "application/json");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    opus_benchmark_status_t status;
    opus_benchmark_snapshot(&status);
    char row[384];
    int n = snprintf(row, sizeof(row),
        "{\"run\":%u,\"state\":%u,\"case\":%u,\"round\":%u,\"rounds\":%u,"
        "\"dram_before\":%u,\"dram_after\":%u,\"state_bytes\":%u,\"empty_task_us\":%u,"
        "\"error\":%d,\"results\":[",
        status.run, status.state, status.current_case, status.round, status.rounds,
        status.dram_before, status.dram_after, status.state_bytes, status.empty_task_us, status.error);
    esp_err_t result = httpd_resp_send_chunk(request, row, n);
    for (unsigned i = 0; result == ESP_OK && i < status.cases; ++i) {
        opus_benchmark_case_t item;
        opus_benchmark_case_snapshot(i, &item);
        n = snprintf(row, sizeof(row),
            "%s{\"id\":%u,\"packets\":%u,\"samples\":%u,\"wall_us\":%u,\"task_us\":%u,"
            "\"max_wall_us\":%u,\"pcm_hash\":%u,\"scratch_bytes\":%u,\"scratch_words\":%u,"
            "\"min_dram\":%u,\"stack_free_lifetime\":%u,\"error\":%d}",
            i ? "," : "", i, item.packets, item.samples, item.wall_us, item.task_us,
            item.max_wall_us, item.pcm_hash, item.scratch_bytes, item.scratch_words,
            item.min_dram, item.stack_free, item.error);
        if (n < 0 || (size_t)n >= sizeof(row)) result = ESP_FAIL;
        else result = httpd_resp_send_chunk(request, row, n);
    }
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, "]}", 2);
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
    return finish_short_response(request, result);
}
#endif

static esp_err_t register_get(const char *uri, esp_err_t (*handler)(httpd_req_t *)) {
    httpd_uri_t route = {
        .uri = uri,
        .method = HTTP_GET,
        .handler = handler,
    };
    return httpd_register_uri_handler(s_server, &route);
}

esp_err_t web_service_start(void) {
    s_bundle_current = bundle_matches_spiffs();
    ESP_LOGI(TAG, "Shared player bundle %s (%u bytes)",
             s_bundle_current ? "ready" : "disabled: SPIFFS assets differ",
             (unsigned)sizeof(web_bundle_gzip));
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;
#if YORADIO_ESP8266_WEB_AUDIO_PAUSE != 0
    /* Audio runs at 5. Preempt only while HTTP is runnable; a blocking send
     * or delay lets audio run. Never suspend a task holding an audio lock. */
    config.task_priority = tskIDLE_PRIORITY + 6;
#endif
    config.stack_size = BOARD_TASK_STACK_WEB;
    config.close_fn = session_closed;
    config.open_fn = session_opened;
    config.max_open_sockets = WEB_MAX_OPEN_SOCKETS;
    config.backlog_conn = WEB_CONNECTION_BACKLOG;
    config.recv_wait_timeout = WEB_IDLE_TIMEOUT_SECONDS;
    config.max_uri_handlers = 26;
#if YORADIO_ESP8266_OPUS_BENCHMARK
    config.max_uri_handlers += 2;
#endif
#if YORADIO_ESP8266_SPIFFS_LOG_HTTP
    config.max_uri_handlers += 2;
#endif
    /* Two WebSockets plus two short HTTP connections. The shared ESP8266
     * loader serializes each tab's static requests. */
    config.lru_purge_enable = true;
    config.send_wait_timeout = CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS;
    esp_err_t result = httpd_start(&s_server, &config);
    if (result != ESP_OK) return result;

    static const char *pages[] = {
        "/", "/index.html", "/settings.html", "/update.html",
    };
    static const char *assets[] = {
        "/theme.css", "/style.css", "/script.js", "/dragpl.js",
        "/player.html", "/options.html", "/logo.svg",
    };
    for (unsigned index = 0; index < sizeof(pages) / sizeof(pages[0]); ++index) {
        if ((result = register_get(pages[index], static_handler)) != ESP_OK)
            return result;
    }
    for (unsigned index = 0; index < sizeof(assets) / sizeof(assets[0]); ++index) {
        if ((result = register_get(assets[index], static_handler)) != ESP_OK)
            return result;
    }
    if ((result = register_get("/webboard", page_handler)) != ESP_OK) return result;
    if ((result = register_get("/emergency", page_handler)) != ESP_OK) return result;
    if ((result = register_get("/updform.html", asset_handler)) != ESP_OK) return result;
    if ((result = register_get("/data/wifi.csv", wifi_file_handler)) != ESP_OK) return result;
    static const char *posts[] = {"/upload", "/webboard", "/"};
    for (unsigned i = 0; i < sizeof(posts)/sizeof(posts[0]); ++i) {
        httpd_uri_t post = {.uri = posts[i], .method = HTTP_POST,
                            .handler = web_upload_handler};
        if ((result = httpd_register_uri_handler(s_server, &post)) != ESP_OK) return result;
    }
    if ((result = register_get("/variables.js", static_handler)) != ESP_OK)
        return result;
    if ((result = register_get("/data/playlist.csv", static_handler)) != ESP_OK)
        return result;
    if ((result = register_get("/api/native/status", status_handler)) != ESP_OK)
        return result;
    if ((result = register_get("/api/native/audio", audio_health_handler)) != ESP_OK)
        return result;
#if YORADIO_ESP8266_OPUS_BENCHMARK
    if ((result = register_get("/api/native/opus-benchmark", opus_benchmark_status_handler)) != ESP_OK)
        return result;
    httpd_uri_t opus_bench = {.uri = "/api/native/opus-benchmark", .method = HTTP_POST,
                              .handler = opus_benchmark_start_handler};
    if ((result = httpd_register_uri_handler(s_server, &opus_bench)) != ESP_OK) return result;
#endif
#if YORADIO_ESP8266_SPIFFS_LOG_HTTP
    if ((result = register_get("/api/native/log", spiffs_log_handler)) != ESP_OK)
        return result;
    if ((result = register_get("/api/native/log/previous", spiffs_log_handler)) != ESP_OK)
        return result;
#endif
    if ((result = register_get("/favicon.ico", static_handler)) != ESP_OK)
        return result;
    httpd_uri_t ota = {.uri = "/update", .method = HTTP_POST,
                       .handler = web_ota_handler};
    if ((result = httpd_register_uri_handler(s_server, &ota)) != ESP_OK) return result;
    httpd_uri_t websocket = {
        .uri = "/ws",
        .method = HTTP_GET,
        .handler = websocket_handler,
        .is_websocket = true,
    };
    result = httpd_register_uri_handler(s_server, &websocket);
    if (result == ESP_OK) {
        ESP_LOGI(TAG, "WebUI: http://<device>:80, WebSocket /ws on port 80");
    }
    return result;
}

void web_service_notify_playlist_changed(void) {
    s_playlist_changed = true;
}

static void poll_on_http_task(void) {
    web_close_poll();
    bool have_client = false;
    for (unsigned i = 0; i < WEB_WS_CLIENTS; ++i)
        have_client |= websocket_socket_active(s_ws_fds[i]);
    if (!have_client) return;
    if (s_playlist_changed) {
        if (broadcast_message("{\"file\":\"/data/playlist.csv\"}")) {
            s_playlist_changed = false;
        }
        return;
    }
    native_state_t state;
    web_status_key_t current;
    capture_status(&current, &state);
    TickType_t now = xTaskGetTickCount();
    bool immediate = !s_have_previous_status ||
                     status_requires_immediate_send(&current,
                                                    &s_previous_status);
    bool heartbeat = !s_last_status_tick ||
                     now - s_last_status_tick >= pdMS_TO_TICKS(WS_HEARTBEAT_MS);
    /* RSSI and buffer fill can fluctuate on every application poll. Sending
     * a full status frame for each fluctuation exhausts the ESP8266's small
     * lwIP pbuf pool while an audio TCP stream is active. Control, station,
     * codec and metadata changes remain immediate; telemetry is sampled by
     * the two-second heartbeat. */
    if (!immediate && !heartbeat) return;
    if (!format_status(&state, s_async_message, sizeof(s_async_message))) return;
    bool station_changed = !s_have_previous_status ||
                           current.station_index !=
                               s_previous_status.station_index;
    if (!broadcast_message(s_async_message)) return;
    if (station_changed) {
        /* In this SDK send_frame_async finishes copying to the socket before
         * returning; it does not retain the caller's payload. Keep status and
         * selection in order on this same HTTP task, without another 250 ms
         * application poll or an additional permanent buffer. */
        char selection[40];
        snprintf(selection, sizeof(selection), "{\"current\":%u}", current.station_index);
        if (!broadcast_message(selection)) return;
    }
    s_previous_status = current;
    s_have_previous_status = true;
    s_last_status_tick = now;
}

static void poll_work(void *argument) {
    (void)argument;
    memory_profile_register(MEMORY_WEB);
    poll_on_http_task();
    s_poll_queued = false;
}

void web_service_poll(void) {
    web_upload_poll();
    if (!s_server || s_poll_queued) return;
    s_poll_queued = true;
    if (httpd_queue_work(s_server, poll_work, NULL) != ESP_OK)
        s_poll_queued = false;
}
