#include "codec_bridge.h"

#include <algorithm>
#include <cstdlib>
#include <cstring>

#include "CodecMemoryArena.h"
#include "sdkconfig.h"
#ifndef CONFIG_YORADIO_AUDIO_MONO
#define CONFIG_YORADIO_AUDIO_MONO 0
#endif
#if CONFIG_YORADIO_HELIX_AAC
#include "aac_decoder.h"
#endif
#include "codec_arena_native.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#if YORADIO_ESP8266_OPUS_BENCHMARK
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#endif
#if CONFIG_YORADIO_OGG_OPUS
#include "native_opus.h"
#include "opus_memory.h"
#endif
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
extern "C" {
#include "../libmad8266/upstream/libmad/config.h"
#include "mad.h"
}
#else
#include "mp3_decoder.h"
#endif

#if YORADIO_ESP8266_AUDIO_PROFILE
extern "C" void audio_profile_decode_begin(void);
extern "C" void audio_profile_decode_end(void);
#endif

namespace {
#if YORADIO_ESP8266_OPUS_BENCHMARK
static helix_opus_init_failure_t s_opus_init_failure;
static_assert(sizeof(s_opus_init_failure) == 20, "Keep init diagnostics bounded");
static void opus_init_diagnostic_reset() {
    taskENTER_CRITICAL();
    s_opus_init_failure = {};
    taskEXIT_CRITICAL();
}
static void opus_init_failed(helix_codec_kind_t kind, uint32_t stage,
                             size_t requested, size_t reserve, int32_t detail) {
    if (kind != HELIX_CODEC_OPUS) return;
    const helix_opus_init_failure_t failure = {
        stage, static_cast<uint32_t>(heap_caps_get_free_size(MALLOC_CAP_8BIT)),
        static_cast<uint32_t>(requested),
        static_cast<uint32_t>(std::max(reserve, size_t(4096))), detail};
    taskENTER_CRITICAL();
    if (!s_opus_init_failure.stage) s_opus_init_failure = failure;
    taskEXIT_CRITICAL();
}
#else
#define opus_init_diagnostic_reset() ((void)0)
#define opus_init_failed(kind, stage, requested, reserve, detail) ((void)0)
#endif

#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
constexpr size_t kLibmadXrSamples = 576U * 2U;
constexpr size_t kLibmadReorderSamples = 576U;
constexpr size_t kLegacyArenaBytes = sizeof(mad_stream) + sizeof(mad_frame) +
                               sizeof(mad_synth) +
                               sizeof(mad_fixed_t) *
                                   (kLibmadXrSamples +
                                    kLibmadReorderSamples) +
                               5U * alignof(max_align_t);
#else
constexpr size_t kLegacyArenaBytes = 23328U;
#endif
#if CONFIG_YORADIO_OGG_OPUS
/* Logical allocation accounting, not an additional physical reservation. */
constexpr size_t kArenaBytes = 32768U + CONFIG_YORADIO_OPUS_SCRATCH_BYTES;
#else
constexpr size_t kArenaBytes = kLegacyArenaBytes;
#endif
/* Reuse the decoder input as read-ahead storage. Older host/experimental
 * configs without this option keep the original single-frame buffer. */
#ifndef CONFIG_YORADIO_STREAM_INPUT_BYTES
#define CONFIG_YORADIO_STREAM_INPUT_BYTES 1536
#endif
constexpr size_t kInputBytes = CONFIG_YORADIO_STREAM_INPUT_BYTES;
static_assert(kInputBytes >= 1536U && kInputBytes <= 8192U,
              "Compressed input must fit the ESP8266 memory budget");
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
constexpr size_t kInputStorageBytes = kInputBytes + MAD_BUFFER_GUARD;
#else
constexpr size_t kInputStorageBytes = kInputBytes;
#endif
/* Helix MP3 reuses one 32-frame synthesis block per callback. Native AAC
 * uses a bounded PCM block, with full-frame output retained for A/B. Allocate the active codec's
 * exact PCM size: reserving AAC's larger buffer while playing MP3 starved
 * lwIP on the ESP8266. */
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
constexpr size_t kMp3PcmSamples = 576U * (CONFIG_YORADIO_AUDIO_MONO ? 1U : 2U);
#else
constexpr size_t kMp3PcmSamples = MP3_PCM_BLOCK_FRAMES *
                                (CONFIG_YORADIO_AUDIO_MONO ? 1U : 2U);
#endif
#if CONFIG_YORADIO_HELIX_AAC
#if YORADIO_ESP8266_AAC_BLOCK_OUTPUT
constexpr size_t kAacPcmSamples = YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES *
                                (CONFIG_YORADIO_AUDIO_MONO ? 1U : 2U);
#else
constexpr size_t kAacPcmSamples = 1024U * 2U;
#endif
constexpr size_t kLegacyMaxPcmSamples = kAacPcmSamples > kMp3PcmSamples ? kAacPcmSamples : kMp3PcmSamples;
#else
constexpr size_t kLegacyMaxPcmSamples = kMp3PcmSamples;
#endif
#if CONFIG_YORADIO_OGG_OPUS
constexpr size_t kMaxPcmSamples = kLegacyMaxPcmSamples > 960U ? kLegacyMaxPcmSamples : 960U;
#else
constexpr size_t kMaxPcmSamples = kLegacyMaxPcmSamples;
#endif
constexpr char kTag[] = "helix_bridge";

size_t input_bytes_for_kind(helix_codec_kind_t kind) {
#if CONFIG_YORADIO_OGG_OPUS
    if (kind == HELIX_CODEC_OPUS) return CONFIG_YORADIO_OPUS_INPUT_BYTES;
#endif
    return kInputBytes;
}
size_t input_storage_bytes(size_t capacity) {
    return capacity + (kInputStorageBytes - kInputBytes);
}

size_t pcm_samples_for_kind(helix_codec_kind_t kind) {
#if CONFIG_YORADIO_OGG_OPUS
    if (kind == HELIX_CODEC_OPUS) return 960U;
#endif
#if CONFIG_YORADIO_HELIX_AAC
    if (kind == HELIX_CODEC_AAC) return kAacPcmSamples;
#endif
    return kMp3PcmSamples;
}

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

#if CONFIG_YORADIO_HELIX_AAC
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
#endif
}

struct helix_codec {
    helix_codec_kind_t kind;
    size_t input_start;
    size_t input_size;
    size_t input_capacity;
    uint8_t *input;
    size_t pcm_samples;
    int16_t *pcm;
    size_t dram_used;
    size_t iram_used;
    size_t reserve_heap_bytes;
};
static constexpr size_t kWorkspaceBytes = sizeof(helix_codec) +
    kArenaBytes + kInputStorageBytes + sizeof(int16_t) * kMaxPcmSamples;

#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
struct LibmadDecoder {
    mad_stream *stream;
    mad_frame *frame;
    mad_synth *synth;
};

LibmadDecoder s_libmad = {};

void libmad_free();

bool libmad_allocate() {
    /* Keep only aligned mad_fixed_t workspaces in the preallocated IRAM word
     * arena. The byte-addressed bit reservoir, frame header, overlap, and
     * synthesis samples remain in DRAM. Every allocation shares one owner and
     * is released as a unit when the decoder stops or changes backend. */
    s_libmad.synth = static_cast<mad_synth *>(CodecArenaCalloc32(
        CODEC_ARENA_MP3, 1, sizeof(mad_synth)));
    s_libmad.stream = static_cast<mad_stream *>(CodecArenaCalloc(
        CODEC_ARENA_MP3, 1, sizeof(mad_stream)));
    s_libmad.frame = static_cast<mad_frame *>(CodecArenaCalloc(
        CODEC_ARENA_MP3, 1, sizeof(mad_frame)));
    if (s_libmad.frame) {
        s_libmad.frame->xr_raw = static_cast<mad_fixed_t *>(
            CodecArenaCalloc32(CODEC_ARENA_MP3, kLibmadXrSamples,
                               sizeof(mad_fixed_t)));
        s_libmad.frame->tmp = static_cast<mad_fixed_t *>(
            CodecArenaCalloc32(CODEC_ARENA_MP3, kLibmadReorderSamples,
                               sizeof(mad_fixed_t)));
    }
    if (!s_libmad.stream || !s_libmad.frame || !s_libmad.synth ||
        !s_libmad.frame->xr_raw || !s_libmad.frame->tmp) {
        libmad_free();
        return false;
    }
    mad_stream_init(s_libmad.stream);
    mad_stream_options(s_libmad.stream, MAD_OPTION_IGNORECRC);
    mad_frame_init(s_libmad.frame);
    mad_synth_init(s_libmad.synth);
    return true;
}

void libmad_free() {
    if (s_libmad.stream) mad_stream_finish(s_libmad.stream);
    if (s_libmad.frame) mad_frame_finish(s_libmad.frame);
    if (s_libmad.frame) CodecArenaFree(s_libmad.frame->tmp);
    if (s_libmad.frame) CodecArenaFree(s_libmad.frame->xr_raw);
    CodecArenaFree(s_libmad.synth);
    CodecArenaFree(s_libmad.stream);
    CodecArenaFree(s_libmad.frame);
    CodecArenaRelease(CODEC_ARENA_MP3);
    s_libmad = {};
}

bool libmad_reset() {
    libmad_free();
    return libmad_allocate();
}
#endif


#if CONFIG_YORADIO_OGG_OPUS
struct OpusWorkspace {
    native_opus_t stream;
    void *state;
    void *scratch;
    void *words;
    helix_pcm_callback_t callback;
    void *context;
};
static OpusWorkspace *s_opus;

static bool emit_opus(void *opaque, const int16_t *pcm, size_t samples,
                      uint32_t bitrate) {
    OpusWorkspace *output = static_cast<OpusWorkspace *>(opaque);
    helix_stream_info_t info = {48000U, bitrate, 1, 16};
    /* libopus has finished this frame. The output pipeline may apply gain in
     * place, just as it does for MP3/AAC, without touching decoder history. */
    for (size_t offset = 0; offset < samples; offset += 512U) {
        size_t count = std::min(samples - offset, size_t(512));
        if (!output->callback(output->context, &info,
                              const_cast<int16_t *>(pcm + offset), count)) return false;
    }
    return true;
}

static void opus_free() {
    yoradio_opus_memory_bind(nullptr, 0, nullptr, 0);
    if (s_opus) {
        CodecArenaFree(s_opus->state);
        CodecArenaFree(s_opus->scratch);
        CodecArenaFree(s_opus->words);
        CodecArenaFree(s_opus);
        s_opus = nullptr;
    }
    CodecArenaRelease(CODEC_ARENA_OPUS);
}

static bool opus_allocate(helix_codec *codec) {
    if (!CodecArenaPreallocatedInIram() || CodecArenaPreallocatedBytes() < 16384U) {
        opus_init_failed(codec->kind, HELIX_OPUS_INIT_IRAM, 16384U, codec->reserve_heap_bytes, 0);
        ESP_LOGE(kTag, "Opus requires the 16-KiB IRAM codec arena");
        return false;
    }
    s_opus = static_cast<OpusWorkspace *>(CodecArenaCalloc(CODEC_ARENA_OPUS, 1, sizeof(OpusWorkspace)));
    if (!s_opus) {
        opus_init_failed(codec->kind, HELIX_OPUS_INIT_WORKSPACE, sizeof(OpusWorkspace), codec->reserve_heap_bytes, 0);
        return false;
    }
    s_opus->words = CodecArenaCalloc32(CODEC_ARENA_OPUS, 1, 16384U);
    if (!s_opus->words)
        opus_init_failed(codec->kind, HELIX_OPUS_INIT_IRAM, 16384U, codec->reserve_heap_bytes, 0);
    s_opus->state = CodecArenaCalloc(CODEC_ARENA_OPUS, 1, native_opus_decoder_size());
    if (!s_opus->state)
        opus_init_failed(codec->kind, HELIX_OPUS_INIT_STATE, native_opus_decoder_size(), codec->reserve_heap_bytes, 0);
    s_opus->scratch = CodecArenaCalloc(CODEC_ARENA_OPUS, 1, CONFIG_YORADIO_OPUS_SCRATCH_BYTES);
    if (!s_opus->scratch)
        opus_init_failed(codec->kind, HELIX_OPUS_INIT_SCRATCH, CONFIG_YORADIO_OPUS_SCRATCH_BYTES, codec->reserve_heap_bytes, 0);
    if (!s_opus->words || !s_opus->state || !s_opus->scratch) return false;
    native_opus_config_t config = {};
    config.decoder_state = s_opus->state;
    config.decoder_state_bytes = native_opus_decoder_size();
    config.scratch = s_opus->scratch;
    config.scratch_bytes = CONFIG_YORADIO_OPUS_SCRATCH_BYTES;
    config.iram = s_opus->words;
    config.iram_bytes = 16384U;
    config.pcm = codec->pcm;
    config.pcm_samples = codec->pcm_samples;
    config.output = emit_opus;
    config.output_ctx = s_opus;
    const int result = native_opus_init_ex(&s_opus->stream, &config, true);
    if (result != 0)
        opus_init_failed(codec->kind, HELIX_OPUS_INIT_NATIVE, native_opus_decoder_size(), codec->reserve_heap_bytes, result);
    return result == 0;
}
#endif

static void free_decoder(helix_codec *codec) {
    helix_codec_kind_t kind = codec->kind;
    codec->kind = static_cast<helix_codec_kind_t>(0);
    if (kind == HELIX_CODEC_MP3) {
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
        libmad_free();
#else
        MP3Decoder_FreeBuffers();
#endif
    }
#if CONFIG_YORADIO_HELIX_AAC
    else if (kind == HELIX_CODEC_AAC) AACDecoder_FreeBuffers();
#endif
#if CONFIG_YORADIO_OGG_OPUS
    else if (kind == HELIX_CODEC_OPUS) opus_free();
#endif
}

static bool allocate_decoder(helix_codec *codec, helix_codec_kind_t kind) {
    codec->kind = kind;
    codec->input_start = codec->input_size = 0;
    if (kind == HELIX_CODEC_MP3) {
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
        return libmad_allocate();
#else
        return MP3Decoder_AllocateBuffers();
#endif
    }
#if CONFIG_YORADIO_HELIX_AAC
    if (kind == HELIX_CODEC_AAC) return AACDecoder_AllocateBuffers();
#endif
#if CONFIG_YORADIO_OGG_OPUS
    if (kind == HELIX_CODEC_OPUS) return opus_allocate(codec);
#endif
    return false;
}

static bool update_codec_memory(helix_codec *codec) {
    size_t word_capacity = CodecArenaPreallocatedBytes();
    bool word_in_iram = CodecArenaPreallocatedInIram();
    codec->dram_used = sizeof(*codec) + input_storage_bytes(codec->input_capacity) +
                       sizeof(int16_t) * codec->pcm_samples +
                       CodecArenaHeapUsed() +
                       (word_in_iram ? 0U : word_capacity);
    codec->iram_used = word_in_iram ? word_capacity : 0U;
    size_t free_heap = esp_get_free_heap_size();
    size_t reserve = codec->reserve_heap_bytes;
#if CONFIG_YORADIO_OGG_OPUS
    if (codec->kind == HELIX_CODEC_OPUS) reserve = std::max(reserve, size_t(4096));
#endif
    if (free_heap >= reserve) return true;
    opus_init_failed(codec->kind, HELIX_OPUS_INIT_RESERVE, reserve, reserve, static_cast<int32_t>(free_heap));
    ESP_LOGE(kTag, "Codec leaves %u heap bytes, reserve requires %u",
             (unsigned)free_heap, (unsigned)reserve);
    return false;
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

#if !CONFIG_YORADIO_MP3_DECODER_LIBMAD
struct Mp3BlockOutput {
    helix_pcm_callback_t callback;
    void *context;
    helix_stream_info_t info;
    bool failed;
};

static bool emit_mp3_block(void *opaque, short *pcm, int samples) {
    Mp3BlockOutput *output = static_cast<Mp3BlockOutput *>(opaque);
    if (samples <= 0 ||
        static_cast<size_t>(samples) > kMp3PcmSamples) {
        output->failed = true;
        return false;
    }
    bool accepted = output->callback(output->context, &output->info, pcm,
                                     static_cast<size_t>(samples));
    output->failed = !accepted;
    return accepted;
}
#endif

#if CONFIG_YORADIO_HELIX_AAC && YORADIO_ESP8266_AAC_BLOCK_OUTPUT
struct AacBlockOutput {
    helix_pcm_callback_t callback;
    void *context;
};
static bool emit_aac_block(void *opaque, short *pcm, int samples) {
    AacBlockOutput &output = *static_cast<AacBlockOutput *>(opaque);
    if (samples <= 0 || static_cast<size_t>(samples) > kAacPcmSamples) return false;
    helix_stream_info_t info = {
        static_cast<uint32_t>(AACGetSampRate()),
        static_cast<uint32_t>(AACGetBitrate()),
        static_cast<uint8_t>(CONFIG_YORADIO_AUDIO_MONO ? 1 : AACGetChannels()), 16,
    };
    return output.callback(output.context, &info, pcm, static_cast<size_t>(samples));
}
#endif

static int decode_one(helix_codec *codec, helix_pcm_callback_t callback,
                      void *context) {
    uint8_t *input = codec->input + codec->input_start;
#if CONFIG_YORADIO_OGG_OPUS
    if (codec->kind == HELIX_CODEC_OPUS) {
        if (!s_opus) return -8;
        s_opus->callback = callback;
        s_opus->context = context;
        size_t consumed = 0;
        int result = native_opus_feed(&s_opus->stream, input, codec->input_size, &consumed);
        consume(codec, consumed);
        if (result < 0) {
            ESP_LOGE(kTag, "Opus stream error %d (libopus %d), scratch %u/%u, words %u/16384",
                     result, s_opus->stream.libopus_error,
                     (unsigned)yoradio_opus_scratch_peak_bytes(),
                     (unsigned)CONFIG_YORADIO_OPUS_SCRATCH_BYTES,
                     (unsigned)yoradio_opus_scratch_peak_words());
            return result;
        }
        return result == 1 ? 0 : 1;
    }
#endif
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
#if YORADIO_ESP8266_AUDIO_PROFILE
        audio_profile_decode_begin();
#endif
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
        size_t supplied = codec->input_size;
        if (supplied < parsed.frame_size + MAD_BUFFER_GUARD) {
            std::memset(input + supplied, 0,
                        parsed.frame_size + MAD_BUFFER_GUARD - supplied);
            supplied = parsed.frame_size + MAD_BUFFER_GUARD;
        }
        mad_stream_buffer(s_libmad.stream, input,
                          static_cast<unsigned long>(supplied));
        int result = mad_frame_decode(s_libmad.frame, s_libmad.stream);
        bool output_failed = false;
        if (result == 0) {
            const unsigned channels = MAD_NCHANNELS(&s_libmad.frame->header);
            const unsigned subbands = MAD_NSBSAMPLES(&s_libmad.frame->header);
            size_t pcm_samples = 0;
            helix_stream_info_t info = {
                s_libmad.frame->header.samplerate,
                s_libmad.frame->header.bitrate,
                static_cast<uint8_t>(CONFIG_YORADIO_AUDIO_MONO ? 1 : channels), 16,
            };
            for (unsigned ns = 0; ns < subbands; ++ns) {
                if (mad_synth_frame_onens(s_libmad.synth,
                                           s_libmad.frame, ns) !=
                    MAD_FLOW_CONTINUE) {
                    output_failed = true;
                    break;
                }
                const mad_pcm &block = s_libmad.synth->pcm;
                for (unsigned sample = 0; sample < block.length; ++sample) {
#if CONFIG_YORADIO_AUDIO_MONO
                    int32_t value = block.samples[0][sample];
                    if (channels == 2) value = (value + block.samples[1][sample]) >> 1;
                    codec->pcm[pcm_samples++] = static_cast<int16_t>(value);
#else
                    codec->pcm[pcm_samples++] = block.samples[0][sample];
                    if (channels == 2)
                        codec->pcm[pcm_samples++] = block.samples[1][sample];
#endif
                }
                if (pcm_samples &&
                    (((ns + 1U) % 18U) == 0U || ns + 1U == subbands)) {
                    if (!callback(context, &info, codec->pcm, pcm_samples)) {
                        output_failed = true;
                        break;
                    }
                    pcm_samples = 0;
                }
            }
        }
#else
        int left = static_cast<int>(parsed.frame_size);
        Mp3BlockOutput output = {
            callback,
            context,
            {parsed.sample_rate, parsed.bitrate,
             static_cast<uint8_t>(CONFIG_YORADIO_AUDIO_MONO ? 1 : parsed.channels), 16},
            false,
        };
        int result = MP3DecodeBlocks(input, &left, codec->pcm,
                                     static_cast<int>(codec->pcm_samples), 0,
                                     emit_mp3_block, &output);
#endif
#if YORADIO_ESP8266_AUDIO_PROFILE
        audio_profile_decode_end();
#endif
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
        if (output_failed) return -5;
        if (result != 0) {
            ESP_LOGW(kTag, "libmad frame error 0x%x: %s",
                     static_cast<unsigned>(s_libmad.stream->error),
                     mad_stream_errorstr(s_libmad.stream));
        }
        consume(codec, parsed.frame_size);
        return 0;
#else
        size_t used = parsed.frame_size - std::min(
            parsed.frame_size, static_cast<size_t>(std::max(left, 0)));
        if (output.failed) return -5;
        if (result != ERR_MP3_NONE) {
            consume(codec, used ? used : 1);
            return 0;
        }
        consume(codec, used ? used : parsed.frame_size);
        return 0;
#endif
    }

#if CONFIG_YORADIO_HELIX_AAC
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
#if YORADIO_ESP8266_AUDIO_PROFILE
    audio_profile_decode_begin();
#endif
#if YORADIO_ESP8266_AAC_BLOCK_OUTPUT
    AacBlockOutput output = {callback, context};
    int result = AACDecodeBlocks(input, &left, codec->pcm,
        static_cast<int>(codec->pcm_samples), YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES,
        CONFIG_YORADIO_AUDIO_MONO, emit_aac_block, &output);
#else
    int result = AACDecode(input, &left, codec->pcm);
#endif
#if YORADIO_ESP8266_AUDIO_PROFILE
    audio_profile_decode_end();
#endif
    size_t used = frame - std::min(frame,
        static_cast<size_t>(std::max(left, 0)));
#if YORADIO_ESP8266_AAC_BLOCK_OUTPUT
    if (result == ERR_AAC_OUTPUT_CANCELLED) return -7;
#endif
    if (result != ERR_AAC_NONE) {
        consume(codec, used ? used : 1);
        return 0;
    }
#if !YORADIO_ESP8266_AAC_BLOCK_OUTPUT
    helix_stream_info_t info = {
        static_cast<uint32_t>(AACGetSampRate()),
        static_cast<uint32_t>(AACGetBitrate()),
        static_cast<uint8_t>(AACGetChannels()),
        static_cast<uint8_t>(AACGetBitsPerSample()),
    };
    size_t samples = static_cast<size_t>(AACGetOutputSamps());
    if (!samples || samples > codec->pcm_samples) return -7;
#if CONFIG_YORADIO_AUDIO_MONO
    if (info.channels == 2) {
        if (samples & 1U) return -7;
        samples /= 2U;
        for (size_t i = 0; i < samples; ++i)
            codec->pcm[i] = static_cast<int16_t>(
                (static_cast<int32_t>(codec->pcm[2U * i]) + codec->pcm[2U * i + 1U]) >> 1);
        info.channels = 1;
    }
#endif
    if (!callback(context, &info, codec->pcm, samples)) return -7;
#endif
    consume(codec, used ? used : frame);
    return 0;
#else
    return -8;
#endif
}

extern "C" bool helix_codec_prepare(void) {
    return CodecArenaPreallocateMp3();
}

#if YORADIO_ESP8266_OPUS_BENCHMARK
extern "C" void helix_codec_opus_init_failure_snapshot(helix_opus_init_failure_t *out) {
    if (!out) return;
    taskENTER_CRITICAL();
    *out = s_opus_init_failure;
    taskEXIT_CRITICAL();
}
#endif

extern "C" helix_codec_t *helix_codec_create(helix_codec_kind_t kind,
                                               size_t reserve_heap_bytes) {
    opus_init_diagnostic_reset();
    if (kind != HELIX_CODEC_MP3
#if CONFIG_YORADIO_OGG_OPUS
        && kind != HELIX_CODEC_OPUS
#endif
#if CONFIG_YORADIO_HELIX_AAC
        && kind != HELIX_CODEC_AAC
#endif
    ) return nullptr;
    if (!helix_codec_prepare()) {
        opus_init_failed(kind, HELIX_OPUS_INIT_IRAM, 16384U, reserve_heap_bytes, 0);
        return nullptr;
    }
    helix_codec *codec = static_cast<helix_codec *>(
        heap_caps_calloc(1, sizeof(*codec), MALLOC_CAP_8BIT));
    if (!codec)
        opus_init_failed(kind, HELIX_OPUS_INIT_CODEC, sizeof(*codec), reserve_heap_bytes, 0);
    if (codec) {
        codec->pcm_samples = pcm_samples_for_kind(kind);
        codec->input_capacity = input_bytes_for_kind(kind);
        codec->input = static_cast<uint8_t *>(
            heap_caps_calloc(1, input_storage_bytes(codec->input_capacity), MALLOC_CAP_8BIT));
        if (!codec->input)
            opus_init_failed(kind, HELIX_OPUS_INIT_INPUT, input_storage_bytes(codec->input_capacity), reserve_heap_bytes, 0);
        codec->pcm = static_cast<int16_t *>(
            heap_caps_malloc(sizeof(int16_t) * codec->pcm_samples,
                             MALLOC_CAP_8BIT));
        if (!codec->pcm)
            opus_init_failed(kind, HELIX_OPUS_INIT_PCM, sizeof(int16_t) * codec->pcm_samples, reserve_heap_bytes, 0);
    }
    if (!codec || !codec->input || !codec->pcm ||
        !CodecArenaBind(nullptr, kArenaBytes)) {
        if (codec && codec->input && codec->pcm)
            opus_init_failed(kind, HELIX_OPUS_INIT_ARENA_BIND, kArenaBytes, reserve_heap_bytes, 0);
        if (codec) {
            heap_caps_free(codec->pcm);
            heap_caps_free(codec->input);
        }
        heap_caps_free(codec);
        ESP_LOGE(kTag, "Heap cannot allocate codec input/PCM workspace");
        return nullptr;
    }
    codec->reserve_heap_bytes = reserve_heap_bytes;
    bool allocated = allocate_decoder(codec, kind);
    if (!allocated) {
        free_decoder(codec);
        CodecArenaUnbind();
        heap_caps_free(codec->pcm);
        heap_caps_free(codec->input);
        heap_caps_free(codec);
        return nullptr;
    }
    if (!update_codec_memory(codec)) {
        helix_codec_destroy(codec);
        return nullptr;
    }
    ESP_LOGI(kTag, "%s workspace: DRAM %u, IRAM %u, arena used %u",
             kind == HELIX_CODEC_MP3
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
                 ? "libmad MP3"
#else
                 ? "Helix MP3"
#endif
                 : (kind == HELIX_CODEC_OPUS ? "Opus" : "Helix AAC"),
             (unsigned)codec->dram_used, (unsigned)codec->iram_used,
             (unsigned)CodecArenaUsed());
    return codec;
}

extern "C" void helix_codec_destroy(helix_codec_t *codec) {
    if (!codec) return;
    free_decoder(codec);
    if (!CodecArenaUnbind()) ESP_LOGE(kTag, "Codec arena is still owned");
    heap_caps_free(codec->pcm);
    heap_caps_free(codec->input);
    heap_caps_free(codec);
}

extern "C" int helix_codec_switch(helix_codec_t *codec,
                                   helix_codec_kind_t kind) {
    opus_init_diagnostic_reset();
    if (!codec || (kind != HELIX_CODEC_MP3
#if CONFIG_YORADIO_OGG_OPUS
                   && kind != HELIX_CODEC_OPUS
#endif
#if CONFIG_YORADIO_HELIX_AAC
                   && kind != HELIX_CODEC_AAC
#endif
                  ))
        return -1;
    if (codec->kind == kind) {
        codec->input_start = codec->input_size = 0;
#if CONFIG_YORADIO_OGG_OPUS
        if (kind == HELIX_CODEC_OPUS) {
            const int result = s_opus ? native_opus_reset(&s_opus->stream) : -2;
            if (result != 0)
                opus_init_failed(kind, HELIX_OPUS_INIT_NATIVE, native_opus_decoder_size(), codec->reserve_heap_bytes, result);
            return result;
        }
#endif
        if (kind == HELIX_CODEC_MP3) {
#if CONFIG_YORADIO_MP3_DECODER_LIBMAD
            if (!libmad_reset()) return -2;
            if (!update_codec_memory(codec)) {
                free_decoder(codec);
                return -3;
            }
            return 0;
#else
            MP3Decoder_ClearBuffer();
            return 0;
#endif
        }
#if CONFIG_YORADIO_HELIX_AAC
        /* A new station may change AAC configuration. Release/rebuild the
         * state; the input/PCM and permanent IRAM arena are retained, but
         * byte-oriented decoder objects are real DRAM heap allocations. */
        free_decoder(codec);
        if (!allocate_decoder(codec, kind)) return -2;
        if (!update_codec_memory(codec)) {
            free_decoder(codec);
            return -3;
        }
        return 0;
#else
        return -1;
#endif
    }
    free_decoder(codec);
    size_t input_capacity = input_bytes_for_kind(kind);
    if (input_capacity != codec->input_capacity) {
        uint8_t *resized = static_cast<uint8_t *>(heap_caps_realloc(
            codec->input, input_storage_bytes(input_capacity), MALLOC_CAP_8BIT));
        if (!resized) {
            opus_init_failed(kind, HELIX_OPUS_INIT_INPUT, input_storage_bytes(input_capacity), codec->reserve_heap_bytes, 0);
            return -2;
        }
        codec->input = resized;
        codec->input_capacity = input_capacity;
        codec->input_start = codec->input_size = 0;
    }
    size_t pcm_samples = pcm_samples_for_kind(kind);
    if (pcm_samples != codec->pcm_samples) {
        int16_t *resized = static_cast<int16_t *>(heap_caps_realloc(
            codec->pcm, sizeof(int16_t) * pcm_samples, MALLOC_CAP_8BIT));
        if (!resized) {
            opus_init_failed(kind, HELIX_OPUS_INIT_PCM, sizeof(int16_t) * pcm_samples, codec->reserve_heap_bytes, 0);
            return -2;
        }
        codec->pcm = resized;
        codec->pcm_samples = pcm_samples;
    }
    if (!allocate_decoder(codec, kind)) {
        free_decoder(codec);
        return -2;
    }
    if (!update_codec_memory(codec)) {
        free_decoder(codec);
        return -3;
    }
    return 0;
}

extern "C" helix_codec_kind_t helix_codec_detect(const uint8_t *data,
                                                   size_t size) {
    /* Never search Ogg packet payload for accidental MP3/AAC sync words. */
    if (size >= 4 && std::memcmp(data, "OggS", 4) == 0) {
#if CONFIG_YORADIO_OGG_OPUS
        if (size >= 27U && data[4] == 0 && data[26]) {
            size_t body = 27U + data[26];
            if (size >= body + 8U && std::memcmp(data + body, "OpusHead", 8) == 0)
                return HELIX_CODEC_OPUS;
        }
#endif
        return static_cast<helix_codec_kind_t>(0);
    }
    Mp3Header header = {};
    int mp3 = find_mp3(data, size, &header);
#if CONFIG_YORADIO_HELIX_AAC
    int aac = find_aac(data, size);
    if (mp3 >= 0 && (aac < 0 || mp3 <= aac)) return HELIX_CODEC_MP3;
    if (aac >= 0) return HELIX_CODEC_AAC;
#else
    if (mp3 >= 0) return HELIX_CODEC_MP3;
#endif
    return static_cast<helix_codec_kind_t>(0);
}

extern "C" uint8_t *helix_codec_write_pointer(helix_codec_t *codec,
                                                size_t *capacity) {
    if (!codec || !capacity) return nullptr;
    if (codec->input_start + codec->input_size == codec->input_capacity) compact(codec);
    *capacity = codec->input_capacity - codec->input_start - codec->input_size;
    return codec->input + codec->input_start + codec->input_size;
}

extern "C" size_t helix_codec_buffered(const helix_codec_t *codec) {
    return codec ? codec->input_size : 0;
}

extern "C" size_t helix_codec_input_capacity(void) {
    return kInputBytes;
}
extern "C" size_t helix_codec_active_input_capacity(const helix_codec_t *codec) {
    return codec ? codec->input_capacity : kInputBytes;
}

extern "C" int helix_codec_buffer_commit(helix_codec_t *codec, size_t size) {
    if (!codec) return -1;
    size_t capacity = 0;
    helix_codec_write_pointer(codec, &capacity);
    if (size > capacity) return -2;
    codec->input_size += size;
    return 0;
}

extern "C" int helix_codec_process_one(helix_codec_t *codec,
                                        helix_pcm_callback_t callback,
                                        void *context) {
    if (!codec || !callback) return -1;
    return decode_one(codec, callback, context);
}

extern "C" int helix_codec_commit(helix_codec_t *codec, size_t size,
                                   helix_pcm_callback_t callback,
                                   void *context) {
    if (!callback) return -1;
    int committed = helix_codec_buffer_commit(codec, size);
    if (committed < 0) return committed;
    while (codec->input_size) {
        size_t before = codec->input_size;
        int result = decode_one(codec, callback, context);
        if (result < 0) return result;
        if (result == 1 || codec->input_size >= before) break;
    }
    return 0;
}

extern "C" int helix_codec_finish(helix_codec_t *codec) {
    if (!codec) return -1;
#if CONFIG_YORADIO_OGG_OPUS
    if (codec->kind == HELIX_CODEC_OPUS && s_opus)
        return native_opus_finish(&s_opus->stream);
#endif
    codec->input_size = codec->input_start = 0;
    return 0;
}

extern "C" const char *helix_codec_error_message(helix_codec_kind_t kind, int result) {
    if (result >= 0) return nullptr;
#if CONFIG_YORADIO_OGG_OPUS
    if (kind == HELIX_CODEC_OPUS && result <= NATIVE_OPUS_ERR_ARGUMENT)
        return native_opus_error_string(result);
#endif
    return "AUDIO STREAM ERROR";
}

extern "C" int helix_codec_feed(helix_codec_t *codec, const uint8_t *data,
                                 size_t size, bool eos,
                                 helix_pcm_callback_t callback,
                                 void *context) {
    if (!codec || (!data && size) || !callback) return -1;
    while (size) {
        if (codec->input_start + codec->input_size == codec->input_capacity) compact(codec);
        size_t free_space = codec->input_capacity - codec->input_start - codec->input_size;
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
    if (eos) return helix_codec_finish(codec);
    return 0;
}

extern "C" size_t helix_codec_workspace_size(void) {
    return kWorkspaceBytes;
}

extern "C" size_t helix_codec_arena_used(const helix_codec_t *codec) {
    return codec ? CodecArenaUsed() : 0;
}

extern "C" size_t helix_codec_dram_used(const helix_codec_t *codec) {
    return codec ? codec->dram_used : 0;
}

extern "C" size_t helix_codec_iram_used(const helix_codec_t *codec) {
    return codec ? codec->iram_used : 0;
}
