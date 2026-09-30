#include "native_state.h"

#include <string.h>
#include <stdio.h>

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

void native_state_set_wifi_rssi(native_state_t *state, int8_t rssi) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        state->wifi_rssi = rssi;
        xSemaphoreGive(state->lock);
    }
}

static void clear_stream_info(native_state_t *state) {
    state->bitrate_kbps = 0;
    state->sample_rate_hz = 0;
    state->channels = 0;
    state->bits_per_sample = 0;
    state->pcm_sample_rate_hz = 0;
    state->pcm_channels = 0;
    state->channels_are_core = false;
    state->format_is_pcm = false;
    state->codec[0] = '\0';
}

void native_state_begin_stream(native_state_t *state, uint32_t generation) {
    if (!state || !state->lock) return;
    // Control commands must invalidate old callbacks even under contention.
    if (xSemaphoreTake(state->lock, portMAX_DELAY) == pdTRUE) {
        // Two control tasks may acquire this mutex in a different order than
        // the generation counter. Never restore the older stream's identity.
        if ((int32_t)(generation - state->audio_generation) > 0) {
            state->audio_generation = generation;
            clear_stream_info(state);
            state->audio_running = false;
            state->title[0] = '\0';
            strcpy(state->stream_format, "idle");
        }
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_audio(native_state_t *state, uint32_t generation,
                            bool running, const char *status) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        if (state->audio_generation == generation) {
            state->audio_running = running;
            if (!running) clear_stream_info(state);
            if (status) strlcpy(state->stream_format, status,
                                 sizeof(state->stream_format));
        }
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_bitrate(native_state_t *state, uint32_t generation,
                              uint32_t bitrate_kbps) {
    if (!state || !state->lock) return;
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        if (state->audio_generation == generation)
            state->bitrate_kbps = bitrate_kbps;
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
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        if (state->audio_generation == generation) {
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
                char rate[16], channels[20];
                format_rate(info->sample_rate_hz, rate, sizeof(rate));
                if (info->channels == 1) strcpy(channels, "mono");
                else if (info->channels == 2) strcpy(channels, "stereo");
                else snprintf(channels, sizeof(channels), "%u channels",
                              info->channels);
                snprintf(state->stream_format, sizeof(state->stream_format),
                         "%s%s %s kHz %s%s", state->codec,
                         info->format_is_pcm ? " PCM" : "", rate,
                         info->channels_are_core ? "core " : "", channels);
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

void native_state_set_station(native_state_t *state, const char *station) {
    if (!state || !state->lock || !station) return;
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        strlcpy(state->station, station, sizeof(state->station));
        state->title[0] = '\0';
        xSemaphoreGive(state->lock);
    }
}

void native_state_set_title(native_state_t *state, const char *title) {
    if (!state || !state->lock || !title) return;
    if (xSemaphoreTake(state->lock, pdMS_TO_TICKS(100)) == pdTRUE) {
        strlcpy(state->title, title, sizeof(state->title));
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

