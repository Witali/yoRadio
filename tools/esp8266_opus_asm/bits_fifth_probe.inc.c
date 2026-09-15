/* Host-only observer, included after rate.h in a generated bands.c copy.
 * Never linked into firmware. Compare the six-step reference with a possible
 * last-step shortcut; count actual calls, not uniformly sampled budgets.
 * The final nearest-endpoint rule is unchanged, including the lo=0 sentinel.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>

static struct { uint64_t calls, skipped, gaps[256]; } y_bits_counts;
static void y_bits_check(int ok) {
    if (!ok) { fputs("bits fifth-step observer mismatch\n", stderr); abort(); }
}
static void y_bits_save(void) {
    const char *name=getenv("YORADIO_BITS_COUNTS");
    y_bits_check(name != NULL);
    FILE *out=fopen(name,"wb"); y_bits_check(out != NULL);
    fprintf(out,"{\"calls\":%" PRIu64 ",\"skippable\":%" PRIu64 ",\"gaps_after_five\":[",
            y_bits_counts.calls,y_bits_counts.skipped);
    for (unsigned i=0;i<256;i++)
        fprintf(out,"%s%" PRIu64,i?",":"",y_bits_counts.gaps[i]);
    fputs("]}\n",out); y_bits_check(fclose(out)==0);
}
__attribute__((constructor)) static void y_bits_init(void) {
    y_bits_check(atexit(y_bits_save)==0);
}
static int y_bits_fifth_probe(const CELTMode *m,int band,int LM,int bits) {
    const unsigned char *cache=m->cache.bits+m->cache.index[(LM+1)*m->nbEBands+band];
    const int original=bits2pulses(m,band,LM,bits);
    int lo=0,hi=cache[0],value=bits-1;
    for (int i=0;i<5;i++) {
        const int mid=(lo+hi+1)>>1;
        if ((int)cache[mid]>=value) hi=mid; else lo=mid;
    }
    const int gap=hi-lo;
    y_bits_check(gap>=0 && gap<256);
    y_bits_counts.calls++; y_bits_counts.gaps[gap]++;
    if (gap<=1) y_bits_counts.skipped++;
    else {
        const int mid=(lo+hi+1)>>1;
        if ((int)cache[mid]>=value) hi=mid; else lo=mid;
    }
    const int candidate=value-(lo==0?-1:(int)cache[lo])<=(int)cache[hi]-value?lo:hi;
    y_bits_check(candidate==original);
    return original; /* Observe, do not change the decoder's selected result. */
}
