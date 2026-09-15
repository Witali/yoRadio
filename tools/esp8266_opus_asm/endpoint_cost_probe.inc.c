/* Host-only path census, not a target-speed measurement. Use the accepted
 * fourth/fifth-step search, check both cached endpoint costs against the
 * original six-step API, and return the original q. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct { uint64_t calls, zero, lower, upper, same; } y_cost_counts;
static void y_cost_check(int ok) {
    if (!ok) { fputs("endpoint cost observer mismatch\n",stderr); abort(); }
}
static void y_cost_save(void) {
    const char *name=getenv("YORADIO_BITS_COUNTS");y_cost_check(name!=NULL);
    FILE *f=fopen(name,"wb");y_cost_check(f!=NULL);
    fprintf(f,"{\"calls\":%" PRIu64 ",\"zero\":%" PRIu64
      ",\"lower\":%" PRIu64 ",\"upper\":%" PRIu64 ",\"same\":%" PRIu64 "}\n",
      y_cost_counts.calls,y_cost_counts.zero,y_cost_counts.lower,y_cost_counts.upper,y_cost_counts.same);
    y_cost_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_cost_init(void) {y_cost_check(atexit(y_cost_save)==0);}
static int y_endpoint_probe(const CELTMode *m,int band,int LM,int bits) {
    const unsigned char *cache=m->cache.bits+m->cache.index[(LM+1)*m->nbEBands+band];
    const int reference=bits2pulses(m,band,LM,bits),value=bits-1;
    int lo=0,hi=cache[0];
    for(int i=0;i<4;i++) {int mid=(lo+hi+1)>>1;if(cache[mid]>=value)hi=mid;else lo=mid;}
    if(hi-lo>1) {int mid=(lo+hi+1)>>1;if(cache[mid]>=value)hi=mid;else lo=mid;
        if(hi-lo>1) {mid=(lo+hi+1)>>1;if(cache[mid]>=value)hi=mid;else lo=mid;}}
    const int lower=lo==0?-1:(int)cache[lo],upper=(int)cache[hi];
    const int use_lower=value-lower<=upper-value,q=use_lower?lo:hi;
    const int cost=q==0?0:(use_lower?lower:upper)+1;
    y_cost_check(q==reference);y_cost_check(cost==pulses2bits(m,band,LM,q));
    y_cost_counts.calls++;if(lo==hi)y_cost_counts.same++;
    if(q==0)y_cost_counts.zero++;else if(use_lower)y_cost_counts.lower++;else y_cost_counts.upper++;
    return reference;
}
