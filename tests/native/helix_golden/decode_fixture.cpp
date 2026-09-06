#include "aac_decoder.h"
#include "mp3_decoder.h"
#include "helix_stage_profile.h"

#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
static unsigned stage_calls[HELIX_STAGE_COUNT];
extern "C" void helix_stage_profile_begin(int stage) { ++stage_calls[stage]; }
extern "C" void helix_stage_profile_end(int) {}
#endif

namespace {

bool write_pcm(std::ofstream &output, const short *pcm, int samples) {
    if (samples < 0 || samples > 4096) return false;
    output.write(reinterpret_cast<const char *>(pcm),
                 static_cast<std::streamsize>(samples * sizeof(*pcm)));
    return output.good();
}

struct GranuleOutput {
    std::ofstream *output;
    int samples;
    bool blocks;
    int calls;
};

bool emit_granule(void *context, short *pcm, int samples) {
    GranuleOutput *sink = static_cast<GranuleOutput *>(context);
    if (samples <= 0 || samples > (YORADIO_HELIX_MP3_MONO ? 576 : 1152)) return false;
    if (sink->blocks && samples != 32 && samples != 64) return false;
    sink->samples += samples;
    ++sink->calls;
    const bool result = write_pcm(*sink->output, pcm, samples);
    /* The real sink changes PCM in place. The next synthesis block must
     * neither reuse these values nor depend on a previous output block. */
    if (sink->blocks) for (int i = 0; i < samples; ++i) pcm[i] = -12345;
    return result;
}

int decode_mp3(std::vector<unsigned char> &input, std::ofstream &output,
               bool granules = false, bool blocks = false) {
    if (!MP3Decoder_AllocateBuffers()) return 10;
    const int capacity = blocks ? 32 * (YORADIO_HELIX_MP3_MONO ? 1 : 2)
        : granules ? (YORADIO_HELIX_MP3_MONO ? 576 : 1152) : 4096;
    std::vector<short> guarded(static_cast<size_t>(capacity) + 2U, 12345);
    short *pcm = guarded.data() + 1;
    size_t cursor = 0;
    size_t frames = 0;
    size_t samples = 0;

    while (cursor + 4 < input.size()) {
        int available = static_cast<int>(input.size() - cursor);
        int sync = MP3FindSyncWord(input.data() + cursor, available);
        if (sync < 0) break;
        cursor += static_cast<size_t>(sync);
        available = static_cast<int>(input.size() - cursor);
        int left = available;
        GranuleOutput sink = {&output, 0, blocks, 0};
        int result = blocks
            ? MP3DecodeBlocks(input.data() + cursor, &left, pcm, capacity, 0, emit_granule, &sink)
            : granules
            ? MP3DecodeGranules(input.data() + cursor, &left, pcm, 0, emit_granule, &sink)
            : MP3Decode(input.data() + cursor, &left, pcm, 0);
        if (guarded.front() != 12345 || guarded.back() != 12345) return 14;
        int consumed = available - left;
        if (consumed <= 0) {
            ++cursor;
            continue;
        }
        cursor += static_cast<size_t>(consumed);
        if (result == ERR_MP3_MAINDATA_UNDERFLOW) continue;
        if (result != ERR_MP3_NONE) {
            std::cerr << "MP3 decode error " << result << " after frame "
                      << frames << "\n";
            MP3Decoder_FreeBuffers();
            return 11;
        }
        int frame_samples = MP3GetOutputSamps();
        if (((granules || blocks) && sink.samples != frame_samples) ||
            (blocks && sink.calls != (MP3GetSampRate() >= 32000 ? 36 : 18)) ||
            (!granules && !blocks && !write_pcm(output, pcm, frame_samples))) {
            MP3Decoder_FreeBuffers();
            return 12;
        }
        samples += static_cast<size_t>(frame_samples);
        ++frames;
    }
    MP3Decoder_FreeBuffers();
#if defined(YORADIO_ESP8266_HELIX_STAGE_PROFILE)
    std::cerr << "huffman=" << stage_calls[HELIX_STAGE_HUFFMAN]
              << " synthesis=" << stage_calls[HELIX_STAGE_SYNTHESIS] << "\n";
#endif
    if (!frames) return 13;
    std::cout << "codec=mp3 frames=" << frames << " samples=" << samples
              << " bytes=" << samples * sizeof(short) << "\n";
    return 0;
}

struct AacOutput { std::ofstream *file; int samples, frames, channels, calls; };
bool emit_aac(void *opaque, short *pcm, int samples) {
    AacOutput &s = *static_cast<AacOutput *>(opaque);
    if (samples != s.frames * s.channels) return false;
    const bool ok = write_pcm(*s.file, pcm, samples);
    s.samples += samples; ++s.calls;
    for (int i = 0; i < samples; ++i) pcm[i] = -12345;
    return ok;
}

int decode_aac(std::vector<unsigned char> &input, std::ofstream &output,
               int blockFrames = 0, bool mono = false) {
    if (!AACDecoder_AllocateBuffers()) return 20;
    const int capacity = blockFrames ? blockFrames * (mono ? 1 : 2) : 4096;
    std::vector<short> guard(capacity + 2, 23456);
    short *pcm = guard.data() + 1;
    size_t cursor = 0;
    size_t frames = 0;
    size_t samples = 0;

    while (cursor + 7 < input.size()) {
        int available = static_cast<int>(input.size() - cursor);
        int sync = AACFindSyncWord(input.data() + cursor, available);
        if (sync < 0) break;
        cursor += static_cast<size_t>(sync);
        available = static_cast<int>(input.size() - cursor);
        int left = available;
        const int headerChannels = (input[cursor + 2] & 1) * 4 + (input[cursor + 3] >> 6);
        AacOutput sink = {&output, 0, blockFrames, mono ? 1 : headerChannels, 0};
        int result = blockFrames
            ? AACDecodeBlocks(input.data() + cursor, &left, pcm, capacity, blockFrames, mono, emit_aac, &sink)
            : AACDecode(input.data() + cursor, &left, pcm);
        if (guard.front() != 23456 || guard.back() != 23456) return 24;
        int consumed = available - left;
        if (consumed <= 0) {
            ++cursor;
            continue;
        }
        cursor += static_cast<size_t>(consumed);
        if (result != ERR_AAC_NONE) {
            std::cerr << "AAC decode error " << result << " after frame "
                      << frames << "\n";
            AACDecoder_FreeBuffers();
            return 21;
        }
        int frame_samples = AACGetOutputSamps();
        if (blockFrames && mono) frame_samples /= AACGetChannels();
        if ((blockFrames && (sink.samples != frame_samples || sink.calls != 1024 / blockFrames)) ||
            (!blockFrames && !write_pcm(output, pcm, frame_samples))) {
            AACDecoder_FreeBuffers();
            return 22;
        }
        samples += static_cast<size_t>(frame_samples);
        ++frames;
    }
    AACDecoder_FreeBuffers();
    if (!frames) return 23;
    std::cout << "codec=aac frames=" << frames << " samples=" << samples
              << " bytes=" << samples * sizeof(short) << "\n";
    return 0;
}

} // namespace

int main(int argc, char **argv) {
    if (argc != 4) {
        std::cerr << "usage: helix-golden <mp3|aac> <input> <pcm-output>\n";
        return 2;
    }
    std::ifstream source(argv[2], std::ios::binary);
    if (!source) return 3;
    std::vector<unsigned char> input(
        (std::istreambuf_iterator<char>(source)),
        std::istreambuf_iterator<char>());
    if (input.empty()) return 4;
    std::ofstream output(argv[3], std::ios::binary | std::ios::trunc);
    if (!output) return 5;
    const std::string codec = argv[1];
    if (codec == "mp3") return decode_mp3(input, output);
    if (codec == "mp3-granules") return decode_mp3(input, output, true);
    if (codec == "mp3-blocks") return decode_mp3(input, output, false, true);
    if (codec == "aac") return decode_aac(input, output);
    if (codec.find("aac-blocks-") == 0)
        return decode_aac(input, output, std::stoi(codec.substr(11)), codec.find("mono") != std::string::npos);
    return 6;
}
