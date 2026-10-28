// Complete raw packet synthesis through public owned APIs; no saved DSP values.
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "vorbis_synthesis_pipeline.h"
#include "cases.h"

#ifdef NDEBUG
#error "Native synthesis qualification requires active assertions"
#endif
#if CONFIG_IDF_TARGET_ESP32
enum { WORKER_CORE = 1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { WORKER_CORE = 0 };
#else
#error "Unsupported target"
#endif

typedef struct { uint32_t row, packet; uint64_t packet_samples, emitted; } capture_t;

static bool packet(void *opaque, const vorbis_synthesis_pipeline_packet_t *metadata) {
    capture_t *capture = opaque;
    assert(xPortGetCoreID() == WORKER_CORE);
    assert(capture->emitted == capture->packet_samples);
    capture->packet = metadata->packet;
    capture->packet_samples = metadata->synthesis.pcm_samples;
    capture->emitted = 0;
    const native_vorbis_timing_result_t *timing = &metadata->synthesis.timing;
    printf("SYN_PACKET row=%" PRIu32 " packet=%" PRIu32 " block=%" PRIu32
        " channels=%" PRIu32 " floor0=%" PRIu32 " floor1=%" PRIu32
        " bits=%" PRIu64 " eop=%u available=%" PRIu32 " discard_start=%" PRIu32
        " discard_end=%" PRIu32 " frames=%" PRIu32 " position=%u end=%" PRId64
        " samples=%" PRIu64 " core=%d\n", capture->row, metadata->packet,
        metadata->blocksize, metadata->channels, metadata->floor0_channels,
        metadata->floor1_channels, metadata->consumed_bits, (unsigned)metadata->end_of_packet,
        timing->available, timing->discard_start, timing->discard_end, timing->count,
        (unsigned)timing->position_kind, timing->end_position,
        metadata->synthesis.pcm_samples, xPortGetCoreID());
    // A packet boundary is an ordinary scheduling point in this isolated fixture.
    vTaskDelay(1);
    return true;
}

static bool pcm(void *opaque, uint32_t ordinal, const int16_t *samples, size_t count) {
    capture_t *capture = opaque;
    assert(xPortGetCoreID() == WORKER_CORE && ordinal == capture->packet);
    assert(count > 0 && count <= 128 && count <= capture->packet_samples - capture->emitted);
    printf("SYN_PCM row=%" PRIu32 " packet=%" PRIu32 " start=%" PRIu64
        " count=%u core=%d runs=", capture->row, ordinal, capture->emitted,
        (unsigned)count, xPortGetCoreID());
    for (size_t i = 0; i < count;) {
        size_t end = i + 1;
        while (end < count && samples[end] == samples[i]) ++end;
        printf("%s%04x:%u", i ? "," : "", (unsigned)(uint16_t)samples[i], (unsigned)(end - i));
        i = end;
    }
    putchar('\n');
    capture->emitted += count;
    vTaskDelay(1);
    return true;
}

static void error(void *opaque, uint32_t ordinal, const char *stage, int status,
                  uint32_t channel, uint32_t route) {
    const capture_t *capture = opaque;
    printf("SYN_ERROR row=%" PRIu32 " packet=%" PRIu32 " stage=%s status=%d channel=%" PRIu32
        " route=%" PRIu32 " core=%d\n", capture->row, ordinal, stage, status,
        channel, route, xPortGetCoreID());
    fflush(stdout);
}

static void worker(void *unused) {
    (void)unused;
    uint64_t packets = 0, frames = 0, samples = 0;
    printf("SYN_WORKER core=%d priority=%u stack=16384\n", xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    for (uint32_t row = 0; row < SYN_CASE_COUNT; ++row) {
        assert(xPortGetCoreID() == WORKER_CORE);
        capture_t capture = {.row = row};
        vorbis_synthesis_pipeline_callbacks_t callbacks = {&capture, packet, pcm, error};
        vorbis_synthesis_pipeline_result_t result;
        printf("SYN_CASE row=%" PRIu32 " id=%s core=%d\n", row, syn_names[row], xPortGetCoreID());
        int status = vorbis_synthesis_pipeline_run(&syn_cases[row], &callbacks, &result);
        printf("SYN_END row=%" PRIu32 " status=%d packets=%" PRIu64 " frames=%" PRIu64
            " samples=%" PRIu64 " floor0=%" PRIu64 " floor1=%" PRIu64
            " allocations=%u releases=%u live_allocations=%u live_bytes=%u"
            " peak_allocations=%u peak_bytes=%u stack_free=%u heap_free=%u heap_min=%u core=%d\n",
            row, status, result.packets, result.frames, result.pcm_samples,
            result.floor0_channels, result.floor1_channels, (unsigned)result.allocations,
            (unsigned)result.releases, (unsigned)result.live_allocations, (unsigned)result.live_payload_bytes,
            (unsigned)result.peak_allocations, (unsigned)result.peak_payload_bytes,
            (unsigned)uxTaskGetStackHighWaterMark(NULL), (unsigned)esp_get_free_heap_size(),
            (unsigned)esp_get_minimum_free_heap_size(), xPortGetCoreID());
        assert(status == 0 && capture.emitted == capture.packet_samples);
        assert(result.live_allocations == 0 && result.live_payload_bytes == 0 && result.allocations == result.releases);
        packets += result.packets; frames += result.frames; samples += result.pcm_samples;
        vTaskDelay(1);
    }
    printf("SYN_COMPLETE cases=%u packets=%" PRIu64 " frames=%" PRIu64 " samples=%" PRIu64 " core=%d\n",
        (unsigned)SYN_CASE_COUNT, packets, frames, samples, xPortGetCoreID());
    printf("SYN_STOP status=CAPTURED\n"); fflush(stdout); esp_restart();
}

void app_main(void) {
    printf("SYN_BEGIN cases=%u coordinator=%d worker=%d data=%s\n",
        (unsigned)SYN_CASE_COUNT, xPortGetCoreID(), WORKER_CORE, SYN_CASES_SHA256);
    fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker, "vorbissynthesis", 16384, NULL, 3, NULL, WORKER_CORE) == pdPASS);
}
