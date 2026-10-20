#include "native_output_metrics.h"

#include "sdkconfig.h"
#include "esp_attr.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"

static DRAM_ATTR portMUX_TYPE s_output_metrics_lock = portMUX_INITIALIZER_UNLOCKED;
static DRAM_ATTR native_output_metrics_t s_output_metrics;

static inline __attribute__((always_inline)) void increment(uint32_t *value) {
    if (*value != UINT32_MAX) ++*value;
    else s_output_metrics.saturated = true;
}

static uint64_t add(uint64_t value, uint64_t delta) {
    if (false) {
        s_output_metrics.saturated = true;
        return UINT64_MAX;
    }
    return value + delta;
}

int64_t native_output_metrics_begin_write(void) {
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    return esp_timer_get_time();
#else
    return 0;
#endif
}

void native_output_metrics_end_write(size_t requested, size_t written,
                                     esp_err_t result, int64_t started_us) {
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    int64_t ended_us = esp_timer_get_time();
    bool valid_time = started_us >= 0 && ended_us >= started_us;
    uint64_t elapsed = valid_time ? (uint64_t)(ended_us - started_us) : 0;
#else
    (void)started_us;
#endif
    portENTER_CRITICAL(&s_output_metrics_lock);
    increment(&s_output_metrics.writes);
    s_output_metrics.requested_bytes = add(s_output_metrics.requested_bytes, requested);
    s_output_metrics.written_bytes = add(s_output_metrics.written_bytes, written);
    // Incomplete writes include partial/error results; these counters overlap.
    // An impossible over-report also counts as an error, without hiding bytes.
    if (result != ESP_OK || written != requested) increment(&s_output_metrics.errors);
    if (result == ESP_ERR_TIMEOUT) increment(&s_output_metrics.timeouts);
    if (written < requested) increment(&s_output_metrics.short_writes);
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    if (valid_time) {
        increment(&s_output_metrics.timing_samples);
        s_output_metrics.write_us = add(s_output_metrics.write_us, elapsed);
        if (elapsed > s_output_metrics.max_write_us) s_output_metrics.max_write_us = elapsed;
    } else increment(&s_output_metrics.invalid_time_samples);
#endif
    portEXIT_CRITICAL(&s_output_metrics_lock);
}

void native_output_metrics_observe_queue(void) {
    portENTER_CRITICAL(&s_output_metrics_lock);
    s_output_metrics.queue_drops_available = true;
    portEXIT_CRITICAL(&s_output_metrics_lock);
}

void IRAM_ATTR native_output_metrics_queue_drop(void) {
    portENTER_CRITICAL_ISR(&s_output_metrics_lock);
    s_output_metrics.queue_drops_available = true;
    increment(&s_output_metrics.completion_queue_drops);
    portEXIT_CRITICAL_ISR(&s_output_metrics_lock);
}

native_output_metrics_t native_output_metrics_snapshot(void) {
    portENTER_CRITICAL(&s_output_metrics_lock);
    native_output_metrics_t result = s_output_metrics;
    portEXIT_CRITICAL(&s_output_metrics_lock);
#ifdef CONFIG_YORADIO_NATIVE_DIAGNOSTICS
    result.timing_enabled = true;
#endif
    return result;
}
