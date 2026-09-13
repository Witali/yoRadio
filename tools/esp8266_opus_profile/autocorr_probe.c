/* Direct autocorrelation regression, including the allocation-required path.
 * A stream-only corpus can miss large signals needing fixed-point scaling. */
#include <assert.h>
#include <setjmp.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "config.h"
#include "celt_lpc.h"
#include "opus_memory.h"
static uint64_t scratch[256], words[2048];
static opus_val16 input[1024], saved[1024], window[120];
static opus_val32 ac[33];
static uint32_t rng = 123456789;
static unsigned cases;
static void run_case(int n, int lag, int overlap, int amplitude, int pattern) {
    for (int i = 0; i < n; i++) {
        rng = 1664525U * rng + 1013904223U;
        input[i] = pattern == 0 ? (i == n/2 ? amplitude : 0) : pattern == 1 ?
            (i & 1 ? -amplitude : amplitude) : (int)(rng % (2U*amplitude+1U)) - amplitude;
    }
    memcpy(saved, input, sizeof(input));
    for (int i = 0; i < overlap; i++) window[i] = (i+1) * 32767 / (overlap+1);
    yoradio_opus_memory_bind(scratch, sizeof(scratch), words, sizeof(words));
    if (setjmp(yoradio_opus_oom)) assert(!"unexpected OOM with full arena");
    int shift = _celt_autocorr(input, ac, window, overlap, lag, n, 0);
    assert(!memcmp(saved, input, sizeof(input)));
    size_t peak = yoradio_opus_scratch_peak_bytes();
    assert(yoradio_opus_scratch_mark().bytes == 0);
    printf("%s{\"n\":%d,\"lag\":%d,\"overlap\":%d,\"amplitude\":%d,\"pattern\":%d,\"shift\":%d,\"scratch_peak\":%zu,\"ac\":[",
        cases++ ? "," : "", n, lag, overlap, amplitude, pattern, shift, peak);
    for (int i = 0; i <= lag; i++) printf("%s%d", i ? "," : "", ac[i]);
    yoradio_opus_memory_bind(scratch, 0, words, sizeof(words));
    int oom = setjmp(yoradio_opus_oom);
    if (!oom) (void)_celt_autocorr(input, ac, window, overlap, lag, n, 0);
    assert((oom != 0) == (peak != 0));
    assert(!memcmp(saved, input, sizeof(input)));
    printf("],\"zero_scratch_oom\":%s}", oom ? "true" : "false");
}
int main(void) {
    const int lengths[] = {15,64,240,1024}, lags[] = {0,4,12,24,32}, overlaps[] = {0,8,120};
    const int amplitudes[] = {0,1,512,2047,30000};
    printf("{\"cases\":[");
    for (unsigned n=0;n<4;n++) for (unsigned lag=0;lag<5;lag++) for (unsigned o=0;o<3;o++)
        for (unsigned a=0;a<5;a++) for (int pattern=0;pattern<3;pattern++)
          if (lags[lag] < lengths[n])
            run_case(lengths[n], lags[lag], overlaps[o] < lengths[n]/2 ? overlaps[o] : lengths[n]/2, amplitudes[a], pattern);
    run_case(64,4,40,30000,2); /* Overlapping windows: original fallback. */
    printf("],\"passed\":true,\"input_preserved\":true,\"oom_contract\":true}\n");
    return 0;
}
