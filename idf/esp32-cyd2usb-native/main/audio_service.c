#include "audio_service.h"

#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "audio_level_led.h"
#include "audio_completion.h"
#include "board_config.h"
#include "esp_audio_dec_default.h"
#include "esp_audio_simple_dec.h"
#include "esp_audio_simple_dec_default.h"
#include "esp_check.h"
#include "esp_crt_bundle.h"
#include "esp_http_client.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_tls_errors.h"
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
#include "stream_body.h"
#include "stream_probe.h"
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
#include "adaptive_input.h"
#endif

#define STREAM_CHUNK_SIZE 2048
#define DECODE_BUFFER_INITIAL 12288
#define ENCODED_RING_SIZE (16 * 1024)
#define PCM_RING_SIZE (8 * 1024)
#define PCM_PACKET_DATA_SIZE 3072
#define MAX_HTTP_REDIRECTS 5
#define STREAM_READ_TIMEOUT_MS 250

typedef struct {
    uint32_t generation;
    native_codec_t requested_codec;
    char url[512];
} play_command_t;

typedef struct {
    uint32_t generation;
    native_codec_t codec;
    uint16_t data_size;
    uint8_t end_of_stream;
    uint8_t data[];
} encoded_packet_t;

typedef struct {
    uint32_t generation;
    uint32_t sample_rate;
    uint8_t bits_per_sample;
    uint8_t channels;
    uint16_t data_size;
    uint32_t end_of_stream;
    uint8_t data[];
} pcm_packet_t;

static const char *const TAG = "audio";
static native_state_t *s_state;
static QueueHandle_t s_commands;
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
static adaptive_input_t *s_encoded;
#define encoded_acquire adaptive_input_acquire
static BaseType_t encoded_commit(adaptive_input_t *input, encoded_packet_t *packet) {
    return adaptive_input_commit_size(input, packet, sizeof(*packet) + packet->data_size);
}
#define encoded_receive adaptive_input_receive
#define encoded_return adaptive_input_return
#else
static RingbufHandle_t s_encoded;
#define encoded_acquire xRingbufferSendAcquire
#define encoded_commit xRingbufferSendComplete
#define encoded_receive xRingbufferReceive
#define encoded_return vRingbufferReturnItem
#endif
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
static bool s_encoded_control_attached;
#endif
static RingbufHandle_t s_pcm;
static atomic_uint s_generation;
static atomic_uint s_decoder_released_generation;
static atomic_uint s_failed_generation;
static SemaphoreHandle_t s_control_lock;

typedef struct {
    uint32_t interval;
    bool seen, valid;
} stream_headers_t;

typedef struct {
    uint32_t generation;
    native_codec_t codec;
    bool first;
    stream_probe_t probe;
} stream_input_t;

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

static void state_set_audio(uint32_t generation, bool running,
                             const char *format) {
    if (running && atomic_load(&s_failed_generation) == generation) return;
    native_state_set_audio(s_state, generation, running, format);
}

static void fail_generation(uint32_t generation) {
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    if (generation == atomic_load(&s_generation)) {
        atomic_store(&s_failed_generation, generation);
    }
    xSemaphoreGive(s_control_lock);
}

static esp_err_t stream_header_event(esp_http_client_event_t *event) {
    if (event->event_id != HTTP_EVENT_ON_HEADER || !event->user_data ||
        !event->header_key || !event->header_value ||
        strcasecmp(event->header_key, "icy-metaint") != 0) return ESP_OK;
    stream_headers_t *headers = event->user_data;
    uint32_t interval;
    if (!stream_body_interval(event->header_value, &interval) ||
        (headers->seen && headers->interval != interval)) {
        headers->valid = false;
    } else {
        headers->interval = interval;
        headers->seen = true;
    }
    return ESP_OK;
}

static esp_err_t open_stream(esp_http_client_handle_t client,
                             stream_headers_t *headers, int64_t deadline) {
    for (unsigned redirect=0; redirect<=MAX_HTTP_REDIRECTS; ++redirect) {
        *headers = (stream_headers_t){.valid=true};
        int64_t remaining = deadline - esp_timer_get_time();
        if (remaining <= 0) return ESP_ERR_TIMEOUT;
        esp_http_client_set_timeout_ms(client, (int)((remaining + 999) / 1000));
        esp_err_t result = esp_http_client_open(client, 0);
        if (result != ESP_OK) return result;
        remaining = deadline - esp_timer_get_time();
        if (remaining <= 0) return ESP_ERR_TIMEOUT;
        esp_http_client_set_timeout_ms(client, (int)((remaining + 999) / 1000));
        int64_t length = esp_http_client_fetch_headers(client);
        if (esp_timer_get_time() >= deadline) return ESP_ERR_TIMEOUT;
        if (length < 0) return ESP_FAIL;
        int status = esp_http_client_get_status_code(client);
        if (status >= 200 && status < 300) return ESP_OK;
        bool redirected = status == 301 || status == 302 || status == 303 ||
                          status == 307 || status == 308;
        if (!redirected || redirect == MAX_HTTP_REDIRECTS) return ESP_FAIL;
        result = esp_http_client_set_redirection(client);
        esp_http_client_close(client);
        if (result != ESP_OK) return result;
    }
    return ESP_FAIL;
}

static int read_stream(esp_http_client_handle_t client, char *buffer,
                        int size, bool *failed) {
    if (*failed) return ESP_FAIL;
    int received = esp_http_client_read(client, buffer, size);
    int tls_code = 0;
    esp_err_t error = esp_http_client_get_and_clear_last_tls_error(client, &tls_code, NULL);
    bool retryable = tls_code == -ESP_TLS_ERR_SSL_TIMEOUT ||
                     tls_code == -ESP_TLS_ERR_SSL_WANT_READ ||
                     tls_code == -ESP_TLS_ERR_SSL_WANT_WRITE;
    if ((error == ESP_ERR_MBEDTLS_SSL_READ_FAILED && !retryable) ||
        (received < 0 && received != -ESP_ERR_HTTP_EAGAIN)) {
        *failed = true;
        esp_http_client_close(client);
        // Authenticated partial bytes remain valid. Never enter failed TLS again.
        if (received <= 0) return ESP_FAIL;
    }
    return received;
}

static bool send_encoded(uint32_t generation, native_codec_t codec,
                         const uint8_t *data, size_t size, uint8_t eos) {
    size_t packet_size = sizeof(encoded_packet_t) + size;
    encoded_packet_t *packet = NULL;
    for (;;) {
        if (atomic_load(&s_generation) != generation ||
            atomic_load(&s_failed_generation) == generation) return false;
        BaseType_t acquired;
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
        if (eos && s_encoded_control_attached)
            acquired = adaptive_input_acquire_control(s_encoded, (void **)&packet,
                packet_size, pdMS_TO_TICKS(50));
        else
#endif
            acquired = encoded_acquire(s_encoded, (void **)&packet, packet_size,
                                         pdMS_TO_TICKS(50));
        if (acquired == pdTRUE) break;
    }
    packet->generation = generation;
    packet->codec = codec;
    packet->data_size = (uint16_t)size;
    packet->end_of_stream = eos;
    if (size) memcpy(packet->data, data, size);
    return encoded_commit(s_encoded, packet) == pdTRUE;
}

#define STREAM_INPUT_ACTIVE(generation) (atomic_load(&s_generation) == (generation) && atomic_load(&s_failed_generation) != (generation))
#define STREAM_PROVISIONAL_RUNNING false
#ifdef CONFIG_YORADIO_FRAME_ROUTER
#include "stream_encoded_router.h"
#endif
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
#include "stream_start.h"
#endif

static inline void stream_transport_reset(void) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    stream_start_abort();
#endif
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    stream_route_reset();
#endif
}

static inline bool stream_initial_pending(native_codec_t codec, bool first) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    return first && stream_start_eligible(codec);
#else
    (void)first;
    return codec == NATIVE_CODEC_AUTO;
#endif
}

static inline bool stream_confirmation_expired(void) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    return s_stream_start.active && esp_timer_get_time()>=s_stream_start.deadline_us;
#else
    return false;
#endif
}

static bool send_stream_audio(uint32_t generation, native_codec_t *codec,
                              const uint8_t *data, size_t size,
                              bool *first_chunk, stream_probe_t *probe) {
    if (!size) return true;
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    stream_route_context_t route = {.generation = generation, .codec = codec};
#endif
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
        if (stream_start_eligible(*codec) && !s_frame_router.bypass) {
            size_t consumed;
            stream_confirm_result_t result=stream_start_feed(&route,data,size,&consumed,false);
            if (s_stream_start.published) *first_chunk=false;
            // Already confirmed frames remain valid even if the following
            // candidate exhausts its search budget. Never discard that prefix.
            bool flushed=stream_route_flush(&route);
            bool ok=result!=STREAM_CONFIRM_INVALID && flushed;
            if (!ok) {
                stream_route_cancel(&route);stream_start_abort();
                probe->result=STREAM_PROBE_INVALID;return false;
            }
            if (result==STREAM_CONFIRM_MORE) return true;
            stream_start_abort();
            data+=consumed;size-=consumed;
            *first_chunk = false; // stream_start_publish already set the provisional status.
        }
#endif
    if (*first_chunk) {
        if (*codec == NATIVE_CODEC_AUTO) {
            size_t consumed = 0;
            switch (stream_probe_feed(probe, data, size, &consumed)) {
                case STREAM_PROBE_MORE: return true;
                case STREAM_PROBE_MP3: *codec = NATIVE_CODEC_MP3; break;
                case STREAM_PROBE_AAC: *codec = NATIVE_CODEC_AAC; break;
                case STREAM_PROBE_FLAC: *codec = NATIVE_CODEC_FLAC; break;
                case STREAM_PROBE_OGG: *codec = NATIVE_CODEC_OGG; break;
                default: return false;
            }
            state_set_audio(generation, false, codec_name(*codec));
            // Replay the assembled header exactly once, before this read's tail.
#ifdef CONFIG_YORADIO_FRAME_ROUTER
            if (!stream_route_feed(&route, probe->header, probe->used))
#else
            if (!send_encoded(generation, *codec, probe->header, probe->used, false))
#endif
                return false;
            *first_chunk = false;
            data += consumed;
            size -= consumed;
        }
        if (*first_chunk) state_set_audio(generation, false, codec_name(*codec));
        *first_chunk = false;
    }
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    return stream_route_feed(&route, data, size) && stream_route_flush(&route);
#else
    return !size || send_encoded(generation, *codec, data, size, false);
#endif
}

static inline uint8_t finish_stream_audio(uint32_t generation, native_codec_t *codec,
        bool *first_chunk, uint8_t reason) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    if ((s_stream_start.active || (*first_chunk && stream_start_eligible(*codec))) &&
        reason==AUDIO_END_EOF) {
        // EOF rescan can discard the incomplete candidate. Preserve its
        // presence before finalization so truncation is not reported as empty.
        bool incomplete=s_stream_start.skip || s_stream_start.recovering ||
            stream_staging_size(&s_stream_start.window);
        size_t consumed;
        stream_route_context_t route={.generation=generation,.codec=codec};
        stream_confirm_result_t result=stream_start_feed(&route,NULL,0,&consumed,true);
        bool flushed=stream_route_flush(&route);
        if (result==STREAM_CONFIRM_READY && flushed) {
            *first_chunk=false;
        } else {
            stream_route_cancel(&route);
            reason=incomplete || s_stream_start.skip || stream_staging_size(&s_stream_start.window)
                ? AUDIO_END_FRAME_TRUNCATED : AUDIO_END_FORMAT_UNKNOWN;
        }
    }
    stream_start_abort();
#else
    (void)generation;(void)first_chunk;
#endif
    if (*codec==NATIVE_CODEC_AUTO &&
        (reason==AUDIO_END_EOF || reason==AUDIO_END_BUFFER_STALLED)) reason=AUDIO_END_FORMAT_UNKNOWN;
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    reason=stream_route_end(*codec,reason);
#endif
    return reason;
}

static bool stream_audio(void *context, const uint8_t *data, size_t size) {
    stream_input_t *input = context;
    if (input->generation != atomic_load(&s_generation)) return false;
    return send_stream_audio(input->generation, &input->codec, data, size,
                              &input->first, &input->probe);
}

static void stream_title(void *context, const char *title) {
    stream_input_t *input = context;
    native_state_set_title(s_state, input->generation, title);
}

static void stream_task(void *argument) {
    (void)argument;
    uint8_t *buffer = malloc(STREAM_CHUNK_SIZE);
    if (!buffer) {
        ESP_LOGE(TAG, "No memory for stream input buffer");
        vTaskDelete(NULL);
        return;
    }
    while (true) {
        play_command_t command;
        xQueueReceive(s_commands, &command, portMAX_DELAY);
        // Release the old decoder/PCM workspace before the next TLS peak.
        while (atomic_load(&s_generation) == command.generation &&
               atomic_load(&s_decoder_released_generation) != command.generation) {
            vTaskDelay(pdMS_TO_TICKS(1));
        }
        if (atomic_load(&s_generation) != command.generation) continue;
        stream_transport_reset();
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
        // Between connections only; never alter published/leased storage.
        adaptive_input_restore(s_encoded);
#endif
        state_set_audio(command.generation, false, "connecting");

        stream_headers_t headers = {.valid=true};
        esp_http_client_config_t config = {
            .url = command.url,
            .timeout_ms = 10000,
            .buffer_size = STREAM_CHUNK_SIZE,
            .buffer_size_tx = 4096,
            .crt_bundle_attach = esp_crt_bundle_attach,
            .disable_auto_redirect = true,
            .max_redirection_count = MAX_HTTP_REDIRECTS,
            .keep_alive_enable = true,
            .user_agent = "yoRadio-native/1",
            .event_handler = stream_header_event,
            .user_data = &headers,
        };
        esp_http_client_handle_t client = esp_http_client_init(&config);
        if (!client) {
            state_set_audio(command.generation, false, "HTTP allocation failed");
            native_health_stream_failure(command.generation, AUDIO_END_ALLOCATION_FAILED, 0);
            continue;
        }
        esp_http_client_set_header(client, "Icy-MetaData", "1");
        esp_err_t result = open_stream(client, &headers,
            esp_timer_get_time() + INT64_C(10000000));
        if (atomic_load(&s_generation) != command.generation) {
            esp_http_client_cleanup(client);
            continue;
        }
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream open failed: %s", esp_err_to_name(result));
            native_health_stream_failure(command.generation, AUDIO_END_UNAVAILABLE, result);
            state_set_audio(command.generation, false, "connection failed");
            esp_http_client_cleanup(client);
            continue;
        }
        if (!headers.valid) {
            native_health_stream_failure(command.generation, AUDIO_END_FORMAT_UNKNOWN, 0);
            state_set_audio(command.generation, false, "invalid ICY interval");
            esp_http_client_cleanup(client);
            continue;
        }
        esp_http_client_set_timeout_ms(client, STREAM_READ_TIMEOUT_MS);
        // MIME is advisory. Automatic selection waits for actual body bytes.
        stream_input_t input = {.generation=command.generation,
            .codec=command.requested_codec, .first=true};
        stream_body_t body;
        stream_body_init(&body, headers.interval);
        int64_t probe_deadline = esp_timer_get_time() +
            (int64_t)STREAM_PROBE_TIMEOUT_MS * 1000;
        bool read_failed = false;
        uint8_t end_reason = AUDIO_END_EOF;
        while (atomic_load(&s_generation) == command.generation &&
               atomic_load(&s_failed_generation) != command.generation) {
            if (read_failed) { end_reason=AUDIO_END_READ_FAILED; break; }
            if ((stream_initial_pending(input.codec, input.first) &&
                esp_timer_get_time() >= probe_deadline) || stream_confirmation_expired()) {
                end_reason = AUDIO_END_FORMAT_UNKNOWN;
                break;
            }
            int received = read_stream(client, (char *)buffer,
                                       STREAM_CHUNK_SIZE, &read_failed);
            // Stop may occur during the blocking read. Drop its old bytes.
            if (atomic_load(&s_generation) != command.generation) break;
            if (received == -ESP_ERR_HTTP_EAGAIN) {
                vTaskDelay(pdMS_TO_TICKS(1));
                continue;
            }
            if (received < 0) {
                ESP_LOGW(TAG, "Stream read failed");
                end_reason = AUDIO_END_READ_FAILED;
                break;
            }
            if (received == 0) {
                if (esp_http_client_is_complete_data_received(client)) break;
                vTaskDelay(pdMS_TO_TICKS(10));
                continue;
            }
            if (!stream_body_feed(&body, buffer, (size_t)received,
                                   stream_audio, stream_title, &input)) {
                ESP_LOGW(TAG, "Compressed audio buffer stalled");
                end_reason = input.probe.result == STREAM_PROBE_INVALID
                               ? AUDIO_END_FORMAT_UNKNOWN : AUDIO_END_BUFFER_STALLED;
                break;
            }
        }
        if (end_reason == AUDIO_END_EOF && body.metadata_remaining) {
            end_reason = AUDIO_END_METADATA_TRUNCATED;
        }
        end_reason = finish_stream_audio(command.generation, &input.codec,
                                          &input.first, end_reason);
        if (send_encoded(command.generation, input.codec, NULL, 0, end_reason) &&
            end_reason != AUDIO_END_EOF)
            native_health_stream_failure(command.generation, end_reason,
                end_reason == AUDIO_END_READ_FAILED ? ESP_FAIL : 0);
        esp_http_client_close(client);
        esp_http_client_cleanup(client);
    }
}

static bool send_pcm(uint32_t generation,
                     const esp_audio_simple_dec_info_t *info,
                     const uint8_t *data, size_t size) {
    size_t frame_bytes = (size_t)info->channel * info->bits_per_sample / 8U;
    if (!info->bits_per_sample || info->bits_per_sample % 8U ||
        !frame_bytes || frame_bytes > PCM_PACKET_DATA_SIZE ||
        size % frame_bytes) return false;
    while (size) {
        size_t chunk = size > PCM_PACKET_DATA_SIZE ? PCM_PACKET_DATA_SIZE
                                                   : size;
        chunk -= chunk % frame_bytes;
        size_t packet_size = sizeof(pcm_packet_t) + chunk;
        pcm_packet_t *packet = NULL;
        for (;;) {
            if (generation != atomic_load(&s_generation)) return false;
            if (xRingbufferSendAcquire(s_pcm, (void **)&packet, packet_size,
                                       pdMS_TO_TICKS(50)) == pdTRUE) break;
        }
        packet->generation = generation;
        packet->sample_rate = info->sample_rate;
        packet->bits_per_sample = info->bits_per_sample;
        packet->channels = info->channel;
        packet->data_size = (uint16_t)chunk;
        packet->end_of_stream = AUDIO_CONTINUE;
        memcpy(packet->data, data, chunk);
        if (xRingbufferSendComplete(s_pcm, packet) != pdTRUE) return false;
        data += chunk;
        size -= chunk;
    }
    return true;
}

static bool send_pcm_end(uint32_t generation, uint8_t reason) {
    pcm_packet_t *packet = NULL;
    for (;;) {
        if (generation != atomic_load(&s_generation)) return false;
        if (xRingbufferSendAcquire(s_pcm, (void **)&packet, sizeof(*packet),
                                   pdMS_TO_TICKS(50)) == pdTRUE) break;
    }
    memset(packet, 0, sizeof(*packet));
    packet->generation = generation;
    packet->end_of_stream = reason;
    return xRingbufferSendComplete(s_pcm, packet) == pdTRUE;
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
        state_set_audio(context->generation, true, format);
    }
    return send_pcm(context->generation, &context->stream_info, pcm, pcm_size);
}
#endif

static void decoder_release(esp_audio_simple_dec_handle_t *decoder,
                             uint8_t **output, size_t *output_size) {
    if (*decoder) esp_audio_simple_dec_close(*decoder);
    *decoder = NULL;
    free(*output);
    *output = NULL;
    *output_size = 0;
}

#if CONFIG_YORADIO_INPUT_PREFILL_MS > 0
#include "input_prefill.h"
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
    uint32_t failed_generation = 0;
#if CONFIG_YORADIO_INPUT_PREFILL_MS > 0
    bool input_prefilled = false;
#endif

    while (true) {
        uint32_t current_generation = atomic_load(&s_generation);
        if (generation != current_generation ||
            atomic_load(&s_failed_generation) == current_generation) {
            decoder_release(&decoder, &output, &output_size);
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            if (legacy_decoder) custom_legacy_decoder_destroy(legacy_decoder);
            legacy_decoder = NULL;
#endif
            generation = current_generation;
            codec = NATIVE_CODEC_AUTO;
#if CONFIG_YORADIO_INPUT_PREFILL_MS > 0
            input_prefilled = false;
#endif
            atomic_store(&s_decoder_released_generation, generation);
        }
        size_t item_size = 0;
        encoded_packet_t *packet = encoded_receive(
            s_encoded, &item_size, pdMS_TO_TICKS(20));
        if (!packet) continue;
        if (packet->generation != atomic_load(&s_generation) ||
            packet->generation == failed_generation ||
            packet->generation == atomic_load(&s_failed_generation)) {
            encoded_return(s_encoded, packet);
            continue;
        }
        uint8_t end_reason = packet->end_of_stream;
        native_health_decoder_stage_t failure_stage = NATIVE_HEALTH_OPEN;
        int32_t failure_result = 0;
#if CONFIG_YORADIO_INPUT_PREFILL_MS > 0
        if (packet->data_size && !input_prefilled) {
            bool control_replay = false;
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
            control_replay = packet == (const void *)s_start_control;
#endif
            if (!control_replay && !prefill_encoded_input(packet->generation,
                    CONFIG_YORADIO_INPUT_PREFILL_MS)) {
                encoded_return(s_encoded, packet);
                continue;
            }
            input_prefilled = true;
        }
#endif
        if (!packet->data_size && end_reason && !decoder
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            && !legacy_decoder
#endif
        ) goto packet_done;
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
                    end_reason = AUDIO_END_ALLOCATION_FAILED;
                }
            } else
#endif
            {
                uint8_t *resized = realloc(output, DECODE_BUFFER_INITIAL);
                if (!resized) {
                    ESP_LOGE(TAG, "%s PCM buffer allocation failed",
                             codec_name(codec));
                    end_reason = AUDIO_END_ALLOCATION_FAILED;
                    goto packet_done;
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
                    failure_result = (int32_t)open_result;
                    ESP_LOGE(TAG, "%s decoder open failed: %d",
                             codec_name(codec), open_result);
                    end_reason = AUDIO_END_ALLOCATION_FAILED;
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
                    failure_stage = NATIVE_HEALTH_PROCESS;
                    failure_result = result;
                    ESP_LOGW(TAG, "Custom %s decode error: %d",
                             codec_name(codec), result);
                    end_reason = AUDIO_END_DECODE_FAILED;
                }
            }
            goto packet_done;
        }
#endif
        if (!decoder) {
            goto packet_done;
        }
        esp_audio_simple_dec_raw_t raw = {
            .buffer = packet->data,
            .len = packet->data_size,
            .eos = packet->end_of_stream,
        };
        while (raw.len || raw.eos) {
            if (generation != atomic_load(&s_generation)) break;
            esp_audio_simple_dec_out_t frame = {
                .buffer = output,
                .len = output_size,
            };
            raw.consumed = 0;
            esp_audio_err_t result =
                esp_audio_simple_dec_process(decoder, &raw, &frame);
            failure_stage = NATIVE_HEALTH_PROCESS;
            failure_result = (int32_t)result;
            if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                if (frame.needed_size <= output_size) {
                    end_reason = AUDIO_END_DECODE_FAILED;
                    break;
                }
                uint8_t *larger = realloc(output, frame.needed_size);
                if (!larger) {
                    end_reason = AUDIO_END_ALLOCATION_FAILED;
                    break;
                }
                output = larger;
                output_size = frame.needed_size;
                continue;
            }
            if (result != ESP_AUDIO_ERR_OK) {
                ESP_LOGW(TAG, "%s decode error: %d", codec_name(codec),
                         result);
                end_reason = AUDIO_END_DECODE_FAILED;
                break;
            }
            if (raw.consumed > raw.len) {
                ESP_LOGE(TAG, "%s decoder consumed invalid input size %lu/%lu",
                         codec_name(codec), (unsigned long)raw.consumed,
                         (unsigned long)raw.len);
                end_reason = AUDIO_END_DECODE_FAILED;
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
                    state_set_audio(generation, true, format);
                    if (!send_pcm(generation, &info, output,
                                  frame.decoded_size)) {
                        failure_stage = NATIVE_HEALTH_PCM;
                        failure_result = ESP_FAIL;
                        ESP_LOGW(TAG, "PCM buffer stalled");
                        end_reason = AUDIO_END_BUFFER_STALLED;
                        break;
                    }
                }
            }
            if (!raw.consumed && !frame.decoded_size && !raw.eos) {
                ESP_LOGE(TAG, "%s decoder made no input progress",
                         codec_name(codec));
                end_reason = AUDIO_END_DECODE_FAILED;
                break;
            }
            // Ogg may retain several packets: EOS drains until no PCM remains.
            if (raw.eos ? (!raw.len && !frame.decoded_size) : raw.len == 0) break;
        }
packet_done:
        if (end_reason) {
            if (audio_completion_is_terminal(end_reason) &&
                end_reason != packet->end_of_stream &&
                packet->generation == atomic_load(&s_generation))
                native_health_decoder_failure(packet->generation, (uint32_t)packet->codec,
                    failure_stage, failure_result, end_reason, packet->data_size);
            decoder_release(&decoder, &output, &output_size);
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            if (legacy_decoder) custom_legacy_decoder_destroy(legacy_decoder);
            legacy_decoder = NULL;
#endif
            if (audio_completion_is_terminal(end_reason)) {
                failed_generation = packet->generation;
                // Stop reads after a decoder failure, without cancelling its
                // already queued PCM or letting HTTP EOF overwrite the error.
                if (end_reason != packet->end_of_stream &&
                    packet->generation == atomic_load(&s_generation)) {
                    fail_generation(packet->generation);
                }
                send_pcm_end(packet->generation, end_reason);
            }
            codec = NATIVE_CODEC_AUTO;
        }
        encoded_return(s_encoded, packet);
    }
}

static void output_task(void *argument) {
    (void)argument;
    uint32_t sample_rate = 0;
    uint32_t generation = atomic_load(&s_generation);
    uint32_t failed_generation = 0;
    while (true) {
        uint32_t current_generation = atomic_load(&s_generation);
        if (generation != current_generation) {
            native_audio_output_discard_pcm();
            generation = current_generation;
            sample_rate = 0;
        }
        size_t item_size = 0;
        pcm_packet_t *packet = xRingbufferReceive(s_pcm, &item_size,
                                                  pdMS_TO_TICKS(5));
        if (!packet) {
            audio_level_led_update_peak(0);
            native_audio_output_idle();
            continue;
        }
        current_generation = atomic_load(&s_generation);
        if (generation != current_generation) {
            native_audio_output_discard_pcm();
            generation = current_generation;
            sample_rate = 0;
        }
        if (packet->generation != current_generation ||
            packet->generation == failed_generation) {
            vRingbufferReturnItem(s_pcm, packet);
            continue;
        }
        if (packet->end_of_stream) {
            esp_err_t result = native_audio_output_flush_pcm();
            if (result != ESP_OK) native_health_output_failure(packet->generation, NATIVE_HEALTH_OUTPUT_FLUSH, result);
            state_set_audio(packet->generation, false,
                result == ESP_OK ? audio_completion_status(packet->end_of_stream)
                                 : audio_completion_status(AUDIO_END_OUTPUT_FAILED));
            vRingbufferReturnItem(s_pcm, packet);
            continue;
        }
        if (packet->sample_rate != sample_rate) {
            esp_err_t result =
                native_audio_output_configure(packet->sample_rate);
            if (result != ESP_OK) {
                native_health_output_failure(generation, NATIVE_HEALTH_OUTPUT_CONFIGURE, result);
                ESP_LOGE(TAG, "%s %lu Hz setup failed: %s",
                         native_audio_output_name(),
                         (unsigned long)packet->sample_rate,
                         esp_err_to_name(result));
                vRingbufferReturnItem(s_pcm, packet);
                failed_generation = generation;
                fail_generation(generation);
                state_set_audio(generation, false, "audio output failed");
                continue;
            }
            sample_rate = packet->sample_rate;
        }
        if (packet->generation != atomic_load(&s_generation)) {
            vRingbufferReturnItem(s_pcm, packet);
            continue;
        }
        audio_level_led_update_pcm(packet->data, packet->data_size,
                                   packet->bits_per_sample,
                                   packet->channels);
        esp_err_t result = native_audio_output_write_pcm(
            packet->data, packet->data_size, packet->bits_per_sample,
            packet->channels);
        if (result != ESP_OK) {
            native_health_output_failure(generation, NATIVE_HEALTH_OUTPUT_WRITE, result);
            ESP_LOGW(TAG, "%s write failed: %s", native_audio_output_name(),
                     esp_err_to_name(result));
            failed_generation = generation;
            fail_generation(generation);
            state_set_audio(generation, false, "audio output failed");
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
    atomic_init(&s_decoder_released_generation, 0);
    atomic_init(&s_failed_generation, 0);
    s_control_lock = xSemaphoreCreateMutex();
    s_commands = xQueueCreate(1, sizeof(play_command_t));
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    s_encoded = adaptive_input_create(ENCODED_RING_SIZE,
        4 * (sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE),
        sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE);
#else
    s_encoded = xRingbufferCreate(ENCODED_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
#endif
    s_pcm = xRingbufferCreate(PCM_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
    if (!s_control_lock || !s_commands || !s_encoded || !s_pcm) return ESP_ERR_NO_MEM;
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    if (!adaptive_input_attach_control(s_encoded, s_start_control, sizeof(s_start_control)))
        return ESP_ERR_NO_MEM;
    s_start_control_attached = s_encoded_control_attached = true;
#endif
    TaskHandle_t stream_handle=NULL, decoder_handle=NULL, output_handle=NULL;
    if (xTaskCreatePinnedToCore(stream_task, "radio_stream",
                                BOARD_TASK_STACK_RADIO_STREAM, NULL, 3,
                                &stream_handle, 0) != pdPASS ||
        xTaskCreatePinnedToCore(decoder_task, "audio_decode",
                                BOARD_TASK_STACK_AUDIO_DECODER, NULL, 5,
                                &decoder_handle, 1) != pdPASS ||
        xTaskCreatePinnedToCore(output_task, "audio_output",
                                BOARD_TASK_STACK_AUDIO_OUTPUT, NULL, 6,
                                &output_handle, 1) != pdPASS) {
        return ESP_ERR_NO_MEM;
    }
    native_health_track_task(NATIVE_HEALTH_STREAM, stream_handle);
    native_health_track_task(NATIVE_HEALTH_DECODE, decoder_handle);
    native_health_track_task(NATIVE_HEALTH_OUTPUT, output_handle);
    ESP_LOGI(TAG,
             "Pipeline ready: %s, 16 KiB compressed + 8 KiB PCM, free heap %u",
             native_audio_output_name(),
             (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT));
    return ESP_OK;
}

esp_err_t audio_service_play(const char *url, native_codec_t codec) {
    if (!url || !url[0] || strlen(url) >= sizeof(((play_command_t *)0)->url)) {
        return ESP_ERR_INVALID_ARG;
    }
    if (!s_control_lock || !s_commands) return ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    play_command_t command = {
        .generation = atomic_fetch_add(&s_generation, 1) + 1,
        .requested_codec = codec,
    };
    strlcpy(command.url, url, sizeof(command.url));
    native_state_begin_audio(s_state, command.generation, url, "connecting");
    native_state_set_pending(s_state, command.generation, true);
    esp_err_t result = xQueueOverwrite(s_commands, &command) == pdTRUE
                         ? ESP_OK : ESP_FAIL;
    if (result != ESP_OK) native_state_set_audio(s_state, command.generation, false, "command failed");
    xSemaphoreGive(s_control_lock);
    return result;
}

void audio_service_stop(void) {
    if (!s_control_lock) return;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    uint32_t generation = atomic_fetch_add(&s_generation, 1) + 1;
    native_state_begin_audio(s_state, generation, NULL, "stopped");
    xSemaphoreGive(s_control_lock);
}

native_input_health_t audio_service_input_health(void) {
    native_input_health_t result = {0};
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    result.leased = true;
    if (s_encoded) {
        adaptive_input_stats_t stats = adaptive_input_stats(s_encoded);
        result.available = true;
        result.resident=stats.resident; result.minimum=stats.minimum;
        result.target=stats.target; result.limit=stats.limit;
        result.ready=stats.ready; result.reading=stats.reading;
        result.writing=stats.writing; result.released=stats.released;
        size_t ready_headers=(size_t)stats.ready*sizeof(encoded_packet_t);
        size_t reading_headers=(size_t)stats.reading*sizeof(encoded_packet_t);
        result.ready_payload_bytes=(uint32_t)(stats.ready_bytes>=ready_headers
            ? stats.ready_bytes-ready_headers : 0);
        result.reading_payload_bytes=(uint32_t)(stats.reading_bytes>=reading_headers
            ? stats.reading_bytes-reading_headers : 0);
    }
#endif
    return result;
}
