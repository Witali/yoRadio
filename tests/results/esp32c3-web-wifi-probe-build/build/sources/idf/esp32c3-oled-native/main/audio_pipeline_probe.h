#pragma once

#include <stdint.h>
#include "sdkconfig.h"

#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
#include <stddef.h>
#include <stdio.h>
#include "esp_timer.h"

// C3 only: aligned single-word stores from one writer per checkpoint. The
// ISR records observations, not FreeRTOS blocked/ready state. A wait flag
// stays set if a queue wakes the task before it is scheduled again.
enum {
    AUDIO_PROBE_OUTPUT_WAIT = 1U,
    AUDIO_PROBE_DECODER_WAIT = 2U,
    AUDIO_PROBE_STREAM_READ = 4U,
    AUDIO_PROBE_PHASE_COUNT = 8U,
    AUDIO_PROBE_EVENTS = 16U,
};
typedef struct {
    uint32_t sequence, timestamp_us, phases;
    uint32_t output_age, pcm_age, input_age, network_age;
} audio_pipeline_probe_event_t;
typedef struct {
    uint32_t sequence, timestamp_us;
    int32_t http_result, esp_tls_error, tls_code, system_errno;
} audio_stream_failure_t;
typedef struct {
    uint32_t output_wait, decoder_wait, stream_read;
    uint32_t output_us, pcm_us, input_us, network_us;
    uint32_t sequence, valid_count;
    uint32_t phase_drops[AUDIO_PROBE_PHASE_COUNT];
    audio_pipeline_probe_event_t events[AUDIO_PROBE_EVENTS];
    audio_stream_failure_t stream_failure;
} audio_pipeline_probe_t;
extern volatile audio_pipeline_probe_t s_audio_pipeline_probe;

#define AUDIO_PROBE_FLAG(field, value) (s_audio_pipeline_probe.field = (value))
#define AUDIO_PROBE_STAMP(field) (s_audio_pipeline_probe.field = (uint32_t)esp_timer_get_time())

// Called only by the DMA overrun ISR after an IRAM system-timer read. No
// allocation, locks or logging. Unsigned microsecond ages wrap after about
// 71.58 minutes; select short sustained-play intervals, excluding idle.
// Unlike C3's CPU cycle counter, the system timer includes WFI wait time.
static inline __attribute__((always_inline)) void audio_pipeline_probe_overrun(uint32_t now_us) {
    uint32_t phases = (s_audio_pipeline_probe.output_wait ? AUDIO_PROBE_OUTPUT_WAIT : 0U) |
                      (s_audio_pipeline_probe.decoder_wait ? AUDIO_PROBE_DECODER_WAIT : 0U) |
                      (s_audio_pipeline_probe.stream_read ? AUDIO_PROBE_STREAM_READ : 0U);
    uint32_t sequence = s_audio_pipeline_probe.sequence + 1U;
    volatile audio_pipeline_probe_event_t *event =
        &s_audio_pipeline_probe.events[sequence & (AUDIO_PROBE_EVENTS - 1U)];
    ++s_audio_pipeline_probe.phase_drops[phases];
    event->sequence = sequence;
    event->timestamp_us = now_us;
    event->phases = phases;
    event->output_age = now_us - s_audio_pipeline_probe.output_us;
    event->pcm_age = now_us - s_audio_pipeline_probe.pcm_us;
    event->input_age = now_us - s_audio_pipeline_probe.input_us;
    event->network_age = now_us - s_audio_pipeline_probe.network_us;
    s_audio_pipeline_probe.sequence = sequence;
    if (s_audio_pipeline_probe.valid_count < AUDIO_PROBE_EVENTS) {
        ++s_audio_pipeline_probe.valid_count;
    }
}
_Static_assert(sizeof(audio_pipeline_probe_t) == 540U, "Bound diagnostic RAM");
_Static_assert((AUDIO_PROBE_EVENTS & (AUDIO_PROBE_EVENTS - 1U)) == 0,
               "Event capacity must be a power of two");

// Task context only. Append a bounded diagnostic object to a complete JSON
// response. Copy the volatile state with interrupts masked before calling.
static inline int audio_pipeline_probe_append(char *body, size_t capacity,
    int length, const audio_pipeline_probe_t *probe) {
    if (length < 1 || (size_t)length >= capacity || body[length - 1] != '}' ||
        probe->valid_count > AUDIO_PROBE_EVENTS) return -1;
    --length;
#define PROBE_APPEND(...) do { \
    int added = snprintf(body + length, capacity - (size_t)length, __VA_ARGS__); \
    if (added < 0 || (size_t)added >= capacity - (size_t)length) return -1; \
    length += added; \
} while (0)
    PROBE_APPEND(",\"pipeline\":{\"timer_hz\":1000000,\"sequence\":%lu,\"phase_drops\":[",
                 (unsigned long)probe->sequence);
    for (unsigned index = 0; index < AUDIO_PROBE_PHASE_COUNT; ++index) {
        PROBE_APPEND("%s%lu", index ? "," : "", (unsigned long)probe->phase_drops[index]);
    }
    PROBE_APPEND("],\"events\":[");
    for (unsigned index = 0; index < probe->valid_count; ++index) {
        uint32_t sequence = probe->sequence - probe->valid_count + 1U + index;
        const audio_pipeline_probe_event_t *event =
            &probe->events[sequence & (AUDIO_PROBE_EVENTS - 1U)];
        PROBE_APPEND("%s[%lu,%lu,%lu,%lu,%lu,%lu,%lu]", index ? "," : "",
            (unsigned long)event->sequence, (unsigned long)event->timestamp_us,
            (unsigned long)event->phases, (unsigned long)event->output_age,
            (unsigned long)event->pcm_age, (unsigned long)event->input_age,
            (unsigned long)event->network_age);
    }
    const audio_stream_failure_t *failure = &probe->stream_failure;
    PROBE_APPEND("],\"stream_failure\":{\"sequence\":%lu,\"timestamp_us\":%lu,"
                 "\"http_result\":%ld,\"esp_tls_error\":%ld,\"tls_code\":%ld,\"system_errno\":%ld}}}",
        (unsigned long)failure->sequence, (unsigned long)failure->timestamp_us,
        (long)failure->http_result, (long)failure->esp_tls_error,
        (long)failure->tls_code, (long)failure->system_errno);
#undef PROBE_APPEND
    return length;
}
#else
#define AUDIO_PROBE_FLAG(field, value) ((void)0)
#define AUDIO_PROBE_STAMP(field) ((void)0)
#endif
