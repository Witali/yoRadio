/* Host-only census: preserve original pulses2bits, including q=0 no-load. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct {uint64_t calls,loads,zero,phase[4];} y_adjust_counts;
static void y_adjust_check(int ok){if(!ok){fputs("PVQ adjustment observer assertion\n",stderr);abort();}}
static void y_adjust_save(void){
 const char *name=getenv("YORADIO_ADJUST_COUNTS");y_adjust_check(name!=NULL);
 FILE *f=fopen(name,"wb");y_adjust_check(f!=NULL);
 fprintf(f,"{\"calls\":%" PRIu64 ",\"loads\":%" PRIu64 ",\"zero\":%" PRIu64 ",\"phase\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "]}\n",y_adjust_counts.calls,y_adjust_counts.loads,y_adjust_counts.zero,y_adjust_counts.phase[0],y_adjust_counts.phase[1],y_adjust_counts.phase[2],y_adjust_counts.phase[3]);
 y_adjust_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_adjust_init(void){y_adjust_check(atexit(y_adjust_save)==0);}
static int y_adjust_probe(const CELTMode *m,int i,int LM,int q){
 y_adjust_check(m->nbEBands==21&&m->cache.size==392&&q>=0);
 y_adjust_counts.calls++;
 if(q==0)y_adjust_counts.zero++;
 else{
  const int pos=(LM+1)*m->nbEBands+i;y_adjust_check(pos>=0&&pos<105);
  const int off=m->cache.index[pos];y_adjust_check(off>=0&&off<392);
  const unsigned char *cache=m->cache.bits+off;y_adjust_check(q<=cache[0]);
  uintptr_t base=(uintptr_t)m->cache.bits,addr=(uintptr_t)(cache+q),aligned=addr&~(uintptr_t)3;
  y_adjust_check((base&3)==0&&addr<base+392&&aligned>=base&&aligned+4<=base+392);
  y_adjust_counts.loads++;y_adjust_counts.phase[addr&3]++;
 }
 return pulses2bits(m,i,LM,q);
}
