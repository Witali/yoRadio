#ifndef YORADIO_STREAM_FAIRNESS_H
#define YORADIO_STREAM_FAIRNESS_H

#include <stdbool.h>
#include <stdint.h>

/* A readable socket or a fast consumer need not block the stream owner.
 * Bound uninterrupted work by elapsed time, not bytes/read calls, so fragmented
 * input keeps its throughput. The caller blocks for one RTOS tick when due,
 * rebases AFTER that block, then rechecks cancellation before another read.
 * This creates an idle-task opportunity without feeding/changing its watchdog.
 */
#define STREAM_FAIRNESS_SLICE_US UINT64_C(20000)

typedef struct {
    uint64_t started_us;
} stream_fairness_t;

static inline void stream_fairness_begin(stream_fairness_t *budget,
                                         uint64_t now_us) {
    budget->started_us = now_us;
}

static inline bool stream_fairness_due(const stream_fairness_t *budget,
                                       uint64_t now_us) {
    return now_us - budget->started_us >= STREAM_FAIRNESS_SLICE_US;
}

#endif
