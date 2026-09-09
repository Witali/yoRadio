#pragma once

#include "esp_err.h"
#include <stdint.h>

typedef struct {
    uint32_t generation, uptime_ms, rx_bytes, pcm_frames, sample_rate;
    uint32_t rx_age_ms, pcm_age_ms;
} audio_service_health_t;

/* Allocation-free, read-only progress counters, not a Playing flag. */
void audio_service_health(audio_service_health_t *health);

esp_err_t audio_service_init(void);
esp_err_t audio_service_play(const char *url);
esp_err_t audio_service_stop(void);

/* Serialized HTTP task only. Long mode waits for owner-side resource release;
 * off/short are no-ops. Always end a successful begin, including send errors. */
esp_err_t audio_service_web_pause_begin(void);
void audio_service_web_pause_end(void);
