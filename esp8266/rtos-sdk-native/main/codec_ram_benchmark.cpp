#include <algorithm>
#include <cstdint>
#include <cstring>

#include "codec_bridge.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "helix_stage_profile.h"

namespace {
constexpr unsigned kWarmupFrames = 8;
constexpr unsigned kMeasuredFrames = 200;
constexpr size_t kMaxFrameBytes = 1536;
constexpr char kTag[] = "codec_ram";

extern "C" const uint8_t _binary_stereo_320_mp3_start[];
extern "C" const uint8_t _binary_stereo_320_mp3_end[];
extern "C" const uint8_t _binary_stereo_320_aac_start[];
extern "C" const uint8_t _binary_stereo_320_aac_end[];

struct FrameView {
    const uint8_t *data;
    size_t size;
};

struct OutputStats {
    uint64_t samples;
    uint32_t sample_rate;
    uint8_t channels;
    uint32_t callbacks;
    volatile int16_t sink;
};

#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
struct StageStats {
    uint64_t microseconds;
    uint32_t maximum_microseconds;
    uint32_t calls;
    uint32_t rejected_samples;
};

StageStats s_stage[HELIX_STAGE_COUNT];
int64_t s_stage_started[HELIX_STAGE_COUNT];
const char *const kStageNames[HELIX_STAGE_COUNT] = {
    "huffman", "dequant", "stereo_filter", "imdct", "synthesis",
    "synthesis_dct", "synthesis_polyphase", "sbr",
};

void reset_stage_profile() {
    std::memset(s_stage, 0, sizeof(s_stage));
    std::memset(s_stage_started, 0, sizeof(s_stage_started));
}

void report_stage_profile(const char *codec, uint64_t decode_us) {
    for (int stage = 0; stage < HELIX_STAGE_COUNT; ++stage) {
        const StageStats &stats = s_stage[stage];
        if (!stats.calls) continue;
        uint32_t percent_x10 = decode_us
            ? static_cast<uint32_t>(stats.microseconds * 1000ULL / decode_us)
            : 0;
        ESP_LOGI(kTag,
                 "%s stage=%s time=%u us avg=%u us max=%u us calls=%u "
                 "rejected=%u load=%u.%u%%",
                 codec, kStageNames[stage],
                 static_cast<unsigned>(stats.microseconds),
                 static_cast<unsigned>(stats.microseconds / stats.calls),
                 static_cast<unsigned>(stats.maximum_microseconds),
                 static_cast<unsigned>(stats.calls),
                 static_cast<unsigned>(stats.rejected_samples),
                 percent_x10 / 10U, percent_x10 % 10U);
    }
}
#else
void reset_stage_profile() {}
void report_stage_profile(const char *, uint64_t) {}
#endif

bool accept_pcm(void *context, const helix_stream_info_t *info,
                int16_t *pcm, size_t samples) {
    OutputStats *output = static_cast<OutputStats *>(context);
    if (!info || !pcm || !samples || !info->sample_rate || !info->channels)
        return false;
    output->samples += samples;
    output->sample_rate = info->sample_rate;
    output->channels = info->channels;
    ++output->callbacks;
    output->sink ^= pcm[0];
    output->sink ^= pcm[samples - 1];
    return true;
}

FrameView first_mp3_frame(const uint8_t *data, size_t size) {
    static const uint16_t rate1[] =
        {0,32,40,48,56,64,80,96,112,128,160,192,224,256,320};
    static const uint16_t rate2[] =
        {0,8,16,24,32,40,48,56,64,80,96,112,128,144,160};
    static const uint32_t sample_rates[] = {44100, 48000, 32000};
    for (size_t offset = 0; offset + 4 <= size; ++offset) {
        const uint8_t *frame = data + offset;
        if (frame[0] != 0xff || (frame[1] & 0xe0) != 0xe0) continue;
        uint8_t version = (frame[1] >> 3) & 3U;
        uint8_t layer = (frame[1] >> 1) & 3U;
        uint8_t bitrate_index = frame[2] >> 4;
        uint8_t sample_index = (frame[2] >> 2) & 3U;
        if (version == 1 || layer != 1 || !bitrate_index ||
            bitrate_index == 15 || sample_index == 3) continue;
        bool mpeg1 = version == 3;
        uint32_t sample_rate = sample_rates[sample_index];
        if (version == 2) sample_rate /= 2;
        if (version == 0) sample_rate /= 4;
        uint32_t bitrate = mpeg1 ? rate1[bitrate_index] : rate2[bitrate_index];
        size_t frame_size = ((mpeg1 ? 144000U : 72000U) * bitrate) /
                            sample_rate + ((frame[2] >> 1) & 1U);
        if (frame_size <= kMaxFrameBytes && offset + frame_size <= size)
            return {frame, frame_size};
    }
    return {nullptr, 0};
}

FrameView first_aac_frame(const uint8_t *data, size_t size) {
    for (size_t offset = 0; offset + 7 <= size; ++offset) {
        const uint8_t *frame = data + offset;
        if (frame[0] != 0xff || (frame[1] & 0xf6) != 0xf0) continue;
        size_t frame_size = (static_cast<size_t>(frame[3] & 3U) << 11) |
                            (static_cast<size_t>(frame[4]) << 3) |
                            (frame[5] >> 5);
        if (frame_size >= 7 && frame_size <= kMaxFrameBytes &&
            offset + frame_size <= size)
            return {frame, frame_size};
    }
    return {nullptr, 0};
}

bool submit_frame(helix_codec_t *codec, const uint8_t *frame,
                  size_t frame_size, OutputStats *output,
                  uint32_t *elapsed_us) {
    size_t capacity = 0;
    uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
    if (!destination || capacity < frame_size) return false;
    std::memcpy(destination, frame, frame_size);
    int64_t started = esp_timer_get_time();
    int result = helix_codec_commit(codec, frame_size, accept_pcm, output);
    *elapsed_us = static_cast<uint32_t>(esp_timer_get_time() - started);
    return result == 0;
}

void run_codec(const char *name, helix_codec_kind_t kind,
               const FrameView &fixture) {
    uint8_t frame_ram[kMaxFrameBytes];
    if (!fixture.data || !fixture.size) {
        ESP_LOGE(kTag, "%s fixture has no complete frame", name);
        return;
    }
    std::memcpy(frame_ram, fixture.data, fixture.size);
    helix_codec_t *codec = helix_codec_create(kind, 0);
    if (!codec) {
        ESP_LOGE(kTag, "%s decoder allocation failed", name);
        return;
    }

    OutputStats output = {};
    const size_t arena_bytes = helix_codec_arena_used(codec);
    uint32_t elapsed = 0;
    for (unsigned index = 0; index < kWarmupFrames; ++index) {
        if (!submit_frame(codec, frame_ram, fixture.size, &output, &elapsed)) {
            ESP_LOGE(kTag, "%s warmup failed at %u", name, index);
            helix_codec_destroy(codec);
            return;
        }
        if ((index & 3U) == 3U) vTaskDelay(1);
    }

    output.samples = 0;
    output.callbacks = 0;
    reset_stage_profile();
    uint64_t total_us = 0;
    uint32_t minimum_us = UINT32_MAX;
    uint32_t maximum_us = 0;
    for (unsigned index = 0; index < kMeasuredFrames; ++index) {
        if (!submit_frame(codec, frame_ram, fixture.size, &output, &elapsed)) {
            ESP_LOGE(kTag, "%s measured decode failed at %u", name, index);
            helix_codec_destroy(codec);
            return;
        }
        total_us += elapsed;
        minimum_us = std::min(minimum_us, elapsed);
        maximum_us = std::max(maximum_us, elapsed);
        if ((index & 7U) == 7U) vTaskDelay(1);
    }

    uint64_t audio_us = output.sample_rate && output.channels
        ? output.samples * 1000000ULL /
          (static_cast<uint64_t>(output.sample_rate) * output.channels)
        : 0;
    uint32_t speed_x1000 = total_us
        ? static_cast<uint32_t>(audio_us * 1000ULL / total_us)
        : 0;
    ESP_LOGI(kTag,
             "%s RAM frame=%u bytes iterations=%u callbacks=%u "
             "decode=%u us avg=%u us min=%u us max=%u us "
             "audio=%u us realtime=%u.%u%% speed=%u.%03ux heap=%u "
             "workspace=%u arena=%u",
             name, static_cast<unsigned>(fixture.size), kMeasuredFrames,
             static_cast<unsigned>(output.callbacks),
             static_cast<unsigned>(total_us),
             static_cast<unsigned>(total_us / kMeasuredFrames), minimum_us,
             maximum_us, static_cast<unsigned>(audio_us),
             speed_x1000 / 10U, speed_x1000 % 10U,
             speed_x1000 / 1000U, speed_x1000 % 1000U,
             static_cast<unsigned>(esp_get_free_heap_size()),
             static_cast<unsigned>(helix_codec_workspace_size()),
             static_cast<unsigned>(arena_bytes));
    report_stage_profile(name, total_us);
    helix_codec_destroy(codec);
}

} // namespace

#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
extern "C" void helix_stage_profile_begin(int stage) {
    if (stage >= 0 && stage < HELIX_STAGE_COUNT)
        s_stage_started[stage] = esp_timer_get_time();
}

extern "C" void helix_stage_profile_end(int stage) {
    if (stage < 0 || stage >= HELIX_STAGE_COUNT) return;
    StageStats &stats = s_stage[stage];
    int64_t elapsed_signed = esp_timer_get_time() - s_stage_started[stage];
    /* The legacy ESP8266 SDK updates its software time base while resetting
     * CCOUNT on every RTOS tick. A read concurrent with that update can move
     * backwards briefly. Reject that timing sample instead of turning it into
     * a 32-bit wraparound; decoder execution itself remains uninterrupted.
     */
    if (elapsed_signed < 0 || elapsed_signed > 1000000) {
        ++stats.rejected_samples;
        return;
    }
    uint32_t elapsed = static_cast<uint32_t>(elapsed_signed);
    stats.microseconds += elapsed;
    stats.maximum_microseconds =
        std::max(stats.maximum_microseconds, elapsed);
    ++stats.calls;
}
#endif

extern "C" void codec_ram_benchmark_run(void) {
    ESP_LOGI(kTag, "begin: CPU-only decode, fixture copied to RAM, Wi-Fi off");
    if (!helix_codec_prepare()) {
        ESP_LOGE(kTag, "cannot reserve codec word arena");
        return;
    }
    run_codec(
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
              "MP3/libmad",
#else
              "MP3/Helix",
#endif
              HELIX_CODEC_MP3,
              first_mp3_frame(_binary_stereo_320_mp3_start,
                              _binary_stereo_320_mp3_end -
                              _binary_stereo_320_mp3_start));
#if CONFIG_YORADIO_HELIX_AAC
    run_codec("AAC", HELIX_CODEC_AAC,
              first_aac_frame(_binary_stereo_320_aac_start,
                              _binary_stereo_320_aac_end -
                              _binary_stereo_320_aac_start));
#endif
    ESP_LOGI(kTag, "complete");
}
