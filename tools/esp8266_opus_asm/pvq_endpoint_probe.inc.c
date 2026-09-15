/* Host-only count of the two original endpoint reads, not the selected-cost
 * duplicate removed earlier. Return original byte and preserve lo==0 guard. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct {uint64_t count[2],phase[2][4];} y_endpoint_counts;
static void y_endpoint_check(int ok){if(!ok){fputs("PVQ endpoint observer assertion\n",stderr);abort();}}
static void y_endpoint_save(void){
 const char *name=getenv("YORADIO_ENDPOINT_COUNTS");y_endpoint_check(name!=NULL);
 FILE *f=fopen(name,"wb");y_endpoint_check(f!=NULL);
 fprintf(f,"{\"lower\":%" PRIu64 ",\"upper\":%" PRIu64 ",\"phase\":[[%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "],[%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "]]}\n",
 y_endpoint_counts.count[0],y_endpoint_counts.count[1],
 y_endpoint_counts.phase[0][0],y_endpoint_counts.phase[0][1],y_endpoint_counts.phase[0][2],y_endpoint_counts.phase[0][3],
 y_endpoint_counts.phase[1][0],y_endpoint_counts.phase[1][1],y_endpoint_counts.phase[1][2],y_endpoint_counts.phase[1][3]);
 y_endpoint_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_endpoint_init(void){y_endpoint_check(atexit(y_endpoint_save)==0);}
static int y_endpoint_probe(const CELTMode *m,const unsigned char *p,int upper){
 uintptr_t base=(uintptr_t)m->cache.bits,addr=(uintptr_t)p,word=addr&~(uintptr_t)3;
 y_endpoint_check((base&3)==0&&m->cache.size==392&&addr>=base&&addr<base+392);
 y_endpoint_check(word>=base&&word+4<=base+392);y_endpoint_check(upper==0||upper==1);
 y_endpoint_counts.count[upper]++;y_endpoint_counts.phase[upper][addr&3]++;return *p;
}
