#include "web_service.h"

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
#include "network_service.h"
#include "radio_control.h"
#include "json_buffer.h"

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

static esp_err_t settings_handler(httpd_req_t *request) {
    if (request->method == HTTP_POST) {
        char query[80];
        char value[16];
        if (httpd_req_get_url_query_str(request, query, sizeof(query)) != ESP_OK) {
            return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                       "Missing settings query");
        }
        if (httpd_query_key_value(query, "volume", value, sizeof(value)) == ESP_OK) {
            unsigned long volume = strtoul(value, NULL, 10);
            if (volume > 254U) volume = 254U;
            native_audio_output_set_volume((uint8_t)volume);
        }
        if (httpd_query_key_value(query, "balance", value, sizeof(value)) == ESP_OK) {
            long balance = strtol(value, NULL, 10);
            if (balance < -16) balance = -16;
            if (balance > 16) balance = 16;
            native_audio_output_set_balance((int8_t)balance);
        }
    }

    char body[64];
    snprintf(body, sizeof(body), "{\"volume\":%u,\"balance\":%d}",
             native_audio_output_get_volume(), native_audio_output_get_balance());
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}

static const char *content_type(const char *path) {
    if (strstr(path, ".html")) return "text/html; charset=utf-8";
    if (strstr(path, ".css")) return "text/css; charset=utf-8";
    if (strstr(path, ".js")) return "application/javascript; charset=utf-8";
    if (strstr(path, ".svg")) return "image/svg+xml";
    if (strstr(path, ".png")) return "image/png";
    if (strstr(path, ".ico")) return "image/x-icon";
    return "application/octet-stream";
}

static esp_err_t static_handler(httpd_req_t *request) {
    char uri[160];
    const char *query = strchr(request->uri, '?');
    size_t uri_len = query ? (size_t)(query - request->uri)
                           : strlen(request->uri);
    if (uri_len >= sizeof(uri) || strstr(request->uri, "..")) {
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "Invalid path");
    }
    memcpy(uri, request->uri, uri_len);
    uri[uri_len] = '\0';
    if (strcmp(uri, "/") == 0) strcpy(uri, "/player.html");

    char path[224];
    snprintf(path, sizeof(path), "/spiffs/www%s", uri);
    FILE *file = fopen(path, "rb");
    bool gzip = false;
    if (!file) {
        strlcat(path, ".gz", sizeof(path));
        file = fopen(path, "rb");
        gzip = file != NULL;
    }
    if (!file) {
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND,
                                   "WebUI file not found");
    }
    httpd_resp_set_type(request, content_type(uri));
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    if (gzip) httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
    char chunk[2048];
    size_t count;
    while ((count = fread(chunk, 1, sizeof(chunk), file)) > 0) {
        if (httpd_resp_send_chunk(request, chunk, count) != ESP_OK) {
            fclose(file);
            httpd_resp_sendstr_chunk(request, NULL);
            return ESP_FAIL;
        }
    }
    fclose(file);
    return httpd_resp_send_chunk(request, NULL, 0);
}

esp_err_t web_service_start(native_state_t *state) {
    s_state = state;
    esp_fill_random(&s_health_boot_id,sizeof(s_health_boot_id));
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 6144;
    config.max_open_sockets = 4;
    config.max_uri_handlers = 16;
    config.lru_purge_enable = true;
    config.uri_match_fn = httpd_uri_match_wildcard;
    httpd_handle_t server = NULL;
    ESP_RETURN_ON_ERROR(httpd_start(&server, &config), TAG,
                        "HTTP server start failed");
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
    httpd_uri_t files = {
        .uri = "/*",
        .method = HTTP_GET,
        .handler = static_handler,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &status), TAG,
                        "Status route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &health), TAG,
                        "Health route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &radio_get), TAG,"Radio GET registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &radio_post), TAG,"Radio POST registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &reconnect), TAG,
                        "Reconnect route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &play), TAG,
                        "Play route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &stop), TAG,
                        "Stop route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &settings_get), TAG,
                        "Settings GET route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &settings_post), TAG,
                        "Settings POST route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &files), TAG,
                        "Static route registration failed");
    if (state->lock && xSemaphoreTake(state->lock, pdMS_TO_TICKS(100))) {
        state->web_ready = true;
        xSemaphoreGive(state->lock);
    }
    ESP_LOGI(TAG, "Native HTTP server started");
    return ESP_OK;
}
