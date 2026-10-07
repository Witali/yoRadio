#pragma once
#include <stdbool.h>
#include <stdint.h>

// Task-local wall time, including time spent ready but preempted. These are
// queue-availability observations, not FreeRTOS blocked CPU-cycle counters.
typedef struct {
    uint64_t us;
    uint32_t count, timeouts, max_us;
} pipeline_wait_t;

static inline void pipeline_wait_record(pipeline_wait_t *stats,
                                        uint32_t us, bool timeout) {
    stats->us += us;
    ++stats->count;
    stats->timeouts += timeout;
    if (us > stats->max_us) stats->max_us = us;
}
