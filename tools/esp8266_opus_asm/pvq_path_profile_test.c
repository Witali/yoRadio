/* Host-only observer unit cases; fake decoder returns known legal L1 vectors.
 * Production decoder/ASM is not linked here. Full PCM equality is checked
 * separately against the real host decoder by profile_pvq_paths.cjs.
 */
#include "pvq_path_profile.c"
#include <string.h>

static const struct sample {
    int n, k, y[6];
    uint64_t dimensions, many, zeros, searches, probes, extra;
    uint64_t columns, column_probes, rows, row_probes;
} samples[] = {
    {2,1,{1,0},0,0,0,0,0,0,0,0,0,0},
    {5,3,{0,1,0,-1,1},3,0,2,1,1,0,0,0,0,0},
    {5,9,{0,5,-1,0,3},3,3,0,0,0,0,0,0,3,9},
    {6,8,{5,0,-2,1,0,0},4,1,1,2,3,1,1,3,0,0},
    {3,3,{-3,0,0},1,1,0,0,0,0,1,3,0,0},
    {3,2,{0,0,-2},1,0,1,0,0,0,0,0,0,0},
    {3,2,{-2,0,0},1,0,0,1,2,1,0,0,0,0},
    {4,6,{2,-4,0,0},2,2,0,0,0,0,1,3,1,3},
    {4,3,{1,0,0,-2},2,0,1,1,1,0,0,0,0,0}
};
static const struct sample *current;
opus_val32 __real_decode_pulses(int *y, int n, int k, ec_dec *dec) {
    (void)dec;
    check(n == current->n && k == current->k);
    opus_val32 energy = 0;
    for (int i=0; i<n; ++i) { y[i]=current->y[i];energy+=y[i]*y[i]; }
    return energy;
}
int main(void) {
    int y[6];
    for (unsigned i=0; i<sizeof(samples)/sizeof(samples[0]); ++i) {
        current=&samples[i];memset(&counts,0,sizeof(counts));
        __wrap_decode_pulses(y,current->n,current->k,NULL);
        check(!memcmp(y,current->y,(size_t)current->n*sizeof(*y)));
        check(counts.calls==1 && counts.dimensions==current->dimensions);
        check(counts.many_pulses==current->many && counts.many_dimensions_zero==current->zeros);
        check(counts.dimension_searches==current->searches && counts.dimension_probes==current->probes);
        check(counts.dimension_extra_probes==current->extra);
        check(counts.column_searches==current->columns && counts.column_probes==current->column_probes);
        check(counts.row_searches==current->rows && counts.row_probes==current->row_probes);
        uint64_t hist=0;for(unsigned j=0;j<33;++j)hist+=counts.dimension_probe_histogram[j];
        check(hist==current->searches);
    }
    puts("{\"passed\":true,\"cases\":9}");
    return 0;
}
