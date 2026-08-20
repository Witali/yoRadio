#include "websocket_service.h"

#include <stdlib.h>
#include <string.h>

#include "audio_service.h"
#include "board_config.h"
#include "display_settings.h"
#include "esp_check.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "native_audio_output.h"
#include "radio_control.h"

#define WS_STATUS_INTERVAL_MS 2000

static const char *const TAG = "websocket";
static httpd_handle_t s_server;
static native_state_t *s_state;

static void json_escape(const char *source, char *target, size_t target_size) {
    size_t written = 0;
    while (*source && written + 1 < target_size) {
        unsigned char value = (unsigned char)*source++;
        if ((value == '"' || value == '\\') && written + 2 < target_size) {
            target[written++] = '\\';
            target[written++] = (char)value;
        } else if (value >= 0x20) {
            target[written++] = (char)value;
        }
    }
    target[written] = '\0';
}

static esp_err_t ws_send_request(httpd_req_t *request, const char *text) {
    httpd_ws_frame_t frame = {
        .final = true,
        .fragmented = false,
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text,
        .len = strlen(text),
    };
    return httpd_ws_send_frame(request, &frame);
}

static esp_err_t ws_send_async(int socket, const char *text) {
    httpd_ws_frame_t frame = {
        .final = true,
        .fragmented = false,
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text,
        .len = strlen(text),
    };
    return httpd_ws_send_data(s_server, socket, &frame);
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
             (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT),
             (unsigned long)state.bitrate_kbps, format,
             display_settings_get_station_uppercase() ? 1U : 0U,
             state.audio_running ? "playing" : "stopped");
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
    native_state_t state;
    native_state_snapshot(s_state, &state);
    char address[20] = "192.168.4.1";
    if (state.network_mode == NATIVE_NETWORK_CLIENT && state.ipv4) {
        esp_ip4_addr_t ip = {.addr = state.ipv4};
        snprintf(address, sizeof(address), IPSTR, IP2STR(&ip));
    }
    char settings[512];
    snprintf(settings, sizeof(settings),
             "{\"sst\":0,\"aif\":1,\"vu\":0,\"softr\":0,\"vut\":0,"
             "\"mdns\":\"yoradio\",\"ipaddr\":\"%s\",\"abuff\":16,"
             "\"mp3decoder\":0,\"normalize\":0,\"normgain\":20,"
             "\"normtarget\":-3,\"normtime\":2000,\"telnet\":0,"
             "\"watchdog\":1}",
             address);
    return ws_send_request(request, settings);
}

static esp_err_t send_screen_settings(httpd_req_t *request) {
    char settings[256];
    unsigned brightness = display_settings_get_brightness();
    snprintf(settings, sizeof(settings),
             "{\"flip\":0,\"inv\":0,\"nump\":0,\"tsf\":0,"
             "\"tsd\":0,\"upst\":%u,\"dspon\":1,\"br\":%u,\"con\":55,"
             "\"scre\":0,\"scrt\":30,\"scrb\":0,\"scrpe\":0,"
             "\"scrpt\":5,\"scrpb\":0}",
             display_settings_get_station_uppercase() ? 1U : 0U,
             brightness);
    return ws_send_request(request, settings);
}

static esp_err_t send_timezone_settings(httpd_req_t *request) {
    return ws_send_request(
        request,
        "{\"tzh\":0,\"tzm\":0,\"sntp1\":\"pool.ntp.org\","
        "\"sntp2\":\"time.nist.gov\",\"timeint\":60,"
        "\"timeintrtc\":24}");
}

static esp_err_t send_weather_settings(httpd_req_t *request) {
    return ws_send_request(request,
                           "{\"wen\":0,\"wlat\":\"\",\"wlon\":\"\","
                           "\"wkey\":\"\",\"wint\":60}");
}

static esp_err_t send_control_settings(httpd_req_t *request) {
    return ws_send_request(
        request, "{\"vols\":8,\"enca\":0,\"irtl\":10,\"skipup\":1}");
}

static esp_err_t send_active_settings(httpd_req_t *request, bool client_mode) {
    if (!client_mode) {
        return ws_send_request(request, "{\"act\":[\"group_wifi\"]}");
    }
    // Weather is intentionally excluded by the ESP32-C3 OLED build profile.
    return ws_send_request(
        request,
        "{\"act\":[\"group_wifi\",\"group_system\",\"group_display\","
        "\"group_oled\",\"group_timezone\",\"group_controls\","
        "\"group_buffer\",\"group_wortc\"]}");
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
        ws_send_request(request,
                        "{\"file\":\"/data/playlist.csv\"}");
    } else if (strcmp(command, "submitplaylistdone") == 0) {
        // The shared WebUI acknowledges that it has reloaded playlist.csv.
    } else if (strcmp(command, "play") == 0) {
        radio_control_play((uint16_t)strtoul(value, NULL, 10));
        send_initial_state(request);
    } else if (strcmp(command, "stop") == 0) {
        audio_service_stop();
        send_initial_state(request);
    } else if (strcmp(command, "toggle") == 0) {
        radio_control_toggle();
        send_initial_state(request);
    } else if (strcmp(command, "prev") == 0 ||
               strcmp(command, "next") == 0) {
        if (strcmp(command, "prev") == 0) radio_control_previous();
        else radio_control_next();
        send_initial_state(request);
    } else if (strcmp(command, "volume") == 0) {
        unsigned volume = strtoul(value, NULL, 10);
        native_audio_output_set_volume(volume > 254 ? 254 : (uint8_t)volume);
        send_initial_state(request);
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
        send_screen_settings(request);
    } else if (strcmp(command, "stationuppercase") == 0) {
        esp_err_t result = display_settings_set_station_uppercase(
            strtoul(value, NULL, 10) != 0, true);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Station uppercase update failed: %s",
                     esp_err_to_name(result));
        }
        send_screen_settings(request);
    } else if (strcmp(command, "volp") == 0 ||
               strcmp(command, "volm") == 0) {
        int volume = native_audio_output_get_volume();
        volume += strcmp(command, "volp") == 0 ? 8 : -8;
        if (volume < 0) volume = 0;
        if (volume > 254) volume = 254;
        native_audio_output_set_volume((uint8_t)volume);
        send_initial_state(request);
    } else if (strcmp(command, "balance") == 0) {
        int balance = strtol(value, NULL, 10);
        if (balance < -16) balance = -16;
        if (balance > 16) balance = 16;
        native_audio_output_set_balance((int8_t)balance);
        send_initial_state(request);
    }
}

static esp_err_t websocket_handler(httpd_req_t *request) {
    if (request->method == HTTP_GET) {
        ESP_LOGI(TAG, "WebUI client connected on socket %d",
                 httpd_req_to_sockfd(request));
        return ESP_OK;
    }

    httpd_ws_frame_t frame = {0};
    ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, 0), TAG,
                        "read WebSocket frame size");
    if (frame.type != HTTPD_WS_TYPE_TEXT || frame.len == 0 || frame.len > 255) {
        return ESP_OK;
    }
    char payload[256];
    frame.payload = (uint8_t *)payload;
    ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, sizeof(payload) - 1),
                        TAG, "read WebSocket frame");
    payload[frame.len] = '\0';
    handle_command(request, payload);
    return ESP_OK;
}

static void status_task(void *argument) {
    (void)argument;
    char status[1280];
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(WS_STATUS_INTERVAL_MS));
        format_status(status, sizeof(status));
        size_t count = CONFIG_LWIP_MAX_SOCKETS;
        int sockets[CONFIG_LWIP_MAX_SOCKETS];
        if (httpd_get_client_list(s_server, &count, sockets) != ESP_OK) continue;
        for (size_t index = 0; index < count; ++index) {
            if (httpd_ws_get_fd_info(s_server, sockets[index]) ==
                HTTPD_WS_CLIENT_WEBSOCKET) {
                ws_send_async(sockets[index], status);
            }
        }
    }
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
        .handle_ws_control_frames = false,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &websocket), TAG,
                        "register native WebSocket route");
    ESP_RETURN_ON_FALSE(xTaskCreate(status_task, "websocket_status", 4096,
                                    NULL, 2, NULL) == pdPASS,
                        ESP_ERR_NO_MEM, TAG, "start WebSocket status task");
    return ESP_OK;
}
