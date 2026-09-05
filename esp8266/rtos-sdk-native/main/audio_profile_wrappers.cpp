#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "codec_bridge.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "helix_stage_profile.h"
#include "lwip/sockets.h"
#include "mp3_decoder.h"
#include "native_audio_normalizer.h"
extern "C" {
#include "native_audio_output.h"
#include "esp8266_nodac_i2s.h"
}
#if CONFIG_YORADIO_HELIX_AAC
#include "aac_decoder.h"
#endif

namespace {
constexpr int64_t kWindowUs =
    int64_t(YORADIO_ESP8266_AUDIO_PROFILE_WINDOW_MS) * 1000;

enum Stage {
    kRecvWait,
    kFrameScan,
    kDecodeCore,
    kPcmOutput,
    kNormalizer,
    kSpiWait,
    kPcmGap,
    kStageCount,
};

struct StageStats {
    uint64_t total_us;
    uint32_t max_us;
    uint32_t calls;
};

StageStats s_stage[kStageCount];
#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
StageStats s_codec_stage[HELIX_STAGE_COUNT];
int64_t s_codec_stage_started[HELIX_STAGE_COUNT];
const char *const kCodecStageNames[HELIX_STAGE_COUNT] = {
    "huffman", "dequant", "stereo_filter", "imdct", "synthesis",
    "synthesis_dct", "synthesis_polyphase", "sbr",
};
uint32_t s_codec_stage_rejected[HELIX_STAGE_COUNT];
#endif
TaskHandle_t s_audio_task;
int64_t s_started_us;
uint64_t s_audio_us;
uint64_t s_network_bytes;
uint32_t s_frames;
char s_codec[8] = "?";
int64_t s_decode_started_us;
uint64_t s_decode_pcm_before;
int64_t s_spi_wait_started_us;
uint32_t s_cpu_total;
uint32_t s_cpu_idle;
bool s_cpu_baseline_valid;
int64_t s_previous_pcm_end;
uint32_t s_underruns_before;
esp8266_nodac_profile_t s_dma_before;
const char *kTag = "audio_profile";

extern "C" size_t g_heap_region_num;
extern "C" heap_region_t g_heap_region[];

bool in_audio_task() {
    return s_audio_task && xTaskGetCurrentTaskHandle() == s_audio_task;
}

uint32_t elapsed_since(int64_t started) {
    int64_t elapsed = esp_timer_get_time() - started;
    return static_cast<uint32_t>(std::max<int64_t>(elapsed, 0));
}

void record(Stage stage, uint64_t elapsed_us) {
    StageStats &stats = s_stage[stage];
    stats.total_us += elapsed_us;
    uint32_t bounded = static_cast<uint32_t>(
        std::min<uint64_t>(elapsed_us, UINT32_MAX));
    stats.max_us = std::max(stats.max_us, bounded);
    ++stats.calls;
}

uint64_t total(Stage stage) {
    return s_stage[stage].total_us;
}

unsigned percent_x10(uint64_t value, uint64_t denominator) {
    return denominator ? static_cast<unsigned>(value * 1000ULL / denominator)
                       : 0U;
}

size_t heap_total_size() {
    size_t total = 0;
    for (size_t i = 0; i < g_heap_region_num; ++i) {
        if (g_heap_region[i].caps & MALLOC_CAP_32BIT)
            total += g_heap_region[i].total_size;
    }
    return total;
}

#if configGENERATE_RUN_TIME_STATS == 1
bool cpu_counters(uint32_t *total, uint32_t *idle) {
    TaskStatus_t tasks[20];
    uint32_t runtime = 0;
    UBaseType_t count = uxTaskGetSystemState(
        tasks, sizeof(tasks) / sizeof(tasks[0]), &runtime);
    if (!count || !runtime) return false;
    uint32_t idle_runtime = 0;
    for (UBaseType_t i = 0; i < count; ++i) {
        if (tasks[i].pcTaskName &&
            std::strcmp(tasks[i].pcTaskName, "IDLE") == 0)
            idle_runtime += tasks[i].ulRunTimeCounter;
    }
    *total = runtime;
    *idle = idle_runtime;
    return true;
}
#endif


void log_stage(const char *name, Stage stage, uint64_t wall_us) {
    const StageStats &stats = s_stage[stage];
    unsigned load = percent_x10(stats.total_us, wall_us);
    ESP_LOGI(kTag, "%s=%u.%03u ms (%u.%u%%), calls=%u max=%u us", name,
             static_cast<unsigned>(stats.total_us / 1000ULL),
             static_cast<unsigned>(stats.total_us % 1000ULL), load / 10U,
             load % 10U, static_cast<unsigned>(stats.calls),
             static_cast<unsigned>(stats.max_us));
}

#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
void reset_codec_stages() {
    std::memset(s_codec_stage, 0, sizeof(s_codec_stage));
    std::memset(s_codec_stage_started, 0, sizeof(s_codec_stage_started));
    std::memset(s_codec_stage_rejected, 0, sizeof(s_codec_stage_rejected));
}

void log_codec_stages(uint64_t wall_us) {
    const uint64_t decode_us = total(kDecodeCore);
    for (int stage = 0; stage < HELIX_STAGE_COUNT; ++stage) {
        const StageStats &stats = s_codec_stage[stage];
        if (!stats.calls) continue;
        const unsigned wall_load = percent_x10(stats.total_us, wall_us);
        const unsigned core_load = percent_x10(stats.total_us, decode_us);
        ESP_LOGI(kTag,
                 "codec_stage=%s time=%u.%03u ms wall=%u.%u%% "
                 "core=%u.%u%% calls=%u max=%u us rejected=%u",
                 kCodecStageNames[stage],
                 static_cast<unsigned>(stats.total_us / 1000ULL),
                 static_cast<unsigned>(stats.total_us % 1000ULL),
                 wall_load / 10U, wall_load % 10U,
                 core_load / 10U, core_load % 10U,
                 static_cast<unsigned>(stats.calls),
                 static_cast<unsigned>(stats.max_us),
                 static_cast<unsigned>(s_codec_stage_rejected[stage]));
    }
}
#else
void reset_codec_stages() {}
void log_codec_stages(uint64_t) {}
#endif

void reset_profile(helix_codec_kind_t kind) {
    std::memset(s_stage, 0, sizeof(s_stage));
    reset_codec_stages();
    s_audio_task = xTaskGetCurrentTaskHandle();
    s_started_us = esp_timer_get_time();
    s_audio_us = 0;
    s_network_bytes = 0;
    s_frames = 0;
    s_previous_pcm_end = 0;
    native_audio_output_spi_stats_t output_stats = {};
    native_audio_output_get_spi_stats(&output_stats);
    s_underruns_before = output_stats.queue_empty_events;
    esp8266_nodac_i2s_profile(&s_dma_before);
    std::snprintf(s_codec, sizeof(s_codec), "%s",
                  kind == HELIX_CODEC_MP3 ? "MP3" : "AAC");
}

void maybe_report() {
    int64_t now = esp_timer_get_time();
    if (!s_started_us || now - s_started_us < kWindowUs) return;
    uint64_t wall_us = static_cast<uint64_t>(now - s_started_us);
    /* Snapshot before logging, and establish the next baseline only after
     * logging. UART output must not inflate these window counters/gaps. */
    native_audio_output_spi_stats_t output_stats = {};
    native_audio_output_get_spi_stats(&output_stats);
    esp8266_nodac_profile_t dma = {};
    esp8266_nodac_i2s_profile(&dma);
    uint64_t output_compute = total(kPcmOutput);
    output_compute -= std::min(output_compute, total(kNormalizer));
    output_compute -= std::min(output_compute, total(kSpiWait));
    unsigned realtime = percent_x10(s_audio_us, wall_us);
    uint32_t kbps = static_cast<uint32_t>(s_network_bytes * 8000ULL / wall_us);
    ESP_LOGI(kTag,
             "=== %s window=%u ms audio=%u ms (%u.%u%% realtime) "
             "frames=%u net=%u kbps ===", s_codec,
             static_cast<unsigned>(wall_us / 1000ULL),
             static_cast<unsigned>(s_audio_us / 1000ULL), realtime / 10U,
             realtime % 10U, static_cast<unsigned>(s_frames),
             static_cast<unsigned>(kbps));
    log_stage("tcp_wait", kRecvWait, wall_us);
    log_stage("frame_scan", kFrameScan, wall_us);
    log_stage("decode_core", kDecodeCore, wall_us);
    log_codec_stages(wall_us);
    log_stage("pcm_output", kPcmOutput, wall_us);
    log_stage("normalize", kNormalizer, wall_us);
    log_stage("output_dma_wait", kSpiWait, wall_us);
    log_stage("pcm_gap", kPcmGap, wall_us);
    ESP_LOGI(kTag,
             "dma eof=%u underrun=%u empty_start=%u blocked_partial=%u "
             "missing_words=%u fifo_empty=%u",
             unsigned(dma.eof_count - s_dma_before.eof_count),
             unsigned(output_stats.queue_empty_events - s_underruns_before),
             unsigned(dma.empty_starts - s_dma_before.empty_starts),
             unsigned(dma.blocked_partial - s_dma_before.blocked_partial),
             unsigned(dma.missing_words - s_dma_before.missing_words),
             unsigned(dma.fifo_empty - s_dma_before.fifo_empty));
    unsigned compute_load = percent_x10(output_compute, wall_us);
    ESP_LOGI(kTag, "gain+mix+pdm=%u.%03u ms (%u.%u%%)",
             static_cast<unsigned>(output_compute / 1000ULL),
             static_cast<unsigned>(output_compute % 1000ULL),
             compute_load / 10U, compute_load % 10U);
#if configGENERATE_RUN_TIME_STATS == 1
    uint32_t cpu_total = 0;
    uint32_t cpu_idle = 0;
    if (cpu_counters(&cpu_total, &cpu_idle)) {
        if (s_cpu_baseline_valid) {
            uint32_t total_delta = cpu_total - s_cpu_total;
            uint32_t idle_delta = cpu_idle - s_cpu_idle;
            unsigned idle_load = percent_x10(idle_delta, total_delta);
            if (idle_load > 1000U) idle_load = 1000U;
            unsigned busy_load = 1000U - idle_load;
            ESP_LOGI(kTag, "cpu busy=%u.%u%% idle=%u.%u%%", busy_load / 10U,
                     busy_load % 10U, idle_load / 10U, idle_load % 10U);
        } else {
            ESP_LOGI(kTag, "cpu baseline captured");
        }
        s_cpu_total = cpu_total;
        s_cpu_idle = cpu_idle;
        s_cpu_baseline_valid = true;
    }
#endif
    size_t heap_total = heap_total_size();
    size_t heap_free = esp_get_free_heap_size();
    size_t heap_min = esp_get_minimum_free_heap_size();
    ESP_LOGI(kTag, "heap total=%u used=%u free=%u min_free=%u",
             static_cast<unsigned>(heap_total),
             static_cast<unsigned>(heap_total -
                                   std::min(heap_total, heap_free)),
             static_cast<unsigned>(heap_free),
             static_cast<unsigned>(heap_min));
    reset_profile(std::strcmp(s_codec, "AAC") == 0 ? HELIX_CODEC_AAC
                                                     : HELIX_CODEC_MP3);
}
}  // namespace

extern "C" int __real_helix_codec_switch(helix_codec_t *,
                                           helix_codec_kind_t);
extern "C" helix_codec_t *__real_helix_codec_create(helix_codec_kind_t,
                                                       size_t);
extern "C" helix_codec_t *__wrap_helix_codec_create(helix_codec_kind_t kind,
                                                       size_t reserve_bytes) {
    helix_codec_t *codec = __real_helix_codec_create(kind, reserve_bytes);
    if (codec) {
        s_cpu_baseline_valid = false;
        reset_profile(kind);
    }
    return codec;
}

extern "C" int __wrap_helix_codec_switch(helix_codec_t *codec,
                                           helix_codec_kind_t kind) {
    int result = __real_helix_codec_switch(codec, kind);
    if (result == 0) {
        s_cpu_baseline_valid = false;
        reset_profile(kind);
    }
    return result;
}

extern "C" ssize_t __real_lwip_recv(int, void *, size_t, int);
extern "C" ssize_t __wrap_lwip_recv(int socket, void *buffer, size_t size,
                                      int flags) {
    int64_t started = esp_timer_get_time();
    ssize_t result = __real_lwip_recv(socket, buffer, size, flags);
    if (in_audio_task()) {
        record(kRecvWait, elapsed_since(started));
        if (result > 0) s_network_bytes += static_cast<size_t>(result);
    }
    return result;
}

extern "C" int __real_helix_codec_commit(helix_codec_t *, size_t,
    helix_pcm_callback_t, void *);
extern "C" int __wrap_helix_codec_commit(helix_codec_t *codec, size_t size,
    helix_pcm_callback_t callback, void *context) {
    uint64_t decode_before = total(kDecodeCore);
    uint64_t pcm_before = total(kPcmOutput);
    int64_t started = esp_timer_get_time();
    int result = __real_helix_codec_commit(codec, size, callback, context);
    uint64_t elapsed = elapsed_since(started);
    uint64_t nested = total(kDecodeCore) - decode_before +
                      total(kPcmOutput) - pcm_before;
    record(kFrameScan, elapsed > nested ? elapsed - nested : 0U);
    maybe_report();
    return result;
}

extern "C" void audio_profile_decode_begin(void) {
    s_decode_started_us = esp_timer_get_time();
    s_decode_pcm_before = total(kPcmOutput);
}

extern "C" void audio_profile_decode_end(void) {
    uint64_t elapsed = elapsed_since(s_decode_started_us);
    uint64_t nested_pcm = total(kPcmOutput) - s_decode_pcm_before;
    record(kDecodeCore, elapsed > nested_pcm ? elapsed - nested_pcm : 0U);
    ++s_frames;
}

extern "C" esp_err_t __real_native_audio_output_write(
    int16_t *, size_t, uint32_t, uint8_t);
extern "C" esp_err_t __wrap_native_audio_output_write(
    int16_t *samples, size_t sample_count, uint32_t sample_rate,
    uint8_t channels) {
    int64_t started = esp_timer_get_time();
    if (s_previous_pcm_end)
        record(kPcmGap, static_cast<uint64_t>(
            std::max<int64_t>(started - s_previous_pcm_end, 0)));
#if YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY
    (void)samples;
    esp_err_t result = ESP_OK;
#else
    esp_err_t result = __real_native_audio_output_write(
        samples, sample_count, sample_rate, channels);
#endif
    record(kPcmOutput, elapsed_since(started));
    s_previous_pcm_end = esp_timer_get_time();
    if (sample_rate && channels)
        s_audio_us += static_cast<uint64_t>(sample_count / channels) *
                      1000000ULL / sample_rate;
    return result;
}

extern "C" void __real_native_audio_normalizer_process(
    int16_t *, size_t, uint8_t);
extern "C" void __wrap_native_audio_normalizer_process(
    int16_t *samples, size_t frames, uint8_t channels) {
    int64_t started = esp_timer_get_time();
    __real_native_audio_normalizer_process(samples, frames, channels);
    record(kNormalizer, elapsed_since(started));
}

extern "C" void audio_profile_spi_wait_begin(void) {
    s_spi_wait_started_us = esp_timer_get_time();
}

extern "C" void audio_profile_spi_wait_end(void) {
    record(kSpiWait, elapsed_since(s_spi_wait_started_us));
}

#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
extern "C" void helix_stage_profile_begin(int stage) {
    if (stage >= 0 && stage < HELIX_STAGE_COUNT)
        s_codec_stage_started[stage] = esp_timer_get_time();
}

extern "C" void helix_stage_profile_end(int stage) {
    if (stage < 0 || stage >= HELIX_STAGE_COUNT) return;
    const int64_t elapsed_signed =
        esp_timer_get_time() - s_codec_stage_started[stage];
    if (elapsed_signed < 0 || elapsed_signed > 1000000) {
        ++s_codec_stage_rejected[stage];
        return;
    }
    StageStats &stats = s_codec_stage[stage];
    const uint32_t elapsed = static_cast<uint32_t>(elapsed_signed);
    stats.total_us += elapsed;
    stats.max_us = std::max(stats.max_us, elapsed);
    ++stats.calls;
}
#endif
