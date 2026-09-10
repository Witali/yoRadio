#ifdef FIR_PROBE_ENTRY
/* Compile the ACTUAL interpolation function twice, not a copied algorithm.
 * The unused outer resampler is discarded by section GC in this unit test. */
#include "resampler_private_IIR_FIR.c"
int FIR_PROBE_ENTRY(int16_t *out, int16_t *in, int32_t max, int32_t step) {
    return (int)(silk_resampler_private_IIR_FIR_INTERPOL(out,in,max,step)-out);
}
#else
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
extern const int16_t silk_resampler_frac_FIR_12[12][4];
int fir_reference(int16_t *,int16_t *,int32_t,int32_t);
int fir_candidate(int16_t *,int16_t *,int32_t,int32_t);
static uint32_t pair_reads, rows;
void yoradio_opus_fir_test_pair(const void *p) {
    uintptr_t offset = (uintptr_t)p-(uintptr_t)silk_resampler_frac_FIR_12;
    assert(((uintptr_t)p&3U)==0 && offset<=92 && (offset&3U)==0);
    ++pair_reads;
    rows |= 1U<<(offset/8);
}
int main(void) {
    enum { INPUT=40000, OUTPUT=70000 };
    int16_t *in=malloc(INPUT*sizeof(*in));
    int16_t *a=malloc((OUTPUT+2)*sizeof(*a)), *b=malloc((OUTPUT+2)*sizeof(*b));
    assert(in && a && b);
    uint32_t seed=123456789, compared=0, cases=0;
    const int32_t steps[]={32767,21845,32768,43690,65536,98304,131072};
    for (unsigned pattern=0;pattern<5;++pattern) {
        for (unsigned i=0;i<INPUT;++i) {
            seed=1664525U*seed+1013904223U;
            in[i]=pattern==0 ? (int16_t)(seed>>16) : pattern==1 ? INT16_MAX :
                pattern==2 ? INT16_MIN : pattern==3 ? ((i&1)?INT16_MIN:INT16_MAX) : 0;
        }
        for (unsigned s=0;s<sizeof(steps)/sizeof(*steps);++s) {
            /* Odd32767 visits ALL65536 fractional phases without overflowing
             * signed index_Q16; the largest read remains inside INPUT. */
            int count=s==0?65536:997, step=steps[s], max=count*step;
            memset(a,0x65,(OUTPUT+2)*sizeof(*a));
            memset(b,0x65,(OUTPUT+2)*sizeof(*b));
            uint32_t before=pair_reads;
            assert(fir_reference(a+1,in,max,step)==count);
            assert(fir_candidate(b+1,in,max,step)==count);
            assert(!memcmp(a,b,(OUTPUT+2)*sizeof(*a)));
            assert(a[0]==0x6565 && a[count+1]==0x6565);
            assert(pair_reads-before==(unsigned)count*4);
            compared+=count; ++cases;
        }
    }
    assert(rows==0xfff);
    printf("{\"passed\":true,\"cases\":%u,\"samples\":%u,\"pair_reads\":%u,\"rows\":%u}\n",
        cases,compared,pair_reads,rows);
    free(in);free(a);free(b);
    return 0;
}
#endif
