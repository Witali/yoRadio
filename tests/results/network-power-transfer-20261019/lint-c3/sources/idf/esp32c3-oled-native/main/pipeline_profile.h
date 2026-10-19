#pragma once

#include "sdkconfig.h"
#include "freertos/ringbuf.h"

#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
#include "esp_timer.h"
#include "pipeline_wait.h"

static inline void *pipeline_receive(RingbufHandle_t ring, size_t *size,
                                     TickType_t timeout,
                                     pipeline_wait_t *stats) {
    void *item = xRingbufferReceive(ring, size, 0);
    if (item) return item;
    int64_t start = esp_timer_get_time();
    item = xRingbufferReceive(ring, size, timeout);
    pipeline_wait_record(stats, (uint32_t)(esp_timer_get_time() - start),
                          item == NULL);
    return item;
}

static inline BaseType_t pipeline_acquire(RingbufHandle_t ring, void **item,
    size_t size, TickType_t timeout, pipeline_wait_t *stats) {
    BaseType_t result = xRingbufferSendAcquire(ring, item, size, 0);
    if (result == pdTRUE) return result;
    int64_t start = esp_timer_get_time();
    result = xRingbufferSendAcquire(ring, item, size, timeout);
    pipeline_wait_record(stats, (uint32_t)(esp_timer_get_time() - start),
                          result != pdTRUE);
    return result;
}
#else
// Discard the stats argument entirely: no fields, clocks or probes in normal
// builds. Preserve the original blocking calls and their exact timeout.
#define pipeline_receive(ring, size, timeout, stats) \
    xRingbufferReceive((ring), (size), (timeout))
#define pipeline_acquire(ring, item, size, timeout, stats) \
    xRingbufferSendAcquire((ring), (item), (size), (timeout))
#endif
