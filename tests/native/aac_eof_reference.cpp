// Host-only reference driver for unmodified FDK AAC. No firmware code here.
#include "aacdecoder_lib.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <vector>

int main(int argc, char **argv) {
    if (argc != 3) return 2;
    std::ifstream file(argv[1], std::ios::binary);
    std::vector<UCHAR> data((std::istreambuf_iterator<char>(file)), {});
    unsigned chunk = static_cast<unsigned>(std::strtoul(argv[2], nullptr, 10));
    if (data.empty() || !chunk) return 2;
    HANDLE_AACDECODER decoder = aacDecoder_Open(TT_MP4_ADTS, 1);
    if (!decoder) return 3;
    INT_PCM pcm[16384];
    unsigned frames = 0, samples = 0, underflows = 0;
    auto drain = [&]() {
        for (;;) {
            AAC_DECODER_ERROR error = aacDecoder_DecodeFrame(decoder, pcm, 16384, 0);
            if (error == AAC_DEC_NOT_ENOUGH_BITS) { ++underflows; return true; }
            if (error != AAC_DEC_OK) return false;
            CStreamInfo *info = aacDecoder_GetStreamInfo(decoder);
            ++frames;
            samples += info->frameSize;
        }
    };
    for (size_t pos = 0; pos < data.size();) {
        UINT size = static_cast<UINT>(std::min<size_t>(chunk, data.size()-pos));
        UCHAR *input = data.data()+pos;
        UINT valid = size;
        if (aacDecoder_Fill(decoder, &input, &size, &valid) != AAC_DEC_OK) return 4;
        if (!drain() || size == valid) return 5;
        pos += size-valid;
    }
    if (!drain() || !frames) return 6;
    CStreamInfo info = *aacDecoder_GetStreamInfo(decoder);
    // NOT_ENOUGH_BITS is a request for input, not an EOF indication. After the
    // caller knows input ended, flush only the documented filterbank delay.
    unsigned flush_frames = (info.outputDelay+info.frameSize-1)/info.frameSize;
    for (unsigned i=0; i<flush_frames; ++i) {
        if (aacDecoder_DecodeFrame(decoder, pcm, 16384, AACDEC_FLUSH) != AAC_DEC_OK) return 7;
    }
    std::printf("{\"frames\":%u,\"samples_per_channel\":%u,\"sample_rate\":%d,"
                "\"channels\":%d,\"core_rate\":%d,\"frame_size\":%d,"
                "\"output_delay\":%u,\"flush_frames\":%u,\"input_underflows\":%u}\n",
                frames,samples,info.sampleRate,info.numChannels,info.aacSampleRate,
                info.frameSize,info.outputDelay,flush_frames,underflows);
    aacDecoder_Close(decoder);
    return 0;
}
