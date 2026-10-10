// Parent wires this isolated source with -Wl,--wrap=app_main. Normal yoRadio
// starts after the boot-only experiment, preserving subsequent WebUI/OTA.
#include <cinttypes>
#include <cstdio>
#include "esp_cpu.h"
#include "esp_heap_caps.h"
#include "esp_private/esp_clk.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "riscv/rv_utils.h"
#include "batches.h"
#include "observed_distribution.h"

namespace {
constexpr size_t kMaximumSamples = 4096;
constexpr unsigned kRounds = 9;
constexpr unsigned kBatchRepeats = 1;
constexpr uint32_t kExpectedCpuHz = 160000000;
constexpr uint32_t kPcerCycleEvent = UINT32_C(1) << 0;
constexpr uint32_t kPcmrCountEnabled = UINT32_C(1) << 0;
constexpr uint32_t kPcmrSaturating = UINT32_C(1) << 1;
static flac_clz::Sample* samples;
static uint32_t* words;
static volatile uint32_t sink;

bool check(bool condition, const char* stage) {
    if(!condition) std::printf("CLZ_BOOT_FAIL stage=%s normal_app_follows=1\n", stage);
    return condition;
}

unsigned reference(flac_clz::Sample sample) {
    unsigned zeros = 0;
    for(unsigned mask = 1U << (sample.valid_bits-1);
        mask && !(sample.cached & mask); mask >>= 1) ++zeros;
    return zeros;
}

unsigned reference32(uint32_t value) {
    unsigned zeros = 0;
    for(uint32_t mask = UINT32_C(0x80000000); mask && !(value & mask); mask >>= 1) ++zeros;
    return zeros;
}

void report_measurement(const char* corpus, const char* domain, const char* variant,
                        size_t count, const uint32_t* timings, uint32_t checksum) {
    uint32_t ordered[kRounds];
    for(unsigned i = 0; i < kRounds; ++i) ordered[i] = timings[i];
    for(unsigned i = 1; i < kRounds; ++i)
        for(unsigned j = i; j && ordered[j] < ordered[j-1]; --j) {
            const uint32_t temp = ordered[j]; ordered[j] = ordered[j-1]; ordered[j-1] = temp;
        }
    std::printf("CLZ_BATCH corpus=%s domain=%s variant=%s samples=%u "
                "batch_repeats=%u rounds=%u min_cycles=%" PRIu32 " median_cycles=%" PRIu32
                " checksum=%" PRIu32 " raw_cycles=",
        corpus, domain, variant, static_cast<unsigned>(count),
        kBatchRepeats, kRounds, ordered[0], ordered[kRounds/2], checksum);
    for(unsigned i = 0; i < kRounds; ++i) std::printf("%s%" PRIu32, i ? "," : "", timings[i]);
    std::printf("\n");
}

bool measure(const char* corpus, size_t count) {
    if(!check(count && count <= kMaximumSamples, "rice-count")) return false;
    uint32_t expected = 0, identity = 0;
    for(size_t i = 0; i < count; ++i) {
        if(!check(samples[i].valid_bits >= 1 && samples[i].valid_bits <= 8,
                  "rice-valid-bits")) return false;
        if(!check(samples[i].cached < (1U << samples[i].valid_bits), "rice-cache")) return false;
        expected += reference(samples[i]);
        identity += samples[i].cached + samples[i].valid_bits;
    }
    uint32_t timings[flac_clz::kVariantCount][kRounds] = {};
    // Warm every candidate once, with identical input, outside timing.
    for(const auto& variant : flac_clz::kVariants) {
        sink = variant.batch(samples, count, kBatchRepeats);
        if(!check(sink == (variant.identity ? identity : expected) * kBatchRepeats,
                  variant.name)) return false;
        vTaskDelay(1);
    }
    for(unsigned round = 0; round < kRounds; ++round) {
        // Rotate all seven candidates across ordering positions.
        for(size_t position = 0; position < flac_clz::kVariantCount; ++position) {
            const size_t selected = (round + position) % flac_clz::kVariantCount;
            const auto& variant = flac_clz::kVariants[selected];
            __asm__ volatile("" ::: "memory");
            const uint32_t before = esp_cpu_get_cycle_count();
            const uint32_t sum = variant.batch(samples, count, kBatchRepeats);
            const uint32_t elapsed = esp_cpu_get_cycle_count() - before;
            __asm__ volatile("" ::: "memory");
            // Preserve work and verify it after the timed interval. Interrupts
            // remain enabled, so min/median summarize actual observed batches.
            sink = sum;
            if(!check(elapsed > 0, "rice-counter-progress")) return false;
            if(!check(sum == (variant.identity ? identity : expected) * kBatchRepeats,
                      variant.name)) return false;
            timings[selected][round] = elapsed;
            vTaskDelay(1);
        }
    }
    for(size_t selected = 0; selected < flac_clz::kVariantCount; ++selected)
        report_measurement(corpus, "rice-cache1to8", flac_clz::kVariants[selected].name,
            count, timings[selected],
            (flac_clz::kVariants[selected].identity ? identity : expected) * kBatchRepeats);
    return true;
}

bool measure32(const char* corpus, size_t count) {
    if(!check(count && count <= kMaximumSamples, "generic32-count")) return false;
    uint32_t expected = 0, identity = 0;
    for(size_t i = 0; i < count; ++i) {
        expected += reference32(words[i]);
        identity += words[i]; // Unsigned wrap is also used by the identity batch.
    }
    uint32_t timings[flac_clz::kVariantCount32][kRounds] = {};
    for(const auto& variant : flac_clz::kVariants32) {
        sink = variant.batch(words, count, kBatchRepeats);
        if(!check(sink == (variant.identity ? identity : expected) * kBatchRepeats,
                  variant.name)) return false;
        vTaskDelay(1);
    }
    for(unsigned round = 0; round < kRounds; ++round)
        for(size_t position = 0; position < flac_clz::kVariantCount32; ++position) {
            const size_t selected = (round + position) % flac_clz::kVariantCount32;
            const auto& variant = flac_clz::kVariants32[selected];
            __asm__ volatile("" ::: "memory");
            const uint32_t before = esp_cpu_get_cycle_count();
            const uint32_t sum = variant.batch(words, count, kBatchRepeats);
            const uint32_t elapsed = esp_cpu_get_cycle_count() - before;
            __asm__ volatile("" ::: "memory");
            sink = sum;
            if(!check(elapsed > 0, "generic32-counter-progress")) return false;
            if(!check(sum == (variant.identity ? identity : expected) * kBatchRepeats,
                      variant.name)) return false;
            timings[selected][round] = elapsed;
            vTaskDelay(1);
        }
    for(size_t selected = 0; selected < flac_clz::kVariantCount32; ++selected)
        report_measurement(corpus, "generic32", flac_clz::kVariants32[selected].name,
            count, timings[selected],
            (flac_clz::kVariants32[selected].identity ? identity : expected) * kBatchRepeats);
    return true;
}

bool run_benchmark() {
    vTaskDelay(pdMS_TO_TICKS(8000)); // Allow passive USB capture before reporting.
    const uint32_t hz = esp_clk_cpu_freq();
    const uint32_t events = RV_READ_CSR(CSR_PCER_MACHINE);
    const uint32_t mode = RV_READ_CSR(CSR_PCMR_MACHINE);
    std::printf("CLZ_ENV target=esp32c3 cpu_hz=%" PRIu32
                " irq_masked=0 baseline=compiler-intrinsic expected_rom=__clzsi2 "
                "normal_app_follows=1 identity_subtracted=0 counter=MPCCR "
                "event_mask=%" PRIu32 " counter_mode=%" PRIu32 "\n", hz, events, mode);
    if(!check(hz == kExpectedCpuHz, "cpu-hz")) return false;
    // On C3 esp_cpu_get_cycle_count reads Espressif's MPCCR CSR (0x7e2).
    // Only the cycle event may be selected; unsigned subtraction requires a
    // running wrapping counter, not saturating or disabled counting.
    if(!check(events == kPcerCycleEvent, "counter-cycle-event")) return false;
    if(!check((mode & kPcmrCountEnabled) && !(mode & kPcmrSaturating),
              "counter-enabled-wrapping")) return false;
    void* memory = heap_caps_malloc(kMaximumSamples * sizeof(uint32_t), MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
    if(!check(memory != nullptr, "workspace-oom")) return false;
    struct WorkspaceGuard {
        void* memory;
        ~WorkspaceGuard() { heap_caps_free(memory); samples = nullptr; words = nullptr; }
    } guard{memory};
    samples = static_cast<flac_clz::Sample*>(memory);
    words = static_cast<uint32_t*>(memory);
    size_t count = 0;
    for(unsigned bits = 1; bits <= 8; ++bits)
        for(unsigned value = 0; value < (1U << bits); ++value)
            samples[count++] = {static_cast<uint8_t>(value), static_cast<uint8_t>(bits)};
    if(!measure("uniform-cached-states", count)) return false;
    for(unsigned value = 0; value < 256; ++value)
        samples[value] = {static_cast<uint8_t>(value), 8};
    if(!measure("uniform-all-bytes", 256)) return false;
    const unsigned worst_values[] = {0, 1, 128};
    for(const auto value : worst_values) {
        for(size_t i = 0; i < kMaximumSamples; ++i) samples[i] = {static_cast<uint8_t>(value), 8};
        if(!measure(value == 0 ? "all-zero" : value == 1 ? "low-one" : "high-one", kMaximumSamples)) return false;
    }
    for(size_t i = 0; i < kMaximumSamples; ++i)
        samples[i] = {static_cast<uint8_t>(i % 3 == 0 ? 0 : i % 3 == 1 ? 1 : 128), 8};
    if(!measure("alternating-paths", kMaximumSamples)) return false;
    if(kClzObservedAvailable) {
        if(!check(kClzObservedCount <= kMaximumSamples, "observed-count")) return false;
        for(unsigned i = 0; i < kClzObservedCount; ++i) samples[i] = kClzObservedSamples[i];
        std::printf("CLZ_OBSERVED original_calls=%llu replay_samples=%u histogram_l1_error=%.9f\n",
            static_cast<unsigned long long>(kClzObservedOriginalCalls),
            kClzObservedCount, kClzObservedL1Error);
        if(!measure("corpus-histogram-replay", kClzObservedCount)) return false;
    } else {
        std::printf("CLZ_OBSERVED unavailable=1 no_corpus_weighted_claim=1\n");
    }
    uint32_t random = UINT32_C(0xC351AC);
    for(size_t i = 0; i < kMaximumSamples; ++i) {
        random ^= random << 13; random ^= random >> 17; random ^= random << 5;
        words[i] = random;
    }
    if(!measure32("uniform-full32", kMaximumSamples)) return false;
    count = 0;
    for(unsigned bit = 0; bit < 32; ++bit) {
        const uint32_t value = UINT32_C(1) << bit;
        words[count++] = value-1; words[count++] = value; words[count++] = value+1;
        words[count++] = ~value; words[count++] = UINT32_MAX >> bit;
    }
    words[count++] = 0; words[count++] = UINT32_MAX;
    if(!measure32("full32-boundaries", count)) return false;
    for(size_t i = 0; i < kMaximumSamples; ++i) words[i] = UINT32_C(1) << (i % 32);
    if(!measure32("full32-powers-of-two", kMaximumSamples)) return false;
    for(size_t i = 0; i < kMaximumSamples; ++i) words[i] = 1;
    if(!measure32("full32-low-one", kMaximumSamples)) return false;
    for(size_t i = 0; i < kMaximumSamples; ++i) words[i] = UINT32_MAX;
    if(!measure32("full32-high-one", kMaximumSamples)) return false;
    std::printf("CLZ_BOOT_PASS normal_app_follows=1\n");
    return true;
}
} // namespace

extern "C" void __real_app_main(void);
extern "C" void __wrap_app_main(void) {
    run_benchmark();
    __real_app_main();
}
