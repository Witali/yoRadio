#include "native_vorbis_xiph_dsp_error.h"

int native_xiph_mdct_init(mdct_lookup *lookup,int n){
  int *bitrev;
  DATA_TYPE *T;

  memset(lookup,0,sizeof(*lookup));
  bitrev=_ogg_malloc(sizeof(*bitrev)*(n/4));
  if(!bitrev)return(-1);
  T=_ogg_malloc(sizeof(*T)*(n+n/4));
  if(!T){
    _ogg_free(bitrev);
    return(-1);
  }

  int i;
  int n2=n>>1;
  int log2n=lookup->log2n=rint(log((float)n)/log(2.f));
  lookup->n=n;
  lookup->trig=T;
  lookup->bitrev=bitrev;

/* trig lookups... */

  for(i=0;i<n/4;i++){
    T[i*2]=FLOAT_CONV(cos((M_PI/n)*(4*i)));
    T[i*2+1]=FLOAT_CONV(-sin((M_PI/n)*(4*i)));
    T[n2+i*2]=FLOAT_CONV(cos((M_PI/(2*n))*(2*i+1)));
    T[n2+i*2+1]=FLOAT_CONV(sin((M_PI/(2*n))*(2*i+1)));
  }
  for(i=0;i<n/8;i++){
    T[n+i*2]=FLOAT_CONV(cos((M_PI/n)*(4*i+2))*.5);
    T[n+i*2+1]=FLOAT_CONV(-sin((M_PI/n)*(4*i+2))*.5);
  }

  /* bitreverse lookup... */

  {
    int mask=(1<<(log2n-1))-1,i,j;
    int msb=1<<(log2n-2);
    for(i=0;i<n/8;i++){
      int acc=0;
      for(j=0;msb>>j;j++)
        if((msb>>j)&i)acc|=1<<j;
      bitrev[i*2]=((~acc)&mask)-1;
      bitrev[i*2+1]=acc;

    }
  }
  lookup->scale=FLOAT_CONV(4.f/n);
  return(0);
}

void mdct_init(mdct_lookup *lookup,int n){
  (void)native_xiph_mdct_init(lookup,n);
}
