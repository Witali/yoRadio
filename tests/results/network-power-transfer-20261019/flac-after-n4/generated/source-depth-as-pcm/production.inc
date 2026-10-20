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
        .bits_per_sample = info->bits_per_sample,
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
