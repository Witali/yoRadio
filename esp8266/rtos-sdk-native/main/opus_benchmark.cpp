/* Diagnostic-only raw-packet benchmark. Wi-Fi, WebUI and OTA remain running;
 * no HTTP audio, demux, normalizer or output is included in the decode window. */
#include "opus_benchmark.h"
#include "CodecMemoryArena.h"
#include "codec_arena_native.h"
#include "opus.h"
#include "opus_memory.h"
#if YORADIO_OPUS_PROFILE_STAGE
#include "opus_stage_profile.h"
#endif
#include "opus_board_fixtures.h"
#include <string.h>
extern "C" {
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
#include "native_audio_output.h"
#endif
}
#if !configGENERATE_RUN_TIME_STATS || !configUSE_TRACE_FACILITY || !CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER
#error "Opus benchmark needs microsecond FreeRTOS runtime counters"
#endif

namespace {
/* 12 x 20-ms own packets per round: output mode measures 24 seconds/case.
 * Round zero warms the SAME decoder/output path but is not scored. */
constexpr unsigned kRounds = YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT ? 100 : 10;
constexpr unsigned kPcmSamples = 960, kPacketBytes = 1536;
opus_benchmark_status_t s_status;
opus_benchmark_case_t s_results[OPUS_BENCH_FIXTURE_COUNT];

uint32_t dram_free() { return heap_caps_get_free_size(MALLOC_CAP_8BIT); }
uint32_t task_time() {
    TaskStatus_t status;
    vTaskGetInfo(nullptr, &status, pdFALSE, eRunning);
    return status.ulRunTimeCounter;
}
/* Flush current-task runtime before/after the timed interval. Runtime counts
 * exclude other tasks but still charge ISR time to the interrupted task.
 * The empty interval quantifies the small snapshot/timer/switch overhead. */
uint32_t empty_interval() {
    vTaskDelay(1);
    uint32_t before = task_time();
    (void)esp_timer_get_time();
    (void)esp_timer_get_time();
    vTaskDelay(1);
    return task_time() - before;
}
void copy_words(void *to, const void *from, size_t bytes) {
    uint32_t *d = static_cast<uint32_t *>(to);
    const volatile uint32_t *s = static_cast<const volatile uint32_t *>(from);
    for (size_t n = 0; n < (bytes + 3U) / 4U; ++n) d[n] = s[n];
}
uint32_t pcm_hash(uint32_t hash, const int16_t *pcm, unsigned count) {
    for (unsigned i = 0; i < count; ++i) {
        uint16_t sample = (uint16_t)pcm[i];
        hash = (hash ^ (sample & 255U)) * 16777619U;
        hash = (hash ^ (sample >> 8)) * 16777619U;
    }
    return hash;
}
void publish(unsigned index, unsigned round, const opus_benchmark_case_t &result) {
    taskENTER_CRITICAL();
    s_status.current_case = index;
    s_status.round = round;
    s_results[index] = result;
    taskEXIT_CRITICAL();
}
}

extern "C" bool opus_benchmark_request(void) {
    taskENTER_CRITICAL();
    bool accepted = s_status.state != 1 && s_status.state != 2;
    if (accepted) {
        uint32_t run = s_status.run + 1;
        memset(&s_status, 0, sizeof(s_status));
        memset(s_results, 0, sizeof(s_results));
        s_status.run = run;
        s_status.state = 1; /* queued; 2 running, 3 complete, 4 error/cancelled */
        s_status.cases = OPUS_BENCH_FIXTURE_COUNT;
        s_status.rounds = kRounds;
    }
    taskEXIT_CRITICAL();
    return accepted;
}
extern "C" void opus_benchmark_cancel_pending(void) {
    taskENTER_CRITICAL();
    if (s_status.state == 1) { s_status.state = 4; s_status.error = -9002; }
    taskEXIT_CRITICAL();
}
extern "C" void opus_benchmark_snapshot(opus_benchmark_status_t *status) {
    taskENTER_CRITICAL();
    *status = s_status;
    taskEXIT_CRITICAL();
}
extern "C" void opus_benchmark_case_snapshot(unsigned index, opus_benchmark_case_t *result) {
    taskENTER_CRITICAL();
    if (index < OPUS_BENCH_FIXTURE_COUNT) *result = s_results[index];
    else memset(result, 0, sizeof(*result));
    taskEXIT_CRITICAL();
}

extern "C" __attribute__((noinline)) void opus_benchmark_run_pending(
    uint32_t generation, bool (*current)(uint32_t)) {
    taskENTER_CRITICAL();
    bool pending = s_status.state == 1;
    if (pending) s_status.state = 2;
    taskEXIT_CRITICAL();
    if (!pending) return;

    const size_t state_bytes = opus_decoder_get_size(1);
    uint32_t before = dram_free();
    int error = 0;
    bool bound = false;
    void *state = nullptr, *scratch = nullptr, *words = nullptr;
    int16_t *pcm = nullptr;
    unsigned char *packet = nullptr;
    taskENTER_CRITICAL();
    s_status.dram_before = before;
    s_status.state_bytes = state_bytes;
    taskEXIT_CRITICAL();
    if (!CodecArenaPreallocatedInIram() ||
        !(bound = CodecArenaBind(nullptr, 16384))) error = -9003;
    if (!error) words = CodecArenaCalloc32(CODEC_ARENA_OPUS, 4096, 4);
    if (!error) {
        state = heap_caps_malloc(state_bytes, MALLOC_CAP_8BIT);
        scratch = heap_caps_malloc(CONFIG_YORADIO_OPUS_SCRATCH_BYTES, MALLOC_CAP_8BIT);
        pcm = static_cast<int16_t *>(heap_caps_malloc(kPcmSamples * 2, MALLOC_CAP_8BIT));
        packet = static_cast<unsigned char *>(heap_caps_malloc(kPacketBytes, MALLOC_CAP_8BIT));
        if (!words || !state || !scratch || !pcm || !packet || dram_free() < 2048)
            error = -9001;
    }
    if (!error) {
        yoradio_opus_memory_bind(scratch, CONFIG_YORADIO_OPUS_SCRATCH_BYTES, words, 16384);
        uint32_t empty = 0;
        for (unsigned i = 0; i < 16; ++i) empty += empty_interval();
        taskENTER_CRITICAL();
        s_status.empty_task_us = (empty + 8) / 16;
        taskEXIT_CRITICAL();
#if YORADIO_OPUS_PROFILE_STAGE
        uint32_t clock_min = UINT32_MAX, clock_max = 0;
        for (unsigned i = 0; i < 128; ++i) {
            uint32_t start = opus_stage_profile_clock();
            uint32_t elapsed = opus_stage_profile_clock() - start;
            if (elapsed < clock_min) clock_min = elapsed;
            if (elapsed > clock_max) clock_max = elapsed;
        }
        taskENTER_CRITICAL();
        s_status.clock_pair_ticks_min = clock_min;
        s_status.clock_pair_ticks_max = clock_max;
        taskEXIT_CRITICAL();
#endif
        for (unsigned f = 0; f < OPUS_BENCH_FIXTURE_COUNT && !error; ++f) {
            opus_bench_fixture_t fixture;
            copy_words(&fixture, &opus_bench_fixtures[f], sizeof(fixture));
            if (fixture.first_packet > OPUS_BENCH_PACKET_COUNT ||
                fixture.packet_count > OPUS_BENCH_PACKET_COUNT - fixture.first_packet) {
                error = -9004; break;
            }
            /* Reset scratch high-water for this case, outside active decode. */
            yoradio_opus_memory_bind(scratch, CONFIG_YORADIO_OPUS_SCRATCH_BYTES, words, 16384);
            opus_benchmark_case_t result = {};
            result.min_dram = dram_free();
            result.stack_free = UINT32_MAX;
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
            native_audio_output_silence();
            native_audio_output_reset_normalizer();
            uint32_t pipeline_start = 0, pipeline_cpu = 0;
            native_audio_output_spi_stats_t dma_before = {};
#endif
            unsigned last_round = 0;
            for (unsigned round = 0; round <= kRounds && !error; ++round) {
                last_round = round;
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
                if (round == 1) {
                    /* Last warmup packet yielded and flushed task runtime.
                     * Keep DMA running across all measured round boundaries. */
                    native_audio_output_get_spi_stats(&dma_before);
                    (void)native_audio_output_fifo_empty(1);
                    pipeline_cpu = task_time();
                    pipeline_start = (uint32_t)esp_timer_get_time();
                }
#endif
                /* Round zero warms flash/decoder and checks the same golden PCM. */
                error = opus_decoder_init(static_cast<OpusDecoder *>(state), 48000, 1);
                uint32_t hash = 2166136261U, samples = 0;
                for (unsigned p = 0; p < fixture.packet_count && !error; ++p) {
                    if (!current(generation)) { error = -9002; break; }
                    opus_bench_packet_t entry;
                    copy_words(&entry, &opus_bench_packets[fixture.first_packet + p], sizeof(entry));
                    if (!entry.length || entry.length > kPacketBytes || (entry.offset & 3) ||
                        entry.offset > OPUS_BENCH_PAYLOAD_BYTES ||
                        ((entry.length + 3U) & ~3U) > OPUS_BENCH_PAYLOAD_BYTES - entry.offset) {
                        error = -9004; break;
                    }
                    copy_words(packet, reinterpret_cast<const unsigned char *>(opus_bench_payload) + entry.offset,
                               entry.length);
#if !YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
                    vTaskDelay(1);
                    uint32_t cpu = task_time();
#endif
#if YORADIO_OPUS_PROFILE_STAGE
                    opus_stage_profile_reset();
                    uint32_t start = opus_stage_profile_clock();
#else
                    int64_t start = esp_timer_get_time();
#endif
                    int decoded = yoradio_opus_decode_bounded(state, packet, entry.length, pcm, kPcmSamples);
#if YORADIO_OPUS_PROFILE_STAGE
                    uint32_t elapsed = opus_stage_profile_clock() - start;
                    const opus_stage_profile_t stage = opus_stage_profile_snapshot();
                    if (round) {
                        result.stage_ticks += stage.ticks;
                        result.stage_calls += stage.calls;
                        if (stage.max_ticks > result.stage_max_ticks)
                            result.stage_max_ticks = stage.max_ticks;
                    }
#else
                    uint32_t elapsed = (uint32_t)(esp_timer_get_time() - start);
#endif
#if !YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
                    vTaskDelay(1);
                    cpu = task_time() - cpu;
#endif
                    if (decoded <= 0) { error = decoded ? decoded : -9005; break; }
                    if ((unsigned)decoded > kPcmSamples) { error = -9010; break; }
                    hash = pcm_hash(hash, pcm, decoded);
                    samples += decoded;
                    if (round) {
                        ++result.packets;
                        result.samples += decoded;
                        result.wall_us += elapsed;
#if !YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
                        result.task_us += cpu;
#endif
                        if (elapsed > result.max_wall_us) result.max_wall_us = elapsed;
                    }
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
                    /* Hash BEFORE output mutates PCM with gain/normalization.
                     * Match the native Opus adapter's <=512-sample callbacks.
                     * No extra PCM buffer, TCP socket, Ogg parsing or ICY here. */
                    const uint32_t output_start = (uint32_t)esp_timer_get_time();
                    for (unsigned offset = 0; offset < (unsigned)decoded;) {
                        if (!current(generation)) { error = -9002; break; }
                        unsigned count = (unsigned)decoded - offset;
                        if (count > 512) count = 512;
                        if (native_audio_output_write(pcm + offset, count, 48000, 1) != ESP_OK) {
                            error = -9008; break;
                        }
                        offset += count;
                        if (round) result.output_samples += count;
                    }
                    const uint32_t output_us = (uint32_t)esp_timer_get_time() - output_start;
                    /* Exactly the ordinary post-packet yield; do not keep the
                     * raw benchmark's two extra timing yields in this mode. */
                    vTaskDelay(1);
                    if (round) {
                        result.output_wall_us += output_us;
                        if (output_us > result.max_output_us) result.max_output_us = output_us;
                        result.pipeline_task_us = task_time() - pipeline_cpu;
                        result.pipeline_wall_us = (uint32_t)esp_timer_get_time() - pipeline_start;
                        native_audio_output_spi_stats_t dma;
                        native_audio_output_get_spi_stats(&dma);
                        result.dma_eofs = dma.chained_transfers - dma_before.chained_transfers;
                        result.dma_misses = dma.queue_empty_events - dma_before.queue_empty_events;
                        result.fifo_empty_seen = native_audio_output_fifo_empty(0);
                    }
#endif
                    result.scratch_bytes = yoradio_opus_scratch_peak_bytes();
                    result.scratch_words = yoradio_opus_scratch_peak_words();
                    uint32_t free = dram_free();
                    if (free < result.min_dram) result.min_dram = free;
                    uint32_t stack = uxTaskGetStackHighWaterMark(nullptr);
                    if (stack < result.stack_free) result.stack_free = stack;
                    publish(f, round, result);
                }
                result.pcm_hash = hash;
                if (!error && (hash != fixture.expected_hash || samples != fixture.samples))
                    error = -9006;
            }
            result.error = error;
            publish(f, last_round, result);
        }
        yoradio_opus_memory_bind(nullptr, 0, nullptr, 0);
    }
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
    /* Also cancel any in-flight output after OOM, generation changes, decoder
     * or sink errors. DMA owns its copied PDM, never these freed PCM arrays. */
    native_audio_output_silence();
#endif
    heap_caps_free(packet);
    heap_caps_free(pcm);
    heap_caps_free(scratch);
    heap_caps_free(state);
    if (bound) {
        CodecArenaFree(words);
        CodecArenaRelease(CODEC_ARENA_OPUS);
        if (!CodecArenaUnbind() && !error) error = -9007;
    }
    taskENTER_CRITICAL();
    s_status.dram_after = dram_free();
    s_status.error = error;
    s_status.state = error ? 4 : 3;
    taskEXIT_CRITICAL();
}
