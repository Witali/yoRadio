/* Host-only observation of each original signed index read. The final int16
 * is read as int16: any target word padding is a separate ELF obligation. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct {uint64_t total,negative,last,phase[4],positions[105];} y_index_counts;
static void y_index_check(int ok){if(!ok){fputs("PVQ index observer assertion\n",stderr);abort();}}
static void y_index_save(void){
 const char *name=getenv("YORADIO_INDEX_COUNTS");y_index_check(name!=NULL);
 FILE *f=fopen(name,"wb");y_index_check(f!=NULL);
 fprintf(f,"{\"total\":%" PRIu64 ",\"negative\":%" PRIu64 ",\"last\":%" PRIu64 ",\"phase\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "],\"positions\":[",y_index_counts.total,y_index_counts.negative,y_index_counts.last,y_index_counts.phase[0],y_index_counts.phase[1],y_index_counts.phase[2],y_index_counts.phase[3]);
 for(int i=0;i<105;i++)fprintf(f,"%s%" PRIu64,i?",":"",y_index_counts.positions[i]);
 fputs("]}\n",f);y_index_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_index_init(void){y_index_check(atexit(y_index_save)==0);}
static int y_index_probe(const CELTMode *m,int pos){
 y_index_check(m->nbEBands==21&&m->cache.size==392&&pos>=0&&pos<105);
 uintptr_t base=(uintptr_t)m->cache.index,addr=(uintptr_t)(m->cache.index+pos);
 y_index_check((base&3)==0&&(addr&1)==0&&addr+2<=base+210);
 int value=m->cache.index[pos];y_index_counts.total++;y_index_counts.positions[pos]++;
 y_index_counts.phase[addr&3]++;y_index_counts.negative+=(value<0);y_index_counts.last+=(pos==104);
 return value;
}
