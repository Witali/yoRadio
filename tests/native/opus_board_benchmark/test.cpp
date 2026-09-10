#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include "opus_benchmark.h"
#if YORADIO_OPUS_PROFILE_STAGE
#include "opus_stage_profile.h"
#endif
#include "CodecMemoryArena.h"
#include "codec_arena_native.h"
#include "opus.h"
#include "opus_memory.h"
#include "opus_board_fixtures.h"
extern "C" {
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
#include "native_audio_output.h"
#endif
}

namespace {
constexpr size_t kStateBytes = 64, kFreeDram = 65536, kGuardBytes = 16;
constexpr unsigned kRounds = YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT ? 100 : 10;
constexpr unsigned char kGuard = 0x5a;
struct Allocation { unsigned char *base; size_t bytes; bool dram; };
std::map<void *, Allocation> live;
unsigned attempts, allocations, frees, failures, fail_at, decode_calls, init_calls;
unsigned memory_binds, memory_unbinds, releases, unbinds, critical_depth;
unsigned total_allocations, total_frees, total_failures, completed_runs;
uint32_t clock_wall, clock_task;
bool arena_bound, arena_iram = true, reject_bind, reject_unbind, low_reserve;
bool wrong_pcm, poll_busy, checked_busy;
unsigned cancel_after, decode_error_at, init_error_at;
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
unsigned output_calls, output_error_at, output_misses_at, dma_eofs, dma_misses;
unsigned silence_calls, normalizer_resets, output_sample_count;
unsigned fifo_empty, fifo_error_at;
bool oversized_decode, large_decode;
#endif
int decode_error = -777;
void *arena_words, *bound_scratch, *bound_words;
uint32_t generation = 73;

opus_benchmark_status_t status() {
    opus_benchmark_status_t value;
    opus_benchmark_snapshot(&value);
    return value;
}
opus_benchmark_case_t result(unsigned index) {
    opus_benchmark_case_t value;
    opus_benchmark_case_snapshot(index, &value);
    return value;
}
void guards() {
    for (const auto &entry : live) {
        const auto &block = entry.second;
        for (size_t n = 0; n < kGuardBytes; ++n) {
            assert(block.base[n] == kGuard);
            assert(block.base[kGuardBytes + block.bytes + n] == kGuard);
        }
    }
}
void *allocate(size_t bytes, bool dram) {
    ++attempts;
    if (attempts == fail_at) { ++failures; ++total_failures; return nullptr; }
    auto *base = static_cast<unsigned char *>(malloc(bytes + 2 * kGuardBytes));
    assert(base);
    memset(base, kGuard, bytes + 2 * kGuardBytes);
    void *pointer = base + kGuardBytes;
    assert((reinterpret_cast<uintptr_t>(pointer) & 3) == 0);
    assert(live.emplace(pointer, Allocation{base, bytes, dram}).second);
    ++allocations; ++total_allocations;
    return pointer;
}
void deallocate(void *pointer) {
    if (!pointer) return;
    guards();
    auto entry = live.find(pointer);
    assert(entry != live.end());
    free(entry->second.base);
    live.erase(entry);
    ++frees; ++total_frees;
}
void clean() {
    assert(live.empty());
    assert(allocations == frees);
    assert(!arena_bound && !arena_words && !bound_scratch && !bound_words);
    assert(critical_depth == 0);
}
void reset_environment() {
    clean();
    attempts = allocations = frees = failures = fail_at = decode_calls = init_calls = 0;
    memory_binds = memory_unbinds = releases = unbinds = 0;
    clock_wall = clock_task = 0;
    arena_iram = true;
    reject_bind = reject_unbind = low_reserve = wrong_pcm = poll_busy = checked_busy = false;
    cancel_after = decode_error_at = init_error_at = 0;
    decode_error = -777;
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
    output_calls = output_error_at = output_misses_at = dma_eofs = dma_misses = 0;
    silence_calls = normalizer_resets = output_sample_count = 0;
    fifo_empty = fifo_error_at = 0;
    oversized_decode = large_decode = false;
#endif
}
bool current(uint32_t supplied) {
    assert(supplied == generation);
    assert(critical_depth == 0);
    assert(status().state == 2);
    if (poll_busy) {
        const auto before = status();
        assert(!opus_benchmark_request());
        opus_benchmark_cancel_pending(); // only queued work is cancelled here
        assert(status().state == 2 && status().run == before.run);
        checked_busy = true;
    }
    return !cancel_after || decode_calls < cancel_after;
}
void queue() {
    const uint32_t prior = status().run;
    assert(opus_benchmark_request());
    auto queued = status();
    assert(queued.state == 1 && queued.run == prior + 1);
    assert(queued.cases == 2 && queued.rounds == kRounds);
    assert(!queued.error && !result(0).packets && !result(1).packets);
    assert(!opus_benchmark_request());
    assert(status().run == queued.run && status().state == 1);
    assert(!attempts);
}
void run() { opus_benchmark_run_pending(generation, current); }
void expect_error(int error) {
    const auto final = status();
    assert(final.state == 4 && final.error == error);
    assert(final.dram_before == kFreeDram && final.dram_after == kFreeDram);
    clean();
}
void successful_run() {
    reset_environment();
    poll_busy = true;
    queue(); run();
    const auto final = status();
    assert(final.state == 3 && !final.error && final.current_case == 1);
    assert(final.dram_before == kFreeDram && final.dram_after == kFreeDram);
    assert(final.state_bytes == kStateBytes && final.empty_task_us == 4);
    assert(decode_calls == 4 * (kRounds + 1) && init_calls == 2 * (kRounds + 1));
    assert(attempts == 5 && allocations == 5 && frees == 5);
    assert(memory_binds == 3 && memory_unbinds == 1 && releases == 1 && unbinds == 1);
    assert(checked_busy);
    for (unsigned f = 0; f < 2; ++f) {
        const auto value = result(f);
        assert(!value.error && value.packets == 2 * kRounds && value.samples == 8 * kRounds);
        assert(value.pcm_hash == 0x03c13f4fU);
#if YORADIO_OPUS_PROFILE_STAGE
        assert(value.stage_calls == value.packets);
        assert(value.stage_cycles == UINT64_C(16000) * value.packets);
        assert(value.stage_max_cycles == 16000);
        assert(final.clock_pair_cycles_min == 0 && final.clock_pair_cycles_max == 0);
#endif
        assert(value.wall_us == 2 * kRounds * 251 && value.max_wall_us == 251);
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
        assert(value.task_us == 0); // Never label pipeline CPU as decoder-only.
        assert(value.output_samples == value.samples);
        assert(value.pipeline_wall_us > value.wall_us + value.output_wall_us);
        assert(value.pipeline_task_us > 0 && value.output_wall_us > 0);
        assert(value.dma_eofs == 2 * kRounds && value.dma_misses == 0);
        assert(value.fifo_empty_seen == 0);
#else
        assert(value.task_us == 2 * kRounds * 204);
#endif
        assert(value.scratch_bytes == 1024 && value.scratch_words == 12000);
        assert(value.stack_free == 1234);
        assert(value.min_dram == kFreeDram - kStateBytes - CONFIG_YORADIO_OPUS_SCRATCH_BYTES - 1920 - 1536);
    }
    const auto invalid = result(2);
    const opus_benchmark_case_t zero = {};
    assert(!memcmp(&invalid, &zero, sizeof(zero)));
    clean();
    run(); // complete work must not execute twice without a new request
    assert(decode_calls == 4 * (kRounds + 1) && attempts == 5);
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
    assert(silence_calls == 3 && normalizer_resets == 2);
    assert(output_calls == decode_calls && output_sample_count == decode_calls * 4);
#endif
    ++completed_runs;
}
}

extern "C" void test_enter_critical(void) { assert(critical_depth++ == 0); }
#if YORADIO_OPUS_PROFILE_STAGE
extern "C" uint32_t opus_stage_profile_clock(void) { return clock_wall * 160; }
#endif
extern "C" void test_exit_critical(void) { assert(critical_depth-- == 1); }
extern "C" void vTaskGetInfo(TaskHandle_t task, TaskStatus_t *value, int stack, eTaskState state) {
    assert(!task && !stack && state == eRunning); value->ulRunTimeCounter = clock_task;
}
extern "C" void vTaskDelay(unsigned ticks) {
    assert(critical_depth == 0 && ticks == 1); clock_wall += 100; clock_task += 2;
}
extern "C" UBaseType_t uxTaskGetStackHighWaterMark(TaskHandle_t task) { assert(!task); return 1234; }
extern "C" int64_t esp_timer_get_time(void) { ++clock_task; return clock_wall++; }
extern "C" void *heap_caps_malloc(size_t bytes, unsigned caps) {
    assert(caps == MALLOC_CAP_8BIT); return allocate(bytes, true);
}
extern "C" void heap_caps_free(void *pointer) {
    if (pointer) assert(live.at(pointer).dram);
    deallocate(pointer);
}
extern "C" size_t heap_caps_get_free_size(unsigned caps) {
    assert(caps == MALLOC_CAP_8BIT);
    if (low_reserve && !live.empty()) return 1800;
    size_t free_bytes = kFreeDram;
    for (const auto &entry : live) if (entry.second.dram) free_bytes -= entry.second.bytes;
    return free_bytes;
}
bool CodecArenaPreallocatedInIram(void) { return arena_iram; }
bool CodecArenaBind(uint8_t *memory, size_t capacity) {
    assert(!arena_bound && !memory && capacity == 16384);
    if (reject_bind) return false;
    arena_bound = true; return true;
}
void *CodecArenaCalloc32(CodecArenaOwner owner, size_t count, size_t bytes) {
    assert(arena_bound && !arena_words && owner == CODEC_ARENA_OPUS && count == 4096 && bytes == 4);
    arena_words = allocate(count * bytes, false);
    if (arena_words) memset(arena_words, 0, count * bytes);
    return arena_words;
}
void CodecArenaFree(void *memory) {
    assert(memory == arena_words);
    deallocate(memory); arena_words = nullptr;
}
void CodecArenaRelease(CodecArenaOwner owner) {
    assert(arena_bound && !arena_words && owner == CODEC_ARENA_OPUS); ++releases;
}
bool CodecArenaUnbind(void) {
    assert(arena_bound && !arena_words); arena_bound = false; ++unbinds; return !reject_unbind;
}
extern "C" int opus_decoder_get_size(int channels) { assert(channels == 1); return kStateBytes; }
extern "C" int opus_decoder_init(OpusDecoder *decoder, int rate, int channels) {
    assert(live.at(decoder).bytes == kStateBytes && rate == 48000 && channels == 1);
    assert(bound_scratch && bound_words);
    ++init_calls;
    decoder->next_packet = 1;
    return init_calls == init_error_at ? -778 : 0;
}
extern "C" void yoradio_opus_memory_bind(void *bytes, size_t byte_count, void *words, size_t word_count) {
    assert(!!bytes == !!byte_count && !!words == !!word_count);
    if (bytes) {
        assert((!bound_scratch && !bound_words) || (bound_scratch == bytes && bound_words == words));
        assert(byte_count == CONFIG_YORADIO_OPUS_SCRATCH_BYTES && word_count == 16384);
        assert(live.at(bytes).dram && words == arena_words);
        ++memory_binds;
    } else { assert(bound_scratch && bound_words); ++memory_unbinds; }
    bound_scratch = bytes; bound_words = words;
}
extern "C" int yoradio_opus_decode_bounded(void *state, const unsigned char *packet,
                                           int length, int16_t *pcm, int capacity) {
    assert(critical_depth == 0 && bound_scratch && bound_words && capacity == 960);
    auto *decoder = static_cast<OpusDecoder *>(state);
    assert(packet[0] == decoder->next_packet++);
    if (packet[0] == 1) {
        const unsigned char expected[] = {1, 0x12, 0xa5, 0};
        assert(length == 3 && !memcmp(packet, expected, sizeof(expected)));
    } else {
        const unsigned char expected[] = {2, 0x80, 0x7f, 0xaa, 0x55, 0, 0, 0};
        assert(length == 5 && !memcmp(packet, expected, sizeof(expected)));
    }
    assert(live.at(pcm).bytes == 1920);
    ++decode_calls;
    clock_wall += 250; clock_task += 200;
#if YORADIO_OPUS_PROFILE_STAGE
    opus_stage_profile_record(16000);
#endif
    if (decode_calls == decode_error_at) return decode_error;
    static const int16_t samples[2][4] = {{0, 32767, -32768, -1}, {1234, -2345, 42, -42}};
    memcpy(pcm, samples[packet[0] - 1], sizeof(samples[0]));
    if (wrong_pcm) pcm[0] ^= 1;
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
    if (oversized_decode) return 961;
    if (large_decode) { memset(pcm, 0, 600 * sizeof(*pcm)); return 600; }
#endif
    guards();
    return 4;
}
extern "C" size_t yoradio_opus_scratch_peak_bytes(void) { return 1024; }
extern "C" size_t yoradio_opus_scratch_peak_words(void) { return 12000; }

#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
extern "C" esp_err_t native_audio_output_write(int16_t *pcm, size_t count, uint32_t rate, uint8_t channels) {
    assert(count && count <= 512 && rate == 48000 && channels == 1);
    assert(live.size() == 5 && !critical_depth);
    ++output_calls;
    if (output_calls == output_error_at) return ESP_FAIL;
    /* Like real gain/normalization: mutable PCM must have been hashed first. */
    for (size_t i=0; i<count; ++i) pcm[i] ^= 1;
    output_sample_count += count;
    ++dma_eofs;
    if (output_calls == output_misses_at) ++dma_misses;
    if (output_calls == fifo_error_at) fifo_empty = 1;
    clock_wall += 300; clock_task += 100;
    return ESP_OK;
}
extern "C" void native_audio_output_silence(void) { ++silence_calls; }
extern "C" void native_audio_output_reset_normalizer(void) { ++normalizer_resets; }
extern "C" void native_audio_output_get_spi_stats(native_audio_output_spi_stats_t *s) {
    *s = {}; s->chained_transfers = dma_eofs; s->queue_empty_events = dma_misses;
}
extern "C" uint32_t native_audio_output_fifo_empty(unsigned clear) {
    unsigned seen = fifo_empty;
    if (clear) fifo_empty = 0;
    return seen;
}
#endif

int main() {
    assert(status().state == 0 && status().run == 0);
    run(); opus_benchmark_cancel_pending();
    assert(status().state == 0 && !attempts);
    queue(); opus_benchmark_cancel_pending();
    assert(status().state == 4 && status().error == -9002);
    run(); assert(!attempts); clean();
    successful_run();

    // Fail exactly one allocation (not all later ones) to exercise partial
    // cleanup on both sides of every allocation site.
    for (unsigned site = 1; site <= 5; ++site) {
        reset_environment(); fail_at = site; queue(); run(); expect_error(-9001);
        assert(attempts == 5 && failures == 1 && allocations == 4 && !decode_calls);
        assert(memory_binds == 0 && memory_unbinds == 0 && releases == 1 && unbinds == 1);
        successful_run();
    }
    reset_environment(); arena_iram = false; queue(); run(); expect_error(-9003);
    assert(!attempts && !unbinds);
    reset_environment(); reject_bind = true; queue(); run(); expect_error(-9003);
    assert(!attempts && !unbinds);
    reset_environment(); low_reserve = true; queue(); run(); expect_error(-9001);
    assert(attempts == 5 && !decode_calls && !memory_binds);

    for (unsigned after : {3U, 2 * (kRounds + 1) + 1}) {
        reset_environment(); cancel_after = after; queue(); run(); expect_error(-9002);
        const unsigned case_index = after < 2 * (kRounds + 1) ? 0 : 1;
        assert(decode_calls == after && memory_binds == case_index + 2 && memory_unbinds == 1);
        assert(result(case_index).error == -9002);
        assert(status().round == (case_index == 0 ? 1U : 0U));
        if (case_index == 1) assert(!result(0).error && result(0).packets == 2 * kRounds);
        successful_run();
    }
    reset_environment(); init_error_at = 1; queue(); run(); expect_error(-778);
    assert(!decode_calls && result(0).error == -778);
    reset_environment(); decode_error_at = 4; queue(); run(); expect_error(-777);
    assert(result(0).error == -777 && decode_calls == 4);
    reset_environment(); decode_error_at = 1; decode_error = 0; queue(); run(); expect_error(-9005);
    reset_environment(); wrong_pcm = true; queue(); run(); expect_error(-9006);
    assert(decode_calls == 2 && !result(0).packets);
    reset_environment(); reject_unbind = true; queue(); run(); expect_error(-9007);
#if YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT
    reset_environment(); output_error_at = 4; queue(); run(); expect_error(-9008);
    assert(silence_calls >= 1 && result(0).error == -9008);
    reset_environment(); large_decode = true; output_error_at = 2; queue(); run(); expect_error(-9008);
    assert(output_calls == 2 && output_sample_count == 512); // failure in second callback
    reset_environment(); oversized_decode = true; queue(); run(); expect_error(-9010);
    assert(!output_calls);
    reset_environment(); output_misses_at = 4; queue(); run();
    assert(status().state == 3 && result(0).dma_misses == 1); // Never hide output gaps.
    clean();
    reset_environment(); fifo_error_at = 4; queue(); run();
    assert(status().state == 3 && result(0).fifo_empty_seen == 1 && !result(0).dma_misses);
    clean();
#endif
    successful_run(); successful_run();
    assert(total_allocations == total_frees && total_failures == 5);
    printf("Opus board benchmark lifecycle PASS: %u complete runs, 5 allocation-failure sites, "
           "queued/running busy, pending/midway cancel, golden PCM, %u paired allocations/frees\n",
           completed_runs, total_allocations);
    return 0;
}
