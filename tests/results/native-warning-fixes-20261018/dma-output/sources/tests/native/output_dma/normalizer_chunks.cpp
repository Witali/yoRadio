#include "AudioNormalizer.h"
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <vector>

int main() {
    const unsigned rates[] = {8000,11025,12000,16000,22050,24000,32000,44100,48000};
    unsigned cases = 0;
    for (unsigned rate : rates) for (unsigned channels : {1U,2U})
    for (unsigned boost : {0U,6U,12U,20U}) for (int target : {-20,-3,0})
    for (unsigned time_ms : {100U,500U,10000U}) {
        const size_t frames = 16384;
        std::vector<int16_t> a(frames*channels);
        uint32_t seed = 12345;
        for (auto &sample : a) {
            seed ^= seed<<13; seed ^= seed>>17; seed ^= seed<<5;
            sample = static_cast<int16_t>(seed);
        }
        auto b = a;
        AudioNormalizer old, next;
        old.configure(true,boost,target,time_ms,rate);
        next.configure(true,boost,target,time_ms,rate);
        size_t old_chunk = 3584/(channels*sizeof(int16_t));
        size_t new_chunk = 2048/(channels*sizeof(int16_t));
        for(size_t first=0; first<frames; first+=old_chunk)
            old.processBlock(a.data()+first*channels,std::min(old_chunk,frames-first),channels);
        for(size_t first=0; first<frames; first+=new_chunk)
            next.processBlock(b.data()+first*channels,std::min(new_chunk,frames-first),channels);
        assert(a == b);
        ++cases;
    }
    std::printf("PASS normalizer cases=%u max_error_lsb=0\n", cases);
}
