#include <cstdint>

#include "config.h"
#include "mad.h"

#include <fstream>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "usage: libmad-golden <mp3-input> <pcm-output>\n";
        return 2;
    }
    std::ifstream source(argv[1], std::ios::binary);
    if (!source) return 3;
    std::vector<unsigned char> input(
        (std::istreambuf_iterator<char>(source)),
        std::istreambuf_iterator<char>());
    if (input.empty()) return 4;
    input.resize(input.size() + MAD_BUFFER_GUARD, 0);

    std::ofstream output(argv[2], std::ios::binary | std::ios::trunc);
    if (!output) return 5;
    mad_stream stream;
    mad_frame frame;
    mad_synth synth;
#if defined(YORADIO_LIBMAD_EXTERNAL_FRAME_WORKSPACE)
    mad_fixed_t xr_raw[576 * 2] = {};
    mad_fixed_t reorder_tmp[576] = {};
    frame.xr_raw = xr_raw;
    frame.tmp = reorder_tmp;
#endif
    mad_stream_init(&stream);
    mad_stream_options(&stream, MAD_OPTION_IGNORECRC);
    mad_frame_init(&frame);
    mad_synth_init(&synth);
    mad_stream_buffer(&stream, input.data(),
                      static_cast<unsigned long>(input.size()));

    size_t frames = 0;
    size_t samples = 0;
    uint32_t rate = 0;
    unsigned channels = 0;
    while (true) {
        if (mad_frame_decode(&frame, &stream) != 0) {
            if (stream.error == MAD_ERROR_BUFLEN) break;
            if (MAD_RECOVERABLE(stream.error)) continue;
            std::cerr << "libmad error 0x" << std::hex << stream.error
                      << ": " << mad_stream_errorstr(&stream) << "\n";
            mad_frame_finish(&frame);
            mad_stream_finish(&stream);
            return 6;
        }
        rate = frame.header.samplerate;
        channels = MAD_NCHANNELS(&frame.header);
        const unsigned subbands = MAD_NSBSAMPLES(&frame.header);
        for (unsigned ns = 0; ns < subbands; ++ns) {
            if (mad_synth_frame_onens(&synth, &frame, ns) !=
                MAD_FLOW_CONTINUE) return 7;
            for (unsigned index = 0; index < synth.pcm.length; ++index) {
                output.write(reinterpret_cast<const char *>(
                                 &synth.pcm.samples[0][index]),
                             sizeof(int16_t));
                ++samples;
                if (channels == 2) {
                    output.write(reinterpret_cast<const char *>(
                                     &synth.pcm.samples[1][index]),
                                 sizeof(int16_t));
                    ++samples;
                }
            }
        }
        ++frames;
    }
    mad_frame_finish(&frame);
    mad_stream_finish(&stream);
    if (!frames || !output.good()) return 8;
    std::cout << "codec=libmad frames=" << frames << " samples=" << samples
              << " bytes=" << samples * sizeof(int16_t) << " rate=" << rate
              << " channels=" << channels
              << " state=" << sizeof(stream) + sizeof(frame) + sizeof(synth)
              << "\n";
    return 0;
}
