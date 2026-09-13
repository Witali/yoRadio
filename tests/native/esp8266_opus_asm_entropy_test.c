#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "entdec.h"
void ec_dec_update_reference(ec_dec *,unsigned,unsigned,unsigned);
static uint32_t seed=0x31415926;
static uint32_t random32(void){seed=seed*1664525u+1013904223u;return seed;}
int main(void){
 unsigned char bytes[256],snapshot[256];unsigned no_refill=0,refill=0,padded=0;
 for(unsigned k=0;k<100000;k++){
  for(unsigned i=0;i<sizeof bytes;i++)bytes[i]=(unsigned char)random32();
  memcpy(snapshot,bytes,sizeof bytes);
  ec_dec a={0};a.buf=bytes;a.storage=k%257;a.offs=a.storage?random32()%(a.storage+1):0;
  a.rng=(random32()&0x7fffffffu)|0x800001u;a.val=random32()%a.rng;
  a.rem=random32()&255;a.nbits_total=random32()%100000;
  a.end_offs=17;a.end_window=0x98765432;a.nend_bits=5;a.error=123;
  unsigned ft=k%2?2+random32()%65534:2+random32()%256;
  unsigned fl=ec_decode(&a,ft),fh=fl+1;
  if(k%3==0)fl=0; /* Includes the special rng-s interval update. */
  ec_dec b=a;int before=a.nbits_total;unsigned offs=a.offs;
  ec_dec_update_reference(&a,fl,fh,ft);ec_dec_update(&b,fl,fh,ft);
  assert(memcmp(&a,&b,sizeof a)==0);assert(memcmp(bytes,snapshot,sizeof bytes)==0);
  if(a.nbits_total==before)no_refill++;else refill++;
  if((unsigned)(a.nbits_total-before)/8>a.offs-offs)padded++;
 }
 assert(no_refill&&refill&&padded);
 printf("{\"passed\":true,\"cases\":100000,\"no_refill\":%u,\"refill\":%u,\"zero_padding\":%u}\n",no_refill,refill,padded);
}
