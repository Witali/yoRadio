

static void clear_stream_info(native_state_t *state) {
    state->bitrate_kbps = state->sample_rate_hz = state->pcm_sample_rate_hz = 0;
    state->bitrate_source = NATIVE_BITRATE_NONE;
    state->channels = state->bits_per_sample = state->pcm_channels = 0;
    state->channels_are_core = state->format_is_pcm = false;
    state->codec[0] = '\0';
}

void native_state_init(native_state_t *state) {
    memset(state, 0, sizeof(*state));
    state->lock = xSemaphoreCreateMutex();
    state->network_mode = NATIVE_NETWORK_STARTING;
    strcpy(state->station, "yoRadio native");
    strcpy(state->stream_format, "idle");
}

void native_state_set_network(native_state_t *state,
                              native_network_mode_t mode,
                              uint32_t ipv4) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        state->network_mode = mode;
        state->ipv4 = ipv4;
        xSemaphoreGive(state->lock);
    }
}

void native_state_snapshot(native_state_t *state, native_state_t *snapshot) {
    if (!state || !snapshot) return;
    memset(snapshot, 0, sizeof(*snapshot));
    if (state->lock &&
        xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        SemaphoreHandle_t lock = state->lock;
        memcpy(snapshot, state, sizeof(*snapshot));
        snapshot->lock = NULL;
        xSemaphoreGive(lock);
    }
}

void native_state_begin_audio_locked(native_state_t *state, uint32_t generation,
                                     const char *station, const char *format) {
    if (!state) return;
    state->audio_generation = generation;
    clear_stream_info(state);
    state->audio_running = false;
    state->audio_pending = false;
    state->audio_failed = false;
    state->title[0] = '\0';
    if (station) strlcpy(state->station, station, sizeof(state->station));
    strlcpy(state->stream_format, format, sizeof(state->stream_format));
}

void native_state_begin_audio(native_state_t *state, uint32_t generation,
                              const char *station, const char *format) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        native_state_begin_audio_locked(state, generation, station, format);
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_audio(native_state_t *state, uint32_t generation,
                            bool running, const char *format) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        // Check under the mutex: Play/Stop may race an old decoder callback.
        if (state->audio_generation == generation && !state->audio_failed) {
            state->audio_running = running;
            state->audio_pending = false;
            if (!running) clear_stream_info(state);
            if (format) strlcpy(state->stream_format, format,
                                sizeof(state->stream_format));
        }
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_title(native_state_t *state, uint32_t generation,
                            const char *title) {
    if (!state || !state->lock || !title) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        if (state->audio_generation == generation) {
            strlcpy(state->title, title, sizeof(state->title));
        }
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_station(native_state_t *state, const char *station) {
    if (!state || !state->lock || !station) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        strlcpy(state->station, station, sizeof(state->station));
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_pending(native_state_t *state, uint32_t generation, bool pending) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        if (state->audio_generation == generation && !state->audio_failed) state->audio_pending = pending;
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_connecting(native_state_t *state, uint32_t generation) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        if (state->audio_generation == generation && !state->audio_failed) {
            state->audio_running = false;
            state->audio_pending = true;
            clear_stream_info(state);
            strcpy(state->stream_format, "connecting");
        }
        xSemaphoreGive(state->lock);
    }
}


void native_state_set_bitrate(native_state_t *state, uint32_t generation,
                              uint32_t bitrate_kbps) {
    native_state_publish_bitrate(state,generation,bitrate_kbps,NATIVE_BITRATE_DECODER);
}

void native_state_publish_bitrate(native_state_t *state, uint32_t generation, uint32_t bitrate_kbps,
                                  native_bitrate_source_t source) {
    if (!state || !state->lock || !bitrate_kbps || source < NATIVE_BITRATE_ICY || source > NATIVE_BITRATE_MEASURED) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        if (state->audio_generation == generation && !state->audio_failed && source >= state->bitrate_source) {
            state->bitrate_kbps = bitrate_kbps;
            state->bitrate_source = source;
        }
        xSemaphoreGive(state->lock);
    }
}

static void format_rate(uint32_t hz, char *output, size_t size) {
    if (hz % 1000U == 0) {
        snprintf(output, size, "%lu", (unsigned long)(hz / 1000U));
    } else {
        snprintf(output, size, "%lu.%03lu", (unsigned long)(hz / 1000U),
                 (unsigned long)(hz % 1000U));
        size_t length = strlen(output);
        while (length && output[length - 1] == '0') output[--length] = '\0';
    }
}

bool native_state_set_stream_info(native_state_t *state, uint32_t generation,
                                  const native_stream_info_t *info) {
    if (!state || !state->lock || !info || !info->codec ||
        !info->sample_rate_hz || !info->channels || !info->bits_per_sample ||
        !info->pcm_sample_rate_hz || !info->pcm_channels) return false;
    bool changed = false;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        if (state->audio_generation == generation && !state->audio_failed) {
            changed = !state->audio_running ||
                strcmp(state->codec, info->codec) != 0 ||
                state->sample_rate_hz != info->sample_rate_hz ||
                state->channels != info->channels ||
                state->bits_per_sample != info->bits_per_sample ||
                state->pcm_sample_rate_hz != info->pcm_sample_rate_hz ||
                state->pcm_channels != info->pcm_channels ||
                state->channels_are_core != info->channels_are_core ||
                state->format_is_pcm != info->format_is_pcm;
            if (changed) {
                strlcpy(state->codec, info->codec, sizeof(state->codec));
                state->sample_rate_hz = info->sample_rate_hz;
                state->channels = info->channels;
                state->bits_per_sample = info->bits_per_sample;
                state->pcm_sample_rate_hz = info->pcm_sample_rate_hz;
                state->pcm_channels = info->pcm_channels;
                state->channels_are_core = info->channels_are_core;
                state->format_is_pcm = info->format_is_pcm;
                state->audio_running = true;
                state->audio_pending = false;
                char rate[16], channels[20];
                format_rate(info->sample_rate_hz, rate, sizeof(rate));
                if (info->channels == 1) strcpy(channels, "mono");
                else if (info->channels == 2) strcpy(channels, "stereo");
                else snprintf(channels, sizeof(channels), "%u channels",
                              info->channels);
                char formatted[80];
                snprintf(formatted, sizeof(formatted),
                         "%s%s %s kHz %s%s", state->codec,
                         info->format_is_pcm ? " PCM" : "", rate,
                         info->channels_are_core ? "core " : "", channels);
                strlcpy(state->stream_format, formatted, sizeof(state->stream_format));
            }
        }
        xSemaphoreGive(state->lock);
    }
    return changed;
}

void native_state_format_stream_details(const native_state_t *state,
                                        char *output, size_t output_size) {
    if (!output || !output_size) return;
    output[0] = '\0';
    if (!state || !state->sample_rate_hz) return;
    if (state->bitrate_kbps) {
        snprintf(output, output_size, "%s %lu kbps", state->stream_format,
                 (unsigned long)state->bitrate_kbps);
    } else {
        strlcpy(output, state->stream_format, output_size);
    }
}

void native_state_fail_audio(native_state_t *state, uint32_t generation, const char *status) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        if (state->audio_generation == generation) {
            state->audio_failed = true;
            state->audio_running = state->audio_pending = false;
            clear_stream_info(state);
            if (status) strlcpy(state->stream_format,status,sizeof(state->stream_format));
        }
        xSemaphoreGive(state->lock);
    }
}
