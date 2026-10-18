#include "web_service.h"

#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "audio_service.h"
#include "esp_check.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_heap_caps.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/task.h"
#include "native_health.h"
#include "native_audio_output.h"
#include "native_audio_settings.h"
#include "network_service.h"
#include "radio_control.h"
#include "json_buffer.h"
#include "web_static.h"
#include "web_upload.h"
#include "web_reboot.h"
#include "native_web_transport.h"
#include "websocket_service.h"

static const char *const TAG = "web";
static native_state_t *s_state;
static uint64_t s_health_boot_id;

static esp_err_t health_handler(httpd_req_t *request) {
    native_health_track_task(NATIVE_HEALTH_HTTP, xTaskGetCurrentTaskHandle());
    native_health_snapshot_t health = native_health_snapshot();
    multi_heap_info_t heap;
    heap_caps_get_info(&heap, MALLOC_CAP_8BIT);
    native_health_runtime_t runtime = {
        .boot_id=s_health_boot_id, .uptime_ms=(uint64_t)(esp_timer_get_time()/1000),
        .reset_reason=(uint32_t)esp_reset_reason(), .heap_free=(uint32_t)heap.total_free_bytes,
        .heap_largest=(uint32_t)heap.largest_free_block, .heap_minimum=(uint32_t)heap.minimum_free_bytes,
        .tasks=(uint32_t)uxTaskGetNumberOfTasks(), .cores=configNUMBER_OF_CORES,
        .internal_free=(uint32_t)heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
        .internal_largest=(uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
        .dma_free=(uint32_t)heap_caps_get_free_size(MALLOC_CAP_DMA),
        .dma_largest=(uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_DMA),
        .input=audio_service_input_health(),
    };
    char body[2304];
    if (!native_health_format_json(body,sizeof(body),&health,&runtime))
        return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Health buffer exhausted");
    httpd_resp_set_type(request,"application/json; charset=utf-8");
    httpd_resp_set_hdr(request,"Cache-Control","no-store");
    return httpd_resp_sendstr(request,body);
}

static esp_err_t status_handler(httpd_req_t *request) {
    native_state_t state;
    native_state_snapshot(s_state, &state);
    const char *mode = "starting";
    if (state.network_mode == NATIVE_NETWORK_CLIENT) mode = "client";
    if (state.network_mode == NATIVE_NETWORK_ACCESS_POINT) mode = "ap";
    if (state.network_mode == NATIVE_NETWORK_ERROR) mode = "error";
    // Enough for the worst six-byte JSON escape of every bounded field.
    char body[2560];
    json_buffer_t output;
    json_buffer_init(&output, body, sizeof(body));
    json_buffer_raw(&output, "{\"firmware\":\"esp-idf-native\",\"arduino\":false,\"network\":");
    json_buffer_string(&output, mode);
    json_buffer_raw(&output, state.audio_running ? ",\"audio\":true,\"station\":"
                                               : ",\"audio\":false,\"station\":");
    json_buffer_string(&output, state.station);
    json_buffer_raw(&output, ",\"format\":");
    json_buffer_string(&output, state.stream_format);
    json_buffer_raw(&output, ",\"title\":");
    json_buffer_string(&output, state.title);
    const char *bitrate_source = state.bitrate_source == NATIVE_BITRATE_ICY ? "icy" :
        state.bitrate_source == NATIVE_BITRATE_DECODER ? "decoder" :
        state.bitrate_source == NATIVE_BITRATE_MEASURED ? "measured" : "none";
    char metadata[256];
    snprintf(metadata,sizeof(metadata),",\"generation\":%lu,\"bitrate\":%lu,\"sample_rate_hz\":%lu,\"channels\":%u,\"bits_per_sample\":%u,\"pcm_sample_rate_hz\":%lu,\"pcm_channels\":%u,\"format_is_pcm\":%s,\"channels_are_core\":%s,\"codec\":",
        (unsigned long)state.audio_generation,(unsigned long)state.bitrate_kbps,(unsigned long)state.sample_rate_hz,
        state.channels,state.bits_per_sample,(unsigned long)state.pcm_sample_rate_hz,state.pcm_channels,
        state.format_is_pcm ? "true" : "false",state.channels_are_core ? "true" : "false");
    json_buffer_raw(&output,metadata);json_buffer_string(&output,state.codec);
    json_buffer_raw(&output,",\"bitrate_source\":");json_buffer_string(&output,bitrate_source);
    char settings[64];
    snprintf(settings, sizeof(settings), ",\"connecting\":%s,\"volume\":%u,\"balance\":%d}",
             state.audio_pending ? "true" : "false",
             native_audio_output_get_volume(), native_audio_output_get_balance());
    json_buffer_raw(&output, settings);
    if (output.failed) return httpd_resp_send_err(request,
        HTTPD_500_INTERNAL_SERVER_ERROR, "Status buffer exhausted");
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}

static bool parse_station_number(const char *text, uint16_t *station) {
    if (!text || !*text) return false;
    uint32_t value = 0;
    for (; *text; ++text) {
        if (*text < '0' || *text > '9') return false;
        value = value * 10U + (unsigned)(*text - '0');
        if (value > UINT16_MAX) return false;
    }
    if (!value) return false;
    *station = (uint16_t)value;
    return true;
}

static esp_err_t radio_handler(httpd_req_t *request) {
    if (request->method == HTTP_POST) {
        char query[96], action[24], value[16];
        if (httpd_req_get_url_query_str(request,query,sizeof(query)) != ESP_OK ||
            httpd_query_key_value(query,"action",action,sizeof(action)) != ESP_OK)
            return httpd_resp_send_err(request,HTTPD_400_BAD_REQUEST,"Missing radio action");
        esp_err_t result = ESP_ERR_INVALID_ARG;
        if (!strcmp(action,"next")) result = radio_control_next();
        else if (!strcmp(action,"previous")) result = radio_control_previous();
        else if (!strcmp(action,"toggle")) result = radio_control_toggle();
        else if (!strcmp(action,"stop")) result = radio_control_stop();
        else if (!strcmp(action,"play")) {
            uint16_t station;
            if (httpd_query_key_value(query,"station",value,sizeof(value)) == ESP_OK &&
                parse_station_number(value,&station)) result = radio_control_play(station);
        } else if (!strcmp(action,"smartstart")) {
            if (httpd_query_key_value(query,"enabled",value,sizeof(value)) == ESP_OK &&
                (!strcmp(value,"0") || !strcmp(value,"1")))
                result = radio_control_set_smartstart_enabled(value[0]=='1');
        }
        if (result != ESP_OK) return httpd_resp_send_err(request,
            result == ESP_ERR_INVALID_ARG || result == ESP_ERR_NOT_FOUND ? HTTPD_400_BAD_REQUEST :
            HTTPD_500_INTERNAL_SERVER_ERROR,"Radio action failed");
    }
    radio_control_snapshot_t radio;
    if (!radio_control_snapshot(&radio))
        return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Radio unavailable");
    native_state_t state;
    native_state_snapshot(s_state,&state);
    char body[1024], prefix[160];
    snprintf(prefix,sizeof(prefix),"{\"current\":%u,\"count\":%u,\"smartstart\":%s,\"playing\":%s,\"connecting\":%s,\"station\":",
        radio.item,radio.count,radio.smartstart ? "true" : "false",
        state.audio_running ? "true" : "false",state.audio_pending ? "true" : "false");
    json_buffer_t output;
    json_buffer_init(&output,body,sizeof(body));
    json_buffer_raw(&output,prefix);json_buffer_string(&output,radio.name);json_buffer_raw(&output,"}");
    if (output.failed) return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Radio buffer exhausted");
    httpd_resp_set_type(request,"application/json; charset=utf-8");
    httpd_resp_set_hdr(request,"Cache-Control","no-store");
    return httpd_resp_sendstr(request,body);
}

static esp_err_t reconnect_handler(httpd_req_t *request) {
    esp_err_t result = network_service_retry_client();
    if (result != ESP_OK) {
        httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR,
                            "No saved client configuration");
        return result;
    }
    httpd_resp_set_type(request, "application/json");
    return httpd_resp_sendstr(request, "{\"reconnecting\":true}");
}

static native_codec_t parse_codec(httpd_req_t *request) {
    char query[80];
    char value[16];
    if (httpd_req_get_url_query_str(request, query, sizeof(query)) == ESP_OK &&
        httpd_query_key_value(query, "codec", value, sizeof(value)) == ESP_OK) {
        if (strcasecmp(value, "mp3") == 0) return NATIVE_CODEC_MP3;
        if (strcasecmp(value, "aac") == 0) return NATIVE_CODEC_AAC;
        if (strcasecmp(value, "flac") == 0) return NATIVE_CODEC_FLAC;
        if (strcasecmp(value, "ogg") == 0 ||
            strcasecmp(value, "opus") == 0 ||
            strcasecmp(value, "vorbis") == 0) return NATIVE_CODEC_OGG;
    }
    return NATIVE_CODEC_AUTO;
}

static esp_err_t play_handler(httpd_req_t *request) {
    if (request->content_len <= 0 || request->content_len >= 512) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Body must contain a stream URL");
    }
    char url[512];
    size_t total = 0;
    while (total < (size_t)request->content_len) {
        int received = httpd_req_recv(request, url + total,
                                      request->content_len - total);
        if (received <= 0) return ESP_FAIL;
        total += received;
    }
    url[total] = '\0';
    esp_err_t result = audio_service_play(url, parse_codec(request));
    if (result != ESP_OK) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Invalid stream URL");
    }
    httpd_resp_set_type(request, "application/json");
    return httpd_resp_sendstr(request, "{\"playing\":true}");
}

static esp_err_t stop_handler(httpd_req_t *request) {
    if (radio_control_stop() != ESP_OK) audio_service_stop();
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    return httpd_resp_sendstr(request, "{\"playing\":false}");
}

static bool parse_setting_integer(const char *text, bool signed_value,
                                   int64_t *value) {
    if (!text || !*text) return false;
    bool negative = signed_value && *text == '-';
    if (negative && !*++text) return false;
    uint32_t limit = signed_value ? (uint32_t)INT32_MAX + (negative ? 1U : 0U)
                                  : UINT32_MAX;
    uint32_t number = 0;
    for (; *text; ++text) {
        if (*text < '0' || *text > '9') return false;
        uint32_t digit = (uint32_t)(*text - '0');
        if (number > (limit - digit) / 10U) return false;
        number = number * 10U + digit;
    }
    *value = negative ? -(int64_t)number : (int64_t)number;
    return true;
}

static esp_err_t settings_handler(httpd_req_t *request) {
    if (request->method == HTTP_POST) {
        char query[192];
        char value[16];
        if (httpd_req_get_url_query_str(request, query, sizeof(query)) != ESP_OK) {
            return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                       "Missing settings query");
        }
        enum { VOLUME, BALANCE, NORMALIZATION, NORMGAIN, NORMTARGET, NORMTIME, COUNT };
        static const char *const keys[COUNT] = {
            "volume", "balance", "normalization", "normgain", "normtarget", "normtime",
        };
        int64_t values[COUNT] = {0};
        bool present[COUNT] = {false};
        bool specified[COUNT] = {false};
        // The SDK returns the first matching key. Reject repeated controls
        // and malformed fields so a later bad value cannot be hidden.
        for (const char *field = query; *field;) {
            const char *end = strchr(field, '&');
            if (!end) end = field + strlen(field);
            const char *equals = memchr(field, '=', (size_t)(end - field));
            if (!equals || equals == field || (*end && !end[1]))
                return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                           "Invalid settings query");
            size_t length = (size_t)(equals - field);
            for (unsigned i = 0; i < COUNT; ++i) {
                if (strlen(keys[i]) != length || strncasecmp(field, keys[i], length) != 0) continue;
                if (specified[i])
                    return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                               "Duplicate settings value");
                specified[i] = true;
            }
            field = *end ? end + 1 : end;
        }
        // Validate the complete update before changing any runtime setting.
        // A truncated optional field is an error, not a missing field.
        for (unsigned i = 0; i < COUNT; ++i) {
            esp_err_t result = httpd_query_key_value(query, keys[i], value, sizeof(value));
            if (result == ESP_ERR_NOT_FOUND && !specified[i]) continue;
            if (result != ESP_OK ||
                !parse_setting_integer(value, i == BALANCE || i == NORMTARGET, &values[i]))
                return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                           "Invalid settings value");
            present[i] = true;
        }
        if ((present[NORMALIZATION] && values[NORMALIZATION] > 1) ||
            (present[NORMGAIN] && values[NORMGAIN] > 20) ||
            (present[NORMTARGET] && (values[NORMTARGET] < -20 || values[NORMTARGET] > 0)) ||
            (present[NORMTIME] && (values[NORMTIME] < 100 || values[NORMTIME] > 10000)))
            return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                       "Settings value out of range");
        if (values[VOLUME] > 254) values[VOLUME] = 254;
        if (values[BALANCE] < -16) values[BALANCE] = -16;
        if (values[BALANCE] > 16) values[BALANCE] = 16;
        // Each setter reports its own persistence result. Multiple settings
        // are applied in order; this is not an NVS transaction or rollback.
        for (unsigned i = 0; i < COUNT; ++i) {
            if (!present[i]) continue;
            esp_err_t result;
            switch (i) {
                case VOLUME: result = native_audio_settings_set_volume((uint8_t)values[i]); break;
                case BALANCE: result = native_audio_settings_set_balance((int8_t)values[i]); break;
                case NORMALIZATION: result = native_audio_settings_set_normalization(values[i] != 0); break;
                case NORMGAIN: result = native_audio_settings_set_normalization_gain_db((uint8_t)values[i]); break;
                case NORMTARGET: result = native_audio_settings_set_normalization_target_dbfs((int8_t)values[i]); break;
                default: result = native_audio_settings_set_normalization_time_ms((uint16_t)values[i]); break;
            }
            if (result != ESP_OK) {
                httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR,
                                    "Settings update failed");
                return result;
            }
        }
    }

    char body[160];
    snprintf(body, sizeof(body),
             "{\"volume\":%u,\"balance\":%d,\"normalization\":%s,\"normgain\":%u,\"normtarget\":%d,\"normtime\":%u}",
             native_audio_output_get_volume(), native_audio_output_get_balance(),
             native_audio_settings_get_normalization() ? "true" : "false",
             native_audio_settings_get_normalization_gain_db(),
             native_audio_settings_get_normalization_target_dbfs(),
             native_audio_settings_get_normalization_time_ms());
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}

static esp_err_t capabilities_handler(httpd_req_t *request) {
    char body[896];
    json_buffer_t output;
    json_buffer_init(&output, body, sizeof(body));
    json_buffer_raw(&output, "{\"schema\":1,\"firmware\":\"esp32-cyd2usb-native\",\"audio_output\":");
    json_buffer_string(&output, native_audio_output_name());
    json_buffer_raw(&output, ",\"websocket\":true,\"websocket_clients\":2,\"radio\":true,\"smartstart\":true,\"normalization\":true,\"wifi_reconnect\":true,\"playlist_upload\":true,\"asset_upload\":true,\"wifi_upload\":true,\"upload_max_bytes\":98304,\"upload_max_files\":16,\"upload_name_max_bytes\":22,\"wifi_file_max_bytes\":799,\"wifi_body_max_bytes\":4096,\"wifi_ssid_max_bytes\":31,\"wifi_password_max_bytes\":63,\"wifi_profiles\":false,\"ota\":false,\"equalizer\":false,\"sd\":false,\"display_controls\":false}");
    if (output.failed) return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR, "Capabilities exhausted");
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}

static atomic_bool s_started;

esp_err_t web_service_start(native_state_t *state) {
    if (!state || !state->lock) return ESP_ERR_INVALID_ARG;
    bool expected = false;
    if (!atomic_compare_exchange_strong(&s_started, &expected, true)) return ESP_ERR_INVALID_STATE;
    // Locks and the reboot task must exist before routes can commit files.
    // Permanent storage mutexes are shared with the network startup/retry.
    esp_err_t result = network_service_storage_init();
    if (result != ESP_OK) {
        atomic_store(&s_started, false);
        return result;
    }
    result = web_reboot_start();
    if (result != ESP_OK) {
        atomic_store(&s_started, false);
        return result;
    }
    result = web_static_start();
    if (result != ESP_OK) {
        if (web_reboot_abort() != ESP_OK) return result;
        atomic_store(&s_started, false);
        return result;
    }
    s_state = state;
    esp_fill_random(&s_health_boot_id,sizeof(s_health_boot_id));
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 6144;
    // LWIP has ten descriptors: HTTPD uses three internal sockets, five
    // clients leave two for the stream and network activity. WS admits two.
    config.max_open_sockets = 5;
    config.send_wait_timeout = CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS;
    config.max_uri_handlers = 16;
    config.lru_purge_enable = true;
    config.uri_match_fn = httpd_uri_match_wildcard;
    httpd_handle_t server = NULL;
    result = native_web_transport_prepare(&config);
    if (result != ESP_OK) goto failed;
    result = httpd_start(&server, &config);
    if (result != ESP_OK) goto failed;
    httpd_uri_t status = {
        .uri = "/api/native/status",
        .method = HTTP_GET,
        .handler = status_handler,
    };
    httpd_uri_t health = {
        .uri = "/api/native/health", .method = HTTP_GET, .handler = health_handler,
    };
    httpd_uri_t reconnect = {
        .uri = "/api/native/reconnect",
        .method = HTTP_POST,
        .handler = reconnect_handler,
    };
    httpd_uri_t radio_get = {.uri="/api/native/radio",.method=HTTP_GET,.handler=radio_handler};
    httpd_uri_t radio_post = {.uri="/api/native/radio",.method=HTTP_POST,.handler=radio_handler};
    httpd_uri_t play = {
        .uri = "/api/native/play*",
        .method = HTTP_POST,
        .handler = play_handler,
    };
    httpd_uri_t stop = {
        .uri = "/api/native/stop",
        .method = HTTP_POST,
        .handler = stop_handler,
    };
    httpd_uri_t settings_get = {
        .uri = "/api/native/settings",
        .method = HTTP_GET,
        .handler = settings_handler,
    };
    httpd_uri_t settings_post = {
        .uri = "/api/native/settings*",
        .method = HTTP_POST,
        .handler = settings_handler,
    };
    httpd_uri_t capabilities = {.uri="/api/native/capabilities", .method=HTTP_GET, .handler=capabilities_handler};
    httpd_uri_t upload = {.uri="/upload", .method=HTTP_POST, .handler=web_upload_handler};
    httpd_uri_t board = {.uri="/webboard", .method=HTTP_POST, .handler=web_board_upload_handler};
    httpd_uri_t wifi = {.uri="/", .method=HTTP_POST, .handler=web_wifi_upload_handler};
    httpd_uri_t files = {
        .uri = "/*",
        .method = HTTP_GET,
        .handler = web_static_handler,
    };
    const httpd_uri_t *routes[] = {&status, &health, &radio_get, &radio_post,
        &reconnect, &play, &stop, &settings_get, &settings_post, &capabilities,
        &upload, &board, &wifi};
    for (unsigned i = 0; i < sizeof(routes) / sizeof(routes[0]); ++i) {
        result = httpd_register_uri_handler(server, routes[i]);
        if (result != ESP_OK) goto failed;
    }
    result = websocket_service_register(server, state);
    if (result != ESP_OK) goto failed;
    result = httpd_register_uri_handler(server, &files);
    if (result != ESP_OK) goto failed;
    result = websocket_service_start();
    if (result != ESP_OK) goto failed;
    web_upload_activate();
    web_static_activate();
    if (state->lock && xSemaphoreTake(state->lock, pdMS_TO_TICKS(100))) {
        state->web_ready = true;
        xSemaphoreGive(state->lock);
    }
    ESP_LOGI(TAG, "Native %s server started", native_web_transport_secure() ? "HTTPS" : "HTTP");
    return ESP_OK;
failed:
    web_upload_deactivate();
    // Keep the server/session workspace alive if a producer has not exited.
    // All ordinary startup failures happen before its task is created.
    if (websocket_service_stop() != ESP_OK) {
        ESP_LOGE(TAG, "WebSocket producer did not stop; retaining server resources");
        return result;
    }
    if (server) {
        if (httpd_stop(server) != ESP_OK) {
            ESP_LOGE(TAG, "HTTP server did not stop; retaining server resources");
            return result;
        }
        websocket_service_server_stopped(server);
    }
    if (native_web_transport_release() != ESP_OK) return result;
    web_static_abort();
    if (web_reboot_abort() != ESP_OK) return result;
    atomic_store(&s_started, false);
    return result;
}
