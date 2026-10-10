#include "custom_flac_adapter.h"
#include "flac_decoder.h"
#include <cassert>
#include <cstdio>
#include <vector>

unsigned flac_test_errors;
struct Capture {
    FILE *output;
    unsigned bits, channels, rate;
    size_t bytes = 0;
};
static bool pcm(void *user, const custom_flac_info_t *info,
                const uint8_t *data, size_t bytes) {
    auto &capture = *static_cast<Capture *>(user);
    assert(info->bits_per_sample == capture.bits);
#ifndef BASELINE
    assert(info->pcm_bits_per_sample == 16);
#endif
    assert(info->channels == capture.channels && info->sample_rate == capture.rate);
    assert(bytes && bytes % (2 * info->channels) == 0);
    assert(fwrite(data, 1, bytes, capture.output) == bytes);
    capture.bytes += bytes;
    return true;
}

int main(int argc, char **argv) {
    assert(argc == 3);
    FILE *input = fopen(argv[1],"rb"); assert(input);
    fseek(input,0,SEEK_END);size_t size=ftell(input);rewind(input);
    std::vector<uint8_t> data(size);assert(fread(data.data(),1,size,input)==size);fclose(input);
    assert(size>42);
    Capture capture = {fopen(argv[2],"wb"),
        unsigned((((data[20]&1)<<4)|(data[21]>>4))+1),
        unsigned(((data[20]>>1)&7)+1),
        unsigned((data[18]<<12)|(data[19]<<4)|(data[20]>>4))};
    assert(capture.output);
    auto *decoder=custom_flac_decoder_create();assert(decoder);
    size_t peak=0,offset=0,index=0;
    const size_t chunks[]={1,3,127,511,1024,17,8192};
    while(offset<size) {
        const size_t chunk=std::min(size-offset,chunks[index++%7]);
        custom_flac_feed_stats_t stats={};
        int result=custom_flac_decoder_feed(decoder,data.data()+offset,chunk,
            offset+chunk==size,pcm,&capture,&stats);
        assert(result>=0 && !flac_test_errors);
        peak=std::max(peak,custom_flac_decoder_memory_used(decoder));offset+=chunk;
    }
    fclose(capture.output);
    custom_flac_decoder_destroy(decoder);
    assert(!FLACDecoder_GetAllocatedBytes());
    assert(capture.bytes);
    printf("PASS bytes=%zu decoder_peak_bytes=%zu chunks=%zu source_bits=%u pcm_bits=16\n",
        capture.bytes,peak,index,capture.bits);
}
