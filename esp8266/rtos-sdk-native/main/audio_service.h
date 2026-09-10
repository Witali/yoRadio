#pragma once

#include "esp_err.h"
#include <stdint.h>

typedef enum {
    AUDIO_TRANSPORT_IDLE = 0,
    AUDIO_TRANSPORT_DNS = 1,
    AUDIO_TRANSPORT_CONNECT = 2,
    AUDIO_TRANSPORT_SEND = 3,
    AUDIO_TRANSPORT_HEADER = 4,
    AUDIO_TRANSPORT_REFILL = 5,
    AUDIO_TRANSPORT_DECODE = 6,
    AUDIO_TRANSPORT_CLOSE = 7,
} audio_transport_phase_t;

typedef struct {
    uint32_t generation, uptime_ms, rx_bytes, pcm_frames, sample_rate;
    uint32_t rx_age_ms, pcm_age_ms;
    uint32_t stack_free;
#if YORADIO_ESP8266_OPUS_DMA_YIELD
    uint32_t frame_yields, frame_yield_skips;
#endif
#if YORADIO_ESP8266_OPUS_STREAM_TEST
    uint32_t transport_phase;
    /* Terminal STREAM_FILL_* result (EOF=3, timeout=4, error=-1), or
     * INT32_MIN before one occurs in this generation. Retained on reconnect. */
    int32_t transport_result, transport_errno;
    uint32_t input_bytes;
#endif
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
