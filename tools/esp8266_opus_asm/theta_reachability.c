/* Host-only proof harness: use the actual vendored function and mode tables.
 * Including bands.c makes its private compute_qn/compute_theta visible here.
 * This is not linked into any firmware and is not a speed benchmark. */
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>
#include "../../esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/bands.c"

#ifdef CUSTOM_MODES
#error This proof covers the standard Opus mode, not custom CELT modes.
#endif

static void require(int ok, const char *message)
{
   if (!ok) { fprintf(stderr, "%s\n", message); exit(1); }
}

int main(void)
{
   int error, lm, i, groups=0, nonsplit=0, min_qb=INT_MAX, min_qn=INT_MAX;
   unsigned long checked=0;
   const CELTMode *m=opus_custom_mode_create(48000,960,&error);
   require(m && error==OPUS_OK, "standard mode unavailable");
   require(BITRES==3 && QTHETA_OFFSET==4, "proof constants changed");
   require(m->nbEBands==21 && m->maxLM==3, "mode dimensions changed");
   /* N and LM halve/decrement together on each recursive call. TF changes
    * change B/N_B, not N or LM. Enumerating LM=0..3 thus includes recursion.
    * LM=-1 cannot split and N<=2 cannot split. */
   for (lm=0;lm<=m->maxLM;lm++) for(i=0;i<m->nbEBands;i++) {
      int n=(m->eBands[i+1]-m->eBands[i])<<lm;
      int b, previous=0;
      const unsigned char *cache;
      int first, half, pulse_cap, offset, n2, qb;
      if(n<=2) { nonsplit++; continue; }
      cache=m->cache.bits+m->cache.index[(lm+1)*m->nbEBands+i];
      first=cache[cache[0]]+13; /* strict > cache[last]+12 */
      half=n>>1;
      pulse_cap=m->logN[i]+(lm-1)*(1<<BITRES);
      offset=(pulse_cap>>1)-QTHETA_OFFSET;
      n2=2*half-1;
      qb=IMIN(8<<BITRES, IMIN(first-pulse_cap-(4<<BITRES),
                            celt_sudiv(first+n2*offset,n2)));
      require(qb>=4,"qn=1 reachable at split threshold");
      if(qb<min_qb) min_qb=qb;
      groups++;
      /* Superset of budgets from the 16383 cap in quant_all_bands. Also test
       * zero/threshold sides of the guard so the proof cannot just skip them. */
      for(b=0;b<=16383;b++) {
         int qn=compute_qn(half,b,offset,pulse_cap,0);
         if(b<first) continue;
         require(qn!=1,"reachable mono qn=1");
         require(qn>=previous,"qn monotonicity violated");
         previous=qn;
         if(qn<min_qn) min_qn=qn;
         checked++;
      }
      printf("{\"lm\":%d,\"band\":%d,\"N\":%d,\"first_budget\":%d,\"minimum_qb\":%d}\n",
             lm,i,n,first,qb);
   }
   /* Positive control: qn=1 exists in the generic helper. With stereo=0
    * its two tell calls cancel, but this budget cannot pass the caller's
    * split guard. Do not label the entire qn=1 branch dead. */
   {
      unsigned char bytes[64]={0};
      ec_dec ec, saved;
      struct band_ctx ctx;
      struct split_ctx split;
      celt_norm x[2]={0},y[2]={0};
      int b=0,fill=3;
      memset(&ctx,0,sizeof(ctx));
      ctx.m=m;ctx.i=8;ctx.ec=&ec;ctx.remaining_bits=512;
      ec_dec_init(&ec,bytes,sizeof(bytes));saved=ec;
      require(compute_qn(2,0,0,8,0)==1,"positive control is not qn=1");
      compute_theta(&ctx,&split,x,y,2,&b,1,1,0,0,&fill);
      require(split.qalloc==0 && b==0 && !memcmp(&ec,&saved,sizeof(ec)),
              "no-entropy identity failed");
      /* Intensity stereo forces qn=1 on valid configurations and may consume
       * an inversion bit. This path is explicitly excluded from the proof. */
      ec_dec_init(&ec,bytes,sizeof(bytes));saved=ec;b=32;fill=3;
      compute_theta(&ctx,&split,x,y,2,&b,1,1,0,1,&fill);
      require(split.qalloc>0 && b<32 && memcmp(&ec,&saved,sizeof(ec)),
              "stereo qn=1 entropy positive control failed");
   }
   require(groups==64 && nonsplit==20,"unexpected state space");
   printf("{\"passed\":true,\"groups\":%d,\"nonsplit_groups\":%d,\"budget_cases\":%lu,"
          "\"minimum_qb\":%d,\"minimum_qn\":%d,\"generic_and_stereo_controls\":true}\n",
          groups,nonsplit,checked,min_qb,min_qn);
   return 0;
}
