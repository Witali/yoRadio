#include "codec_bridge.h"

#include <algorithm>
#include <cstdlib>
#include <cstring>

#include "CodecMemoryArena.h"
#include "aac_decoder.h"
#include "codec_arena_native.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "mp3_decoder.h"

namespace {
constexpr size_t kArenaBytes = 23328U;
/* 1536 bytes covers a maximum-size 320-kbit/s MP3 frame and normal
 * high-bitrate ADTS AAC frames while conserving scarce ESP8266 DRAM. */
constexpr size_t kInputBytes = 1536U;
constexpr size_t kPcmSamples = 1152U * 2U;
constexpr char kTag[] = "helix_bridge";

struct Mp3Header {
    size_t frame_size;
    uint32_t bitrate;
    uint32_t sample_rate;
    uint8_t channels;
};

bool parse_mp3(const uint8_t *data, size_t size, Mp3Header *header) {
    static const uint16_t rate1[] =
        {0,32,40,48,56,64,80,96,112,128,160,192,224,256,320};
    static const uint16_t rate2[] =
        {0,8,16,24,32,40,48,56,64,80,96,112,128,144,160};
    static const uint32_t samples[] = {44100, 48000, 32000};
    if (size < 4 || data[0] != 0xff || (data[1] & 0xe0) != 0xe0) return false;
    uint8_t version = (data[1] >> 3) & 3;
    uint8_t layer = (data[1] >> 1) & 3;
    uint8_t bitrate_index = data[2] >> 4;
    uint8_t sample_index = (data[2] >> 2) & 3;
    if (version == 1 || layer != 1 || bitrate_index == 0 ||
        bitrate_index == 15 || sample_index == 3) return false;
    bool mpeg1 = version == 3;
    uint32_t sample_rate = samples[sample_index];
    if (version == 2) sample_rate /= 2;
    if (version == 0) sample_rate /= 4;
    uint32_t bitrate = (mpeg1 ? rate1[bitrate_index] : rate2[bitrate_index]);
    size_t frame_size = ((mpeg1 ? 144000U : 72000U) * bitrate) /
                        sample_rate + ((data[2] >> 1) & 1U);
    if (frame_size < 24 || frame_size > kInputBytes) return false;
    *header = {frame_size, bitrate * 1000U, sample_rate,
               static_cast<uint8_t>((data[3] >> 6) == 3 ? 1 : 2)};
    return true;
}

int find_mp3(const uint8_t *data, size_t size, Mp3Header *header) {
    for (size_t offset = 0; offset + 4 <= size; ++offset)
        if (parse_mp3(data + offset, size - offset, header))
            return static_cast<int>(offset);
    return -1;
}

int find_aac(const uint8_t *data, size_t size) {
    for (size_t offset = 0; offset + 1 < size; ++offset)
        if (data[offset] == 0xff && (data[offset + 1] & 0xf6) == 0xf0)
            return static_cast<int>(offset);
    return -1;
}

size_t aac_frame_size(const uint8_t *data, size_t size) {
    if (size < 7) return 0;
    return (static_cast<size_t>(data[3] & 3U) << 11) |
           (static_cast<size_t>(data[4]) << 3) | (data[5] >> 5);
}
}

struct helix_codec {
    helix_codec_kind_t kind;
    size_t input_start;
    size_t input_size;
    uint8_t *arena;
    uint8_t *input;
    int16_t *pcm;
};
static constexpr size_t kWorkspaceBytes = sizeof(helix_codec) +
    kArenaBytes + kInputBytes + sizeof(int16_t) * kPcmSamples;


static void free_decoder(helix_codec *codec) {
    if (codec->kind == HELIX_CODEC_MP3) MP3Decoder_FreeBuffers();
    else if (codec->kind == HELIX_CODEC_AAC) AACDecoder_FreeBuffers();
}

static bool allocate_decoder(helix_codec *codec, helix_codec_kind_t kind) {
    codec->kind = kind;
    codec->input_start = codec->input_size = 0;
    return kind == HELIX_CODEC_MP3 ? MP3Decoder_AllocateBuffers()
                                   : AACDecoder_AllocateBuffers();
}

static void consume(helix_codec *codec, size_t count) {
    count = std::min(count, codec->input_size);
    codec->input_start += count;
    codec->input_size -= count;
    if (!codec->input_size) codec->input_start = 0;
}

static void compact(helix_codec *codec) {
    if (codec->input_start && codec->input_size) {
        std::memmove(codec->input, codec->input + codec->input_start,
                     codec->input_size);
        codec->input_start = 0;
    }
}

static int decode_one(helix_codec *codec, helix_pcm_callback_t callback,
                      void *context) {
    uint8_t *input = codec->input + codec->input_start;
    if (codec->kind == HELIX_CODEC_MP3) {
        Mp3Header parsed = {};
        int sync = find_mp3(input, codec->input_size, &parsed);
        if (sync < 0) {
            if (codec->input_size > 3) consume(codec, codec->input_size - 3);
            return 1;
        }
        if (sync) {
            consume(codec, static_cast<size_t>(sync));
            input = codec->input + codec->input_start;
        }
        if (codec->input_size < parsed.frame_size) return 1;
        int left = static_cast<int>(parsed.frame_size);
        int result = MP3Decode(input, &left, codec->pcm, 0);
        size_t used = parsed.frame_size - std::min(
            parsed.frame_size, static_cast<size_t>(std::max(left, 0)));
        if (result != ERR_MP3_NONE) {
            consume(codec, used ? used : 1);
            return 0;
        }
        helix_stream_info_t info = {
            static_cast<uint32_t>(MP3GetSampRate()),
            static_cast<uint32_t>(MP3GetBitrate()),
            static_cast<uint8_t>(MP3GetChannels()),
            static_cast<uint8_t>(MP3GetBitsPerSample()),
        };
        size_t samples = static_cast<size_t>(MP3GetOutputSamps());
        if (!samples || samples > kPcmSamples || !callback(context, &info,
                                                           codec->pcm,
                                                           samples)) return -5;
        consume(codec, used ? used : parsed.frame_size);
        return 0;
    }

    int sync = find_aac(input, codec->input_size);
    if (sync < 0) {
        if (codec->input_size > 1) consume(codec, codec->input_size - 1);
        return 1;
    }
    if (sync) {
        consume(codec, static_cast<size_t>(sync));
        input = codec->input + codec->input_start;
    }
    if (codec->input_size < 7) return 1;
    size_t frame = aac_frame_size(input, codec->input_size);
    if (!frame || frame > kInputBytes) return -6;
    if (codec->input_size < frame) return 1;
    int left = static_cast<int>(frame);
    int result = AACDecode(input, &left, codec->pcm);
    size_t used = frame - std::min(frame,
        static_cast<size_t>(std::max(left, 0)));
    if (result != ERR_AAC_NONE) {
        consume(codec, used ? used : 1);
        return 0;
    }
    helix_stream_info_t info = {
        static_cast<uint32_t>(AACGetSampRate()),
        static_cast<uint32_t>(AACGetBitrate()),
        static_cast<uint8_t>(AACGetChannels()),
        static_cast<uint8_t>(AACGetBitsPerSample()),
    };
    size_t samples = static_cast<size_t>(AACGetOutputSamps());
    if (!samples || samples > kPcmSamples ||
        !callback(context, &info, codec->pcm, samples)) return -7;
    consume(codec, used ? used : frame);
    return 0;
}

extern "C" helix_codec_t *helix_codec_create(helix_codec_kind_t kind,
                                               size_t reserve_heap_bytes) {
    if (kind != HELIX_CODEC_MP3 && kind != HELIX_CODEC_AAC) return nullptr;
    size_t free_heap = esp_get_free_heap_size();
    if (free_heap < kWorkspaceBytes + reserve_heap_bytes) {
        ESP_LOGE(kTag, "Need %u bytes, free heap %u, reserve %u",
                 (unsigned)kWorkspaceBytes, (unsigned)free_heap,
                 (unsigned)reserve_heap_bytes);
        return nullptr;
    }
    helix_codec *codec = static_cast<helix_codec *>(std::calloc(1, sizeof(*codec)));
    if (codec) {
        codec->input = static_cast<uint8_t *>(
            heap_caps_malloc(kInputBytes, MALLOC_CAP_8BIT));
        codec->pcm = static_cast<int16_t *>(
            heap_caps_malloc(sizeof(int16_t) * kPcmSamples, MALLOC_CAP_8BIT));
    }
    if (!codec || !codec->input || !codec->pcm ||
        !CodecArenaBind(nullptr, kArenaBytes)) {
        if (codec) {
            heap_caps_free(codec->pcm);
            heap_caps_free(codec->input);
            heap_caps_free(codec->arena);
        }
        std::free(codec);
        ESP_LOGE(kTag, "Heap cannot allocate %u-byte workspace",
                 (unsigned)kWorkspaceBytes);
        return nullptr;
    }
    bool allocated = allocate_decoder(codec, kind);
    if (!allocated) {
        if (kind == HELIX_CODEC_MP3) MP3Decoder_FreeBuffers();
        else AACDecoder_FreeBuffers();
        CodecArenaUnbind();
        heap_caps_free(codec->pcm);
        heap_caps_free(codec->input);
        heap_caps_free(codec->arena);
        std::free(codec);
        return nullptr;
    }
    ESP_LOGI(kTag, "%s workspace: %u bytes, arena used: %u",
             kind == HELIX_CODEC_MP3 ? "MP3" : "AAC",
             (unsigned)kWorkspaceBytes, (unsigned)CodecArenaUsed());
    return codec;
}

extern "C" void helix_codec_destroy(helix_codec_t *codec) {
    if (!codec) return;
    free_decoder(codec);
    if (!CodecArenaUnbind()) ESP_LOGE(kTag, "Codec arena is still owned");
    heap_caps_free(codec->pcm);
    heap_caps_free(codec->input);
    heap_caps_free(codec->arena);
    std::free(codec);
}

extern "C" int helix_codec_switch(helix_codec_t *codec,
                                   helix_codec_kind_t kind) {
    if (!codec || (kind != HELIX_CODEC_MP3 && kind != HELIX_CODEC_AAC))
        return -1;
    if (codec->kind == kind) {
        codec->input_start = codec->input_size = 0;
        if (kind == HELIX_CODEC_MP3) {
            MP3Decoder_ClearBuffer();
            return 0;
        }
        /* AAC has no public state-reset entry point. Release/rebuild its
         * objects inside the same bound arena; the outer heap block remains
         * allocated and cannot fragment. */
        free_decoder(codec);
        return allocate_decoder(codec, kind) ? 0 : -2;
    }
    free_decoder(codec);
    if (!allocate_decoder(codec, kind)) {
        free_decoder(codec);
        return -2;
    }
    return 0;
}

extern "C" helix_codec_kind_t helix_codec_detect(const uint8_t *data,
                                                   size_t size) {
    Mp3Header header = {};
    int mp3 = find_mp3(data, size, &header);
    int aac = find_aac(data, size);
    if (mp3 >= 0 && (aac < 0 || mp3 <= aac)) return HELIX_CODEC_MP3;
    if (aac >= 0) return HELIX_CODEC_AAC;
    return static_cast<helix_codec_kind_t>(0);
}

extern "C" uint8_t *helix_codec_write_pointer(helix_codec_t *codec,
                                                size_t *capacity) {
    if (!codec || !capacity) return nullptr;
    if (codec->input_start + codec->input_size == kInputBytes) compact(codec);
    *capacity = kInputBytes - codec->input_start - codec->input_size;
    return codec->input + codec->input_start + codec->input_size;
}

extern "C" int helix_codec_commit(helix_codec_t *codec, size_t size,
                                   helix_pcm_callback_t callback,
                                   void *context) {
    if (!codec || !callback) return -1;
    size_t capacity = 0;
    helix_codec_write_pointer(codec, &capacity);
    if (size > capacity) return -2;
    codec->input_size += size;
    while (codec->input_size) {
        size_t before = codec->input_size;
        int result = decode_one(codec, callback, context);
        if (result < 0) return result;
        if (result == 1 || codec->input_size >= before) break;
    }
    return 0;
}

extern "C" int helix_codec_feed(helix_codec_t *codec, const uint8_t *data,
                                 size_t size, bool eos,
                                 helix_pcm_callback_t callback,
                                 void *context) {
    if (!codec || (!data && size) || !callback) return -1;
    while (size) {
        if (codec->input_start + codec->input_size == kInputBytes) compact(codec);
        size_t free_space = kInputBytes - codec->input_start - codec->input_size;
        if (!free_space) {
            int result = decode_one(codec, callback, context);
            if (result != 0) return result == 1 ? -2 : result;
            continue;
        }
        size_t copied = std::min(size, free_space);
        std::memcpy(codec->input + codec->input_start + codec->input_size,
                    data, copied);
        data += copied;
        size -= copied;
        int result = helix_codec_commit(codec, copied, callback, context);
        if (result < 0) return result;
    }
    if (eos) codec->input_size = codec->input_start = 0;
    return 0;
}

extern "C" size_t helix_codec_workspace_size(void) {
    return kWorkspaceBytes;
}

extern "C" size_t helix_codec_arena_used(const helix_codec_t *codec) {
    return codec ? CodecArenaUsed() : 0;
}
