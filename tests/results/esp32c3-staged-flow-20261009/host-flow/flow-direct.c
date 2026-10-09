#include "output_flow_stubs.h"
typedef struct {
    int64_t start_us;
    pipeline_wait_t empty, submit;
    uint32_t overruns;
} output_flow_t;

static void output_flow_reset(output_flow_t *flow, bool active) {
    *flow = (output_flow_t){
        .start_us = active ? esp_timer_get_time() : 0,
        .overruns = native_audio_output_dma_overruns(),
    };
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
    native_i2s_take_wait_profile();
#endif
}

static void output_flow_report(output_flow_t *flow, uint32_t generation) {
    int64_t now = esp_timer_get_time();
    if (!flow->start_us || now - flow->start_us < DECODE_STATS_INTERVAL_US) return;
    uint32_t overruns = native_audio_output_dma_overruns();
#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM
    pipeline_wait_t dma = native_i2s_take_wait_profile();
    ESP_LOGI(TAG,
        "PERF FLOW_OUT: gen=%lu window_us=%llu "
        "empty_us=%llu empty_n=%lu empty_timeouts=%lu empty_max=%lu "
        "submit_us=%llu submit_n=%lu submit_max=%lu "
        "dma_us=%llu dma_n=%lu dma_timeouts=%lu dma_max=%lu overruns=%lu",
        (unsigned long)generation, (unsigned long long)(now - flow->start_us),
        (unsigned long long)flow->empty.us, (unsigned long)flow->empty.count,
        (unsigned long)flow->empty.timeouts, (unsigned long)flow->empty.max_us,
        (unsigned long long)flow->submit.us, (unsigned long)flow->submit.count,
        (unsigned long)flow->submit.max_us, (unsigned long long)dma.us,
        (unsigned long)dma.count, (unsigned long)dma.timeouts,
        (unsigned long)dma.max_us, (unsigned long)(overruns - flow->overruns));
#else
    // The stock staged driver does not expose a separate DMA wait. Report
    // its entire submission time under a distinct marker, never as zero wait.
    ESP_LOGI(TAG,
        "PERF FLOW_STAGED_OUT: gen=%lu window_us=%llu "
        "empty_us=%llu empty_n=%lu empty_timeouts=%lu empty_max=%lu "
        "submit_us=%llu submit_n=%lu submit_max=%lu overruns=%lu",
        (unsigned long)generation, (unsigned long long)(now - flow->start_us),
        (unsigned long long)flow->empty.us, (unsigned long)flow->empty.count,
        (unsigned long)flow->empty.timeouts, (unsigned long)flow->empty.max_us,
        (unsigned long long)flow->submit.us, (unsigned long)flow->submit.count,
        (unsigned long)flow->submit.max_us, (unsigned long)(overruns - flow->overruns));
#endif
    // Do not erase a completion interrupt occurring while the log is written.
    *flow = (output_flow_t){.start_us = now, .overruns = overruns};
}

#include "output_flow.c"
