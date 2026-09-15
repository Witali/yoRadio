/* Host-only reference-path census. Never linked into the target firmware.
 * Compare a possible fourth-step exit with the accepted fifth-step exit.
 * The observer returns the original result; no CPU timing is inferred. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct { uint64_t calls, fourth, fifth, gaps4[256], gaps5[256]; } y_fourth;
static void y_fourth_check(int ok) {
    if (!ok) { fputs("fourth-step observer mismatch\n",stderr); abort(); }
}
static void y_fourth_save(void) {
    const char *name=getenv("YORADIO_BITS_COUNTS");
    y_fourth_check(name!=NULL);
    FILE *f=fopen(name,"wb"); y_fourth_check(f!=NULL);
    fprintf(f,"{\"calls\":%" PRIu64 ",\"fourth\":%" PRIu64 ",\"fifth\":%" PRIu64,
            y_fourth.calls,y_fourth.fourth,y_fourth.fifth);
    for (int stage=4;stage<=5;stage++) {
        fprintf(f,",\"gaps_after_%d\":[",stage);
        for (unsigned i=0;i<256;i++)
            fprintf(f,"%s%" PRIu64,i?",":"",stage==4?y_fourth.gaps4[i]:y_fourth.gaps5[i]);
        fputs("]",f);
    }
    fputs("}\n",f); y_fourth_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_fourth_init(void) {
    y_fourth_check(atexit(y_fourth_save)==0);
}
static int y_bits_fourth_probe(const CELTMode *m,int band,int LM,int bits) {
    const unsigned char *cache=m->cache.bits+m->cache.index[(LM+1)*m->nbEBands+band];
    const int original=bits2pulses(m,band,LM,bits),value=bits-1;
    int lo=0,hi=cache[0],lo4=0,hi4=0,lo5=0,hi5=0;
    for (int i=1;i<=6;i++) {
        const int mid=(lo+hi+1)>>1;
        if ((int)cache[mid]>=value) hi=mid; else lo=mid;
        if (i==4) {lo4=lo;hi4=hi;}
        if (i==5) {lo5=lo;hi5=hi;}
    }
    const int g4=hi4-lo4,g5=hi5-lo5;
    y_fourth_check(g4>=0&&g4<256&&g5>=0&&g5<256);
    y_fourth.calls++;y_fourth.gaps4[g4]++;y_fourth.gaps5[g5]++;
    if (g4<=1) {y_fourth.fourth++;y_fourth_check(g5<=1);}
    if (g5<=1) y_fourth.fifth++;
    if (g4<=1) {lo=lo4;hi=hi4;}
    else if (g5<=1) {lo=lo5;hi=hi5;}
    const int candidate=value-(lo==0?-1:(int)cache[lo])<=(int)cache[hi]-value?lo:hi;
    y_fourth_check(candidate==original);
    return original;
}
