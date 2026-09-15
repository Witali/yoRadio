/* Host-only count at each quant_partition entry. Linked target reads
 * cache[0] unconditionally here; the extra host observer is not target code. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct { uint64_t rows, minus_one, phase[4]; } y_row_counts;
static void y_row_check(int ok) { if(!ok){fputs("PVQ row observer assertion\n",stderr);abort();} }
static void y_row_save(void) {
 const char *name=getenv("YORADIO_ROW_COUNTS");y_row_check(name!=NULL);
 FILE *f=fopen(name,"wb");y_row_check(f!=NULL);
 fprintf(f,"{\"rows\":%" PRIu64 ",\"minus_one\":%" PRIu64 ",\"phase\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "]}\n",
 y_row_counts.rows,y_row_counts.minus_one,y_row_counts.phase[0],y_row_counts.phase[1],y_row_counts.phase[2],y_row_counts.phase[3]);
 y_row_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_row_init(void){y_row_check(atexit(y_row_save)==0);}
static int y_row_probe(const CELTMode *m,const unsigned char *p,int LM) {
 uintptr_t base=(uintptr_t)m->cache.bits,addr=(uintptr_t)p,word=addr&~(uintptr_t)3;
 y_row_check((base&3)==0 && m->cache.size==392 && addr>=base && addr<base+392);
 y_row_check(word>=base && word+4<=base+392);
 y_row_counts.rows++;y_row_counts.minus_one+=LM==-1;y_row_counts.phase[addr&3]++;
 return *p;
}
