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

#define STREAM_INPUT_ACTIVE(generation) (atomic_load(&s_generation) == (generation) && atomic_load(&s_failed_generation) != (generation))
static uint32_t s_decoder_bitrate_generation, s_decoder_bitrate_bps;
static int64_t s_decoder_bitrate_updated_us;

bool native_audio_output_supports_pcm(uint8_t bits_per_sample,
                                      uint8_t channels) {
    return channels && (bits_per_sample == 8 || bits_per_sample == 16 ||
                        bits_per_sample == 24 || bits_per_sample == 32);
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
    strlcpy(command.url, url, sizeof(command.url));
    native_state_begin_audio(s_state, command.generation, url, "connecting");
    native_state_set_connecting(s_state, command.generation);
    esp_err_t result = xQueueOverwrite(s_commands, &command) == pdTRUE
                         ? ESP_OK : ESP_FAIL;
    s_last_command_valid = result == ESP_OK;
    if (s_last_command_valid) s_last_command = command;
    if (result != ESP_OK) native_state_set_audio(s_state, command.generation, false, "command failed");
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
    native_state_begin_audio(s_state, generation, NULL, "stopped");
    xSemaphoreGive(s_control_lock);
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
