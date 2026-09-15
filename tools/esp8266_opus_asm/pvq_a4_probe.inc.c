/* Host-only count of the two remaining a4 flash reads. No target timing.
 * Return the original byte; verify the full aligned word is readable. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct { uint64_t first, upper, phase[4]; } y_a4_counts;
static void y_a4_check(int ok) {
    if (!ok) { fputs("PVQ a4 observer assertion\n",stderr); abort(); }
}
static void y_a4_save(void) {
    const char *name=getenv("YORADIO_A4_COUNTS");y_a4_check(name!=NULL);
    FILE *f=fopen(name,"wb");y_a4_check(f!=NULL);
    fprintf(f,"{\"first\":%" PRIu64 ",\"upper\":%" PRIu64
      ",\"phase\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "]}\n",
      y_a4_counts.first,y_a4_counts.upper,y_a4_counts.phase[0],
      y_a4_counts.phase[1],y_a4_counts.phase[2],y_a4_counts.phase[3]);
    y_a4_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_a4_init(void) {y_a4_check(atexit(y_a4_save)==0);}
static int y_a4_probe(const CELTMode *m,const unsigned char *p,int upper) {
    uintptr_t base=(uintptr_t)m->cache.bits,addr=(uintptr_t)p,word=addr&~(uintptr_t)3;
    y_a4_check((base&3)==0 && m->cache.size==392);
    y_a4_check(addr>=base && addr<base+392 && word>=base && word+4<=base+392);
    y_a4_check(upper==0 || upper==1);
    if(upper)y_a4_counts.upper++;else y_a4_counts.first++;
    y_a4_counts.phase[addr&3]++;
    return *p;
}
