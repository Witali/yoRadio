#include "audio_service.h"

#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>

#include "driver/dac_continuous.h"
#include "esp_audio_dec_default.h"
#include "esp_audio_simple_dec.h"
#include "esp_audio_simple_dec_default.h"
#include "esp_crt_bundle.h"
#include "esp_http_client.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/queue.h"
#include "freertos/ringbuf.h"
#include "freertos/task.h"

#define STREAM_CHUNK_SIZE 2048
#define DECODE_BUFFER_INITIAL 12288
#define ENCODED_RING_SIZE (12 * 1024)
#define PCM_RING_SIZE (12 * 1024)
#define PCM_PACKET_DATA_SIZE 4096

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

static void decoder_task(void *argument) {
    (void)argument;
    esp_audio_dec_register_default();
    esp_audio_simple_dec_register_default();
    uint8_t *output = malloc(DECODE_BUFFER_INITIAL);
    size_t output_size = DECODE_BUFFER_INITIAL;
    esp_audio_simple_dec_handle_t decoder = NULL;
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

static esp_err_t configure_dac(dac_continuous_handle_t *handle,
                               uint32_t sample_rate) {
    if (*handle) {
        dac_continuous_disable(*handle);
        dac_continuous_del_channels(*handle);
        *handle = NULL;
    }
    dac_continuous_config_t config = {
        .chan_mask = DAC_CHANNEL_MASK_CH1,
        .desc_num = 6,
        .buf_size = 1024,
        .freq_hz = sample_rate,
        .offset = 0,
        .clk_src = DAC_DIGI_CLK_SRC_APLL,
        .chan_mode = DAC_CHANNEL_MODE_SIMUL,
    };
    esp_err_t result = dac_continuous_new_channels(&config, handle);
    if (result != ESP_OK) return result;
    result = dac_continuous_enable(*handle);
    if (result != ESP_OK) return result;
    uint8_t silence[1024];
    memset(silence, 0x80, sizeof(silence));
    size_t written;
    return dac_continuous_write(*handle, silence, sizeof(silence), &written,
                                1000);
}

static size_t pcm_to_dac(const pcm_packet_t *packet, uint8_t *output,
                         size_t output_capacity) {
    if (packet->bits_per_sample != 16 || packet->channels == 0) return 0;
    size_t frame_bytes = (size_t)packet->channels * 2;
    size_t frames = packet->data_size / frame_bytes;
    if (frames > output_capacity) frames = output_capacity;
    const int16_t *samples = (const int16_t *)packet->data;
    for (size_t frame = 0; frame < frames; ++frame) {
        int32_t mono = samples[frame * packet->channels];
        if (packet->channels >= 2) {
            mono = (mono + samples[frame * packet->channels + 1]) / 2;
        }
        int32_t value = (mono >> 8) + 128;
        if (value < 0) value = 0;
        if (value > 255) value = 255;
        output[frame] = (uint8_t)value;
    }
    return frames;
}

static void output_task(void *argument) {
    (void)argument;
    dac_continuous_handle_t dac = NULL;
    uint32_t sample_rate = 0;
    uint8_t *dac_data = malloc(PCM_PACKET_DATA_SIZE);
    if (!dac_data) {
        ESP_LOGE(TAG, "No memory for DAC conversion buffer");
        vTaskDelete(NULL);
    }
    while (true) {
        size_t item_size = 0;
        pcm_packet_t *packet = xRingbufferReceive(s_pcm, &item_size,
                                                  pdMS_TO_TICKS(20));
        if (!packet) {
            if (dac) {
                memset(dac_data, 0x80, 256);
                size_t written;
                dac_continuous_write(dac, dac_data, 256, &written, 100);
            }
            continue;
        }
        if (packet->sample_rate != sample_rate) {
            esp_err_t result = configure_dac(&dac, packet->sample_rate);
            if (result != ESP_OK) {
                ESP_LOGE(TAG, "DAC %lu Hz setup failed: %s",
                         (unsigned long)packet->sample_rate,
                         esp_err_to_name(result));
                vRingbufferReturnItem(s_pcm, packet);
                continue;
            }
            sample_rate = packet->sample_rate;
        }
        size_t size = pcm_to_dac(packet, dac_data, PCM_PACKET_DATA_SIZE);
        if (size && dac) {
            size_t written;
            dac_continuous_write(dac, dac_data, size, &written, 1000);
        }
        vRingbufferReturnItem(s_pcm, packet);
    }
}

esp_err_t audio_service_start(native_state_t *state) {
    s_state = state;
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
    ESP_LOGI(TAG, "Pipeline ready: 12 KiB compressed + 12 KiB PCM, free heap %u",
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
