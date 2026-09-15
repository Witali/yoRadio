/* Host-only census of exact PVQ boundary guards; no target change.
 * Count only basic no-split calls. Return the original index in all cases. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct { uint64_t calls, zero_fast, upper_fast, upper_loaded, after_three; } y_boundary_counts;
static void y_boundary_check(int ok) {
    if (!ok) { fputs("PVQ boundary observer mismatch\n",stderr); abort(); }
}
static void y_boundary_save(void) {
    const char *name=getenv("YORADIO_BITS_COUNTS");y_boundary_check(name!=NULL);
    FILE *f=fopen(name,"wb");y_boundary_check(f!=NULL);
    fprintf(f,"{\"calls\":%" PRIu64 ",\"zero_fast\":%" PRIu64
      ",\"upper_fast\":%" PRIu64 ",\"upper_loaded\":%" PRIu64 ",\"after_three\":%" PRIu64 "}\n",
      y_boundary_counts.calls,y_boundary_counts.zero_fast,y_boundary_counts.upper_fast,
      y_boundary_counts.upper_loaded,y_boundary_counts.after_three);
    y_boundary_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_boundary_init(void) {y_boundary_check(atexit(y_boundary_save)==0);}
static int y_boundary_probe(const CELTMode *m,int band,int LM,int bits) {
    const unsigned char *cache=m->cache.bits+m->cache.index[(LM+1)*m->nbEBands+band];
    const int reference=bits2pulses(m,band,LM,bits);
    y_boundary_check(cache[0]>0);
    const int zero=bits<=(cache[1]+1)/2,upper=bits>cache[cache[0]]+1;
    y_boundary_check(!(zero&&upper));
    if(zero)y_boundary_check(reference==0);
    if(upper)y_boundary_check(reference==cache[0]);
    int lo=0,hi=cache[0],value=bits-1;
    for(int i=0;i<3;i++){int mid=(lo+hi+1)>>1;if(cache[mid]>=value)hi=mid;else lo=mid;}
    y_boundary_counts.calls++;y_boundary_counts.zero_fast+=zero;y_boundary_counts.upper_fast+=upper;
    y_boundary_counts.upper_loaded+=upper&&LM!=-1;y_boundary_counts.after_three+=hi-lo<=1;
    return reference;
}
