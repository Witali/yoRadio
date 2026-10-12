#include "web_service.h"

#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "audio_service.h"
#include "cpu_profiler.h"
#include "deep_sleep_clock.h"
#include "display_settings.h"
#include "board_config.h"
#include "esp_check.h"
#include "esp_heap_caps.h"
#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "network_service.h"
#include "native_audio_output.h"
#include "audio_pipeline_probe.h"
#include "radio_control.h"
#include "web_pages_bridge.h"
#include "web_ota.h"
#include "web_upload.h"
#include "websocket_service.h"

#define WEB_MAX_OPEN_SOCKETS 7
#define WEB_STATIC_QUEUE_DEPTH WEB_MAX_OPEN_SOCKETS
#define WEB_STATIC_WORKER_PRIORITY 3

static const char *const TAG = "web";
static native_state_t *s_state;
// Technical session identity only; regenerated before HTTP starts on each boot.
static uint64_t s_health_boot_id;
static QueueHandle_t s_static_request_queue;
static TaskHandle_t
    s_static_worker_tasks[CONFIG_YORADIO_WEB_STATIC_WORKERS];

static FILE *open_nonempty_file(const char *path) {
    FILE *file = fopen(path, "rb");
    if (!file) return NULL;
    // SPIFFS does not guarantee useful seek/tell results for every damaged
    // directory entry.  Prove that at least one byte can actually be read so
    // a zero-byte raw file cannot shadow its valid .gz counterpart.
    if (fgetc(file) == EOF || fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        return NULL;
    }
    return file;
}

static bool web_asset_available(const char *name) {
    char path[224];
    snprintf(path, sizeof(path), "/spiffs/www/%s.gz", name);
    FILE *file = open_nonempty_file(path);
    if (!file) return false;
    fclose(file);
    return true;
}

static bool web_ui_available(void) {
    static const char *const required[] = {
        "theme.css",
        "style.css",
        "script.js",
        "dragpl.js",
        "player.html",
        "options.html",
        "logo.svg",
    };
    for (size_t index = 0; index < sizeof(required) / sizeof(required[0]);
         ++index) {
        if (!web_asset_available(required[index])) return false;
    }
    return true;
}

static esp_err_t status_handler(httpd_req_t *request) {
    cpu_profiler_poll();
    native_state_t state;
    native_state_snapshot(s_state, &state);
    const char *mode = "starting";
    if (state.network_mode == NATIVE_NETWORK_CLIENT) mode = "client";
    if (state.network_mode == NATIVE_NETWORK_ACCESS_POINT) mode = "ap";
    if (state.network_mode == NATIVE_NETWORK_ERROR) mode = "error";
    char body[640];
    snprintf(body, sizeof(body),
             "{\"firmware\":\"esp32c3-oled-native\",\"arduino\":false,"
             "\"network\":\"%s\",\"rssi\":%d,\"audio\":%s,\"station\":\"%s\","
             "\"format\":\"%s\",\"sample_rate\":%lu,\"channels\":%u,"
             "\"bits_per_sample\":%u,\"pcm_sample_rate\":%lu,"
             "\"pcm_channels\":%u,\"format_is_pcm\":%s,"
             "\"channels_are_core\":%s}",
             mode, state.wifi_rssi,
             state.audio_running ? "true" : "false", state.station,
             state.stream_format, (unsigned long)state.sample_rate_hz,
             state.channels, state.bits_per_sample,
             (unsigned long)state.pcm_sample_rate_hz, state.pcm_channels,
             state.format_is_pcm ? "true" : "false",
             state.channels_are_core ? "true" : "false");
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
}

#include "decoder_arena.h"
#include "tls_input_reserve.h"
static esp_err_t health_handler(httpd_req_t *request) {
    // Snapshot on demand: no sampler task, retained buffers or console output.
    // Use the same 8-bit allocation capability as the existing heap profiler.
    multi_heap_info_t heap;
    heap_caps_get_info(&heap, MALLOC_CAP_8BIT);
    cpu_profiler_faults_t faults = cpu_profiler_faults();
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    // The diagnostic event sequence and output counter must describe the
    // same ISR boundary. Serialize the copied data after restoring IRQs.
    UBaseType_t previous_mask = portSET_INTERRUPT_MASK_FROM_ISR();
    native_audio_output_health_t output = native_audio_output_health();
    audio_pipeline_probe_t probe = s_audio_pipeline_probe;
    portCLEAR_INTERRUPT_MASK_FROM_ISR(previous_mask);
    // Bound the full 16-event history, input and optional arena counters at
    // uint32 maxima. Both diagnostic variants use the same stack workspace.
    char body[2560];
#else
    native_audio_output_health_t output = native_audio_output_health();
#ifdef CONFIG_YORADIO_SHARED_DECODER_ARENA
    char body[768];
#else
    char body[512];
#endif
#endif
    int length = snprintf(body, sizeof(body),
        "{\"schema\":1,\"boot_id\":\"%016llx\",\"uptime_ms\":%llu,"
        "\"reset_reason\":%u,\"heap\":%lu,\"largest\":%lu,"
        "\"minimum_heap\":%lu,\"tasks\":%lu,"
        "\"allocation_failures\":%lu,\"task_watchdog_events\":%lu,"
        "\"output\":{\"available\":%s,\"completion_queue_drops\":%lu,\"write_errors\":%lu}}",
        (unsigned long long)s_health_boot_id,
        (unsigned long long)(esp_timer_get_time() / 1000),
        (unsigned)esp_reset_reason(), (unsigned long)heap.total_free_bytes,
        (unsigned long)heap.largest_free_block,
        (unsigned long)heap.minimum_free_bytes,
        (unsigned long)uxTaskGetNumberOfTasks(),
        (unsigned long)faults.allocation_failures,
        (unsigned long)faults.task_watchdog_events,
        output.available ? "true" : "false",
        (unsigned long)output.completion_queue_drops,
        (unsigned long)output.write_errors);
#ifdef CONFIG_YORADIO_SHARED_DECODER_ARENA
    decoder_arena_stats_t arena = decoder_arena_stats();
    if (length > 0 && (size_t)length < sizeof(body)) {
        --length; // Replace the outer closing brace with an additional object.
        int added = snprintf(body + length, sizeof(body) - length,
            ",\"decoder_arena\":{\"capacity\":%u,\"live\":%u,\"peak\":%u,"
            "\"blocks\":%u,\"free\":%u,\"largest\":%u,\"failures\":%u}}",
            (unsigned)arena.capacity, (unsigned)arena.live, (unsigned)arena.peak,
            (unsigned)arena.blocks, (unsigned)arena.free_bytes,
            (unsigned)arena.largest, arena.failures);
        length = added < 0 ? -1 : length + added;
    }
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
    if (length > 0 && (size_t)length < sizeof(body)) {
        --length;
        int added = snprintf(body + length, sizeof(body) - length,
            ",\"arena_timing\":{\"malloc\":[%lu,%lu],\"free\":[%lu,%lu],"
            "\"realloc\":[%lu,%lu],\"snapshot\":[%lu,%lu]}}",
            (unsigned long)arena.timing[ARENA_MALLOC].calls, (unsigned long)arena.timing[ARENA_MALLOC].max_us,
            (unsigned long)arena.timing[ARENA_FREE].calls, (unsigned long)arena.timing[ARENA_FREE].max_us,
            (unsigned long)arena.timing[ARENA_REALLOC].calls, (unsigned long)arena.timing[ARENA_REALLOC].max_us,
            (unsigned long)arena.timing[ARENA_SNAPSHOT].calls, (unsigned long)arena.timing[ARENA_SNAPSHOT].max_us);
        length = added < 0 ? -1 : length + added;
    }
#endif
#endif
#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    if (length > 0 && (size_t)length < sizeof(body)) {
        adaptive_input_stats_t input = tls_input_reserve_input_stats();
        --length;
        int added = snprintf(body + length, sizeof(body) - length,
            ",\"input_queue\":{\"resident\":%u,\"occupied\":%u,\"minimum\":%u,"
            "\"limit\":%u,\"packet_capacity\":%u}}", input.resident, input.occupied,
            input.minimum, input.limit, (unsigned)input.packet_capacity);
        length = added < 0 ? -1 : length + added;
    }
#endif
    length = audio_pipeline_probe_append(body, sizeof(body), length, &probe);
#endif
    if (length < 0 || (size_t)length >= sizeof(body)) {
        return httpd_resp_send_err(request, HTTPD_500_INTERNAL_SERVER_ERROR,
                                   "Health response overflow");
    }
    httpd_resp_set_type(request, "application/json; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_send(request, body, length);
}

static esp_err_t web_memory_handler(httpd_req_t *request) {
    unsigned static_min = UINT32_MAX;
    for (unsigned i = 0; i < CONFIG_YORADIO_WEB_STATIC_WORKERS; ++i) {
        unsigned free = uxTaskGetStackHighWaterMark(s_static_worker_tasks[i]);
        if (free < static_min) static_min = free;
    }
    char body[256];
    snprintf(body, sizeof(body),
        "{\"download_chunk_bytes\":%u,\"download_workers\":%u,"
        "\"static_stack_bytes_each\":%u,\"static_stack_free_min\":%u,"
        "\"http_stack_bytes\":8192,\"http_stack_free_min\":%u}",
        CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES, CONFIG_YORADIO_WEB_STATIC_WORKERS,
        BOARD_TASK_STACK_WEB_STATIC, static_min,
        (unsigned)uxTaskGetStackHighWaterMark(NULL));
    httpd_resp_set_type(request, "application/json");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, body);
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
    audio_service_stop();
    httpd_resp_set_type(request, "application/json");
    return httpd_resp_sendstr(request, "{\"playing\":false}");
}

static esp_err_t send_recovery_page(httpd_req_t *request) {
    httpd_resp_set_type(request, "text/html; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, yoradio_emptyfs_html());
}

static esp_err_t webboard_page_handler(httpd_req_t *request) {
    return send_recovery_page(request);
}

static esp_err_t emergency_handler(httpd_req_t *request) {
    httpd_resp_set_type(request, "text/html; charset=utf-8");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, yoradio_emergency_form());
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

static esp_err_t finish_static_response(httpd_req_t *request,
                                        esp_err_t result) {
    if (result == ESP_OK) {
        // The WebSocket is the only connection the UI needs to keep open.
        // Reclaim each short-lived asset socket as soon as its response has
        // been queued, leaving descriptors available to the audio client.
        httpd_sess_trigger_close(request->handle,
                                 httpd_req_to_sockfd(request));
    }
    return result;
}

static esp_err_t serve_static_request(httpd_req_t *request) {
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
    if (strcmp(uri, "/script.js") == 0 || strcmp(uri, "/script.js.gz") == 0) {
        extern const uint8_t script_start[] asm("_binary_native_script_js_gz_start");
        extern const uint8_t script_end[] asm("_binary_native_script_js_gz_end");
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
        httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
        httpd_resp_set_hdr(request, "Connection", "close");
        return finish_static_response(request, httpd_resp_send(request,
            (const char *)script_start, script_end - script_start));
    }
    if (strcmp(uri, "/") == 0 || strcmp(uri, "/index.html") == 0 ||
        strcmp(uri, "/settings.html") == 0 ||
        strcmp(uri, "/update.html") == 0 || strcmp(uri, "/ir.html") == 0) {
        if (strcmp(uri, "/") == 0 && !web_ui_available()) {
            return send_recovery_page(request);
        }
        httpd_resp_set_type(request, "text/html; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_hdr(request, "Connection", "close");
        return finish_static_response(
            request, httpd_resp_sendstr(request, yoradio_index_html()));
    }
    if (strcmp(uri, "/variables.js") == 0) {
        native_state_t state;
        native_state_snapshot(s_state, &state);
        char variables[512];
        snprintf(variables, sizeof(variables),
                 "var yoVersion='idf-%s';\n"
                 "var webUiRevision='native05-ota';\n"
                 "var formAction='%s';\n"
                 "var playMode='%s';\n"
                 "var equalizerEnabled=false;\n"
                 "var nativeFirmwareOnly=true;\n"
                 "var nativeFirmwareName='ESP32-C3 OLED native';\n"
                 "var nativeFirmwareInfo='/api/native/ota';\n",
                 esp_get_idf_version(),
                 state.network_mode == NATIVE_NETWORK_CLIENT &&
                         web_ui_available()
                     ? "webboard"
                     : "",
                 state.network_mode == NATIVE_NETWORK_CLIENT ? "player"
                                                              : "ap");
        httpd_resp_set_type(request, "application/javascript; charset=utf-8");
        httpd_resp_set_hdr(request, "Cache-Control", "no-store");
        httpd_resp_set_hdr(request, "Connection", "close");
        return finish_static_response(request,
                                      httpd_resp_sendstr(request, variables));
    }

    char path[224];
    bool gzip = false;
    if (strncmp(uri, "/data/", 6) == 0) {
        snprintf(path, sizeof(path), "/spiffs%s", uri);
    } else {
        if (strlen(uri) > 3 && strcmp(uri + strlen(uri) - 3, ".gz") == 0) {
            snprintf(path, sizeof(path), "/spiffs/www%s", uri);
        } else {
            snprintf(path, sizeof(path), "/spiffs/www%s.gz", uri);
        }
        gzip = true;
    }
    FILE *file = open_nonempty_file(path);
    if (!file) {
        return httpd_resp_send_err(request, HTTPD_404_NOT_FOUND,
                                   "WebUI file not found");
    }
    httpd_resp_set_type(request, content_type(uri));
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache");
    httpd_resp_set_hdr(request, "Connection", "close");
    if (gzip) httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
    // Private to this worker. Its entire stack is allocated at startup,
    // before requests can arrive; no payload allocation occurs per download.
    char chunk[CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES];
    size_t count;
    while ((count = fread(chunk, 1, sizeof(chunk), file)) > 0) {
        if (httpd_resp_send_chunk(request, chunk, count) != ESP_OK) {
            fclose(file);
            httpd_resp_sendstr_chunk(request, NULL);
            return ESP_FAIL;
        }
    }
    bool read_failed = ferror(file) != 0;
    fclose(file);
    if (read_failed) return ESP_FAIL; // Do not terminate a truncated body as success.
    return finish_static_response(
        request, httpd_resp_send_chunk(request, NULL, 0));
}

static void static_worker_task(void *argument) {
    (void)argument;
    while (true) {
        httpd_req_t *request = NULL;
        if (xQueueReceive(s_static_request_queue, &request, portMAX_DELAY) !=
            pdTRUE) {
            continue;
        }
        esp_err_t result = serve_static_request(request);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "Static response failed for %s: %s", request->uri,
                     esp_err_to_name(result));
        }
        result = httpd_req_async_handler_complete(request);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Static request completion failed: %s",
                     esp_err_to_name(result));
        }
    }
}

static esp_err_t start_static_workers(void) {
    s_static_request_queue =
        xQueueCreate(WEB_STATIC_QUEUE_DEPTH, sizeof(httpd_req_t *));
    ESP_RETURN_ON_FALSE(s_static_request_queue, ESP_ERR_NO_MEM, TAG,
                        "create static request queue");
    for (size_t index = 0; index < CONFIG_YORADIO_WEB_STATIC_WORKERS;
         ++index) {
        char name[configMAX_TASK_NAME_LEN];
        snprintf(name, sizeof(name), "web_static_%u", (unsigned)index);
        if (xTaskCreate(static_worker_task, name, BOARD_TASK_STACK_WEB_STATIC,
                        NULL, WEB_STATIC_WORKER_PRIORITY,
                        &s_static_worker_tasks[index]) != pdPASS) {
            for (size_t created = 0; created < index; ++created) {
                vTaskDelete(s_static_worker_tasks[created]);
                s_static_worker_tasks[created] = NULL;
            }
            vQueueDelete(s_static_request_queue);
            s_static_request_queue = NULL;
            return ESP_ERR_NO_MEM;
        }
    }
    ESP_LOGI(TAG, "Static content workers: %u, send timeout: %u seconds",
             (unsigned)CONFIG_YORADIO_WEB_STATIC_WORKERS,
             (unsigned)CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS);
    return ESP_OK;
}

static esp_err_t static_handler(httpd_req_t *request) {
    httpd_req_t *async_request = NULL;
    esp_err_t result =
        httpd_req_async_handler_begin(request, &async_request);
    if (result != ESP_OK) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        httpd_resp_set_hdr(request, "Connection", "close");
        return httpd_resp_sendstr(request, "Static worker unavailable");
    }
    if (xQueueSend(s_static_request_queue, &async_request, 0) != pdTRUE) {
        httpd_resp_set_status(async_request, "503 Service Unavailable");
        httpd_resp_set_hdr(async_request, "Connection", "close");
        httpd_resp_sendstr(async_request, "Static worker queue full");
        httpd_req_async_handler_complete(async_request);
    }
    return ESP_OK;
}

static esp_err_t with_awake_request(httpd_req_t *request,
                                     esp_err_t (*handler)(httpd_req_t *)) {
    if (!deep_sleep_clock_begin_activity()) {
        httpd_resp_set_status(request, "503 Service Unavailable");
        return httpd_resp_sendstr(request, "Clock is entering sleep");
    }
    display_settings_note_activity();
    esp_err_t result = handler(request);
    display_settings_note_activity();
    deep_sleep_clock_end_activity();
    return result;
}

static esp_err_t sleep_guarded_reconnect_handler(httpd_req_t *request) {
    return with_awake_request(request, reconnect_handler);
}
static esp_err_t sleep_guarded_play_handler(httpd_req_t *request) {
    return with_awake_request(request, play_handler);
}
static esp_err_t sleep_guarded_stop_handler(httpd_req_t *request) {
    return with_awake_request(request, stop_handler);
}
static esp_err_t sleep_guarded_upload_handler(httpd_req_t *request) {
    return with_awake_request(request, web_upload_handler);
}
static esp_err_t sleep_guarded_webboard_upload_handler(httpd_req_t *request) {
    return with_awake_request(request, web_board_upload_handler);
}
static esp_err_t sleep_guarded_emergency_handler(httpd_req_t *request) {
    return with_awake_request(request, emergency_handler);
}
static esp_err_t sleep_guarded_recovery_wifi_handler(httpd_req_t *request) {
    return with_awake_request(request, web_wifi_upload_handler);
}

esp_err_t web_service_start(native_state_t *state) {
    s_state = state;
    esp_fill_random(&s_health_boot_id, sizeof(s_health_boot_id));
    ESP_RETURN_ON_ERROR(start_static_workers(), TAG,
                        "start static content workers");
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 8192; // Upload payload is a bounded, temporary heap buffer.
    // Browsers commonly fetch six assets in parallel. Keep those connections
    // plus the persistent WebSocket alive; with four sockets the LRU purge
    // closed /ws during page startup and the shared UI spinner never stopped.
    config.max_open_sockets = WEB_MAX_OPEN_SOCKETS;
    config.max_uri_handlers = 15; // Includes WebSocket, memory probe and final wildcard.
    config.lru_purge_enable = true;
    config.send_wait_timeout = CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS;
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
        .uri = "/api/native/health", .method = HTTP_GET,
        .handler = health_handler,
    };
    httpd_uri_t ota = {
        .uri = "/update", .method = HTTP_POST, .handler = web_ota_handler,
    };
    httpd_uri_t ota_info = {
        .uri = "/api/native/ota", .method = HTTP_GET,
        .handler = web_ota_info_handler,
    };
    httpd_uri_t reconnect = {
        .uri = "/api/native/reconnect",
        .method = HTTP_POST,
        .handler = sleep_guarded_reconnect_handler,
    };
    httpd_uri_t play = {
        .uri = "/api/native/play*",
        .method = HTTP_POST,
        .handler = sleep_guarded_play_handler,
    };
    httpd_uri_t stop = {
        .uri = "/api/native/stop",
        .method = HTTP_POST,
        .handler = sleep_guarded_stop_handler,
    };
    httpd_uri_t upload = {
        .uri = "/upload",
        .method = HTTP_POST,
        .handler = sleep_guarded_upload_handler,
    };
    httpd_uri_t webboard_page = {
        .uri = "/webboard",
        .method = HTTP_GET,
        .handler = webboard_page_handler,
    };
    httpd_uri_t webboard_upload = {
        .uri = "/webboard",
        .method = HTTP_POST,
        .handler = sleep_guarded_webboard_upload_handler,
    };
    httpd_uri_t emergency = {
        .uri = "/emergency",
        .method = HTTP_GET,
        .handler = sleep_guarded_emergency_handler,
    };
    httpd_uri_t recovery_wifi = {
        .uri = "/",
        .method = HTTP_POST,
        .handler = sleep_guarded_recovery_wifi_handler,
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
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &ota), TAG,
                        "OTA route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &ota_info), TAG,
                        "OTA info route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &reconnect), TAG,
                        "Reconnect route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &play), TAG,
                        "Play route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &stop), TAG,
                        "Stop route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &upload), TAG,
                        "Upload route registration failed");
    ESP_RETURN_ON_ERROR(
        httpd_register_uri_handler(server, &webboard_page), TAG,
        "Web board page route registration failed");
    ESP_RETURN_ON_ERROR(
        httpd_register_uri_handler(server, &webboard_upload), TAG,
        "Web board upload route registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &emergency), TAG,
                        "Emergency page route registration failed");
    ESP_RETURN_ON_ERROR(
        httpd_register_uri_handler(server, &recovery_wifi), TAG,
        "Recovery Wi-Fi route registration failed");
    httpd_uri_t memory = {
        .uri = "/api/native/web-memory", .method = HTTP_GET,
        .handler = web_memory_handler,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &memory), TAG,
                        "Web memory route registration failed");
    ESP_RETURN_ON_ERROR(websocket_service_register(server, state), TAG,
                        "WebSocket service registration failed");
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &files), TAG,
                        "Static route registration failed");
    if (state->lock && xSemaphoreTake(state->lock, pdMS_TO_TICKS(100))) {
        state->web_ready = true;
        xSemaphoreGive(state->lock);
    }
    ESP_LOGI(TAG, "Native HTTP server started");
    return ESP_OK;
}
