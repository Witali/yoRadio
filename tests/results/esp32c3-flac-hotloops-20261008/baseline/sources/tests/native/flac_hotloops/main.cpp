#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "profile.h"
// The runner freezes/instruments this translation unit; production is untouched.
#include "measured_decoder.cpp"

int main(int argc, char** argv) {
    assert(argc == 4);
    const unsigned repeats = std::strtoul(argv[3], nullptr, 10);
    assert(repeats > 0);
    FILE* input = fopen(argv[1], "rb"); assert(input);
    fseek(input, 0, SEEK_END); const size_t size = ftell(input); rewind(input);
    std::vector<uint8_t> file(size);
    assert(fread(file.data(), 1, size, input) == size); fclose(input);
    assert(size > 42 && memcmp(file.data(), "fLaC", 4) == 0);
    const unsigned block = (file[10] << 8) | file[11];
    const unsigned channels = ((file[20] >> 1) & 7) + 1;
    const unsigned bits = (((file[20] & 1) << 4) | (file[21] >> 4)) + 1;
    const unsigned rate = (file[18] << 12) | (file[19] << 4) | (file[20] >> 4);
    const uint64_t samples = (uint64_t(file[21] & 15) << 32) |
        (uint64_t(file[22]) << 24) | (uint64_t(file[23]) << 16) |
        (uint64_t(file[24]) << 8) | file[25];
    assert(samples && channels <= MAX_CHANNELS);
    size_t offset = 4;
    while (true) {
        assert(offset + 4 <= file.size());
        const bool last = file[offset] & 128;
        const size_t length = (file[offset+1] << 16) | (file[offset+2] << 8) | file[offset+3];
        offset += 4 + length; assert(offset <= file.size());
        if (last) break;
    }
    assert(FLACDecoder_AllocateBuffers(block, channels));
    std::vector<short> decoded(samples * channels);
    short pcm[FLAC_OUTPUT_FRAMES * MAX_CHANNELS];
    uint64_t decode_ns = 0;
    for (unsigned repeat = 0; repeat < repeats; ++repeat) {
        FLACDecoder_ClearBuffer(); FLACDecoderReset();
        FLACSetRawBlockParams(channels, rate, bits, samples, file.size());
        int left = file.size() - offset, result;
        size_t written = 0;
        do {
            const int before = left;
            const uint64_t start = flac_profile::clock_ns();
            result = FLACDecode(file.data() + file.size() - left, &left, pcm);
            decode_ns += flac_profile::clock_ns() - start;
            assert(result >= 0 && left >= 0 && left <= before);
            const unsigned n = FLACGetOutputSamps();
            assert(n <= FLAC_OUTPUT_FRAMES * channels && written + n <= decoded.size());
            for (unsigned i = 0; i < n / channels; ++i)
                for (unsigned ch = 0; ch < channels; ++ch)
                    decoded[written++] = pcm[2*i+ch];
            assert(before != left || n);
        } while (left || result == GIVE_NEXT_LOOP);
        assert(result == 0 && written == decoded.size());
    }
    FILE* output = fopen(argv[2], "wb"); assert(output);
    assert(fwrite(decoded.data(), sizeof(short), decoded.size(), output) == decoded.size());
    fclose(output); FLACDecoder_FreeBuffers();
    printf("DECODE_NS %llu\n", (unsigned long long)decode_ns);
    flac_profile::print();
}
