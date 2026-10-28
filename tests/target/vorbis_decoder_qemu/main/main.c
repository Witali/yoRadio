// Exercise the persistent public owner directly, without the older batch helper.
#include <assert.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "native_vorbis_decoder.h"
#include "decoder_case.h"
#include "cases.h"

#ifdef NDEBUG
#error "Native decoder qualification requires active assertions"
#endif
#if CONFIG_IDF_TARGET_ESP32
enum { WORKER_CORE = 1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { WORKER_CORE = 0 };
#else
#error "Unsupported target"
#endif

enum { GUARD_BYTES = 16 };
static const uint64_t COOKIE = UINT64_C(0xdec0dec012345678);
typedef union {
    max_align_t alignment;
    struct { size_t bytes; uint64_t cookie; } record;
} allocation_t;
typedef struct {
    uint64_t allocations, releases, live, bytes, peak_live, peak_bytes;
    uint64_t attempts, failures, failed_bytes;
    bool clearing;
    native_vorbis_decoder_t **slot;
} tracker_t;
typedef struct { uint64_t packets, frames, samples, floor0, floor1; } totals_t;

static void *tracked_allocate(void *opaque, size_t bytes) {
    tracker_t *t = opaque;
    assert(bytes && bytes <= SIZE_MAX - sizeof(allocation_t) - GUARD_BYTES);
    ++t->attempts;
    allocation_t *h = malloc(sizeof(*h) + bytes + GUARD_BYTES);
    if (!h) { ++t->failures; t->failed_bytes = bytes; return NULL; }
    h->record.bytes = bytes; h->record.cookie = COOKIE;
    void *data = h + 1;
    memset((uint8_t *)data + bytes, 0xd7, GUARD_BYTES);
    ++t->allocations; ++t->live; t->bytes += bytes;
    if (t->live > t->peak_live) t->peak_live = t->live;
    if (t->bytes > t->peak_bytes) t->peak_bytes = t->bytes;
    return data;
}

static void tracked_release(void *opaque, void *data) {
    tracker_t *t = opaque;
    assert(data);
    if (t->clearing) assert(t->slot && !*t->slot);
    allocation_t *h = (allocation_t *)data - 1;
    assert(h->record.cookie == COOKIE && t->live && t->bytes >= h->record.bytes);
    for (unsigned i = 0; i < GUARD_BYTES; ++i)
        assert(((const uint8_t *)data)[h->record.bytes+i] == 0xd7);
    --t->live; t->bytes -= h->record.bytes; ++t->releases;
    h->record.cookie = 0;
    free(h);
}

static bool same_timing(const native_vorbis_timing_t *a, const native_vorbis_timing_t *b) {
    return a->short_size == b->short_size && a->long_size == b->long_size &&
        a->previous_size == b->previous_size && a->position_known == b->position_known &&
        a->end_seen == b->end_seen && a->bounded_sample_count == b->bounded_sample_count &&
        a->bounded_prediction == b->bounded_prediction;
}

static bool same_span(const native_vorbis_timing_result_t *a, const native_vorbis_timing_result_t *b) {
    return a->available == b->available && a->discard_start == b->discard_start &&
        a->discard_end == b->discard_end && a->count == b->count &&
        a->position_kind == b->position_kind && a->end_position == b->end_position;
}

static bool same_info(const native_vorbis_decoder_info_t *a, const native_vorbis_decoder_info_t *b) {
    const native_vorbis_identification_t *x = &a->identification, *y = &b->identification;
    return x->channels == y->channels && x->sample_rate == y->sample_rate &&
        x->bitrate_maximum_bits == y->bitrate_maximum_bits && x->bitrate_nominal_bits == y->bitrate_nominal_bits &&
        x->bitrate_minimum_bits == y->bitrate_minimum_bits && x->blocksize_0 == y->blocksize_0 &&
        x->blocksize_1 == y->blocksize_1 && same_timing(&a->timing, &b->timing) &&
        a->end_of_stream == b->end_of_stream;
}

static bool same_result(const native_vorbis_decoder_result_t *a, const native_vorbis_decoder_result_t *b) {
    return a->blocksize == b->blocksize && a->channels == b->channels &&
        a->floor0_channels == b->floor0_channels && a->floor1_channels == b->floor1_channels &&
        a->consumed_bits == b->consumed_bits && a->end_of_packet == b->end_of_packet &&
        a->synthesis.channels == b->synthesis.channels && a->synthesis.pcm_samples == b->synthesis.pcm_samples &&
        same_span(&a->synthesis.timing, &b->synthesis.timing);
}

static void poison(void *output, size_t bytes) { memset(output, 0xa5, bytes); }
static void unchanged(const void *output, size_t bytes) {
    for (size_t i = 0; i < bytes; ++i) assert(((const uint8_t *)output)[i] == 0xa5);
}
static uint64_t pcm_hash(const int16_t *pcm, size_t samples) {
    uint64_t hash = UINT64_C(14695981039346656037);
    for (size_t i = 0; i < samples; ++i) {
        uint16_t word = (uint16_t)pcm[i];
        hash ^= word & 255U; hash *= UINT64_C(1099511628211);
        hash ^= word >> 8; hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static native_vorbis_decoder_packet_t packet_copy(const decoder_case_t *c, uint32_t ordinal,
    uint8_t storage[DEC_MAX_PACKET_BYTES]) {
    assert(ordinal < c->packets && c->offsets[ordinal] <= c->offsets[ordinal+1] &&
        c->offsets[ordinal+1] <= c->audio_bytes);
    size_t bytes = c->offsets[ordinal+1] - c->offsets[ordinal];
    assert(bytes <= DEC_MAX_PACKET_BYTES && c->bits[ordinal] == (uint64_t)bytes * 8);
    memcpy(storage, c->audio+c->offsets[ordinal], bytes);
    return (native_vorbis_decoder_packet_t){.data = storage, .bytes = bytes, .bits = c->bits[ordinal],
        .granule_position = c->granules[ordinal], .end_of_stream = c->eos[ordinal] != 0,
        .discontinuity = c->gaps[ordinal] != 0};
}

static void emit_pcm(uint32_t row, uint32_t packet, const int16_t *pcm, size_t samples) {
    for (size_t start = 0; start < samples; start += 128) {
        size_t count = samples-start < 128 ? samples-start : 128;
        printf("DEC_PCM row=%" PRIu32 " packet=%" PRIu32 " start=%u count=%u core=%d runs=",
            row, packet, (unsigned)start, (unsigned)count, xPortGetCoreID());
        for (size_t i = 0; i < count;) {
            size_t end = i+1;
            while (end < count && pcm[start+end] == pcm[start+i]) ++end;
            printf("%s%04x:%u", i ? "," : "", (unsigned)(uint16_t)pcm[start+i], (unsigned)(end-i));
            i = end;
        }
        putchar('\n');
        vTaskDelay(1);
    }
}

static void run_resource_control(void) {
    native_vorbis_decoder_t *decoder = NULL;
    tracker_t owner = {.slot = &decoder};
    native_vorbis_setup_allocator_t allocator = {&owner, tracked_allocate, tracked_release};
    native_vorbis_decoder_status_t status = native_vorbis_decoder_replace(&decoder,
        dec_resource_identification, sizeof(dec_resource_identification), DEC_RESOURCE_IDENTIFICATION_BITS,
        dec_resource_setup, sizeof(dec_resource_setup), DEC_RESOURCE_SETUP_BITS, &allocator);
    assert(status == NATIVE_VORBIS_DECODER_NO_MEMORY && !decoder && !owner.live && !owner.bytes &&
        owner.allocations == owner.releases && owner.attempts == owner.allocations+1 &&
        owner.failures == 1 && owner.failed_bytes == UINT64_C(8355840));
    printf("DEC_RESOURCE status=%d channels=255 short=8192 long=8192 identification_bits=233 setup_bits=404"
        " failed_bytes=%" PRIu64 " failures=%" PRIu64 " attempts=%" PRIu64 " allocations=%" PRIu64
        " releases=%" PRIu64 " live=%" PRIu64 " bytes=%" PRIu64 " handle_null=1"
        " peak_allocations=%" PRIu64 " peak_bytes=%" PRIu64 " overhead=%u core=%d\n",
        status, owner.failed_bytes, owner.failures, owner.attempts, owner.allocations, owner.releases,
        owner.live, owner.bytes, owner.peak_live, owner.peak_bytes,
        (unsigned)(sizeof(allocation_t)+GUARD_BYTES), xPortGetCoreID());
    native_vorbis_decoder_clear(&decoder);
    assert(!decoder && owner.allocations == owner.releases);
    vTaskDelay(1);
}

static totals_t run_case(uint32_t row) {
    const decoder_case_t *c = &dec_cases[row];
    native_vorbis_decoder_t *decoder = NULL;
    tracker_t owner = {.slot = &decoder}, caller = {0};
    native_vorbis_setup_allocator_t allocator = {&owner, tracked_allocate, tracked_release};
    uint8_t identification[DEC_MAX_IDENTIFICATION_BYTES], setup[DEC_MAX_SETUP_BYTES], input[DEC_MAX_PACKET_BYTES];
    assert(c->identification_bytes <= sizeof(identification) && c->setup_bytes <= sizeof(setup));
    memcpy(identification, c->identification, c->identification_bytes);
    memcpy(setup, c->setup, c->setup_bytes);
    native_vorbis_decoder_status_t status = native_vorbis_decoder_replace(&decoder,
        identification, c->identification_bytes, (uint64_t)c->identification_bytes*8,
        setup, c->setup_bytes, (uint64_t)c->setup_bytes*8, &allocator);
    assert(status == NATIVE_VORBIS_DECODER_OK && decoder);
    memset(identification, 0x5a, sizeof(identification)); memset(setup, 0x5a, sizeof(setup));
    memset(&allocator, 0, sizeof(allocator)); // No caller descriptor/header borrow may survive replace.
    native_vorbis_decoder_info_t info;
    assert(native_vorbis_decoder_info(decoder, &info) == NATIVE_VORBIS_DECODER_OK);
    printf("DEC_OPEN row=%" PRIu32 " status=0 rate=%" PRIu32 " channels=%" PRIu32
        " short=%" PRIu32 " long=%" PRIu32 " allocator_copy=1 headers_poisoned=1"
        " allocations=%" PRIu64 " releases=%" PRIu64 " live=%" PRIu64 " bytes=%" PRIu64 " core=%d\n",
        row, info.identification.sample_rate, info.identification.channels, info.identification.blocksize_0,
        info.identification.blocksize_1, owner.allocations, owner.releases, owner.live, owner.bytes, xPortGetCoreID());
    size_t maximum = (size_t)info.identification.channels * (info.identification.blocksize_1/2);
    assert(maximum && maximum <= SIZE_MAX/sizeof(int16_t));
    size_t output_bytes = maximum*sizeof(int16_t);
    int16_t *output = tracked_allocate(&caller, output_bytes), *warm = tracked_allocate(&caller, output_bytes);
    assert(output && warm);
    printf("DEC_BUFFER row=%" PRIu32 " samples=%u caller_allocations=%" PRIu64
        " caller_bytes=%" PRIu64 " overhead=%u core=%d\n", row, (unsigned)maximum,
        caller.allocations, caller.bytes, (unsigned)(sizeof(allocation_t)+GUARD_BYTES), xPortGetCoreID());
    native_vorbis_decoder_result_t saved[2]; size_t warm_offsets[3] = {0};
    totals_t totals = {0};
    for (uint32_t ordinal = 0; ordinal < c->packets; ++ordinal) {
        native_vorbis_decoder_packet_t packet = packet_copy(c, ordinal, input);
        native_vorbis_decoder_info_t before = info;
        native_vorbis_decoder_requirements_t needed;
        uint64_t allocations = owner.allocations, releases = owner.releases;
        assert(native_vorbis_decoder_measure(decoder, &packet, &needed) == NATIVE_VORBIS_DECODER_OK &&
            owner.allocations == allocations && owner.releases == releases && needed.pcm_samples <= maximum);
        assert(native_vorbis_decoder_info(decoder, &info) == 0 && same_info(&before, &info));
        native_vorbis_decoder_result_t result;
        poison(output, output_bytes); poison(&result, sizeof(result));
        size_t refused_capacity = needed.pcm_samples ? (size_t)needed.pcm_samples-1 : SIZE_MAX;
        int expected = needed.pcm_samples ? NATIVE_VORBIS_DECODER_OUTPUT_CAPACITY : NATIVE_VORBIS_DECODER_RANGE;
        status = native_vorbis_decoder_process(decoder, &packet, output, refused_capacity, &result);
        assert(status == expected && owner.allocations == allocations && owner.releases == releases);
        unchanged(output, output_bytes); unchanged(&result, sizeof(result));
        assert(native_vorbis_decoder_info(decoder, &info) == 0 && same_info(&before, &info));
        printf("DEC_REFUSAL row=%" PRIu32 " packet=%" PRIu32 " status=%d required=%" PRIu64
            " supplied=%" PRIu64 " allocations_before=%" PRIu64 " allocations_after=%" PRIu64
            " releases_before=%" PRIu64 " releases_after=%" PRIu64
            " output_equal=1 result_equal=1 info_equal=1 core=%d\n", row, ordinal, status,
            needed.pcm_samples, (uint64_t)refused_capacity, allocations, owner.allocations,
            releases, owner.releases, xPortGetCoreID());
        status = native_vorbis_decoder_process(decoder, &packet, output, maximum, &result);
        assert(status == 0 && result.blocksize == needed.blocksize && result.channels == needed.channels &&
            result.synthesis.channels == result.channels && result.synthesis.pcm_samples == needed.pcm_samples &&
            same_span(&result.synthesis.timing, &needed.timing));
        size_t count = (size_t)result.synthesis.pcm_samples;
        unchanged((uint8_t *)output+count*sizeof(*output), output_bytes-count*sizeof(*output));
        if (ordinal < 2) {
            saved[ordinal] = result;
            assert(warm_offsets[ordinal] <= maximum-count);
            memcpy(warm+warm_offsets[ordinal], output, count*sizeof(*output));
            warm_offsets[ordinal+1] = warm_offsets[ordinal]+count;
        }
        const native_vorbis_timing_result_t *t = &result.synthesis.timing;
        printf("DEC_PACKET row=%" PRIu32 " packet=%" PRIu32 " block=%" PRIu32 " channels=%" PRIu32
            " floor0=%" PRIu32 " floor1=%" PRIu32 " bits=%" PRIu64 " eop=%u available=%" PRIu32
            " discard_start=%" PRIu32 " discard_end=%" PRIu32 " frames=%" PRIu32 " position=%u end=%" PRId64
            " samples=%" PRIu64 " granule=%" PRId64 " eos=%u gap=%u allocations=%" PRIu64
            " releases=%" PRIu64 " live=%" PRIu64 " bytes=%" PRIu64 " core=%d\n", row, ordinal,
            result.blocksize, result.channels, result.floor0_channels, result.floor1_channels,
            result.consumed_bits, (unsigned)result.end_of_packet, t->available, t->discard_start,
            t->discard_end, t->count, (unsigned)t->position_kind, t->end_position, result.synthesis.pcm_samples,
            packet.granule_position, (unsigned)packet.end_of_stream, (unsigned)packet.discontinuity,
            owner.allocations, owner.releases, owner.live, owner.bytes, xPortGetCoreID());
        assert(native_vorbis_decoder_info(decoder, &info) == 0);
        printf("DEC_INFO row=%" PRIu32 " packet=%" PRIu32 " previous=%" PRIu32 " known=%" PRIu32
            " eos=%" PRIu32 " sample_count=%" PRIu64 " prediction=%" PRIu64 " terminal=%u core=%d\n",
            row, ordinal, info.timing.previous_size, info.timing.position_known, info.timing.end_seen,
            info.timing.bounded_sample_count, info.timing.bounded_prediction, (unsigned)info.end_of_stream, xPortGetCoreID());
        emit_pcm(row, ordinal, output, count);
        ++totals.packets; totals.frames += t->count; totals.samples += count;
        totals.floor0 += result.floor0_channels; totals.floor1 += result.floor1_channels;
        memset(input, 0x5a, sizeof(input)); // No completed packet borrow survives process.
        vTaskDelay(1);
    }
    assert(info.end_of_stream && c->packets >= 2);
    native_vorbis_decoder_info_t terminal = info;
    native_vorbis_decoder_packet_t first = packet_copy(c, 0, input);
    native_vorbis_decoder_requirements_t requirements;
    native_vorbis_decoder_result_t result;
    poison(output, output_bytes); poison(&requirements, sizeof(requirements)); poison(&result, sizeof(result));
    uint64_t allocations = owner.allocations, releases = owner.releases;
    int measured = native_vorbis_decoder_measure(decoder, &first, &requirements);
    int processed = native_vorbis_decoder_process(decoder, &first, output, maximum, &result);
    assert(measured == NATIVE_VORBIS_DECODER_END_OF_STREAM && processed == NATIVE_VORBIS_DECODER_END_OF_STREAM &&
        owner.allocations == allocations && owner.releases == releases);
    unchanged(output, output_bytes); unchanged(&requirements, sizeof(requirements)); unchanged(&result, sizeof(result));
    assert(native_vorbis_decoder_info(decoder, &info) == 0 && same_info(&terminal, &info));
    printf("DEC_EOS row=%" PRIu32 " measure=%d process=%d allocations_delta=0 releases_delta=0"
        " output_equal=1 result_equal=1 requirements_equal=1 info_equal=1 core=%d\n",
        row, measured, processed, xPortGetCoreID());
    assert(native_vorbis_decoder_reset(decoder) == 0 && owner.allocations == allocations && owner.releases == releases);
    assert(native_vorbis_decoder_info(decoder, &info) == 0 && !info.end_of_stream && !info.timing.previous_size &&
        !info.timing.position_known && !info.timing.end_seen && !info.timing.bounded_sample_count && !info.timing.bounded_prediction);
    printf("DEC_RESET row=%" PRIu32 " allocations_delta=0 releases_delta=0 primed=0 terminal=0 core=%d\n", row, xPortGetCoreID());
    for (uint32_t ordinal = 0; ordinal < 2; ++ordinal) {
        native_vorbis_decoder_packet_t packet = packet_copy(c, ordinal, input);
        assert(native_vorbis_decoder_measure(decoder, &packet, &requirements) == 0);
        poison(output, output_bytes);
        assert(native_vorbis_decoder_process(decoder, &packet, output, maximum, &result) == 0 &&
            same_result(&result, &saved[ordinal]) && owner.allocations == allocations && owner.releases == releases);
        size_t count = (size_t)result.synthesis.pcm_samples;
        assert(count == warm_offsets[ordinal+1]-warm_offsets[ordinal] && !memcmp(output, warm+warm_offsets[ordinal], count*sizeof(*output)));
        unchanged((uint8_t *)output+count*sizeof(*output), output_bytes-count*sizeof(*output));
        printf("DEC_RETRY row=%" PRIu32 " packet=%" PRIu32 " samples=%u result_equal=1 pcm_equal=1"
            " pcm_hash=%" PRIu64 " allocations_delta=0 releases_delta=0 core=%d\n",
            row, ordinal, (unsigned)count, pcm_hash(output, count), xPortGetCoreID());
        memset(input, 0x5a, sizeof(input));
        vTaskDelay(1);
    }
    owner.clearing = true;
    native_vorbis_decoder_clear(&decoder);
    owner.clearing = false;
    assert(!decoder && !owner.live && !owner.bytes && owner.allocations == owner.releases);
    allocations = owner.allocations; releases = owner.releases;
    native_vorbis_decoder_clear(&decoder); native_vorbis_decoder_clear(NULL);
    assert(owner.allocations == allocations && owner.releases == releases);
    printf("DEC_CLEAR row=%" PRIu32 " handle_null=1 allocations=%" PRIu64 " releases=%" PRIu64
        " live=0 bytes=0 caller_live=%" PRIu64 " null_noops=1 core=%d\n",
        row, owner.allocations, owner.releases, caller.live, xPortGetCoreID());
    tracked_release(&caller, warm); tracked_release(&caller, output);
    assert(!caller.live && !caller.bytes && caller.allocations == caller.releases);
    printf("DEC_END row=%" PRIu32 " status=0 packets=%" PRIu64 " frames=%" PRIu64 " samples=%" PRIu64
        " floor0=%" PRIu64 " floor1=%" PRIu64 " capacity_refusals=%" PRIu32 " terminal_refusals=2 resets=1 retries=2 clears=1"
        " owner_allocations=%" PRIu64 " owner_releases=%" PRIu64 " owner_live=0 owner_bytes=0"
        " owner_peak_allocations=%" PRIu64 " owner_peak_bytes=%" PRIu64
        " caller_allocations=%" PRIu64 " caller_releases=%" PRIu64 " caller_live=0 caller_bytes=0"
        " caller_peak_allocations=%" PRIu64 " caller_peak_bytes=%" PRIu64
        " overhead=%u stack_free=%u heap_free=%u heap_min=%u core=%d\n", row, totals.packets,
        totals.frames, totals.samples, totals.floor0, totals.floor1, c->packets,
        owner.allocations, owner.releases, owner.peak_live, owner.peak_bytes,
        caller.allocations, caller.releases, caller.peak_live, caller.peak_bytes,
        (unsigned)(sizeof(allocation_t)+GUARD_BYTES), (unsigned)uxTaskGetStackHighWaterMark(NULL),
        (unsigned)esp_get_free_heap_size(), (unsigned)esp_get_minimum_free_heap_size(), xPortGetCoreID());
    return totals;
}

static void worker(void *unused) {
    (void)unused;
    totals_t total = {0};
    printf("DEC_WORKER core=%d priority=%u stack=16384\n", xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    run_resource_control(); // The unchanged full small corpus must recover afterward.
    for (uint32_t row = 0; row < DEC_CASE_COUNT; ++row) {
        assert(xPortGetCoreID() == WORKER_CORE);
        printf("DEC_CASE row=%" PRIu32 " id=%s core=%d\n", row, dec_names[row], xPortGetCoreID());
        totals_t one = run_case(row);
        total.packets += one.packets; total.frames += one.frames; total.samples += one.samples;
        vTaskDelay(1);
    }
    printf("DEC_COMPLETE cases=%u packets=%" PRIu64 " frames=%" PRIu64 " samples=%" PRIu64
        " capacity_refusals=%" PRIu64 " terminal_refusals=%u resets=%u retries=%u clears=%u"
        " live_owner=0 live_caller=0 core=%d\n", (unsigned)DEC_CASE_COUNT, total.packets,
        total.frames, total.samples, total.packets, 2U*DEC_CASE_COUNT, (unsigned)DEC_CASE_COUNT,
        2U*DEC_CASE_COUNT, (unsigned)DEC_CASE_COUNT, xPortGetCoreID());
    printf("DEC_STOP status=CAPTURED\n"); fflush(stdout); esp_restart();
}

void app_main(void) {
    printf("DEC_BEGIN cases=%u coordinator=%d worker=%d data=%s transport=%s resource=%s\n",
        (unsigned)DEC_CASE_COUNT, xPortGetCoreID(), WORKER_CORE, DEC_CASES_SHA256, DEC_TRANSPORT_SHA256,
        DEC_RESOURCE_SHA256);
    fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker, "vorbisdecoder", 16384, NULL, 3, NULL, WORKER_CORE) == pdPASS);
}
