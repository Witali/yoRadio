#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdatomic.h>

enum { STREAM_CHUNK_SIZE = 2048 };
#ifndef CONFIG_YORADIO_INPUT_PREFILL_MS
#define CONFIG_YORADIO_INPUT_PREFILL_MS 500
#endif
#ifndef CONFIG_YORADIO_INPUT_PREFILL_MIN_MS
#define CONFIG_YORADIO_INPUT_PREFILL_MIN_MS 0
#endif
typedef int native_codec_t;
typedef unsigned TickType_t;
static unsigned tick_ms = 1, sleeps;
#define pdMS_TO_TICKS(ms) ((ms) / tick_ms)
#define ESP_LOGI(tag, ...) do { if (0) printf(__VA_ARGS__); } while (0)
static atomic_uint s_generation;
static void *s_encoded = (void *)1;
static int64_t now_us, full_at_us, cancel_at_us;
static bool initially_full;

typedef struct {
    uint32_t generation;
    native_codec_t codec;
    uint16_t data_size;
    uint8_t end_of_stream;
    uint8_t data[];
} encoded_packet_t;
#define INPUT_PREFILL_POLL_MS 10U

static int64_t esp_timer_get_time(void) { return now_us; }
static void vTaskDelay(TickType_t ticks) {
    assert(ticks > 0);
    now_us += ticks * tick_ms * 1000LL;
    ++sleeps;
    if (cancel_at_us >= 0 && now_us >= cancel_at_us)
        atomic_fetch_add(&s_generation, 1);
}
static bool full_now(void) {
    return initially_full || (full_at_us >= 0 && now_us >= full_at_us);
}
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
typedef struct { unsigned resident, occupied; } adaptive_input_stats_t;
static unsigned resident;
static adaptive_input_stats_t adaptive_input_stats(void *input) {
    assert(input == s_encoded);
    return (adaptive_input_stats_t){resident, full_now() ? resident : 1};
}
#else
static size_t xRingbufferGetCurFreeSize(void *input) {
    assert(input == s_encoded);
    size_t next_packet = sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE;
    return full_now() ? next_packet - 1 : next_packet;
}
#endif

static bool prefill_encoded_input(uint32_t generation) {
    // The decoder retains its first input lease. Only the producer appends
    // packets while we wait; no queued or leased storage may be reclaimed.
    // Normally finish when the producer needs the consumer to make room.
    // An optional minimum delay adds margin for bursty delivery without
    // changing capacity, including the TLS-reduced adaptive queue.
    const int64_t started_us = esp_timer_get_time();
    const int64_t maximum_us = CONFIG_YORADIO_INPUT_PREFILL_MS * 1000LL;
    TickType_t poll_ticks = pdMS_TO_TICKS(INPUT_PREFILL_POLL_MS);
    if (!poll_ticks) poll_ticks = 1;
    bool full = false;
    while (atomic_load(&s_generation) == generation) {
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
        adaptive_input_stats_t capacity = adaptive_input_stats(s_encoded);
        full = capacity.occupied >= capacity.resident;
#else
        full = xRingbufferGetCurFreeSize(s_encoded) <
               sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE;
#endif
#if CONFIG_YORADIO_INPUT_PREFILL_MIN_MS > 0
        _Static_assert(CONFIG_YORADIO_INPUT_PREFILL_MIN_MS <= CONFIG_YORADIO_INPUT_PREFILL_MS,
                       "Minimum prefill must not exceed its deadline");
        int64_t elapsed_us = esp_timer_get_time() - started_us;
        if (elapsed_us >= maximum_us ||
            (full && elapsed_us >= CONFIG_YORADIO_INPUT_PREFILL_MIN_MS * 1000LL)) break;
#else
        // Keep the original early-full path when the experiment is disabled.
        if (full || esp_timer_get_time() - started_us >= maximum_us) break;
#endif
        vTaskDelay(poll_ticks);
    }
    bool current = atomic_load(&s_generation) == generation;
    ESP_LOGI(TAG, "PERF INPUT_PREFILL: generation=%lu elapsed_ms=%lu full=%u cancelled=%u",
             (unsigned long)generation,
             (unsigned long)((esp_timer_get_time() - started_us) / 1000LL),
             full, !current);
    return current;
}

static void reset(unsigned generation) {
    atomic_store(&s_generation, generation);
    now_us = 0;
    full_at_us = cancel_at_us = -1;
    sleeps = 0;
    tick_ms = 1;
    initially_full = false;
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    resident = 4;
#endif
}

int main(void) {
    const int64_t maximum_us = CONFIG_YORADIO_INPUT_PREFILL_MS * 1000LL;
    const int64_t minimum_us = CONFIG_YORADIO_INPUT_PREFILL_MIN_MS * 1000LL;
    const int64_t rounded_minimum = (minimum_us + 9999) / 10000 * 10000;
    reset(7); // A fast producer observes only the configured minimum delay.
    full_at_us = 17000;
    int64_t fast_time = rounded_minimum > 20000 ? rounded_minimum : 20000;
    assert(prefill_encoded_input(7) && now_us == fast_time && sleeps == fast_time / 10000);

    reset(7); // Sparse input/short finite data cannot wait forever.
    assert(prefill_encoded_input(7) && now_us == maximum_us && sleeps == maximum_us / 10000);

    reset(7); // Stop or replacement cancels before decoder creation.
    cancel_at_us = 35000;
    assert(!prefill_encoded_input(7) && now_us == 40000 && sleeps == 4);

    reset(8); // Already-stale generation does not even poll or sleep.
    assert(!prefill_encoded_input(7) && now_us == 0 && sleeps == 0);

    reset(0); // Generation zero and wraparound are ordinary valid values.
    initially_full = true;
    assert(prefill_encoded_input(0) && now_us == rounded_minimum);
    reset(UINT32_MAX);
    cancel_at_us = 10000;
    assert(!prefill_encoded_input(UINT32_MAX) && now_us == 10000);

    reset(7); // A coarse tick cannot turn the loop into a busy spin.
    tick_ms = 20;
    assert(prefill_encoded_input(7) && now_us == maximum_us && sleeps == maximum_us / 20000);

    reset(7); // Cancellation wins even if the queue becomes full together.
    full_at_us = cancel_at_us = 10000;
    assert(!prefill_encoded_input(7) && now_us == 10000);

    reset(7); // A late producer still exits before the maximum when possible.
    full_at_us = maximum_us - 30000;
    int64_t late_time = rounded_minimum > full_at_us ? rounded_minimum : full_at_us;
    assert(prefill_encoded_input(7) && now_us == late_time);

    reset(7); // Minimum delay is rounded up by polling, including coarse ticks.
    tick_ms = 20;
    initially_full = true;
    assert(prefill_encoded_input(7) && now_us == (minimum_us + 19999) / 20000 * 20000);

#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    reset(7); // The TLS-reduced two-slot queue uses its actual capacity.
    resident = 2;
    full_at_us = 10000;
    int64_t reduced_time = rounded_minimum > 10000 ? rounded_minimum : 10000;
    assert(prefill_encoded_input(7) && now_us == reduced_time);
    reset(7); // A defensive zero-capacity snapshot never deadlocks startup.
    resident = 0;
    initially_full = true;
    assert(prefill_encoded_input(7) && now_us == rounded_minimum);
#endif
    puts("PASS initial input prefill: timing, backpressure, cancellation, wrap and coarse ticks");
}
