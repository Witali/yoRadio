#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>

#define RESAMPLER_SCALE 32768U
#include "interpolation.inc"

static int16_t reference(int16_t previous, int16_t current, uint32_t fraction) {
    int64_t product = ((int64_t)current - previous) * fraction;
    product += product >= 0 ? 16384 : -16384;
    int64_t value = previous + product / 32768;
    assert(value >= INT16_MIN && value <= INT16_MAX);
    return (int16_t)value;
}
static uint32_t random_value = 0x8245d936U;
static uint32_t next_random(void) {
    random_value = random_value * 1664525U + 1013904223U;
    return random_value;
}
static int16_t next_sample(void) {
    uint32_t high = next_random() >> 16;
    return (int16_t)(high <= INT16_MAX ? (int32_t)high : (int32_t)high - 65536);
}
int main(void) {
    const int16_t endpoints[] = {INT16_MIN, INT16_MIN+1, -16384, -1, 0, 1, 16384, INT16_MAX-1, INT16_MAX};
    uint64_t cases = 0;
    for (unsigned i=0; i<sizeof(endpoints)/sizeof(endpoints[0]); ++i)
        for (unsigned j=0; j<sizeof(endpoints)/sizeof(endpoints[0]); ++j)
            for (uint32_t fraction=0; fraction<=RESAMPLER_SCALE; ++fraction) {
                assert(interpolate_sample(endpoints[i],endpoints[j],fraction) == reference(endpoints[i],endpoints[j],fraction));
                ++cases;
            }
    for (unsigned i=0; i<1000000; ++i) {
        int16_t previous=next_sample(),current=next_sample();
        uint32_t fraction=next_random() % (RESAMPLER_SCALE+1U);
        assert(interpolate_sample(previous,current,fraction)==reference(previous,current,fraction));
        ++cases;
    }
    printf("PASS interpolation: %llu exact wide-reference cases, full fraction range and signed endpoints\n",(unsigned long long)cases);
}
