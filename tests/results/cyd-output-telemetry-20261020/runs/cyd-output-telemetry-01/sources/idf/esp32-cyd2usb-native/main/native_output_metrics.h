#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"

// Boot-cumulative observations of actual driver write calls, including bias,
// prime and idle writes. Bytes are the caller's driver-buffer units; they are
// not necessarily input PCM bytes or samples physically transmitted by DMA.
// All counters saturate instead of wrapping; saturated reports any lost range.
typedef struct {
    uint64_t requested_bytes, written_bytes;
    uint64_t write_us, max_write_us;
    uint32_t writes, errors, timeouts, short_writes;
    uint32_t timing_samples, invalid_time_samples;
    uint32_t completion_queue_drops;
    bool timing_enabled, queue_drops_available, saturated;
} native_output_metrics_t;

// Call immediately around the synchronous driver API, outside any critical
// section. Quiet builds never read the clock. Diagnostic wall time includes
// copying, driver locks, queue waits and preemption; it is not DMA wait time.
int64_t native_output_metrics_begin_write(void);
void native_output_metrics_end_write(size_t requested, size_t written,
                                     esp_err_t result, int64_t started_us);

// The counter becomes available after a completion-queue callback has been
// registered successfully. Availability and observations remain valid across
// pause/reconfigure. A drop is a driver queue event, not an audible underrun.
void native_output_metrics_observe_queue(void);
// ISR-safe: short portMUX update in DRAM, no clock, logging or allocation.
void native_output_metrics_queue_drop(void);
native_output_metrics_t native_output_metrics_snapshot(void);
