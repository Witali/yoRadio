#include "config.h"
#include "rate.h"
#include "inverse.h"
#include <assert.h>
#include <stdio.h>

/* Compare with the actual upstream inline, not another handwritten search. */
int main(void) {
    static const opus_int16 zero_index = 0;
    CELTMode mode = {0};
    mode.cache.index = &zero_index;
    mode.nbEBands = 0;
    unsigned count = 0;
    for (unsigned row = 0; row < 23; ++row) {
        unsigned offset = (unsigned)row_offsets[row];
        mode.cache.bits = reference_bits + offset;
        unsigned mapped = (offset_map_words[offset >> 2] >> ((offset & 3) * 8)) & 255;
        assert(mapped == row);
        for (int b = -256; b < 16384; ++b) {
            int expected = bits2pulses(&mode, 0, 0, b);
            unsigned got = b < 0 ? 0 : b > 256 ? mode.cache.bits[0] :
                (inverse_words[row * 65 + ((unsigned)b >> 2)] >> ((b & 3) * 8)) & 255;
            assert(got == (unsigned)expected);
            ++count;
        }
    }
    printf("{\"passed\":true,\"combinations\":%u}\n", count);
    return 0;
}
