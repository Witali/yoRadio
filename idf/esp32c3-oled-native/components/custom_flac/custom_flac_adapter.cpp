#include "custom_flac_adapter.h"

#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <new>

#include "esp_log.h"
#include "esp_timer.h"
#include "flac_decoder.h"

namespace {

constexpr size_t kInitialInputCapacity = 4096;
constexpr size_t kInputSlack = 2048;
constexpr size_t kUnknownFrameWindow = 32 * 1024;
constexpr size_t kMaximumFrameWindow = 64 * 1024;
constexpr size_t kPcmSamplesPerCall = 2048 * MAX_CHANNELS;
constexpr char kTag[] = "custom_flac";

uint32_t read_be24(const uint8_t *data) {
    return (static_cast<uint32_t>(data[0]) << 16) |
           (static_cast<uint32_t>(data[1]) << 8) | data[2];
}

uint64_t read_total_samples(const uint8_t *streaminfo) {
    return (static_cast<uint64_t>(streaminfo[13] & 0x0f) << 32) |
           (static_cast<uint64_t>(streaminfo[14]) << 24) |
           (static_cast<uint64_t>(streaminfo[15]) << 16) |
           (static_cast<uint64_t>(streaminfo[16]) << 8) | streaminfo[17];
}

}  // namespace

struct custom_flac_decoder {
    uint8_t *input = nullptr;
    size_t input_size = 0;
    size_t input_capacity = 0;
    size_t frame_window = 0;
    bool header_ready = false;
    bool at_frame_start = true;
    custom_flac_info_t info = {};
    int16_t pcm[kPcmSamplesPerCall] = {};
};

static bool reserve_input(custom_flac_decoder *decoder, size_t required) {
    if (required <= decoder->input_capacity) return true;
    size_t capacity = decoder->input_capacity
                          ? decoder->input_capacity
                          : kInitialInputCapacity;
    while (capacity < required && capacity < kMaximumFrameWindow + kInputSlack) {
        capacity *= 2;
    }
    if (capacity < required || capacity > kMaximumFrameWindow + kInputSlack) {
        return false;
    }
    auto *resized = static_cast<uint8_t *>(
        std::realloc(decoder->input, capacity));
    if (!resized) return false;
    decoder->input = resized;
    decoder->input_capacity = capacity;
    return true;
}

static int parse_header(custom_flac_decoder *decoder) {
    if (decoder->input_size < 4) return 1;
    if (std::memcmp(decoder->input, "fLaC", 4) != 0) return -1;

    size_t offset = 4;
    bool have_streaminfo = false;
    uint16_t max_block_size = 0;
    uint32_t max_frame_size = 0;
    uint64_t total_samples = 0;
    while (true) {
        if (decoder->input_size < offset + 4) return 1;
        const uint8_t block_header = decoder->input[offset];
        const uint8_t block_type = block_header & 0x7f;
        const uint32_t block_size = read_be24(decoder->input + offset + 1);
        if (block_size > kMaximumFrameWindow ||
            offset + 4 + block_size > kMaximumFrameWindow) {
            ESP_LOGE(kTag, "FLAC metadata is too large: %lu bytes",
                     static_cast<unsigned long>(block_size));
            return -2;
        }
        if (decoder->input_size < offset + 4 + block_size) return 1;
        if (block_type == 0) {
            if (block_size != 34) return -3;
            const uint8_t *streaminfo = decoder->input + offset + 4;
            max_block_size =
                (static_cast<uint16_t>(streaminfo[2]) << 8) | streaminfo[3];
            max_frame_size = read_be24(streaminfo + 7);
            decoder->info.sample_rate =
                (static_cast<uint32_t>(streaminfo[10]) << 12) |
                (static_cast<uint32_t>(streaminfo[11]) << 4) |
                (streaminfo[12] >> 4);
            decoder->info.channels = ((streaminfo[12] >> 1) & 0x07) + 1;
            decoder->info.bits_per_sample =
                (((streaminfo[12] & 0x01) << 4) | (streaminfo[13] >> 4)) + 1;
            total_samples = read_total_samples(streaminfo);
            have_streaminfo = true;
        }
        offset += 4 + block_size;
        if (block_header & 0x80) break;
    }

    if (!have_streaminfo || !max_block_size ||
        decoder->info.channels < 1 || decoder->info.channels > MAX_CHANNELS ||
        (decoder->info.bits_per_sample != 8 &&
         decoder->info.bits_per_sample != 16) ||
        !decoder->info.sample_rate) {
        return -4;
    }
    decoder->frame_window = max_frame_size ? max_frame_size
                                           : kUnknownFrameWindow;
    if (decoder->frame_window > kMaximumFrameWindow ||
        !reserve_input(decoder, decoder->frame_window + kInputSlack)) {
        return -5;
    }
    if (!FLACDecoder_AllocateBuffers(max_block_size, decoder->info.channels)) {
        return -6;
    }
    FLACSetRawBlockParams(decoder->info.channels, decoder->info.sample_rate,
                          decoder->info.bits_per_sample,
                          static_cast<uint32_t>(total_samples), 0);
    std::memmove(decoder->input, decoder->input + offset,
                 decoder->input_size - offset);
    decoder->input_size -= offset;
    decoder->header_ready = true;
    ESP_LOGI(kTag,
             "yoRadio FLAC: %lu Hz, %u-bit, %u ch, block %u, frame %lu, buffers %lu bytes",
             static_cast<unsigned long>(decoder->info.sample_rate),
             decoder->info.bits_per_sample, decoder->info.channels,
             max_block_size, static_cast<unsigned long>(decoder->frame_window),
             static_cast<unsigned long>(FLACDecoder_GetAllocatedBytes()));
    return 0;
}

static int decode_available(custom_flac_decoder *decoder, bool eos,
                            custom_flac_pcm_callback_t callback, void *user,
                            custom_flac_feed_stats_t *stats) {
    while (decoder->input_size &&
           (!decoder->at_frame_start || eos ||
            decoder->input_size >= decoder->frame_window)) {
        if (decoder->at_frame_start) {
            int sync = FLACFindSyncWord(decoder->input,
                                        static_cast<int>(decoder->input_size));
            if (sync < 0) {
                if (!eos && decoder->input_size < decoder->frame_window) return 1;
                size_t keep = eos ? 0 : 1;
                if (decoder->input_size > keep) {
                    size_t drop = decoder->input_size - keep;
                    std::memmove(decoder->input, decoder->input + drop, keep);
                    decoder->input_size = keep;
                    stats->input_bytes += static_cast<uint32_t>(drop);
                }
                return eos ? -7 : 1;
            }
            if (sync) {
                std::memmove(decoder->input, decoder->input + sync,
                             decoder->input_size - sync);
                decoder->input_size -= sync;
                stats->input_bytes += static_cast<uint32_t>(sync);
            }
        }

        int bytes_left = static_cast<int>(decoder->input_size);
        int64_t started = esp_timer_get_time();
        int8_t result = FLACDecode(decoder->input, &bytes_left, decoder->pcm);
        uint32_t elapsed = static_cast<uint32_t>(esp_timer_get_time() - started);
        stats->decode_us += elapsed;
        ++stats->decode_calls;
        stats->max_call_us = std::max(stats->max_call_us, elapsed);

        size_t consumed = decoder->input_size -
                          std::min(decoder->input_size,
                                   static_cast<size_t>(std::max(bytes_left, 0)));
        uint16_t samples = FLACGetOutputSamps();
        if (samples) {
            size_t frames = samples / decoder->info.channels;
            if (decoder->info.channels == 1) {
                for (size_t i = 0; i < frames; ++i) {
                    decoder->pcm[i] = decoder->pcm[i * 2];
                }
            }
            size_t pcm_size = frames * decoder->info.channels * sizeof(int16_t);
            if (!callback(user, &decoder->info,
                          reinterpret_cast<const uint8_t *>(decoder->pcm),
                          pcm_size)) {
                return -8;
            }
        }

        if (result < 0) {
            ESP_LOGW(kTag, "FLAC decode error %d", result);
            size_t drop = std::min<size_t>(decoder->input_size, consumed ? consumed : 2);
            std::memmove(decoder->input, decoder->input + drop,
                         decoder->input_size - drop);
            decoder->input_size -= drop;
            stats->input_bytes += static_cast<uint32_t>(drop);
            decoder->at_frame_start = true;
            FLACDecoderReset();
            continue;
        }

        if (consumed) {
            std::memmove(decoder->input, decoder->input + consumed,
                         decoder->input_size - consumed);
            decoder->input_size -= consumed;
            stats->input_bytes += static_cast<uint32_t>(consumed);
        }
        if (result == GIVE_NEXT_LOOP) {
            decoder->at_frame_start = false;
            continue;
        }
        if (samples && consumed) {
            decoder->at_frame_start = true;
            continue;
        }
        if (consumed) {
            decoder->at_frame_start = false;
            continue;
        }
        return 1;
    }
    return 0;
}

extern "C" custom_flac_decoder_t *custom_flac_decoder_create(void) {
    auto *decoder = new (std::nothrow) custom_flac_decoder;
    if (!decoder || !reserve_input(decoder, kInitialInputCapacity)) {
        delete decoder;
        return nullptr;
    }
    return decoder;
}

extern "C" void custom_flac_decoder_destroy(custom_flac_decoder_t *decoder) {
    if (!decoder) return;
    FLACDecoder_FreeBuffers();
    std::free(decoder->input);
    delete decoder;
}

extern "C" int custom_flac_decoder_feed(
    custom_flac_decoder_t *decoder, const uint8_t *data, size_t size, bool eos,
    custom_flac_pcm_callback_t callback, void *user,
    custom_flac_feed_stats_t *stats) {
    if (!decoder || (!data && size) || !callback || !stats) return -1;
    *stats = {};
    if (size) {
        if (!reserve_input(decoder, decoder->input_size + size)) return -2;
        std::memcpy(decoder->input + decoder->input_size, data, size);
        decoder->input_size += size;
    }
    if (!decoder->header_ready) {
        int parsed = parse_header(decoder);
        if (parsed != 0) return parsed;
    }
    return decode_available(decoder, eos, callback, user, stats);
}
