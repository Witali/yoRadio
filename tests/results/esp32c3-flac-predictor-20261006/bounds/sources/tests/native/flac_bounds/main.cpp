#include "flac_decoder.h"
#include <cassert>
#include <cstdio>
#include <vector>

int main(int argc, char **argv) {
    assert(argc == 4);
    FILE *input = fopen(argv[1], "rb"); assert(input);
    fseek(input, 0, SEEK_END); size_t size = ftell(input); rewind(input);
    std::vector<uint8_t> file(size); assert(fread(file.data(), 1, size, input) == size); fclose(input);
    assert(size > 42 && memcmp(file.data(), "fLaC", 4) == 0);
    const unsigned block = (file[10] << 8) | file[11];
    const unsigned channels = ((file[20] >> 1) & 7) + 1;
    const unsigned bits = (((file[20] & 1) << 4) | (file[21] >> 4)) + 1;
    const unsigned rate = (file[18] << 12) | (file[19] << 4) | (file[20] >> 4);
    size_t offset = 4;
    while (true) {
        bool last = file[offset] & 128;
        size_t length = (file[offset+1] << 16) | (file[offset+2] << 8) | file[offset+3];
        offset += 4 + length;
        assert(offset <= file.size());
        if (last) break;
    }
    size_t limit = strcmp(argv[2], "full") ? strtoul(argv[2], nullptr, 10) : file.size()-offset;
    if(strncmp(argv[2], "tail-", 5)==0) limit = file.size()-offset-strtoul(argv[2]+5,nullptr,10);
    assert(limit <= file.size()-offset);
    // Exact allocation: no tail slack can hide an overread from ASan.
    uint8_t *encoded = static_cast<uint8_t *>(malloc(limit ? limit : 1));
    memcpy(encoded, file.data()+offset, limit);
    assert(FLACDecoder_AllocateBuffers(block, channels));
    FLACSetRawBlockParams(channels, rate, bits, 0, 0);
    FLACDecoderReset();
    FILE *output = fopen(argv[3], "wb"); assert(output);
    int left = limit;
    int result = 0;
    size_t frames = 0;
    short pcm[FLAC_OUTPUT_FRAMES * MAX_CHANNELS];
    unsigned calls = 0;
    do {
        int before = left;
        result = FLACDecode(encoded + limit-left, &left, pcm);
        unsigned count = FLACGetOutputSamps();
        assert(left >= 0 && left <= before);
        assert(count <= FLAC_OUTPUT_FRAMES * channels);
        if (result < 0) { assert(count == 0); break; }
        for (unsigned i=0; i<count/channels; ++i)
            assert(fwrite(pcm+2*i, sizeof(short), channels, output) == channels);
        frames += count/channels;
        assert(++calls < 100000);
    } while (left > 0 || result == GIVE_NEXT_LOOP);
    fclose(output);
    assert(strcmp(argv[2], "full") ? result < 0 : result == 0);
    FLACDecoder_FreeBuffers(); free(encoded);
    printf("result=%d frames=%zu calls=%u remaining=%d\n", result, frames, calls, left);
    return 0;
}
