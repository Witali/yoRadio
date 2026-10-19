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
