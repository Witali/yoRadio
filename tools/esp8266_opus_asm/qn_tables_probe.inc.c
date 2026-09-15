/* Host-only counts. Return the original values; no target code or timing claim. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
static struct {
 uint64_t logn[2], exp2[2], logn_index[21], exp2_index[8];
 uint64_t partition, partition_n2, search, search_n2;
} y_qn_counts;
static void y_qn_check(int ok){if(!ok){fputs("QN table observer assertion\n",stderr);abort();}}
static void y_qn_array(FILE *f,const uint64_t *v,int n){
 fputc('[',f);for(int i=0;i<n;i++)fprintf(f,"%s%" PRIu64,i?",":"",v[i]);fputc(']',f);
}
static void y_qn_save(void){
 const char *name=getenv("YORADIO_QN_COUNTS");y_qn_check(name!=NULL);
 FILE *f=fopen(name,"wb");y_qn_check(f!=NULL);
 fputs("{\"logn\":",f);y_qn_array(f,y_qn_counts.logn,2);
 fputs(",\"exp2\":",f);y_qn_array(f,y_qn_counts.exp2,2);
 fputs(",\"logn_index\":",f);y_qn_array(f,y_qn_counts.logn_index,21);
 fputs(",\"exp2_index\":",f);y_qn_array(f,y_qn_counts.exp2_index,8);
 fprintf(f,",\"partition\":%" PRIu64 ",\"partition_n2\":%" PRIu64 ",\"search\":%" PRIu64 ",\"search_n2\":%" PRIu64 "}\n",y_qn_counts.partition,y_qn_counts.partition_n2,y_qn_counts.search,y_qn_counts.search_n2);
 y_qn_check(fclose(f)==0);
}
__attribute__((constructor)) static void y_qn_init(void){y_qn_check(atexit(y_qn_save)==0);}
static int y_qn_logn(const CELTMode *m,int i,int stereo){
 y_qn_check(m->nbEBands==21&&i>=0&&i<21&&(stereo==0||stereo==1));
 y_qn_counts.logn[stereo]++;y_qn_counts.logn_index[i]++;
 return m->logN[i];
}
static int y_qn_exp2(const opus_int16 *table,int index,int stereo){
 y_qn_check(index>=0&&index<8&&(stereo==0||stereo==1));
 y_qn_counts.exp2[stereo]++;y_qn_counts.exp2_index[index]++;
 return table[index];
}
