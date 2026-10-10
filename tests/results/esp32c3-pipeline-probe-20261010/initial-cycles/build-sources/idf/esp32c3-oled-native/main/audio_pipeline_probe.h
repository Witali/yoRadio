#pragma once

#include <stdint.h>
#include "sdkconfig.h"

#ifdef CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC
#include <stddef.h>
#include <stdio.h>
#include "esp_cpu.h"

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
    uint32_t sequence, cycle, phases;
    uint32_t output_age, pcm_age, input_age, network_age;
} audio_pipeline_probe_event_t;
typedef struct {
    uint32_t output_wait, decoder_wait, stream_read;
    uint32_t output_cycle, pcm_cycle, input_cycle, network_cycle;
    uint32_t sequence, valid_count;
    uint32_t phase_drops[AUDIO_PROBE_PHASE_COUNT];
    audio_pipeline_probe_event_t events[AUDIO_PROBE_EVENTS];
} audio_pipeline_probe_t;
extern volatile audio_pipeline_probe_t s_audio_pipeline_probe;

#define AUDIO_PROBE_FLAG(field, value) (s_audio_pipeline_probe.field = (value))
#define AUDIO_PROBE_TICK(field) (s_audio_pipeline_probe.field = esp_cpu_get_cycle_count())

// Called only by the DMA overrun ISR. No calls, allocation, locks or logging.
// Unsigned ages are modulo 2^32 CPU cycles; idle ages can wrap. Interpret
// short sustained-play intervals only. Lifetime sequence/histograms wrap too.
static inline __attribute__((always_inline)) void audio_pipeline_probe_overrun(uint32_t cycle) {
    uint32_t phases = (s_audio_pipeline_probe.output_wait ? AUDIO_PROBE_OUTPUT_WAIT : 0U) |
                      (s_audio_pipeline_probe.decoder_wait ? AUDIO_PROBE_DECODER_WAIT : 0U) |
                      (s_audio_pipeline_probe.stream_read ? AUDIO_PROBE_STREAM_READ : 0U);
    uint32_t sequence = s_audio_pipeline_probe.sequence + 1U;
    volatile audio_pipeline_probe_event_t *event =
        &s_audio_pipeline_probe.events[sequence & (AUDIO_PROBE_EVENTS - 1U)];
    ++s_audio_pipeline_probe.phase_drops[phases];
    event->sequence = sequence;
    event->cycle = cycle;
    event->phases = phases;
    event->output_age = cycle - s_audio_pipeline_probe.output_cycle;
    event->pcm_age = cycle - s_audio_pipeline_probe.pcm_cycle;
    event->input_age = cycle - s_audio_pipeline_probe.input_cycle;
    event->network_age = cycle - s_audio_pipeline_probe.network_cycle;
    s_audio_pipeline_probe.sequence = sequence;
    if (s_audio_pipeline_probe.valid_count < AUDIO_PROBE_EVENTS) {
        ++s_audio_pipeline_probe.valid_count;
    }
}
_Static_assert(sizeof(audio_pipeline_probe_t) == 516U, "Bound diagnostic RAM");
_Static_assert((AUDIO_PROBE_EVENTS & (AUDIO_PROBE_EVENTS - 1U)) == 0,
               "Event capacity must be a power of two");

// Task context only. Append a bounded diagnostic object to a complete JSON
// response. Copy the volatile state with interrupts masked before calling.
static inline int audio_pipeline_probe_append(char *body, size_t capacity,
    int length, const audio_pipeline_probe_t *probe, unsigned cpu_mhz) {
    if (length < 1 || (size_t)length >= capacity || body[length - 1] != '}' ||
        probe->valid_count > AUDIO_PROBE_EVENTS) return -1;
    --length;
#define PROBE_APPEND(...) do { \
    int added = snprintf(body + length, capacity - (size_t)length, __VA_ARGS__); \
    if (added < 0 || (size_t)added >= capacity - (size_t)length) return -1; \
    length += added; \
} while (0)
    PROBE_APPEND(",\"pipeline\":{\"cpu_mhz\":%u,\"sequence\":%lu,\"phase_drops\":[", cpu_mhz,
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
            (unsigned long)event->sequence, (unsigned long)event->cycle,
            (unsigned long)event->phases, (unsigned long)event->output_age,
            (unsigned long)event->pcm_age, (unsigned long)event->input_age,
            (unsigned long)event->network_age);
    }
    PROBE_APPEND("]}}");
#undef PROBE_APPEND
    return length;
}
#else
#define AUDIO_PROBE_FLAG(field, value) ((void)0)
#define AUDIO_PROBE_TICK(field) ((void)0)
#endif
