#pragma once
/* Existing PCM/ownership suites deliberately exclude telemetry. The separate
 * cyd_output_telemetry gate links the complete production metrics service. */
#ifndef IRAM_ATTR
#define IRAM_ATTR
#endif
static inline int64_t native_output_metrics_begin_write(void) { return 0; }
static inline void native_output_metrics_end_write(size_t requested, size_t written,
        esp_err_t result, int64_t started) {
    (void)requested; (void)written; (void)result; (void)started;
}
static inline void native_output_metrics_observe_queue(void) {}
static inline void native_output_metrics_queue_drop(void) {}
