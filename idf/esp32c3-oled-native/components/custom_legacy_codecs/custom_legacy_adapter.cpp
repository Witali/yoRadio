#include "custom_legacy_adapter.h"

#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <new>

#include "esp_log.h"
#include "esp_timer.h"
#include "sdkconfig.h"

#ifdef CONFIG_YORADIO_AAC_DECODER_HELIX
#include "aac_decoder.h"
#endif
#ifdef CONFIG_YORADIO_MP3_DECODER_HELIX
#include "mp3_decoder.h"
#endif
#ifdef CONFIG_YORADIO_MP3_DECODER_MINIMP3
#include "CodecMemoryArena.h"
#define MINIMP3_ONLY_MP3
#define MINIMP3_NO_SIMD
#define MINIMP3_EXTERNAL_SCRATCH
#define MINIMP3_IMPLEMENTATION
#include "minimp3.h"
#endif

namespace {

constexpr size_t kInitialInputCapacity = 4096;
constexpr size_t kMaximumInputCapacity = 16 * 1024;
constexpr size_t kMaximumPcmSamples = 1152 * 2;
constexpr char kTag[] = "custom_legacy";

struct Mp3Header {
    size_t frame_size;
    uint32_t bitrate;
    uint32_t sample_rate;
    uint8_t channels;
};

bool parse_mp3_header(const uint8_t *data, size_t size, Mp3Header *header) {
    static const uint16_t mpeg1_bitrates[15] = {
        0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320};
    static const uint16_t mpeg2_bitrates[15] = {
        0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160};
    static const uint32_t sample_rates[3] = {44100, 48000, 32000};
    if (!data || size < 4 || data[0] != 0xff || (data[1] & 0xe0) != 0xe0) {
        return false;
    }
    uint8_t version = (data[1] >> 3) & 3;
    uint8_t layer = (data[1] >> 1) & 3;
    uint8_t bitrate_index = data[2] >> 4;
    uint8_t rate_index = (data[2] >> 2) & 3;
    if (version == 1 || layer != 1 || bitrate_index == 0 ||
        bitrate_index == 15 || rate_index == 3) {
        return false;
    }
    bool mpeg1 = version == 3;
    uint32_t rate = sample_rates[rate_index];
    if (version == 2) rate /= 2;
    if (version == 0) rate /= 4;
    uint32_t bitrate_kbps = mpeg1 ? mpeg1_bitrates[bitrate_index]
                                  : mpeg2_bitrates[bitrate_index];
    size_t frame_size =
        ((mpeg1 ? 144000U : 72000U) * bitrate_kbps) / rate +
        ((data[2] >> 1) & 1);
    if (frame_size < 24 || frame_size > kMaximumInputCapacity) return false;
    *header = {frame_size, bitrate_kbps * 1000U, rate,
               static_cast<uint8_t>((data[3] >> 6) == 3 ? 1 : 2)};
    return true;
}

int find_mp3_sync(const uint8_t *data, size_t size, Mp3Header *header) {
    for (size_t offset = 0; offset + 4 <= size; ++offset) {
        if (parse_mp3_header(data + offset, size - offset, header)) {
            return static_cast<int>(offset);
        }
    }
    return -1;
}

#ifdef CONFIG_YORADIO_AAC_DECODER_HELIX
int find_aac_sync(const uint8_t *data, size_t size) {
    for (size_t offset = 0; offset + 1 < size; ++offset) {
        if (data[offset] == 0xff && (data[offset + 1] & 0xf6) == 0xf0) {
            return static_cast<int>(offset);
        }
    }
    return -1;
}

size_t adts_frame_size(const uint8_t *data, size_t size) {
    if (size < 7) return 0;
    return (static_cast<size_t>(data[3] & 3) << 11) |
           (static_cast<size_t>(data[4]) << 3) | (data[5] >> 5);
}
#endif

}  // namespace

struct custom_legacy_decoder {
    custom_legacy_kind_t kind;
    uint8_t *input = nullptr;
    size_t input_size = 0;
    size_t input_capacity = 0;
    int16_t pcm[kMaximumPcmSamples] = {};
#ifdef CONFIG_YORADIO_MP3_DECODER_MINIMP3
    mp3dec_t minimp3 = {};
#endif
};

static bool reserve_input(custom_legacy_decoder *decoder, size_t required) {
    if (required <= decoder->input_capacity) return true;
    size_t capacity = decoder->input_capacity ? decoder->input_capacity
                                              : kInitialInputCapacity;
    while (capacity < required && capacity < kMaximumInputCapacity) capacity *= 2;
    if (capacity < required || capacity > kMaximumInputCapacity) return false;
    uint8_t *resized = static_cast<uint8_t *>(
        std::realloc(decoder->input, capacity));
    if (!resized) return false;
    decoder->input = resized;
    decoder->input_capacity = capacity;
    return true;
}

static void consume_input(custom_legacy_decoder *decoder, size_t consumed,
                          custom_legacy_feed_stats_t *stats) {
    consumed = std::min(consumed, decoder->input_size);
    std::memmove(decoder->input, decoder->input + consumed,
                 decoder->input_size - consumed);
    decoder->input_size -= consumed;
    stats->input_bytes += static_cast<uint32_t>(consumed);
}

static int decode_aac(custom_legacy_decoder *decoder,
                      custom_legacy_pcm_callback_t callback, void *user,
                      custom_legacy_feed_stats_t *stats) {
#ifndef CONFIG_YORADIO_AAC_DECODER_HELIX
    (void)decoder; (void)callback; (void)user; (void)stats;
    return -10;
#else
    int sync = find_aac_sync(decoder->input, decoder->input_size);
    if (sync < 0) {
        if (decoder->input_size > 1) consume_input(decoder, decoder->input_size - 1, stats);
        return 1;
    }
    if (sync) consume_input(decoder, static_cast<size_t>(sync), stats);
    size_t frame_size = adts_frame_size(decoder->input, decoder->input_size);
    if (!frame_size || frame_size > kMaximumInputCapacity) return -11;
    if (decoder->input_size < frame_size) return 1;

    int bytes_left = static_cast<int>(frame_size);
    int64_t started = esp_timer_get_time();
    int result = AACDecode(decoder->input, &bytes_left, decoder->pcm);
    uint32_t elapsed = static_cast<uint32_t>(esp_timer_get_time() - started);
    stats->decode_us += elapsed;
    ++stats->decode_calls;
    stats->max_call_us = std::max(stats->max_call_us, elapsed);
    size_t consumed = frame_size - std::min(frame_size,
        static_cast<size_t>(std::max(bytes_left, 0)));
    if (result != ERR_AAC_NONE) {
        ESP_LOGW(kTag, "Helix AAC frame error %d", result);
        consume_input(decoder, consumed ? consumed : 1, stats);
        return 0;
    }
    custom_legacy_info_t info = {
        static_cast<uint32_t>(AACGetSampRate()),
        static_cast<uint8_t>(AACGetBitsPerSample()),
        static_cast<uint8_t>(AACGetChannels()),
        static_cast<uint32_t>(AACGetBitrate()),
    };
    size_t pcm_size = static_cast<size_t>(AACGetOutputSamps()) * sizeof(int16_t);
    if (!info.sample_rate || info.channels < 1 || info.channels > 2 ||
        pcm_size > sizeof(decoder->pcm)) return -12;
    if (!callback(user, &info, reinterpret_cast<uint8_t *>(decoder->pcm), pcm_size)) {
        return -13;
    }
    consume_input(decoder, consumed ? consumed : frame_size, stats);
    return 0;
#endif
}

static int decode_mp3(custom_legacy_decoder *decoder,
                      custom_legacy_pcm_callback_t callback, void *user,
                      custom_legacy_feed_stats_t *stats) {
    Mp3Header parsed = {};
    int sync = find_mp3_sync(decoder->input, decoder->input_size, &parsed);
    if (sync < 0) {
        if (decoder->input_size > 3) consume_input(decoder, decoder->input_size - 3, stats);
        return 1;
    }
    if (sync) consume_input(decoder, static_cast<size_t>(sync), stats);
    if (decoder->input_size < parsed.frame_size) return 1;

    int result = 0;
    size_t consumed = parsed.frame_size;
    size_t output_samples = 0;
    custom_legacy_info_t info = {parsed.sample_rate, 16, parsed.channels,
                                 parsed.bitrate};
    int64_t started = esp_timer_get_time();
#if defined(CONFIG_YORADIO_MP3_DECODER_HELIX)
    int bytes_left = static_cast<int>(parsed.frame_size);
    result = MP3Decode(decoder->input, &bytes_left, decoder->pcm, 0);
    consumed = parsed.frame_size - std::min(parsed.frame_size,
        static_cast<size_t>(std::max(bytes_left, 0)));
    if (result == ERR_MP3_NONE) {
        info.sample_rate = MP3GetSampRate();
        info.channels = MP3GetChannels();
        info.bits_per_sample = MP3GetBitsPerSample();
        info.bitrate = MP3GetBitrate();
        output_samples = MP3GetOutputSamps();
    }
#elif defined(CONFIG_YORADIO_MP3_DECODER_MINIMP3)
    mp3dec_frame_info_t frame_info = {};
    int per_channel = mp3dec_decode_frame(&decoder->minimp3, decoder->input,
                                           static_cast<int>(parsed.frame_size),
                                           decoder->pcm, &frame_info);
    if (frame_info.frame_bytes != static_cast<int>(parsed.frame_size)) result = -1;
    if (!result) {
        info.sample_rate = frame_info.hz;
        info.channels = frame_info.channels;
        info.bitrate = frame_info.bitrate_kbps * 1000U;
        output_samples = static_cast<size_t>(per_channel) * frame_info.channels;
    }
#else
    result = -1;
#endif
    uint32_t elapsed = static_cast<uint32_t>(esp_timer_get_time() - started);
    stats->decode_us += elapsed;
    ++stats->decode_calls;
    stats->max_call_us = std::max(stats->max_call_us, elapsed);
    if (result != 0) {
        ESP_LOGW(kTag, "Custom MP3 frame error %d", result);
        consume_input(decoder, consumed ? consumed : 1, stats);
        return 0;
    }
    size_t pcm_size = output_samples * sizeof(int16_t);
    if (!info.sample_rate || info.channels < 1 || info.channels > 2 ||
        pcm_size > sizeof(decoder->pcm)) return -21;
    if (pcm_size && !callback(user, &info,
                              reinterpret_cast<uint8_t *>(decoder->pcm),
                              pcm_size)) return -22;
    consume_input(decoder, consumed ? consumed : parsed.frame_size, stats);
    return 0;
}

extern "C" custom_legacy_decoder_t *custom_legacy_decoder_create(
    custom_legacy_kind_t kind) {
    bool supported =
#ifdef CONFIG_YORADIO_AAC_DECODER_HELIX
        kind == CUSTOM_LEGACY_AAC ||
#endif
#if defined(CONFIG_YORADIO_MP3_DECODER_HELIX) || defined(CONFIG_YORADIO_MP3_DECODER_MINIMP3)
        kind == CUSTOM_LEGACY_MP3 ||
#endif
        false;
    if (!supported) return nullptr;
    auto *decoder = new (std::nothrow) custom_legacy_decoder;
    if (!decoder || !reserve_input(decoder, kInitialInputCapacity)) {
        delete decoder;
        return nullptr;
    }
    decoder->kind = kind;
    bool allocated = false;
    if (kind == CUSTOM_LEGACY_AAC) {
#ifdef CONFIG_YORADIO_AAC_DECODER_HELIX
        allocated = AACDecoder_AllocateBuffers();
#endif
    } else {
#ifdef CONFIG_YORADIO_MP3_DECODER_HELIX
        allocated = MP3Decoder_AllocateBuffers();
#elif defined(CONFIG_YORADIO_MP3_DECODER_MINIMP3)
        allocated = mp3dec_alloc_scratch();
        if (allocated) mp3dec_init(&decoder->minimp3);
#endif
    }
    if (!allocated) {
        custom_legacy_decoder_destroy(decoder);
        return nullptr;
    }
    ESP_LOGI(kTag, "Using yoRadio %s decoder",
             kind == CUSTOM_LEGACY_AAC ? "Helix AAC-LC" :
#ifdef CONFIG_YORADIO_MP3_DECODER_MINIMP3
             "minimp3"
#else
             "Helix MP3"
#endif
    );
    return decoder;
}

extern "C" void custom_legacy_decoder_destroy(custom_legacy_decoder_t *decoder) {
    if (!decoder) return;
    if (decoder->kind == CUSTOM_LEGACY_AAC) {
#ifdef CONFIG_YORADIO_AAC_DECODER_HELIX
        AACDecoder_FreeBuffers();
#endif
    } else {
#ifdef CONFIG_YORADIO_MP3_DECODER_HELIX
        MP3Decoder_FreeBuffers();
#elif defined(CONFIG_YORADIO_MP3_DECODER_MINIMP3)
        mp3dec_free_scratch();
#endif
    }
    std::free(decoder->input);
    delete decoder;
}

extern "C" int custom_legacy_decoder_feed(
    custom_legacy_decoder_t *decoder, const uint8_t *data, size_t size, bool eos,
    custom_legacy_pcm_callback_t callback, void *user,
    custom_legacy_feed_stats_t *stats) {
    if (!decoder || (!data && size) || !callback || !stats) return -1;
    *stats = {};
    if (size) {
        if (!reserve_input(decoder, decoder->input_size + size)) return -2;
        std::memcpy(decoder->input + decoder->input_size, data, size);
        decoder->input_size += size;
    }
    while (decoder->input_size) {
        size_t before = decoder->input_size;
        int result = decoder->kind == CUSTOM_LEGACY_AAC
                         ? decode_aac(decoder, callback, user, stats)
                         : decode_mp3(decoder, callback, user, stats);
        if (result < 0 || result == 1) return result;
        if (decoder->input_size >= before) return -3;
    }
    (void)eos;
    return 0;
}
