/* Audit-only experiment: not linked into the firmware. Keep fixed-point
 * multiplication and rounding unchanged; evaluate the reciprocal once. */
#include "config.h"
#include "mathops.h"

__attribute__((noinline)) opus_val32 opus_div_original(opus_val32 a, opus_val32 b)
{
    return celt_div(a, b);
}

__attribute__((noinline)) opus_val32 opus_div_once(opus_val32 a, opus_val32 b)
{
    const opus_val32 reciprocal = celt_rcp(b);
    return MULT32_32_Q31(a, reciprocal);
}

#ifdef OPUS_HOIST_HOST
#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static unsigned calls;
opus_val32 __real_celt_rcp(opus_val32 x);
opus_val32 __wrap_celt_rcp(opus_val32 x)
{
    ++calls;
    return __real_celt_rcp(x);
}

static void check(opus_val32 a, opus_val32 b)
{
    calls = 0;
    const opus_val32 before = opus_div_original(a, b);
    assert(calls == 3);
    calls = 0;
    const opus_val32 after = opus_div_once(a, b);
    assert(calls == 1 && before == after);
}

int main(void)
{
    const opus_val32 numerators[] = {INT32_MIN, INT32_MIN+1, -65536, -32768,
        -1, 0, 1, 32767, 65535, INT32_MAX-1, INT32_MAX};
    unsigned count = 0;
    for (unsigned i = 0; i < sizeof(numerators)/sizeof(*numerators); ++i) {
        for (int b = 1; b <= 65536; ++b) {
            check(numerators[i], b);
            ++count;
        }
    }
    uint32_t seed = 0x7349;
    for (unsigned i = 0; i < 1000000; ++i) {
        seed = seed*1664525u + 1013904223u;
        const opus_val32 a = (opus_val32)seed;
        seed = seed*1664525u + 1013904223u;
        check(a, (opus_val32)((seed & 0x7fffffffu) | 1u));
        ++count;
    }
    printf("{\"passed\":true,\"cases\":%u,\"original_calls\":3,\"once_calls\":1}\n", count);
    return 0;
}
#endif
