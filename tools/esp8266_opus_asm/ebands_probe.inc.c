/* Host-only semantic read census. Not linked into target firmware.
 * A source expression can be evaluated twice by MIN/MAX and be CSE'd by GCC;
 * these counts are NOT counts of LX106 loads or flash cache misses. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
typedef struct { uint64_t total, indices[22]; const char *function; } y_eband_site;
static y_eband_site y_eband_counts[Y_EBAND_SITES];
static void y_eband_check(int ok) {
   if (!ok) { fputs("eBands observer assertion\n", stderr); abort(); }
}
static void y_eband_save(void) {
   const char *prefix=getenv("YORADIO_EBAND_COUNTS"); char name[2048];
   y_eband_check(prefix != NULL);
   int n=snprintf(name,sizeof(name),"%s.%s.json",prefix,Y_EBAND_UNIT);
   y_eband_check(n>0 && (size_t)n<sizeof(name));
   FILE *f=fopen(name,"wb"); y_eband_check(f != NULL); fputs("[",f);
   for (int i=0;i<Y_EBAND_SITES;i++) {
      const y_eband_site *s=&y_eband_counts[i];
      fprintf(f,"%s{\"id\":%d,\"function\":\"%s\",\"total\":%" PRIu64 ",\"indices\":[",
         i?",":"",i,s->function?s->function:"",s->total);
      for (int j=0;j<22;j++) fprintf(f,"%s%" PRIu64,j?",":"",s->indices[j]);
      fputs("]}",f);
   }
   fputs("]\n",f); y_eband_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_eband_init(void) {
   y_eband_check(atexit(y_eband_save)==0);
}
__attribute__((noinline)) static int16_t y_eband_read(const int16_t *p,int index,int site,const char *fn) {
   static const int16_t expected[22]={0,1,2,3,4,5,6,7,8,10,12,14,16,20,24,28,34,40,48,60,78,100};
   y_eband_check(site>=0 && site<Y_EBAND_SITES && index>=0 && index<22);
   int16_t v=p[index]; y_eband_check(v==expected[index]);
   y_eband_site *s=&y_eband_counts[site];
   y_eband_check(s->function==NULL || strcmp(s->function,fn)==0);
   s->function=fn; s->total++; s->indices[index]++; return v;
}
