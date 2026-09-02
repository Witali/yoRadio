#include "web_service.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "board_config.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_audio_output.h"
#include "native_state.h"
#include "persistent_settings.h"
#include "playlist_service.h"
#include "radio_control.h"
#include "web_pages_bridge.h"

#define WS_HEARTBEAT_MS 2000U
#define WS_COMMAND_MAX 255U
#define WEB_STATUS_CAPACITY 1088U
#define WEB_MAX_OPEN_SOCKETS 4U
#define WEB_CONNECTION_BACKLOG 3U
#define WEB_IDLE_TIMEOUT_SECONDS 2U
#define WEB_SEND_CHUNK_SIZE 512U
#define WEB_STATIC_SCRATCH_SIZE 512U

extern const unsigned char _binary_script_js_gz_start[];
extern const unsigned char _binary_script_js_gz_end[];

static const char *TAG = "web";
static httpd_handle_t s_server;
static volatile int s_ws_fd = -1;
static volatile bool s_send_pending;
static volatile bool s_playlist_changed;
static volatile bool s_current_pending;
static uint16_t s_pending_current;
static char s_async_message[WEB_STATUS_CAPACITY];
/* All static routes run serially on the HTTP task, so one DRAM buffer can
 * replace the former 512/672-byte per-handler stack arrays. */
static char s_static_scratch[WEB_STATIC_SCRATCH_SIZE];

typedef struct {
    bool playing;
    bool connecting;
    int8_t rssi;
    uint16_t station_index;
    uint16_t buffer_percent;
    uint8_t volume;
    uint32_t bitrate_kbps;
    uint32_t sample_rate_hz;
    uint8_t channels;
    codec_type_t codec;
    char station[128];
    char title[192];
} web_status_key_t;

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

static void pace_static_send(void) {
    /* The ESP8266 TCP window is deliberately small; let lwIP/Wi-Fi drain
     * it between chunks instead of filling all pbufs in one HTTP burst. */
    vTaskDelay(1);
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
        pace_static_send();
        text += count;
        remaining -= count;
    }
    return httpd_resp_send_chunk(request, NULL, 0);
}

static void json_escape(const char *source, char *target, size_t capacity) {
    size_t written = 0;
    if (!capacity) return;
    while (source && *source && written + 1U < capacity) {
        unsigned char value = (unsigned char)*source++;
        if ((value == '"' || value == '\\') && written + 2U < capacity) {
            target[written++] = '\\';
            target[written++] = (char)value;
        } else if (value >= 0x20U) {
            target[written++] = (char)value;
        }
    }
    target[written] = '\0';
}

static void capture_status(web_status_key_t *key) {
    native_state_t state;
    native_state_snapshot(&state);
    memset(key, 0, sizeof(*key));
    key->playing = state.playing;
    key->connecting = state.connecting;
    key->rssi = state.wifi_rssi;
    key->station_index = state.station_index;
    key->buffer_percent = state.buffer_percent;
    key->volume = state.volume;
    key->bitrate_kbps = state.bitrate_kbps;
    key->sample_rate_hz = state.sample_rate_hz;
    key->channels = state.channels;
    key->codec = state.codec;
    copy_text(key->station, sizeof(key->station), state.station);
    copy_text(key->title, sizeof(key->title), state.title);
}

static bool status_requires_immediate_send(const web_status_key_t *current,
                                           const web_status_key_t *previous) {
    return current->playing != previous->playing ||
           current->connecting != previous->connecting ||
           current->station_index != previous->station_index ||
           current->volume != previous->volume ||
           current->bitrate_kbps != previous->bitrate_kbps ||
           current->sample_rate_hz != previous->sample_rate_hz ||
           current->channels != previous->channels ||
           current->codec != previous->codec ||
           strcmp(current->station, previous->station) != 0 ||
           strcmp(current->title, previous->title) != 0;
}

static void format_stream(const web_status_key_t *status, char *output,
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

static void format_status(const web_status_key_t *status, char *output,
                          size_t capacity) {
    char station[260];
    char title[390];
    char stream[64];
    char escaped_stream[130];
    json_escape(status->station, station, sizeof(station));
    json_escape(status->title, title, sizeof(title));
    format_stream(status, stream, sizeof(stream));
    json_escape(stream, escaped_stream, sizeof(escaped_stream));
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    snprintf(output, capacity,
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
             station, title, status->volume, settings.balance, status->rssi,
             status->playing ? status->buffer_percent : 0U,
             (unsigned long)status->bitrate_kbps, escaped_stream,
             settings.station_uppercase ? 1U : 0U,
             status->playing ? "playing" : "stopped");
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

static void async_send_work(void *argument) {
    (void)argument;
    int socket = s_ws_fd;
    if (websocket_socket_active(socket)) {
        httpd_ws_frame_t frame = {
            .final = true,
            .fragmented = false,
            .type = HTTPD_WS_TYPE_TEXT,
            .payload = (uint8_t *)s_async_message,
            .len = strlen(s_async_message),
        };
        if (httpd_ws_send_frame_async(s_server, socket, &frame) != ESP_OK) {
            httpd_sess_trigger_close(s_server, socket);
            s_ws_fd = -1;
        } else {
            httpd_sess_update_lru_counter(s_server, socket);
        }
    } else {
        s_ws_fd = -1;
    }
    s_send_pending = false;
}

static bool queue_message(const char *message) {
    if (!s_server || s_ws_fd < 0 || s_send_pending) return false;
    if (!websocket_socket_active(s_ws_fd)) {
        s_ws_fd = -1;
        return false;
    }
    if (message != s_async_message)
        copy_text(s_async_message, sizeof(s_async_message), message);
    s_send_pending = true;
    if (httpd_queue_work(s_server, async_send_work, NULL) != ESP_OK) {
        s_send_pending = false;
        return false;
    }
    return true;
}

static esp_err_t send_initial_state(httpd_req_t *request) {
    web_status_key_t status;
    char current[40];
    capture_status(&status);
    format_status(&status, s_static_scratch, sizeof(s_static_scratch));
    esp_err_t result = ws_send(request, s_static_scratch);
    if (result != ESP_OK) return result;
    snprintf(current, sizeof(current), "{\"current\":%u}",
             status.station_index);
    if ((result = ws_send(request, current)) != ESP_OK) return result;
    if ((result = ws_send(request, "{\"sdinit\":0}")) != ESP_OK)
        return result;
    return ws_send(request, "{\"playermode\":\"modeweb\"}");
}

static esp_err_t send_active_settings(httpd_req_t *request) {
    native_state_t state;
    native_state_snapshot(&state);
    if (state.network_mode != NETWORK_CLIENT) {
        return ws_send(request, "{\"act\":[\"group_wifi\"]}");
    }
    esp_err_t result = ws_send(
        request,
        "{\"act\":[\"group_wifi\",\"group_system\",\"group_display\","
        "\"group_oled\",\"group_timezone\",\"group_controls\","
        "\"group_encoder\",\"group_wortc\"]}");
    if (result != ESP_OK) return result;
    return ws_send(request,
                   "{\"hide\":[\"telnet\",\"skipup\",\"mdnsnamerow\","
                   "\"radiolink\",\"group_weather\",\"group_buffer\"]}");
}

static esp_err_t send_system_settings(httpd_req_t *request) {
    persistent_settings_t settings;
    persistent_settings_get(&settings);
    native_state_t state;
    native_state_snapshot(&state);
    char body[420];
    snprintf(body, sizeof(body),
             "{\"sst\":%u,\"aif\":1,\"vu\":0,\"softr\":0,\"vut\":0,"
             "\"mdns\":\"%s\",\"ipaddr\":\"%s\",\"abuff\":0,"
             "\"abuffmax\":0,\"mp3decoder\":0,\"normalize\":%u,"
             "\"normgain\":%u,\"normtarget\":%d,\"normtime\":%u,"
             "\"telnet\":0,\"watchdog\":0}",
             settings.smart_start, settings.mdns_name,
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
        send_initial_state(request);
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
        int target = (int)parse_unsigned(value, 254U);
        radio_control_adjust_volume(target - (int)native_audio_output_volume());
        send_initial_state(request);
    } else if (strcmp(command, "volp") == 0 ||
               strcmp(command, "volm") == 0) {
        persistent_settings_t settings;
        persistent_settings_get(&settings);
        int delta = settings.volume_steps;
        radio_control_adjust_volume(strcmp(command, "volp") == 0 ? delta
                                                                  : -delta);
        send_initial_state(request);
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
        if (changed) update_settings(&settings, reload_audio);
    }
}

static esp_err_t websocket_handler(httpd_req_t *request) {
    if (request->method == HTTP_GET) {
        ESP_LOGI(TAG, "WebUI client connected on socket %d",
                 httpd_req_to_sockfd(request));
        return ESP_OK;
    }

    int socket = httpd_req_to_sockfd(request);
    if (s_ws_fd >= 0 && s_ws_fd != socket &&
        websocket_socket_active(s_ws_fd)) {
        httpd_sess_trigger_close(s_server, s_ws_fd);
    }
    s_ws_fd = socket;
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
    /* A conforming client closes after receiving the complete response
     * because prepare_short_response() emitted Connection: close. Queuing a
     * server-side close after a successful send can run before lwIP drains
     * its TCP queue and truncate the final chunk on a lossy link. Only force
     * cleanup when the response already failed. */
    if (result != ESP_OK) {
        (void)httpd_sess_trigger_close(request->handle,
                                      httpd_req_to_sockfd(request));
    }
    return result;
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
    if (request_path_equals(request, "/") && !web_ui_available()) {
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
             "var webUiRevision='8266n01';\n"
             "var formAction='%s';\n"
             "var playMode='%s';\n"
             "var equalizerEnabled=false;\n",
             state.network_mode == NETWORK_CLIENT && web_ui_available()
                 ? "webboard" : "",
             state.network_mode == NETWORK_CLIENT ? "player" : "ap");
    httpd_resp_set_type(request, "application/javascript; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return finish_short_response(request, send_string(request, body));
}

static esp_err_t asset_handler(httpd_req_t *request) {
    prepare_short_response(request);
    if (request_path_equals(request, "/script.js")) {
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
            pace_static_send();
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
        pace_static_send();
    }
    fclose(file);
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
    return finish_short_response(request, result);
}

static esp_err_t playlist_handler(httpd_req_t *request) {
    prepare_short_response(request);
    FILE *file = open_nonempty(PLAYLIST_PATH);
    if (!file || !playlist_service_count()) {
        if (file) fclose(file);
        return httpd_resp_send_404(request);
    }
    httpd_resp_set_type(request, "text/csv; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    esp_err_t result = ESP_OK;
    while (fgets(s_static_scratch, sizeof(s_static_scratch), file)) {
        if (!playlist_service_entry_supported(s_static_scratch)) continue;
        result = httpd_resp_send_chunk(request, s_static_scratch,
                                       strlen(s_static_scratch));
        if (result != ESP_OK) break;
        pace_static_send();
    }
    if (ferror(file) && result == ESP_OK) result = ESP_FAIL;
    fclose(file);
    if (result == ESP_OK) result = httpd_resp_send_chunk(request, NULL, 0);
    return finish_short_response(request, result);
}

static esp_err_t status_handler(httpd_req_t *request) {
    prepare_short_response(request);
    native_state_t state;
    native_state_snapshot(&state);
    char station[260];
    json_escape(state.station, station, sizeof(station));
    char body[420];
    snprintf(body, sizeof(body),
             "{\"firmware\":\"esp8266-native\",\"port\":80,"
             "\"websocket\":\"/ws\",\"network\":%d,\"rssi\":%d,"
             "\"playing\":%s,\"station\":\"%s\",\"codec\":\"%s\","
             "\"bitrate\":%lu}",
             state.network_mode, state.wifi_rssi,
             state.playing ? "true" : "false", station,
             native_codec_name(state.codec),
             (unsigned long)state.bitrate_kbps);
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return finish_short_response(request, send_string(request, body));
}

static esp_err_t favicon_handler(httpd_req_t *request) {
    prepare_short_response(request);
    httpd_resp_set_type(request, "image/x-icon");
    return finish_short_response(request, httpd_resp_send(request, NULL, 0));
}

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
    return serve_static_request(request);
}

static esp_err_t register_get(const char *uri, esp_err_t (*handler)(httpd_req_t *)) {
    httpd_uri_t route = {
        .uri = uri,
        .method = HTTP_GET,
        .handler = handler,
    };
    return httpd_register_uri_handler(s_server, &route);
}

esp_err_t web_service_start(void) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;
    config.stack_size = BOARD_TASK_STACK_WEB;
    config.max_open_sockets = WEB_MAX_OPEN_SOCKETS;
    config.backlog_conn = WEB_CONNECTION_BACKLOG;
    config.recv_wait_timeout = WEB_IDLE_TIMEOUT_SECONDS;
    config.max_uri_handlers = 18;
    /* The ESP8266 page loader serializes static requests so one persistent
     * HTTP/1.1 session normally serves the whole page beside the WebSocket.
     * Four sessions allow one complete UI (WebSocket + HTTP keep-alive) and
     * one reconnecting or diagnostic client. Queue a small connection burst
     * and evict the oldest idle session before exhausting heap. */
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
    if ((result = register_get("/variables.js", static_handler)) != ESP_OK)
        return result;
    if ((result = register_get("/data/playlist.csv", static_handler)) != ESP_OK)
        return result;
    if ((result = register_get("/api/native/status", status_handler)) != ESP_OK)
        return result;
    if ((result = register_get("/favicon.ico", static_handler)) != ESP_OK)
        return result;
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

void web_service_poll(void) {
    if (!s_server || s_ws_fd < 0 || s_send_pending) return;
    if (!websocket_socket_active(s_ws_fd)) {
        s_ws_fd = -1;
        return;
    }
    if (s_current_pending) {
        char current[40];
        snprintf(current, sizeof(current), "{\"current\":%u}",
                 s_pending_current);
        if (queue_message(current)) s_current_pending = false;
        return;
    }
    if (s_playlist_changed) {
        if (queue_message("{\"file\":\"/data/playlist.csv\"}")) {
            s_playlist_changed = false;
        }
        return;
    }
    web_status_key_t current;
    capture_status(&current);
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
    format_status(&current, s_async_message, sizeof(s_async_message));
    bool station_changed = !s_have_previous_status ||
                           current.station_index !=
                               s_previous_status.station_index;
    if (!queue_message(s_async_message)) return;
    if (station_changed) {
        /* The status is sent first. The current index follows on the next
         * poll so one static asynchronous send buffer is sufficient. */
        s_pending_current = current.station_index;
        s_current_pending = true;
    }
    s_previous_status = current;
    s_have_previous_status = true;
    s_last_status_tick = now;
}
