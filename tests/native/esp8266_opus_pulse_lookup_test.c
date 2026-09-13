#include "config.h"
#include "rate.h"
#include "lookup.model.h"
#include "lookup.testdata.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>

int main(void) {
    static const opus_int16 zero_index = 0;
    static const unsigned char custom[] = {3, 5, 20, 50};
    CELTMode mode = {0};
    mode.cache.index = &zero_index;
    unsigned count = 0, hits = 0, fallbacks = 0;
    for (unsigned row = 0; row < 23; ++row) {
        mode.cache.bits = y_opus_cache_bits50 + y_row_offsets[row];
        for (int b = -256; b < 16384; ++b) {
            int expected = bits2pulses(&mode, 0, 0, b);
            int result = y_pulse_lookup(mode.cache.bits, b);
            if (result < 0) { ++fallbacks; result = bits2pulses(&mode, 0, 0, b); }
            else ++hits;
            assert(result == expected); ++count;
        }
        assert(y_pulse_lookup(mode.cache.bits, INT_MIN) == -1);
        assert(y_pulse_lookup(mode.cache.bits, INT_MAX) == -1);
    }
    for (unsigned off = 0; off < 392; ++off) {
        int known = 0;
        for (unsigned row = 0; row < 23; ++row) known |= off == y_row_offsets[row];
        if (!known) assert(y_pulse_lookup(y_opus_cache_bits50 + off, 64) == -1);
    }
    mode.cache.bits = custom;
    for (int b = -256; b <= 300; ++b) {
        assert(y_pulse_lookup(custom, b) == -1);
        /* The fallback is the original function and remains callable. */
        assert(bits2pulses(&mode, 0, 0, b) >= 0);
    }
    printf("{\"passed\":true,\"combinations\":%u,\"lookup_hits\":%u,\"fallbacks\":%u}\n", count, hits, fallbacks);
}
