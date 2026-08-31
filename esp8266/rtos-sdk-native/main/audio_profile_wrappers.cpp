#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "codec_bridge.h"
#include "driver/spi.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lwip/sockets.h"
#include "mp3_decoder.h"
#include "native_audio_normalizer.h"
#include "native_audio_output.h"
#if CONFIG_YORADIO_HELIX_AAC
#include "aac_decoder.h"
#endif

namespace {
constexpr int64_t kWindowUs = 5000000;

enum Stage {
    kRecvWait,
    kFrameScan,
    kDecodeCore,
    kPcmOutput,
    kNormalizer,
    kSpiWait,
    kStageCount,
};

struct StageStats {
    uint64_t total_us;
    uint32_t max_us;
    uint32_t calls;
};

StageStats s_stage[kStageCount];
TaskHandle_t s_audio_task;
int64_t s_started_us;
uint64_t s_audio_us;
uint64_t s_network_bytes;
uint32_t s_frames;
char s_codec[8] = "?";
int64_t s_decode_started_us;
uint64_t s_decode_pcm_before;
const char *kTag = "audio_profile";

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

void log_stage(const char *name, Stage stage, uint64_t wall_us) {
    const StageStats &stats = s_stage[stage];
    unsigned load = percent_x10(stats.total_us, wall_us);
    ESP_LOGI(kTag, "%s=%u.%03u ms (%u.%u%%), calls=%u max=%u us", name,
             static_cast<unsigned>(stats.total_us / 1000ULL),
             static_cast<unsigned>(stats.total_us % 1000ULL), load / 10U,
             load % 10U, static_cast<unsigned>(stats.calls),
             static_cast<unsigned>(stats.max_us));
}

void reset_profile(helix_codec_kind_t kind) {
    std::memset(s_stage, 0, sizeof(s_stage));
    s_audio_task = xTaskGetCurrentTaskHandle();
    s_started_us = esp_timer_get_time();
    s_audio_us = 0;
    s_network_bytes = 0;
    s_frames = 0;
    std::snprintf(s_codec, sizeof(s_codec), "%s",
                  kind == HELIX_CODEC_MP3 ? "MP3" : "AAC");
}

void maybe_report() {
    int64_t now = esp_timer_get_time();
    if (!s_started_us || now - s_started_us < kWindowUs) return;
    uint64_t wall_us = static_cast<uint64_t>(now - s_started_us);
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
    log_stage("pcm_output", kPcmOutput, wall_us);
    log_stage("normalize", kNormalizer, wall_us);
    log_stage("spi_wait", kSpiWait, wall_us);
    unsigned compute_load = percent_x10(output_compute, wall_us);
    ESP_LOGI(kTag, "gain+mix+pdm=%u.%03u ms (%u.%u%%)",
             static_cast<unsigned>(output_compute / 1000ULL),
             static_cast<unsigned>(output_compute % 1000ULL),
             compute_load / 10U, compute_load % 10U);
    reset_profile(std::strcmp(s_codec, "AAC") == 0 ? HELIX_CODEC_AAC
                                                     : HELIX_CODEC_MP3);
}
}  // namespace

extern "C" int __real_helix_codec_switch(helix_codec_t *,
                                           helix_codec_kind_t);
extern "C" int __wrap_helix_codec_switch(helix_codec_t *codec,
                                           helix_codec_kind_t kind) {
    int result = __real_helix_codec_switch(codec, kind);
    if (result == 0) reset_profile(kind);
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
    esp_err_t result = __real_native_audio_output_write(
        samples, sample_count, sample_rate, channels);
    record(kPcmOutput, elapsed_since(started));
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

extern "C" esp_err_t __real_spi_trans(spi_host_t, spi_trans_t *);
extern "C" esp_err_t __wrap_spi_trans(spi_host_t host,
                                        spi_trans_t *transaction) {
    int64_t started = esp_timer_get_time();
    esp_err_t result = __real_spi_trans(host, transaction);
    if (in_audio_task()) record(kSpiWait, elapsed_since(started));
    return result;
}
