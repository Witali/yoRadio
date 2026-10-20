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
        .output_driver=native_output_metrics_snapshot(),
    };
    char body[2304];
    if (!native_health_format_json(body,sizeof(body),&health,&runtime))
        return httpd_resp_send_err(request,HTTPD_500_INTERNAL_SERVER_ERROR,"Health buffer exhausted");
    httpd_resp_set_type(request,"application/json; charset=utf-8");
    httpd_resp_set_hdr(request,"Cache-Control","no-store");
    return httpd_resp_sendstr(request,body);
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
