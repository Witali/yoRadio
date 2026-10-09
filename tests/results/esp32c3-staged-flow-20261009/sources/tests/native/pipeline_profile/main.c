#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include "pipeline_profile.h"

static int token, calls, clocks;
static TickType_t blocking_timeout;
static bool available, eventually_ready;
static int64_t now;

int64_t esp_timer_get_time(void) { ++clocks; return now; }
void *xRingbufferReceive(RingbufHandle_t ring, size_t *size, TickType_t timeout) {
    assert(ring == &token);
    ++calls;
    if (!timeout) { *size = available ? 7 : 0; return available ? &token : NULL; }
    assert(timeout == blocking_timeout);
    now += 1234;
    *size = eventually_ready ? 7 : 0;
    return eventually_ready ? &token : NULL;
}
BaseType_t xRingbufferSendAcquire(RingbufHandle_t ring, void **item,
                                size_t size, TickType_t timeout) {
    assert(size == 99);
    size_t received;
    *item = xRingbufferReceive(ring, &received, timeout);
    return *item ? pdTRUE : 0;
}

int main(void) {
    size_t size;
    void *item;
#ifdef CONFIG_YORADIO_PIPELINE_PROFILE
    pipeline_wait_t stats = {0};
    available = true;
    assert(pipeline_receive(&token, &size, 20, &stats) == &token);
    assert(size == 7 && calls == 1 && clocks == 0 && stats.count == 0);
    assert(pipeline_acquire(&token, &item, 99, 250, &stats) == pdTRUE);
    assert(item == &token && calls == 2 && clocks == 0);
    available = false;
    eventually_ready = true;
    blocking_timeout = 20;
    assert(pipeline_receive(&token, &size, 20, &stats) == &token);
    assert(calls == 4 && stats.count == 1 && stats.us == 1234 && stats.timeouts == 0);
    blocking_timeout = 250;
    assert(pipeline_acquire(&token, &item, 99, 250, &stats) == pdTRUE);
    eventually_ready = false;
    assert(pipeline_acquire(&token, &item, 99, 250, &stats) != pdTRUE);
    blocking_timeout = 20;
    assert(!pipeline_receive(&token, &size, 20, &stats));
    assert(stats.count == 4 && stats.us == 4936 && stats.max_us == 1234 && stats.timeouts == 2);
    // 64-bit totals must not wrap at 2^32 microseconds.
    pipeline_wait_record(&stats, UINT32_MAX, false);
    assert(stats.us == 4936ULL + UINT32_MAX && stats.max_us == UINT32_MAX);
#else
    // The nonexistent stats expressions must not even be evaluated/compiled.
    blocking_timeout = 20;
    eventually_ready = true;
    assert(pipeline_receive(&token, &size, 20, &missing.input) == &token);
    assert(calls == 1 && clocks == 0);
    blocking_timeout = 250;
    assert(pipeline_acquire(&token, &item, 99, 250, &missing.pcm) == pdTRUE);
    assert(calls == 2 && clocks == 0);
#endif
    puts("PASS: immediate, blocked, timeout, ownership and disabled profile");
}
