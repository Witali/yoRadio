/* Diagnostic stream profile only. One audio owner; nested PCM output is
 * subtracted from process_one. Wall time includes preemption, not just CPU.
 * 80 bytes of DRAM; no ISR changes, allocations, logging or per-sample hooks. */
#if YORADIO_ESP8266_OPUS_STREAM_TEST
enum { AUDIO_STAGE_READ, AUDIO_STAGE_DECODE, AUDIO_STAGE_OUTPUT, AUDIO_STAGE_WAIT,
       AUDIO_STAGE_INPUT_WAIT,
       AUDIO_STAGE_COUNT };
typedef struct { uint32_t us, maximum, calls, misses; } audio_stage_stats_t;
typedef struct { uint32_t us, misses, output_us, output_misses; } audio_stage_mark_t;
static audio_stage_stats_t s_stages[AUDIO_STAGE_COUNT];

static uint32_t audio_stage_now(void) {
    /* This SDK combines g_esp_os_us with CCOUNT without locking, while the
     * tick ISR updates the former and clears the latter. Read one coherent
     * pair; never mask interrupts across the measured operation itself. */
    taskENTER_CRITICAL();
    uint32_t now = (uint32_t)esp_timer_get_time();
    taskEXIT_CRITICAL();
    return now;
}

static uint32_t audio_stage_misses(void) {
    native_audio_output_spi_stats_t stats;
    native_audio_output_get_spi_stats(&stats);
    return stats.queue_empty_events;
}
static audio_stage_mark_t audio_stage_start(void) {
    audio_stage_mark_t mark = {
        .misses = audio_stage_misses(),
        .output_us = s_stages[AUDIO_STAGE_OUTPUT].us,
        .output_misses = s_stages[AUDIO_STAGE_OUTPUT].misses,
        .us = audio_stage_now(),
    };
    return mark;
}
static void audio_stage_finish(unsigned stage, audio_stage_mark_t mark) {
    uint32_t elapsed = audio_stage_now() - mark.us;
    uint32_t misses = audio_stage_misses() - mark.misses;
    /* Starting/reconfiguring DMA resets its counter. Do not interpret that as
     * billions of misses. Ordinary unsigned rollover still produces a delta. */
    if (misses > INT32_MAX) misses = 0;
    if (stage == AUDIO_STAGE_DECODE) {
        uint32_t nested = s_stages[AUDIO_STAGE_OUTPUT].us - mark.output_us;
        uint32_t nested_misses = s_stages[AUDIO_STAGE_OUTPUT].misses - mark.output_misses;
        elapsed = elapsed >= nested ? elapsed - nested : 0;
        misses = misses >= nested_misses ? misses - nested_misses : 0;
    }
    taskENTER_CRITICAL();
    audio_stage_stats_t *stats = &s_stages[stage];
    stats->us += elapsed;
    if (elapsed > stats->maximum) stats->maximum = elapsed;
    ++stats->calls;
    stats->misses += misses;
    taskEXIT_CRITICAL();
}

/* Cumulative modulo-2^32 counters. Compare snapshots <71 minutes apart and
 * discard intervals spanning reset/generation changes. Maxima are since boot.
 * Opening/closing HTTP and uninstrumented work remain unattributed. Never
 * interpret a miss counter as the duration of silence. */
int audio_service_stage_json(char *body, size_t capacity) {
    audio_stage_stats_t snapshot[AUDIO_STAGE_COUNT];
    uint32_t generation, uptime;
    taskENTER_CRITICAL();
    memcpy(snapshot, s_stages, sizeof(snapshot));
    generation = s_generation;
    uptime = xTaskGetTickCount() * portTICK_PERIOD_MS;
    taskEXIT_CRITICAL();
    int size = snprintf(body, capacity, "{\"profile_version\":2,\"generation\":%u,\"uptime_ms\":%u,\"stages\":[",
                        (unsigned)generation, (unsigned)uptime);
    if (size < 0 || (size_t)size >= capacity) return -1;
    for (unsigned i = 0; i < AUDIO_STAGE_COUNT; ++i) {
        const audio_stage_stats_t *s = &snapshot[i];
        int n = snprintf(body + size, capacity - (size_t)size, "%s[%u,%u,%u,%u]",
                         i ? "," : "", (unsigned)s->us, (unsigned)s->maximum,
                         (unsigned)s->calls, (unsigned)s->misses);
        if (n < 0 || (size_t)n >= capacity - (size_t)size) return -1;
        size += n;
    }
    if ((size_t)size + 3U > capacity) return -1;
    memcpy(body + size, "]}", 3);
    return size + 2;
}
#define AUDIO_STAGE_BEGIN(name) audio_stage_mark_t name = audio_stage_start()
#define AUDIO_STAGE_END(stage, name) audio_stage_finish(stage, name)
#else
#define AUDIO_STAGE_BEGIN(name) ((void)0)
#define AUDIO_STAGE_END(stage, name) ((void)0)
#endif
