#include "audio_service.h"

#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "audio_level_led.h"
#include "audio_completion.h"
#include "board_config.h"
#include "decoder_registration.h"
#include "esp_audio_simple_dec.h"
#include "esp_check.h"
#include "esp_crt_bundle.h"
#include "esp_http_client.h"
#include "http_request_buffer.h"
#include "native_tls_rx_reserve.h"
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
#include "network_service.h"
#include "stream_body.h"
#include "stream_bitrate.h"
#include "stream_probe.h"
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
#include "native_input_reclaim.h"
#endif
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
#include "custom_flac_adapter.h"
#endif
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
    bool maintenance;
    bool restore;
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
enum { AUDIO_START_OFF, AUDIO_STARTING, AUDIO_START_READY };
static atomic_uint s_start_state;
static uint8_t *s_stream_buffer;
// Output/LED initialization has process lifetime. Retain successful setup
// across pipeline-allocation retries instead of allocating driver buffers twice.
static bool s_output_initialized, s_led_initialized;

enum { MAINTENANCE_OFF, MAINTENANCE_REQUESTED, MAINTENANCE_HELD,
       MAINTENANCE_ABORTING, MAINTENANCE_END_RESUME, MAINTENANCE_END_STOP };
enum { MAINTENANCE_STREAM = 1U, MAINTENANCE_DECODER = 2U,
       MAINTENANCE_OUTPUT = 4U, MAINTENANCE_ALL = 7U };
static atomic_uint s_maintenance_phase;
static atomic_uint s_maintenance_acks;
static atomic_int s_maintenance_error;
static atomic_bool s_maintenance_waiter;
static portMUX_TYPE s_maintenance_token_lock = portMUX_INITIALIZER_UNLOCKED;
// Control lock owns intent/token data. Owners only inspect the atomic phase
// and acknowledgements; they never retain the HTTP caller's token/storage.
static uint64_t s_maintenance_epoch;
static play_command_t s_last_command;
static bool s_last_command_valid, s_maintenance_resume;

static bool maintenance_active(void) {
    return atomic_load(&s_maintenance_phase) != MAINTENANCE_OFF;
}

static bool maintenance_acked(unsigned bits) {
    return (atomic_load(&s_maintenance_acks) & bits) == bits;
}

// State lock is held. The caller has validated this maintenance generation.
static void maintenance_state_locked(uint32_t generation, bool quiet) {
    esp_err_t error = atomic_load(&s_maintenance_error);
    const char *status = error == ESP_ERR_TIMEOUT
        ? (quiet ? "maintenance timeout; cleanup complete" : "maintenance timeout; cleanup pending")
        : error != ESP_OK
        ? (quiet ? "maintenance failed; cleanup complete" : "maintenance failed; cleanup pending")
        : (quiet ? "maintenance paused" : "maintenance cleanup pending");
    native_state_begin_audio_locked(s_state, generation, NULL, status);
    s_state->audio_pending = !quiet;
    s_state->audio_failed = error != ESP_OK;
}

static void maintenance_publish_state(uint32_t generation, bool quiet,
                                       TickType_t timeout) {
    portENTER_CRITICAL(&s_maintenance_token_lock);
    uint64_t epoch = s_maintenance_epoch;
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    if (!maintenance_active() || generation != atomic_load(&s_generation) ||
        xSemaphoreTake(s_state->lock, timeout) != pdTRUE) return;
    portENTER_CRITICAL(&s_maintenance_token_lock);
    bool current = epoch == s_maintenance_epoch && maintenance_active() &&
                   generation == atomic_load(&s_generation);
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    // OFF publication also takes the state lock, so it cannot race this
    // recheck/write and leave a late cleanup status over resumed playback.
    if (current) maintenance_state_locked(generation, quiet);
    xSemaphoreGive(s_state->lock);
}

// All owners are quiescent before this runs, so the queued restore cannot be
// consumed until OFF is published. No blocking state/NVS/driver calls here.
static esp_err_t maintenance_finish_locked(bool resume) {
    if (xSemaphoreTake(s_state->lock, 0) != pdTRUE) return ESP_ERR_TIMEOUT;
    if (resume && s_maintenance_resume && s_last_command_valid) {
        play_command_t command = s_last_command;
        command.generation = atomic_load(&s_generation) + 1U;
        command.maintenance = false;
        command.restore = true;
        if (xQueueOverwrite(s_commands, &command) != pdTRUE) {
            xSemaphoreGive(s_state->lock);
            return ESP_FAIL;
        }
        maintenance_state_locked(atomic_load(&s_generation), true);
        // This is an accepted pending Play even before the stream owner
        // consumes it. A second maintenance must retain that resume intent.
        s_state->audio_generation = command.generation;
        s_state->audio_pending = true;
        s_state->audio_failed = false;
        const char *status = atomic_load(&s_maintenance_error) == ESP_ERR_TIMEOUT
            ? "maintenance timeout; resume pending"
            : atomic_load(&s_maintenance_error) != ESP_OK
            ? "maintenance failed; resume pending" : "maintenance resume pending";
        strlcpy(s_state->stream_format, status, sizeof(s_state->stream_format));
        atomic_store(&s_generation, command.generation);
        s_last_command = command;
        network_service_audio_accept(command.generation, true);
    } else {
        maintenance_state_locked(atomic_load(&s_generation), true);
        if (atomic_load(&s_maintenance_error) == ESP_OK)
            strlcpy(s_state->stream_format, "stopped", sizeof(s_state->stream_format));
    }
    native_audio_output_request_pause(false);
    portENTER_CRITICAL(&s_maintenance_token_lock);
    atomic_store(&s_maintenance_phase, MAINTENANCE_OFF);
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    xSemaphoreGive(s_state->lock);
    return ESP_OK;
}

static void maintenance_try_abort(void) {
    unsigned phase = atomic_load(&s_maintenance_phase);
    if ((phase != MAINTENANCE_ABORTING && phase != MAINTENANCE_END_RESUME &&
         phase != MAINTENANCE_END_STOP) ||
        atomic_load(&s_maintenance_waiter) || !maintenance_acked(MAINTENANCE_ALL) ||
        xSemaphoreTake(s_control_lock, 0) != pdTRUE) return;
    phase = atomic_load(&s_maintenance_phase);
    if ((phase == MAINTENANCE_ABORTING || phase == MAINTENANCE_END_RESUME ||
         phase == MAINTENANCE_END_STOP) && !atomic_load(&s_maintenance_waiter) &&
        maintenance_acked(MAINTENANCE_ALL))
        (void)maintenance_finish_locked(phase != MAINTENANCE_END_STOP);
    xSemaphoreGive(s_control_lock);
}

static void maintenance_ack(unsigned bit) {
    atomic_fetch_or(&s_maintenance_acks, bit);
    maintenance_try_abort();
}

static void maintenance_park(uint32_t generation) {
    // A subsequent maintenance can start before a parked owner observes OFF.
    // The new generation must make that owner leave and acknowledge anew.
    while (maintenance_active() && atomic_load(&s_generation) == generation) {
        maintenance_try_abort();
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

static void maintenance_output_error(esp_err_t result) {
    int expected = ESP_OK;
    atomic_compare_exchange_strong(&s_maintenance_error, &expected, result);
    unsigned phase = MAINTENANCE_REQUESTED;
    atomic_compare_exchange_strong(&s_maintenance_phase, &phase, MAINTENANCE_ABORTING);
}

typedef struct {
    uint32_t interval;
    uint32_t bitrate_kbps;
    bool seen, valid;
} stream_headers_t;

typedef struct {
    uint32_t generation;
    native_codec_t codec;
    bool first;
    stream_probe_t probe;
    stream_bitrate_meter_t bitrate;
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

static uint32_t s_decoder_bitrate_generation, s_decoder_bitrate_bps;
static int64_t s_decoder_bitrate_updated_us;

static void state_set_decoder_bitrate(uint32_t generation, uint32_t bitrate_bps) {
    if (!bitrate_bps || generation != atomic_load(&s_generation)) return;
    if (s_decoder_bitrate_generation != generation) {
        s_decoder_bitrate_generation = generation;
        s_decoder_bitrate_bps = 0;
        s_decoder_bitrate_updated_us = 0;
    }
    if (bitrate_bps == s_decoder_bitrate_bps) return;
    int64_t now = esp_timer_get_time();
    if (s_decoder_bitrate_bps && now-s_decoder_bitrate_updated_us < 1000000LL) return;
    s_decoder_bitrate_bps = bitrate_bps;
    s_decoder_bitrate_updated_us = now;
    native_state_set_bitrate(s_state,generation,(uint32_t)(((uint64_t)bitrate_bps+500U)/1000U));
}

static bool publish_stream_info(uint32_t generation, native_codec_t codec,
                                 const esp_audio_simple_dec_info_t *info) {
    if (generation != atomic_load(&s_generation) ||
        generation == atomic_load(&s_failed_generation) || !info->sample_rate ||
        !native_audio_output_supports_pcm(info->bits_per_sample, info->channel)) return false;
    native_stream_info_t description = {
        .codec=codec_name(codec), .sample_rate_hz=info->sample_rate,
        .channels=info->channel, .bits_per_sample=info->bits_per_sample,
        .pcm_sample_rate_hz=info->sample_rate, .pcm_channels=info->channel,
        // The public AAC API confirms decoder PCM, not nominal HE/PS layout.
        .format_is_pcm=codec==NATIVE_CODEC_AAC,
    };
    native_state_set_stream_info(s_state,generation,&description);
    state_set_decoder_bitrate(generation,info->bitrate);
    return generation == atomic_load(&s_generation) &&
           generation != atomic_load(&s_failed_generation);
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
        !event->header_key || !event->header_value) return ESP_OK;
    stream_headers_t *headers = event->user_data;
    if (strcasecmp(event->header_key,"icy-br") == 0) {
        uint32_t bitrate;
        if (!headers->bitrate_kbps && stream_body_interval(event->header_value,&bitrate) && bitrate)
            headers->bitrate_kbps = bitrate;
        return ESP_OK; // Optional hint; malformed values never reject audio.
    }
    if (strcasecmp(event->header_key,"icy-metaint") != 0) return ESP_OK;
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
        if (status >= 200 && status < 300) {
#ifdef CONFIG_YORADIO_HTTP_REQUEST_BUFFER_RELEASE
            if (headers->valid) {
                esp_err_t released = yoradio_http_client_release_request_buffer(client);
                if (released != ESP_OK)
                    ESP_LOGD(TAG, "HTTP request buffer retained: %s", esp_err_to_name(released));
            }
#endif
            return ESP_OK;
        }
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
    if (!send_stream_audio(input->generation, &input->codec, data, size,
                             &input->first, &input->probe)) return false;
    uint32_t kbps = stream_bitrate_meter_add(&input->bitrate, size, esp_timer_get_time());
    if (kbps) native_state_publish_bitrate(s_state,input->generation,kbps,NATIVE_BITRATE_MEASURED);
    return true;
}

static void stream_title(void *context, const char *title) {
    stream_input_t *input = context;
    native_state_set_title(s_state, input->generation, title);
}

static void stream_task(void *argument) {
    (void)argument;
    uint8_t *buffer = s_stream_buffer;
    while (true) {
        if (maintenance_active()) {
            // Only this owner can cancel producer staging. HTTP cleanup on
            // every exit below has completed before the stream ack.
            uint32_t parked_generation = atomic_load(&s_generation);
            stream_transport_reset();
            maintenance_ack(MAINTENANCE_STREAM);
            maintenance_park(parked_generation);
            continue;
        }
        play_command_t command;
        if (xQueueReceive(s_commands, &command, pdMS_TO_TICKS(50)) != pdTRUE)
            continue;
        if (command.maintenance || maintenance_active()) continue;
        // Release the old decoder/PCM workspace before the next TLS peak.
        while (atomic_load(&s_generation) == command.generation &&
               atomic_load(&s_decoder_released_generation) != command.generation) {
            vTaskDelay(pdMS_TO_TICKS(1));
        }
        if (atomic_load(&s_generation) != command.generation) {
            network_service_audio_finish(command.generation);
            continue;
        }
        network_service_audio_receive(command.generation);
        stream_transport_reset();
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
        // Between connections only; never alter published/leased storage.
        adaptive_input_restore(s_encoded);
#endif
        if (command.restore)
            native_state_begin_audio(s_state, command.generation, NULL, "connecting");
        native_state_set_connecting(s_state, command.generation);

        stream_headers_t headers = {.valid=true};
        esp_http_client_config_t config = {
            .url = command.url,
            .timeout_ms = 10000,
            .buffer_size = STREAM_CHUNK_SIZE,
            .buffer_size_tx = 4096,
            .crt_bundle_attach = native_tls_rx_reserve_crt_bundle_attach,
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
            network_service_audio_finish(command.generation);
            continue;
        }
        esp_http_client_set_header(client, "Icy-MetaData", "1");
        esp_err_t result = open_stream(client, &headers,
            esp_timer_get_time() + INT64_C(10000000));
        if (atomic_load(&s_generation) != command.generation) {
            esp_http_client_cleanup(client);
            network_service_audio_finish(command.generation);
            continue;
        }
        if (result != ESP_OK) {
            ESP_LOGE(TAG, "Stream open failed: %s", esp_err_to_name(result));
            native_health_stream_failure(command.generation, AUDIO_END_UNAVAILABLE, result);
            state_set_audio(command.generation, false, "connection failed");
            esp_http_client_cleanup(client);
            network_service_audio_finish(command.generation);
            continue;
        }
        if (!headers.valid) {
            native_health_stream_failure(command.generation, AUDIO_END_FORMAT_UNKNOWN, 0);
            state_set_audio(command.generation, false, "invalid ICY interval");
            esp_http_client_cleanup(client);
            network_service_audio_finish(command.generation);
            continue;
        }
        native_state_publish_bitrate(s_state,command.generation,headers.bitrate_kbps,NATIVE_BITRATE_ICY);
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
        network_service_audio_finish(command.generation);
    }
}

static bool send_pcm(uint32_t generation,
                     const esp_audio_simple_dec_info_t *info,
                     const uint8_t *data, size_t size) {
    size_t frame_bytes = (size_t)info->channel * info->bits_per_sample / 8U;
    if (!native_audio_output_supports_pcm(info->bits_per_sample, info->channel) ||
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
    native_codec_t codec;
    esp_audio_simple_dec_info_t stream_info;
} custom_legacy_output_context_t;

static bool custom_legacy_output(void *user, const custom_legacy_info_t *info,
                                 const uint8_t *pcm, size_t pcm_size) {
    custom_legacy_output_context_t *context = user;
    if (context->generation != atomic_load(&s_generation)) return false;
    context->stream_info = (esp_audio_simple_dec_info_t){
            .sample_rate = info->sample_rate,
            .bits_per_sample = info->bits_per_sample,
            .channel = info->channels,
            .bitrate = info->bitrate,
    };
    if (!publish_stream_info(context->generation,context->codec,&context->stream_info)) return false;
    return send_pcm(context->generation, &context->stream_info, pcm, pcm_size);
}
#endif

#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
typedef struct {
    uint32_t generation;
} custom_flac_output_context_t;

static bool custom_flac_output(void *user, const custom_flac_info_t *info,
                               const uint8_t *pcm, size_t pcm_size) {
    custom_flac_output_context_t *context = user;
    if (context->generation != atomic_load(&s_generation) ||
        context->generation == atomic_load(&s_failed_generation) ||
        !info->sample_rate || info->bits_per_sample < 4 ||
        info->bits_per_sample > 24 || info->channels > 2 || info->pcm_bits_per_sample != 16 ||
        !native_audio_output_supports_pcm(info->pcm_bits_per_sample, info->channels))
        return false;
    native_stream_info_t description = {
        .codec = "FLAC", .sample_rate_hz = info->sample_rate,
        .channels = info->channels, .bits_per_sample = info->bits_per_sample,
        .pcm_sample_rate_hz = info->sample_rate, .pcm_channels = info->channels,
    };
    native_state_set_stream_info(s_state, context->generation, &description);
    state_set_decoder_bitrate(context->generation, info->bitrate);
    esp_audio_simple_dec_info_t pcm_info = {
        .sample_rate = info->sample_rate,
        .bits_per_sample = info->pcm_bits_per_sample,
        .channel = info->channels,
    };
    return send_pcm(context->generation, &pcm_info, pcm, pcm_size);
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
    uint8_t *output = NULL;
    size_t output_size = 0;
    esp_audio_simple_dec_handle_t decoder = NULL;
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
    // The shared core has process-global sample workspace. This task is its
    // sole owner; destroy it before opening any successor or publishing ACK.
    custom_flac_decoder_t *flac_decoder = NULL;
#endif
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
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
            if (flac_decoder) custom_flac_decoder_destroy(flac_decoder);
            flac_decoder = NULL;
#endif
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
        if (!packet) {
            // Stream ack is the producer barrier: after it, an empty FIFO
            // cannot be followed by an old late commit or a control packet.
            if (maintenance_active() && maintenance_acked(MAINTENANCE_STREAM) &&
                generation == atomic_load(&s_generation)) {
                decoder_release(&decoder, &output, &output_size);
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
                if (flac_decoder) custom_flac_decoder_destroy(flac_decoder);
                flac_decoder = NULL;
#endif
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
                if (legacy_decoder) custom_legacy_decoder_destroy(legacy_decoder);
                legacy_decoder = NULL;
#endif
                maintenance_ack(MAINTENANCE_DECODER);
                maintenance_park(generation);
            }
            continue;
        }
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
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
            && !flac_decoder
#endif
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            && !legacy_decoder
#endif
        ) goto packet_done;
        if (packet->generation != generation || packet->codec != codec) {
            if (decoder) esp_audio_simple_dec_close(decoder);
            decoder = NULL;
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
            if (flac_decoder) custom_flac_decoder_destroy(flac_decoder);
            flac_decoder = NULL;
#endif
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            if (legacy_decoder) custom_legacy_decoder_destroy(legacy_decoder);
            legacy_decoder = NULL;
#endif
            generation = packet->generation;
            codec = packet->codec;
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
            legacy_context = (custom_legacy_output_context_t){
                .generation = generation,
                .codec = codec,
            };
#endif
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
            if (codec == NATIVE_CODEC_FLAC) {
                free(output);
                output = NULL;
                output_size = 0;
                flac_decoder = custom_flac_decoder_create();
                if (!flac_decoder) {
                    ESP_LOGE(TAG, "Custom FLAC decoder allocation failed");
                    end_reason = AUDIO_END_ALLOCATION_FAILED;
                }
            } else
#endif
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
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
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
        if (codec == NATIVE_CODEC_FLAC) {
            if (flac_decoder) {
                custom_flac_feed_stats_t feed_stats = {0};
                custom_flac_output_context_t context = {.generation = generation};
                int result = custom_flac_decoder_feed(
                    flac_decoder, packet->data, packet->data_size,
                    packet->end_of_stream, custom_flac_output, &context, &feed_stats);
                if (result < 0 && generation == atomic_load(&s_generation)) {
                    failure_stage = NATIVE_HEALTH_PROCESS;
                    failure_result = result;
                    end_reason = AUDIO_END_DECODE_FAILED;
                }
            }
            goto packet_done;
        }
#endif
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
            if (frame.decoded_size > output_size) {
                failure_result = ESP_FAIL;
                end_reason = AUDIO_END_DECODE_FAILED;
                break;
            }
            raw.buffer += raw.consumed;
            raw.len -= raw.consumed;
            if (frame.decoded_size) {
                esp_audio_simple_dec_info_t info = {0};
                esp_audio_err_t info_result = esp_audio_simple_dec_get_info(decoder, &info);
                if (info_result != ESP_AUDIO_ERR_OK || !publish_stream_info(generation,codec,&info)) {
                    failure_stage = NATIVE_HEALTH_INFO;
                    failure_result = info_result == ESP_AUDIO_ERR_OK ? ESP_FAIL : (int32_t)info_result;
                    end_reason = AUDIO_END_DECODE_FAILED;
                    break;
                }
                if (!send_pcm(generation, &info, output,frame.decoded_size)) {
                    failure_stage = NATIVE_HEALTH_PCM;
                    failure_result = ESP_FAIL;
                    ESP_LOGW(TAG, "PCM buffer stalled");
                    end_reason = AUDIO_END_BUFFER_STALLED;
                    break;
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
#ifdef CONFIG_YORADIO_FLAC_DECODER_CUSTOM
            if (flac_decoder) custom_flac_decoder_destroy(flac_decoder);
            flac_decoder = NULL;
#endif
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
    uint32_t status_generation = 0;
    esp_err_t maintenance_status = ESP_OK;
    while (true) {
        uint32_t current_generation = atomic_load(&s_generation);
        esp_err_t error = atomic_load(&s_maintenance_error);
        if (maintenance_active() && (status_generation != current_generation ||
                                     maintenance_status != error)) {
            maintenance_publish_state(current_generation, false, portMAX_DELAY);
            status_generation = current_generation;
            maintenance_status = error;
        }
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
            if (maintenance_active()) {
                if (maintenance_acked(MAINTENANCE_DECODER) &&
                    generation == atomic_load(&s_generation)) {
                    esp_err_t result = native_audio_output_pause();
                    if (result != ESP_OK) {
                        maintenance_output_error(result);
                        vTaskDelay(pdMS_TO_TICKS(20));
                        continue;
                    }
                    sample_rate = 0;
                    maintenance_publish_state(generation, true, portMAX_DELAY);
                    if (generation != atomic_load(&s_generation)) continue;
                    maintenance_ack(MAINTENANCE_OUTPUT);
                    maintenance_park(generation);
                }
                continue;
            }
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
            if (result != ESP_OK && !maintenance_active()) {
                native_health_output_failure(packet->generation, NATIVE_HEALTH_OUTPUT_FLUSH, result);
                fail_generation(packet->generation);
                native_state_fail_audio(s_state,packet->generation,audio_completion_status(AUDIO_END_OUTPUT_FAILED));
            }
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
                if (maintenance_active()) {
                    vRingbufferReturnItem(s_pcm, packet);
                    continue;
                }
                native_health_output_failure(generation, NATIVE_HEALTH_OUTPUT_CONFIGURE, result);
                ESP_LOGE(TAG, "%s %lu Hz setup failed: %s",
                         native_audio_output_name(),
                         (unsigned long)packet->sample_rate,
                         esp_err_to_name(result));
                vRingbufferReturnItem(s_pcm, packet);
                failed_generation = generation;
                fail_generation(generation);
                native_state_fail_audio(s_state,generation,"audio output failed");
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
        if (result != ESP_OK && !maintenance_active()) {
            native_health_output_failure(generation, NATIVE_HEALTH_OUTPUT_WRITE, result);
            ESP_LOGW(TAG, "%s write failed: %s", native_audio_output_name(),
                     esp_err_to_name(result));
            failed_generation = generation;
            fail_generation(generation);
            native_state_fail_audio(s_state,generation,"audio output failed");
        }
        vRingbufferReturnItem(s_pcm, packet);
    }
}

typedef struct {
    TaskFunction_t run;
    const char *name;
    uint32_t stack_size;
    UBaseType_t priority;
    BaseType_t core;
} pipeline_task_t;

static void gated_pipeline_task(void *argument) {
    const pipeline_task_t *task = argument;
    // A task may run immediately on either core after creation. Until notified
    // it owns no pipeline resources, so failed startup can safely delete it.
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    task->run(NULL);
    vTaskDelete(NULL);
}

static void discard_pipeline_startup(TaskHandle_t *tasks, bool codecs_registered) {
    for (unsigned i = 0; i < 3; ++i) {
        if (tasks[i]) vTaskDelete(tasks[i]);
    }
    if (s_pcm) vRingbufferDelete(s_pcm);
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    if (s_encoded) adaptive_input_destroy(s_encoded);
#else
    if (s_encoded) vRingbufferDelete(s_encoded);
#endif
    if (s_commands) vQueueDelete(s_commands);
    if (s_control_lock) vSemaphoreDelete(s_control_lock);
    free(s_stream_buffer);
    s_pcm = NULL;
    s_encoded = NULL;
    s_commands = NULL;
    s_control_lock = NULL;
    s_stream_buffer = NULL;
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    s_start_control_attached = s_encoded_control_attached = false;
#endif
    if (codecs_registered) decoder_unregister_codecs();
    s_state = NULL;
    // Last publication: readers seeing OFF cannot observe freed resources.
    atomic_store(&s_start_state, AUDIO_START_OFF);
}

esp_err_t audio_service_start(native_state_t *state) {
    if (!state || !state->lock) return ESP_ERR_INVALID_ARG;
    unsigned expected = AUDIO_START_OFF;
    if (!atomic_compare_exchange_strong(&s_start_state, &expected, AUDIO_STARTING))
        return ESP_ERR_INVALID_STATE;
    static const pipeline_task_t task_config[3] = {
        {stream_task, "radio_stream", BOARD_TASK_STACK_RADIO_STREAM, 3, 0},
        {decoder_task, "audio_decode", BOARD_TASK_STACK_AUDIO_DECODER, 5, 1},
        {output_task, "audio_output", BOARD_TASK_STACK_AUDIO_OUTPUT, 6, 1},
    };
    TaskHandle_t tasks[3] = {NULL};
    bool codecs_registered = false;
    esp_err_t result = ESP_ERR_NO_MEM;
    s_state = state;
    atomic_init(&s_generation, 0);
    atomic_init(&s_decoder_released_generation, 0);
    atomic_init(&s_failed_generation, 0);
    s_stream_buffer = malloc(STREAM_CHUNK_SIZE);
    if (!s_stream_buffer) goto failed;
    s_control_lock = xSemaphoreCreateMutex();
    if (!s_control_lock) goto failed;
    s_commands = xQueueCreate(1, sizeof(play_command_t));
    if (!s_commands) goto failed;
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    s_encoded = adaptive_input_create(ENCODED_RING_SIZE,
        4 * (sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE),
        sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE);
#else
    s_encoded = xRingbufferCreate(ENCODED_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
#endif
    if (!s_encoded) goto failed;
    s_pcm = xRingbufferCreate(PCM_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
    if (!s_pcm) goto failed;
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    if (!adaptive_input_attach_control(s_encoded, s_start_control, sizeof(s_start_control)))
        goto failed;
    s_start_control_attached = s_encoded_control_attached = true;
#endif
    esp_audio_err_t registration = decoder_register_codecs();
    if (registration != ESP_AUDIO_ERR_OK) {
        ESP_LOGE(TAG, "Decoder registration failed: %d", registration);
        result = registration == ESP_AUDIO_ERR_MEM_LACK ? ESP_ERR_NO_MEM : ESP_FAIL;
        goto failed;
    }
    codecs_registered = true;
    for (unsigned i = 0; i < 3; ++i) {
        if (xTaskCreatePinnedToCore(gated_pipeline_task, task_config[i].name,
                task_config[i].stack_size, (void *)&task_config[i], task_config[i].priority,
                &tasks[i], task_config[i].core) != pdPASS) goto failed;
    }
    if (!s_output_initialized) {
        result = native_audio_output_init();
        if (result != ESP_OK) goto failed;
        s_output_initialized = true;
    }
    if (!s_led_initialized) {
        result = audio_level_led_init();
        if (result != ESP_OK) goto failed;
        s_led_initialized = true;
    }
    native_health_track_task(NATIVE_HEALTH_STREAM, tasks[0]);
    native_health_track_task(NATIVE_HEALTH_DECODE, tasks[1]);
    native_health_track_task(NATIVE_HEALTH_OUTPUT, tasks[2]);
    atomic_store(&s_start_state, AUDIO_START_READY);
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    // All fallible startup work has committed. A rejected optional binding
    // must not roll back READY or destroy a pool published to another task.
    if (!native_input_reclaim_bind(s_encoded))
        ESP_LOGW(TAG, "TLS input reclamation not attached");
#endif
    for (unsigned i = 0; i < 3; ++i) xTaskNotifyGive(tasks[i]);
    ESP_LOGI(TAG,
             "Pipeline ready: %s, 16 KiB compressed + 8 KiB PCM, free heap %u",
             native_audio_output_name(),
             (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT));
    return ESP_OK;
failed:
    discard_pipeline_startup(tasks, codecs_registered);
    return result;
}

esp_err_t audio_service_play(const char *url, native_codec_t codec) {
    if (!url || !url[0] || strlen(url) >= sizeof(((play_command_t *)0)->url)) {
        return ESP_ERR_INVALID_ARG;
    }
    if (atomic_load(&s_start_state) != AUDIO_START_READY) return ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    if (maintenance_active()) {
        xSemaphoreGive(s_control_lock);
        return ESP_ERR_INVALID_STATE;
    }
    play_command_t command = {
        .generation = atomic_fetch_add(&s_generation, 1) + 1,
        .requested_codec = codec,
    };
    network_service_audio_accept(command.generation, true);
    strlcpy(command.url, url, sizeof(command.url));
    native_state_begin_audio(s_state, command.generation, url, "connecting");
    native_state_set_connecting(s_state, command.generation);
    esp_err_t result = xQueueOverwrite(s_commands, &command) == pdTRUE
                         ? ESP_OK : ESP_FAIL;
    s_last_command_valid = result == ESP_OK;
    if (s_last_command_valid) s_last_command = command;
    if (result != ESP_OK) {
        native_state_set_audio(s_state, command.generation, false, "command failed");
        network_service_audio_finish(command.generation);
    }
    xSemaphoreGive(s_control_lock);
    return result;
}

void audio_service_stop(void) {
    if (atomic_load(&s_start_state) != AUDIO_START_READY) return;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    if (maintenance_active()) {
        s_maintenance_resume = false;
        xSemaphoreGive(s_control_lock);
        return;
    }
    uint32_t generation = atomic_fetch_add(&s_generation, 1) + 1;
    network_service_audio_accept(generation, false);
    native_state_begin_audio(s_state, generation, NULL, "stopped");
    xSemaphoreGive(s_control_lock);
}

static TickType_t maintenance_remaining_ticks(int64_t deadline) {
    int64_t remaining = deadline - esp_timer_get_time();
    if (remaining <= 0) return 0;
    uint64_t ms = ((uint64_t)remaining + 999U) / 1000U;
    uint64_t ticks = (ms * configTICK_RATE_HZ + 999U) / 1000U;
    // portMAX_DELAY is never an allowed maintenance API wait.
    if (ticks >= portMAX_DELAY) ticks = portMAX_DELAY - 1U;
    return (TickType_t)ticks;
}

esp_err_t audio_service_maintenance_begin(uint32_t timeout_ms,
                                         audio_maintenance_token_t *token) {
    if (!token) return ESP_ERR_INVALID_ARG;
    token->epoch = 0;
    if (!timeout_ms) return ESP_ERR_INVALID_ARG;
    if (atomic_load(&s_start_state) != AUDIO_START_READY)
        return ESP_ERR_INVALID_STATE;
    int64_t deadline = esp_timer_get_time() + (int64_t)timeout_ms * 1000;
    if (xSemaphoreTake(s_control_lock, maintenance_remaining_ticks(deadline)) != pdTRUE)
        return ESP_ERR_TIMEOUT;
    if (maintenance_active() || s_maintenance_epoch == UINT64_MAX) {
        xSemaphoreGive(s_control_lock);
        return ESP_ERR_INVALID_STATE;
    }
    // A failed snapshot must be distinguishable from a stopped stream. Do
    // not use native_state_snapshot's silent zero-on-timeout result here.
    if (!s_state->lock || xSemaphoreTake(s_state->lock,
            maintenance_remaining_ticks(deadline)) != pdTRUE) {
        xSemaphoreGive(s_control_lock);
        return ESP_ERR_TIMEOUT;
    }
    uint32_t generation = atomic_load(&s_generation);
    bool resume = s_last_command_valid && s_last_command.generation == generation &&
        s_state->audio_generation == generation && !s_state->audio_failed &&
        (s_state->audio_running || s_state->audio_pending);
    if (esp_timer_get_time() >= deadline) {
        xSemaphoreGive(s_state->lock);
        xSemaphoreGive(s_control_lock);
        return ESP_ERR_TIMEOUT;
    }
    s_maintenance_resume = resume;
    atomic_store(&s_maintenance_acks, 0);
    atomic_store(&s_maintenance_error, ESP_OK);
    atomic_store(&s_maintenance_waiter, true);
    atomic_store(&s_generation, generation + 1U);
    portENTER_CRITICAL(&s_maintenance_token_lock);
    uint64_t epoch = ++s_maintenance_epoch;
    atomic_store(&s_maintenance_phase, MAINTENANCE_REQUESTED);
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    network_service_audio_accept(generation + 1U, false);
    // Cancellation can make an in-flight write fail immediately on core 1.
    // Publish maintenance first so that failure is not reported as an output
    // fault. The generation already invalidates old producer/decoder work.
    native_audio_output_request_pause(true);
    maintenance_state_locked(generation + 1U, false);
    xSemaphoreGive(s_state->lock);
    play_command_t command = {.generation = generation + 1U, .maintenance = true};
    esp_err_t result = xQueueOverwrite(s_commands, &command) == pdTRUE ? ESP_OK : ESP_FAIL;
    xSemaphoreGive(s_control_lock);

    while (result == ESP_OK) {
        result = atomic_load(&s_maintenance_error);
        if (result != ESP_OK) break;
        if (esp_timer_get_time() >= deadline) { result = ESP_ERR_TIMEOUT; break; }
        if (maintenance_acked(MAINTENANCE_ALL) &&
            xSemaphoreTake(s_control_lock, maintenance_remaining_ticks(deadline)) == pdTRUE) {
            if (esp_timer_get_time() < deadline &&
                atomic_load(&s_maintenance_phase) == MAINTENANCE_REQUESTED &&
                atomic_load(&s_maintenance_error) == ESP_OK) {
                portENTER_CRITICAL(&s_maintenance_token_lock);
                atomic_store(&s_maintenance_phase, MAINTENANCE_HELD);
                token->epoch = epoch;
                portEXIT_CRITICAL(&s_maintenance_token_lock);
                atomic_store(&s_maintenance_waiter, false);
                xSemaphoreGive(s_control_lock);
                return ESP_OK;
            }
            xSemaphoreGive(s_control_lock);
        }
        vTaskDelay(1);
    }
    int no_error = ESP_OK;
    atomic_compare_exchange_strong(&s_maintenance_error, &no_error, result);
    maintenance_publish_state(generation + 1U, maintenance_acked(MAINTENANCE_OUTPUT), 0);
    unsigned phase = MAINTENANCE_REQUESTED;
    atomic_compare_exchange_strong(&s_maintenance_phase, &phase, MAINTENANCE_ABORTING);
    atomic_store(&s_maintenance_waiter, false);
    maintenance_try_abort();
    return result;
}

esp_err_t audio_service_maintenance_end(audio_maintenance_token_t *token,
                                       bool resume_previous) {
    if (!token || !token->epoch) return ESP_ERR_INVALID_ARG;
    esp_err_t result = ESP_ERR_INVALID_STATE;
    // Guaranteed handoff: even if control is busy the request lives in audio
    // state, and parked owners retry it. Nothing here can retain HTTP storage.
    portENTER_CRITICAL(&s_maintenance_token_lock);
    if (token->epoch == s_maintenance_epoch &&
        atomic_load(&s_maintenance_phase) == MAINTENANCE_HELD) {
        atomic_store(&s_maintenance_phase, resume_previous
            ? MAINTENANCE_END_RESUME : MAINTENANCE_END_STOP);
        token->epoch = 0;
        result = ESP_OK;
    }
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    return result;
}

native_input_health_t audio_service_input_health(void) {
    native_input_health_t result = {0};
    if (atomic_load(&s_start_state) != AUDIO_START_READY) return result;
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
