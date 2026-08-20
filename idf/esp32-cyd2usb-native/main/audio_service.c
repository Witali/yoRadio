#include "audio_service.h"

#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#include "audio_level_led.h"
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
#if defined(CONFIG_YORADIO_AAC_DECODER_HELIX) || \
    defined(CONFIG_YORADIO_MP3_DECODER_HELIX) || \
    defined(CONFIG_YORADIO_MP3_DECODER_MINIMP3)
#define YORADIO_CUSTOM_LEGACY_DECODER 1
#include "custom_legacy_adapter.h"
#endif
#include "native_audio_output.h"

#define STREAM_CHUNK_SIZE 2048
#define DECODE_BUFFER_INITIAL 12288
#define ENCODED_RING_SIZE (8 * 1024)
#define PCM_RING_SIZE (8 * 1024)
#define PCM_PACKET_DATA_SIZE 3072

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

static bool send_encoded(uint32_t generation, native_codec_t codec,
                         const uint8_t *data, size_t size, bool eos) {
    size_t packet_size = sizeof(encoded_packet_t) + size;
    encoded_packet_t *packet = NULL;
    if (xRingbufferSendAcquire(s_encoded, (void **)&packet, packet_size,
                               pdMS_TO_TICKS(1000)) != pdTRUE) return false;
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
            .max_redirection_count = 5,
            .keep_alive_enable = true,
            .user_agent = "yoRadio-native/1",
        };
        esp_http_client_handle_t client = esp_http_client_init(&config);
        if (!client) {
            state_set_audio(false, "HTTP allocation failed");
            continue;
        }
        esp_http_client_set_header(client, "Icy-MetaData", "0");
        esp_err_t result = esp_http_client_open(client, 0);
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream open failed: %s", esp_err_to_name(result));
            state_set_audio(false, "connection failed");
            esp_http_client_cleanup(client);
            continue;
        }
        esp_http_client_fetch_headers(client);
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
        if (xRingbufferSendAcquire(s_pcm, (void **)&packet, packet_size,
                                   pdMS_TO_TICKS(1000)) != pdTRUE) return false;
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

#ifdef YORADIO_CUSTOM_LEGACY_DECODER
typedef struct {
    uint32_t generation;
    esp_audio_simple_dec_info_t stream_info;
    bool stream_info_ready;
} custom_legacy_output_context_t;

static bool custom_legacy_output(void *user, const custom_legacy_info_t *info,
                                 const uint8_t *pcm, size_t pcm_size) {
    custom_legacy_output_context_t *context = user;
    if (context->generation != atomic_load(&s_generation)) return false;
    if (!context->stream_info_ready) {
        context->stream_info = (esp_audio_simple_dec_info_t){
            .sample_rate = info->sample_rate,
            .bits_per_sample = info->bits_per_sample,
            .channel = info->channels,
            .bitrate = info->bitrate,
        };
        context->stream_info_ready = true;
        char format[48];
        snprintf(format, sizeof(format), "%lu kHz %s",
                 (unsigned long)(info->sample_rate / 1000),
                 info->channels == 1 ? "mono" : "stereo");
        state_set_audio(true, format);
    }
    return send_pcm(context->generation, &context->stream_info, pcm, pcm_size);
}
#endif

static void decoder_task(void *argument) {
    (void)argument;
    // Register only the selected Espressif codecs. The custom minimp3/Helix
    // implementation is linked directly and does not use this registry.
#ifdef CONFIG_YORADIO_MP3_DECODER_ESPRESSIF
    esp_mp3_dec_register();
#endif
#ifdef CONFIG_YORADIO_AAC_DECODER_ESPRESSIF
    esp_aac_dec_register();
#endif
    esp_flac_dec_register();
    esp_vorbis_dec_register();
    esp_opus_dec_register();
    esp_audio_simple_dec_register_default();
    uint8_t *output = NULL;
    size_t output_size = 0;
    esp_audio_simple_dec_handle_t decoder = NULL;
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
    custom_legacy_decoder_t *legacy_decoder = NULL;
    custom_legacy_output_context_t legacy_context = {0};
#endif
    uint32_t generation = 0;
    native_codec_t codec = NATIVE_CODEC_AUTO;

    while (true) {
        size_t item_size = 0;
        encoded_packet_t *packet = xRingbufferReceive(
            s_encoded, &item_size, portMAX_DELAY);
        if (!packet) continue;
        if (packet->generation != generation || packet->codec != codec) {
            if (decoder) esp_audio_simple_dec_close(decoder);
            decoder = NULL;
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            if (legacy_decoder) custom_legacy_decoder_destroy(legacy_decoder);
            legacy_decoder = NULL;
#endif
            generation = packet->generation;
            codec = packet->codec;
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            legacy_context = (custom_legacy_output_context_t){
                .generation = generation,
            };
            if (
#ifdef CONFIG_YORADIO_AAC_DECODER_HELIX
                codec == NATIVE_CODEC_AAC ||
#endif
#if defined(CONFIG_YORADIO_MP3_DECODER_HELIX) || defined(CONFIG_YORADIO_MP3_DECODER_MINIMP3)
                codec == NATIVE_CODEC_MP3 ||
#endif
                false) {
                free(output);
                output = NULL;
                output_size = 0;
                legacy_decoder = custom_legacy_decoder_create(
                    codec == NATIVE_CODEC_AAC ? CUSTOM_LEGACY_AAC
                                              : CUSTOM_LEGACY_MP3);
                if (!legacy_decoder) {
                    ESP_LOGE(TAG, "Custom %s decoder allocation failed",
                             codec_name(codec));
                    state_set_audio(false, "decoder allocation failed");
                }
            } else
#endif
            {
                uint8_t *resized = realloc(output, DECODE_BUFFER_INITIAL);
                if (!resized) {
                    ESP_LOGE(TAG, "%s PCM buffer allocation failed",
                             codec_name(codec));
                    state_set_audio(false, "PCM allocation failed");
                    vRingbufferReturnItem(s_encoded, packet);
                    continue;
                }
                output = resized;
                output_size = DECODE_BUFFER_INITIAL;
                esp_audio_simple_dec_cfg_t cfg = {
                    .dec_type = simple_decoder_type(codec),
                    .dec_cfg = NULL,
                    .cfg_size = 0,
                    .use_frame_dec = false,
                };
                esp_audio_err_t open_result =
                    esp_audio_simple_dec_open(&cfg, &decoder);
                if (open_result != ESP_AUDIO_ERR_OK) {
                    ESP_LOGE(TAG, "%s decoder open failed: %d",
                             codec_name(codec), open_result);
                    state_set_audio(false, "decoder allocation failed");
                }
            }
        }
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
        if (
#ifdef CONFIG_YORADIO_AAC_DECODER_HELIX
            codec == NATIVE_CODEC_AAC ||
#endif
#if defined(CONFIG_YORADIO_MP3_DECODER_HELIX) || defined(CONFIG_YORADIO_MP3_DECODER_MINIMP3)
            codec == NATIVE_CODEC_MP3 ||
#endif
            false) {
            if (legacy_decoder) {
                custom_legacy_feed_stats_t feed_stats = {0};
                int result = custom_legacy_decoder_feed(
                    legacy_decoder, packet->data, packet->data_size,
                    packet->end_of_stream, custom_legacy_output,
                    &legacy_context, &feed_stats);
                if (result < 0 &&
                    generation == atomic_load(&s_generation)) {
                    ESP_LOGW(TAG, "Custom %s decode error: %d",
                             codec_name(codec), result);
                    state_set_audio(false, "decode failed");
                }
            }
            vRingbufferReturnItem(s_encoded, packet);
            continue;
        }
#endif
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
            raw.consumed = 0;
            esp_audio_err_t result =
                esp_audio_simple_dec_process(decoder, &raw, &frame);
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
                break;
            }
            if (raw.consumed > raw.len) {
                ESP_LOGE(TAG, "%s decoder consumed invalid input size %lu/%lu",
                         codec_name(codec), (unsigned long)raw.consumed,
                         (unsigned long)raw.len);
                break;
            }
            raw.buffer += raw.consumed;
            raw.len -= raw.consumed;
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
            if (!raw.consumed && !frame.decoded_size && !raw.eos) {
                ESP_LOGE(TAG, "%s decoder made no input progress",
                         codec_name(codec));
                break;
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
            audio_level_led_update_peak(0);
            native_audio_output_idle();
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
        audio_level_led_update_pcm(packet->data, packet->data_size,
                                   packet->bits_per_sample,
                                   packet->channels);
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
    ESP_RETURN_ON_ERROR(audio_level_led_init(), TAG,
                        "initialize audio level LED");
    atomic_init(&s_generation, 0);
    s_commands = xQueueCreate(1, sizeof(play_command_t));
    s_encoded = xRingbufferCreate(ENCODED_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
    s_pcm = xRingbufferCreate(PCM_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
    if (!s_commands || !s_encoded || !s_pcm) return ESP_ERR_NO_MEM;
    if (xTaskCreatePinnedToCore(stream_task, "radio_stream", 6144, NULL, 3,
                                NULL, 0) != pdPASS ||
        xTaskCreatePinnedToCore(decoder_task, "audio_decode", 16384, NULL, 5,
                                NULL, 1) != pdPASS ||
        xTaskCreatePinnedToCore(output_task, "audio_output", 4096, NULL, 6,
                                NULL, 1) != pdPASS) {
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
