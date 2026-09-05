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
};

bool emit_granule(void *context, short *pcm, int samples) {
    GranuleOutput *sink = static_cast<GranuleOutput *>(context);
    if (samples <= 0 || samples > (YORADIO_HELIX_MP3_MONO ? 576 : 1152)) return false;
    sink->samples += samples;
    return write_pcm(*sink->output, pcm, samples);
}

int decode_mp3(std::vector<unsigned char> &input, std::ofstream &output, bool granules = false) {
    if (!MP3Decoder_AllocateBuffers()) return 10;
    short pcm[4096] = {};
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
        GranuleOutput sink = {&output, 0};
        const int capacity = YORADIO_HELIX_MP3_MONO ? 576 : 1152;
        pcm[capacity] = 12345;
        int result = granules
            ? MP3DecodeGranules(input.data() + cursor, &left, pcm, 0, emit_granule, &sink)
            : MP3Decode(input.data() + cursor, &left, pcm, 0);
        if (granules && pcm[capacity] != 12345) return 14;
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
        if ((granules && sink.samples != frame_samples) ||
            (!granules && !write_pcm(output, pcm, frame_samples))) {
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

int decode_aac(std::vector<unsigned char> &input, std::ofstream &output) {
    if (!AACDecoder_AllocateBuffers()) return 20;
    short pcm[4096] = {};
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
        int result = AACDecode(input.data() + cursor, &left, pcm);
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
        if (!write_pcm(output, pcm, frame_samples)) {
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
    if (codec == "aac") return decode_aac(input, output);
    return 6;
}
