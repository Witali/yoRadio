#include "audio_service.h"

#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#include "esp_audio_dec_default.h"
#include "esp_audio_simple_dec.h"
#include "esp_audio_simple_dec_default.h"
#include "esp_check.h"
#include "esp_crt_bundle.h"
#include "esp_http_client.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/queue.h"
#include "freertos/ringbuf.h"
#include "freertos/task.h"
#include "native_audio_output.h"

#define STREAM_CHUNK_SIZE 2048
#define DECODE_BUFFER_INITIAL 12288
#define ENCODED_RING_SIZE (8 * 1024)
#define PCM_RING_SIZE (8 * 1024)
#define PCM_PACKET_DATA_SIZE 3072
#define MAX_HTTP_REDIRECTS 5

typedef struct {
    uint32_t generation;
    native_codec_t requested_codec;
    char url[512];
} play_command_t;

typedef struct {
    uint32_t generation;
    native_codec_t codec;
    uint16_t data_size;
    bool end_of_stream;
    uint8_t data[];
} encoded_packet_t;

typedef struct {
    uint32_t generation;
    uint32_t sample_rate;
    uint8_t bits_per_sample;
    uint8_t channels;
    uint16_t data_size;
    uint8_t data[];
} pcm_packet_t;

static const char *const TAG = "audio";
static native_state_t *s_state;
static QueueHandle_t s_commands;
static RingbufHandle_t s_encoded;
static RingbufHandle_t s_pcm;
static atomic_uint s_generation;

static native_codec_t codec_from_content_type(const char *content_type) {
    if (!content_type) return NATIVE_CODEC_AUTO;
    if (strstr(content_type, "mpeg") || strstr(content_type, "mp3")) {
        return NATIVE_CODEC_MP3;
    }
    if (strstr(content_type, "aac") || strstr(content_type, "aacp")) {
        return NATIVE_CODEC_AAC;
    }
    if (strstr(content_type, "flac")) return NATIVE_CODEC_FLAC;
    if (strstr(content_type, "ogg") || strstr(content_type, "opus")) {
        return NATIVE_CODEC_OGG;
    }
    return NATIVE_CODEC_AUTO;
}

static native_codec_t codec_from_signature(const uint8_t *data, size_t size) {
    if (size >= 4 && memcmp(data, "fLaC", 4) == 0) return NATIVE_CODEC_FLAC;
    if (size >= 4 && memcmp(data, "OggS", 4) == 0) return NATIVE_CODEC_OGG;
    if (size >= 3 && memcmp(data, "ID3", 3) == 0) return NATIVE_CODEC_MP3;
    if (size >= 2 && data[0] == 0xff && (data[1] & 0xf6) == 0xf0) {
        return NATIVE_CODEC_AAC;
    }
    if (size >= 2 && data[0] == 0xff && (data[1] & 0xe0) == 0xe0) {
        return NATIVE_CODEC_MP3;
    }
    return NATIVE_CODEC_MP3;
}

static esp_audio_simple_dec_type_t simple_decoder_type(native_codec_t codec) {
    switch (codec) {
        case NATIVE_CODEC_AAC:
            return ESP_AUDIO_SIMPLE_DEC_TYPE_AAC;
        case NATIVE_CODEC_FLAC:
            return ESP_AUDIO_SIMPLE_DEC_TYPE_FLAC;
        case NATIVE_CODEC_OGG:
            return ESP_AUDIO_SIMPLE_DEC_TYPE_OGG;
        case NATIVE_CODEC_MP3:
        default:
            return ESP_AUDIO_SIMPLE_DEC_TYPE_MP3;
    }
}

static const char *codec_name(native_codec_t codec) {
    switch (codec) {
        case NATIVE_CODEC_AAC: return "AAC";
        case NATIVE_CODEC_FLAC: return "FLAC";
        case NATIVE_CODEC_OGG: return "OGG";
        case NATIVE_CODEC_MP3: return "MP3";
        default: return "auto";
    }
}

static void state_set_audio(bool running, const char *format) {
    if (!s_state || !s_state->lock) return;
    if (xSemaphoreTake(s_state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        s_state->audio_running = running;
        if (format) strlcpy(s_state->stream_format, format,
                            sizeof(s_state->stream_format));
        xSemaphoreGive(s_state->lock);
    }
}

static bool http_status_is_redirect(int status) {
    return status == 301 || status == 302 || status == 303 || status == 307 ||
           status == 308;
}

static esp_err_t open_stream(esp_http_client_handle_t client,
                             const char *requested_url) {
    for (unsigned redirect = 0; redirect <= MAX_HTTP_REDIRECTS; ++redirect) {
        ESP_LOGI(TAG, "Opening stream%s: %s",
                 redirect ? " after redirect" : "", requested_url);
        esp_err_t result = esp_http_client_open(client, 0);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream transport open failed: %s (errno %d)",
                     esp_err_to_name(result), esp_http_client_get_errno(client));
            return result;
        }

        int64_t headers = esp_http_client_fetch_headers(client);
        int status = esp_http_client_get_status_code(client);
        if (headers < 0) {
            ESP_LOGE(TAG,
                     "Stream response headers failed: status %d, errno %d",
                     status, esp_http_client_get_errno(client));
            esp_http_client_close(client);
            return ESP_ERR_HTTP_FETCH_HEADER;
        }
        ESP_LOGI(TAG, "Stream response: HTTP %d, length %lld", status,
                 (long long)headers);

        if (status >= 200 && status < 300) return ESP_OK;
        if (!http_status_is_redirect(status) || redirect == MAX_HTTP_REDIRECTS) {
            esp_http_client_close(client);
            return http_status_is_redirect(status) ? ESP_ERR_HTTP_MAX_REDIRECT
                                                   : ESP_FAIL;
        }
        result = esp_http_client_set_redirection(client);
        esp_http_client_close(client);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream redirect failed: %s",
                     esp_err_to_name(result));
            return result;
        }
    }
    return ESP_ERR_HTTP_MAX_REDIRECT;
}

static bool send_encoded(uint32_t generation, native_codec_t codec,
                         const uint8_t *data, size_t size, bool eos) {
    size_t packet_size = sizeof(encoded_packet_t) + size;
    encoded_packet_t *packet = NULL;
    while (xRingbufferSendAcquire(s_encoded, (void **)&packet, packet_size,
                                  pdMS_TO_TICKS(250)) != pdTRUE) {
        // A slow decoder must apply TCP backpressure, not terminate the
        // station. Short waits still let a station change cancel promptly.
        if (atomic_load(&s_generation) != generation) return false;
    }
    packet->generation = generation;
    packet->codec = codec;
    packet->data_size = (uint16_t)size;
    packet->end_of_stream = eos;
    if (size) memcpy(packet->data, data, size);
    return xRingbufferSendComplete(s_encoded, packet) == pdTRUE;
}

static void stream_task(void *argument) {
    (void)argument;
    uint8_t *buffer = malloc(STREAM_CHUNK_SIZE);
    if (!buffer) {
        ESP_LOGE(TAG, "No memory for stream input buffer");
        vTaskDelete(NULL);
    }
    while (true) {
        play_command_t command;
        xQueueReceive(s_commands, &command, portMAX_DELAY);
        state_set_audio(false, "connecting");

        esp_http_client_config_t config = {
            .url = command.url,
            .timeout_ms = 10000,
            .buffer_size = STREAM_CHUNK_SIZE,
            .buffer_size_tx = 4096,
            .crt_bundle_attach = esp_crt_bundle_attach,
            .disable_auto_redirect = false,
            .max_redirection_count = MAX_HTTP_REDIRECTS,
            .keep_alive_enable = true,
            .user_agent = "yoRadio-native/1",
        };
        esp_http_client_handle_t client = esp_http_client_init(&config);
        if (!client) {
            state_set_audio(false, "HTTP allocation failed");
            continue;
        }
        esp_http_client_set_header(client, "Icy-MetaData", "0");
        esp_err_t result = open_stream(client, command.url);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream connection failed for %s: %s", command.url,
                     esp_err_to_name(result));
            state_set_audio(false, "connection failed");
            esp_http_client_cleanup(client);
            continue;
        }
        native_codec_t codec = command.requested_codec;
        if (codec == NATIVE_CODEC_AUTO) {
            char *content_type = NULL;
            if (esp_http_client_get_response_header(
                    client, "Content-Type", &content_type) == ESP_OK) {
                codec = codec_from_content_type(content_type);
            }
        }
        bool first_chunk = true;
        while (atomic_load(&s_generation) == command.generation) {
            int received = esp_http_client_read(client, (char *)buffer,
                                                STREAM_CHUNK_SIZE);
            if (received < 0) {
                ESP_LOGW(TAG, "Stream read failed");
                break;
            }
            if (received == 0) {
                if (esp_http_client_is_complete_data_received(client)) break;
                vTaskDelay(pdMS_TO_TICKS(10));
                continue;
            }
            if (first_chunk) {
                first_chunk = false;
                if (codec == NATIVE_CODEC_AUTO) {
                    codec = codec_from_signature(buffer, received);
                }
                state_set_audio(false, codec_name(codec));
            }
            if (!send_encoded(command.generation, codec, buffer, received,
                              false)) {
                ESP_LOGW(TAG, "Compressed audio buffer stalled");
                break;
            }
        }
        send_encoded(command.generation, codec, NULL, 0, true);
        esp_http_client_close(client);
        esp_http_client_cleanup(client);
    }
}

static bool send_pcm(uint32_t generation,
                     const esp_audio_simple_dec_info_t *info,
                     const uint8_t *data, size_t size) {
    while (size) {
        size_t chunk = size > PCM_PACKET_DATA_SIZE ? PCM_PACKET_DATA_SIZE
                                                   : size;
        size_t packet_size = sizeof(pcm_packet_t) + chunk;
        pcm_packet_t *packet = NULL;
        while (xRingbufferSendAcquire(s_pcm, (void **)&packet, packet_size,
                                      pdMS_TO_TICKS(250)) != pdTRUE) {
            if (atomic_load(&s_generation) != generation) return false;
        }
        packet->generation = generation;
        packet->sample_rate = info->sample_rate;
        packet->bits_per_sample = info->bits_per_sample;
        packet->channels = info->channel;
        packet->data_size = (uint16_t)chunk;
        memcpy(packet->data, data, chunk);
        if (xRingbufferSendComplete(s_pcm, packet) != pdTRUE) return false;
        data += chunk;
        size -= chunk;
    }
    return true;
}

static void decoder_task(void *argument) {
    (void)argument;
    esp_audio_dec_register_default();
    esp_audio_simple_dec_register_default();
    uint8_t *output = malloc(DECODE_BUFFER_INITIAL);
    size_t output_size = DECODE_BUFFER_INITIAL;
    esp_audio_simple_dec_handle_t decoder = NULL;
    uint32_t generation = 0;
    uint32_t failed_generation = 0;
    native_codec_t codec = NATIVE_CODEC_AUTO;

    while (true) {
        size_t item_size = 0;
        encoded_packet_t *packet = xRingbufferReceive(
            s_encoded, &item_size, portMAX_DELAY);
        if (!packet) continue;
        if (packet->generation != atomic_load(&s_generation)) {
            vRingbufferReturnItem(s_encoded, packet);
            continue;
        }
        if (packet->generation == failed_generation) {
            vRingbufferReturnItem(s_encoded, packet);
            continue;
        }
        if (packet->generation != generation || packet->codec != codec) {
            if (decoder) esp_audio_simple_dec_close(decoder);
            decoder = NULL;
            generation = packet->generation;
            codec = packet->codec;
            esp_audio_simple_dec_cfg_t cfg = {
                .dec_type = simple_decoder_type(codec),
                .dec_cfg = NULL,
                .cfg_size = 0,
                .use_frame_dec = false,
            };
            esp_audio_err_t open_result =
                esp_audio_simple_dec_open(&cfg, &decoder);
            if (open_result != ESP_AUDIO_ERR_OK) {
                ESP_LOGE(TAG, "%s decoder open failed: %d", codec_name(codec),
                         open_result);
                state_set_audio(false, "decoder allocation failed");
            }
        }
        if (!decoder) {
            vRingbufferReturnItem(s_encoded, packet);
            continue;
        }
        esp_audio_simple_dec_raw_t raw = {
            .buffer = packet->data,
            .len = packet->data_size,
            .eos = packet->end_of_stream,
        };
        while (raw.len || raw.eos) {
            esp_audio_simple_dec_out_t frame = {
                .buffer = output,
                .len = output_size,
            };
            esp_audio_err_t result =
                esp_audio_simple_dec_process(decoder, &raw, &frame);
            // A continuously fed decoder is always runnable. On the
            // single-core C3, give the idle task one tick per decode call so
            // it can service the task watchdog without reducing audio task
            // priority or starving the PDM output task.
            vTaskDelay(1);
            if (generation != atomic_load(&s_generation)) break;
            if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                uint8_t *larger = realloc(output, frame.needed_size);
                if (!larger) {
                    state_set_audio(false, "PCM allocation failed");
                    break;
                }
                output = larger;
                output_size = frame.needed_size;
                continue;
            }
            if (result != ESP_AUDIO_ERR_OK) {
                ESP_LOGW(TAG, "%s decode error: %d", codec_name(codec),
                         result);
                state_set_audio(false, "decode failed");
                failed_generation = generation;
                break;
            }
            if (frame.decoded_size) {
                esp_audio_simple_dec_info_t info = {0};
                if (esp_audio_simple_dec_get_info(decoder, &info) ==
                    ESP_AUDIO_ERR_OK) {
                    char format[48];
                    snprintf(format, sizeof(format), "%lu kHz %s",
                             (unsigned long)(info.sample_rate / 1000),
                             info.channel == 1 ? "mono" : "stereo");
                    state_set_audio(true, format);
                    if (!send_pcm(generation, &info, output,
                                  frame.decoded_size)) {
                        ESP_LOGW(TAG, "PCM buffer stalled");
                        break;
                    }
                }
            }
            if (packet->end_of_stream || raw.len == 0) break;
        }
        vRingbufferReturnItem(s_encoded, packet);
    }
}

static void output_task(void *argument) {
    (void)argument;
    uint32_t sample_rate = 0;
    while (true) {
        size_t item_size = 0;
        pcm_packet_t *packet = xRingbufferReceive(s_pcm, &item_size,
                                                  pdMS_TO_TICKS(5));
        if (!packet) {
            native_audio_output_idle();
            continue;
        }
        if (packet->generation != atomic_load(&s_generation)) {
            vRingbufferReturnItem(s_pcm, packet);
            continue;
        }
        if (packet->sample_rate != sample_rate) {
            esp_err_t result =
                native_audio_output_configure(packet->sample_rate);
            if (result != ESP_OK) {
                ESP_LOGE(TAG, "%s %lu Hz setup failed: %s",
                         native_audio_output_name(),
                         (unsigned long)packet->sample_rate,
                         esp_err_to_name(result));
                vRingbufferReturnItem(s_pcm, packet);
                continue;
            }
            sample_rate = packet->sample_rate;
        }
        esp_err_t result = native_audio_output_write_pcm(
            packet->data, packet->data_size, packet->bits_per_sample,
            packet->channels);
        if (result != ESP_OK) {
            ESP_LOGW(TAG, "%s write failed: %s", native_audio_output_name(),
                     esp_err_to_name(result));
        }
        vRingbufferReturnItem(s_pcm, packet);
    }
}

esp_err_t audio_service_start(native_state_t *state) {
    s_state = state;
    ESP_RETURN_ON_ERROR(native_audio_output_init(), TAG,
                        "initialize audio output");
    atomic_init(&s_generation, 0);
    s_commands = xQueueCreate(1, sizeof(play_command_t));
    s_encoded = xRingbufferCreate(ENCODED_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
    s_pcm = xRingbufferCreate(PCM_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
    if (!s_commands || !s_encoded || !s_pcm) return ESP_ERR_NO_MEM;
    // ESP32-C3 has one core. Priorities keep output ahead of decode and
    // networking while ordinary xTaskCreate avoids an invalid core-1 pin.
    if (xTaskCreate(stream_task, "radio_stream", 6144, NULL, 3, NULL) !=
            pdPASS ||
        xTaskCreate(decoder_task, "audio_decode", 16384, NULL, 5, NULL) !=
            pdPASS ||
        xTaskCreate(output_task, "audio_output", 4096, NULL, 6, NULL) !=
            pdPASS) {
        return ESP_ERR_NO_MEM;
    }
    ESP_LOGI(TAG,
             "Pipeline ready: %s, 8 KiB compressed + 8 KiB PCM, free heap %u",
             native_audio_output_name(),
             (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT));
    return ESP_OK;
}

esp_err_t audio_service_play(const char *url, native_codec_t codec) {
    if (!url || !url[0] || strlen(url) >= sizeof(((play_command_t *)0)->url)) {
        return ESP_ERR_INVALID_ARG;
    }
    play_command_t command = {
        .generation = atomic_fetch_add(&s_generation, 1) + 1,
        .requested_codec = codec,
    };
    strlcpy(command.url, url, sizeof(command.url));
    if (s_state && s_state->lock &&
        xSemaphoreTake(s_state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        strlcpy(s_state->station, url, sizeof(s_state->station));
        xSemaphoreGive(s_state->lock);
    }
    return xQueueOverwrite(s_commands, &command) == pdTRUE ? ESP_OK
                                                            : ESP_FAIL;
}

void audio_service_stop(void) {
    atomic_fetch_add(&s_generation, 1);
    state_set_audio(false, "stopped");
}
