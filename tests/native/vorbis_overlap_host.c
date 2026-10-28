// Stateful overlap capture with immediate failure snapshots of every borrow.
#include "native_vorbis_overlap.h"
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks,refusals,cases,cancellations,resets;
#define CHECK(x) do { ++checks; assert(x); } while (0)
typedef struct { unsigned char *raw,*data; size_t bytes; } buffer_t;
static buffer_t make(size_t bytes) {
    CHECK(bytes<=SIZE_MAX-32);buffer_t b={.raw=malloc(bytes+32),.bytes=bytes};CHECK(b.raw);
    b.data=b.raw+16;memset(b.raw,0xa5,bytes+32);return b;
}
static void guards(const buffer_t *b) {
    for(size_t i=0;i<16;++i){CHECK(b->raw[i]==0xa5);CHECK(b->data[b->bytes+i]==0xa5);}
}
static buffer_t copy(const buffer_t *b) {buffer_t c=make(b->bytes);memcpy(c.data,b->data,b->bytes);return c;}
static void unchanged(const buffer_t *b,const buffer_t *c) {
    guards(b);CHECK(b->bytes==c->bytes);CHECK(!memcmp(b->data,c->data,b->bytes));
}
static void destroy(buffer_t *b){guards(b);free(b->raw);memset(b,0,sizeof(*b));}
static void put32(FILE *f,uint32_t u){unsigned char b[4]={(unsigned char)u,(unsigned char)(u>>8),(unsigned char)(u>>16),(unsigned char)(u>>24)};CHECK(fwrite(b,1,4,f)==4);}
static void put64(FILE *f,uint64_t u){put32(f,(uint32_t)u);put32(f,(uint32_t)(u>>32));}
static uint64_t bits(double x){uint64_t u;memcpy(&u,&x,8);return u;}
static void values(FILE *f,const double *p,size_t n){for(size_t i=0;i<n;++i)put64(f,bits(p[i]));}
static buffer_t lookup[8],lookup_copy[8];
static native_vorbis_window_plan_t plans[8];
static unsigned char plan_copy[8][sizeof(native_vorbis_window_plan_t)];
static void check_plans(void){for(unsigned i=0;i<8;++i){unchanged(&lookup[i],&lookup_copy[i]);CHECK(!memcmp(&plans[i],plan_copy[i],sizeof(plans[i])));}}
static void prepare(FILE *f){
    put32(f,8);
    for(unsigned i=0;i<8;++i){uint32_t n=64U<<i;lookup[i]=make(n/2*8);
        CHECK(native_vorbis_window_prepare(n,(double *)lookup[i].data,n/2,&plans[i])==0);
        lookup_copy[i]=copy(&lookup[i]);memcpy(plan_copy[i],&plans[i],sizeof(plans[i]));
        put32(f,n);values(f,plans[i].rise,n/2);
    }
}
typedef struct {buffer_t input,history,previous,current;native_vorbis_overlap_t state;native_vorbis_overlap_terms_t result;uint32_t large;} context_t;

static void refused_push(context_t *c,native_vorbis_overlap_t *state,
    const native_vorbis_transform_block_t *source,size_t sc,double *previous,size_t pc,
    double *current,size_t cc,native_vorbis_overlap_terms_t *result,int wanted){
    buffer_t ib=copy(&c->input),hb=copy(&c->history),pb=copy(&c->previous),cb=copy(&c->current);
    unsigned char sb[sizeof(c->state)],rb[sizeof(c->result)],actual_state[sizeof(c->state)],actual_source[sizeof(*source)],
        small[sizeof(native_vorbis_window_plan_t)],large[sizeof(native_vorbis_window_plan_t)];
    memcpy(sb,&c->state,sizeof(sb));memcpy(rb,&c->result,sizeof(rb));
    if(state)memcpy(actual_state,state,sizeof(actual_state));
    if(source)memcpy(actual_source,source,sizeof(actual_source));
    const native_vorbis_window_plan_t *sp=state?state->short_plan:NULL,*lp=state?state->long_plan:NULL;
    if(sp)memcpy(small,sp,sizeof(small));
    if(lp)memcpy(large,lp,sizeof(large));
    CHECK(native_vorbis_overlap_push(state,source,sc,previous,pc,current,cc,result)==wanted);++refusals;
    CHECK(!memcmp(sb,&c->state,sizeof(sb)));CHECK(!memcmp(rb,&c->result,sizeof(rb)));
    if(state)CHECK(!memcmp(actual_state,state,sizeof(actual_state)));
    if(source)CHECK(!memcmp(actual_source,source,sizeof(actual_source)));
    if(sp)CHECK(!memcmp(small,sp,sizeof(small)));
    if(lp)CHECK(!memcmp(large,lp,sizeof(large)));
    unchanged(&c->input,&ib);unchanged(&c->history,&hb);unchanged(&c->previous,&pb);unchanged(&c->current,&cb);
    destroy(&cb);destroy(&pb);destroy(&hb);destroy(&ib);check_plans();
}
static void controls(context_t *c,native_vorbis_transform_block_t *source,uint32_t count){
    double *p=(double *)c->previous.data,*q=(double *)c->current.data;size_t n=source->count;
#define REF(S,I,IC,P,PC,Q,QC,R,E) refused_push(c,S,I,IC,P,PC,Q,QC,R,E)
    REF(NULL,source,n,p,count,q,count,&c->result,-1);
    REF(&c->state,NULL,n,p,count,q,count,&c->result,-1);
    REF(&c->state,source,n,p,count,q,count,NULL,-1);
    REF(&c->state,source,n-1,p,count,q,count,&c->result,-4);
    REF(&c->state,source,SIZE_MAX,p,count,q,count,&c->result,-2);
    REF(&c->state,source,n,p,SIZE_MAX,q,count,&c->result,-2);
    REF(&c->state,source,n,p,count,q,SIZE_MAX,&c->result,-2);
    if(count){
        REF(&c->state,source,n,NULL,count,q,count,&c->result,-1);
        REF(&c->state,source,n,p,count,NULL,count,&c->result,-1);
        REF(&c->state,source,n,p,count-1,q,count,&c->result,-4);
        REF(&c->state,source,n,p,count,q,count-1,&c->result,-4);
    }
    native_vorbis_transform_block_t bad=*source;bad.count=63;
    REF(&c->state,&bad,n,p,count,q,count,&c->result,-1);
    bad=*source;bad.samples=NULL;REF(&c->state,&bad,n,p,count,q,count,&c->result,-1);
    native_vorbis_overlap_t bs=c->state;bs.previous_size=63;
    REF(&bs,source,n,p,count,q,count,&c->result,-1);
    bs=c->state;bs.short_plan=NULL;REF(&bs,source,n,p,count,q,count,&c->result,-1);
    bs=c->state;bs.long_plan=NULL;REF(&bs,source,n,p,count,q,count,&c->result,-1);
    bs=c->state;bs.history=NULL;REF(&bs,source,n,p,count,q,count,&c->result,-1);
    bs=c->state;bs.history_capacity=SIZE_MAX;REF(&bs,source,n,p,count,q,count,&c->result,-2);
    bs=c->state;bs.history_capacity=c->large/2-1;REF(&bs,source,n,p,count,q,count,&c->result,-4);
    native_vorbis_window_plan_t bp=*c->state.short_plan;bp.blocksize=63;
    bs=c->state;bs.short_plan=&bp;REF(&bs,source,n,p,count,q,count,&c->result,-1);
    bp=*c->state.long_plan;bp.rise=NULL;bs=c->state;bs.long_plan=&bp;
    REF(&bs,source,n,p,count,q,count,&c->result,-1);
    const uint64_t invalid[]={UINT64_C(0x7ff8000000000001),UINT64_C(0x7ff0000000000001),UINT64_C(0x7ff0000000000000),UINT64_C(0xfff0000000000000)};
    double *data=(double *)c->input.data;unsigned char saved[8];memcpy(saved,data+n-1,8);
    for(unsigned i=0;i<4;++i){memcpy(data+n-1,&invalid[i],8);REF(&c->state,source,n,p,count,q,count,&c->result,-2);}
    memcpy(data+n-1,saved,8);
    if(c->state.previous_size){
        double *tail=(double *)c->history.data+c->state.previous_size/2-1;memcpy(saved,tail,8);
        for(unsigned i=0;i<4;++i){memcpy(tail,&invalid[i],8);REF(&c->state,source,n,p,count,q,count,&c->result,-2);}
        memcpy(tail,saved,8);
    }
#undef REF
}
static void ancillary(context_t *c,const native_vorbis_window_plan_t *s,const native_vorbis_window_plan_t *l){
    native_vorbis_overlap_t candidate;memset(&candidate,0xa5,sizeof(candidate));
    unsigned char before[sizeof(candidate)];memcpy(before,&candidate,sizeof(before));buffer_t hist=copy(&c->history);
#define INIT(S,L,H,C,D,E) do{CHECK(native_vorbis_overlap_init(S,L,H,C,D)==(E));++refusals;CHECK(!memcmp(before,&candidate,sizeof(before)));unchanged(&c->history,&hist);}while(0)
    INIT(NULL,l,(double *)c->history.data,c->large/2,&candidate,-1);
    INIT(s,NULL,(double *)c->history.data,c->large/2,&candidate,-1);
    INIT(s,l,NULL,c->large/2,&candidate,-1);
    INIT(s,l,(double *)c->history.data,c->large/2-1,&candidate,-4);
    INIT(s,l,(double *)c->history.data,SIZE_MAX,&candidate,-2);
    INIT(s,l,(double *)c->history.data,c->large/2,NULL,-1);
    native_vorbis_window_plan_t bad=*s;bad.blocksize=63;INIT(&bad,l,(double *)c->history.data,c->large/2,&candidate,-1);
    bad=*l;bad.rise=NULL;INIT(s,&bad,(double *)c->history.data,c->large/2,&candidate,-1);
    if(s->blocksize<l->blocksize)INIT(l,s,(double *)c->history.data,c->large/2,&candidate,-1);
#undef INIT
    destroy(&hist);native_vorbis_overlap_requirements_t req;memset(&req,0xa5,sizeof(req));
    unsigned char rb[sizeof(req)];memcpy(rb,&req,sizeof(rb));unsigned char state_before[sizeof(c->state)];memcpy(state_before,&c->state,sizeof(state_before));
#define MEASURE(S,N,R,E) do{CHECK(native_vorbis_overlap_measure(S,N,R)==(E));++refusals;CHECK(!memcmp(rb,&req,sizeof(rb)));CHECK(!memcmp(state_before,&c->state,sizeof(state_before)));}while(0)
    MEASURE(NULL,s->blocksize,&req,-1);MEASURE(&c->state,s->blocksize,NULL,-1);MEASURE(&c->state,63,&req,-1);
    native_vorbis_overlap_t bs=c->state;bs.previous_size=63;MEASURE(&bs,s->blocksize,&req,-1);
#undef MEASURE
    CHECK(native_vorbis_overlap_reset(NULL)==-1);++refusals;
    memcpy(before,&bs,sizeof(bs));CHECK(native_vorbis_overlap_reset(&bs)==-1);++refusals;CHECK(!memcmp(before,&bs,sizeof(bs)));
    check_plans();
}
static double ordinary(uint32_t step,uint32_t i){return ((int)((i*37+step*19)%257)-128)/128.0;}
static double sample(unsigned pattern,uint32_t step,uint32_t i,uint32_t n,const native_vorbis_window_plan_t *plan){
    if(pattern==1){if(step==2&&i>=n/2)return plan->rise[i-n/2];if(step==3&&i<n/2)return -plan->rise[n/2-i-1];return ordinary(step,i);}
    if(pattern==2)return step&1?0.0:ordinary(step,i);
    uint32_t v=i+step*17;
    switch(v%12){case 0:return DBL_MAX;case 1:return -DBL_MAX;case 2:return DBL_TRUE_MIN;case 3:return -DBL_TRUE_MIN;case 4:return 0.0;case 5:return -0.0;case 6:return 0x1p-1000;case 7:return -0x1p800;case 8:return 1.0;case 9:return -1.0;default:return ((int)(v%1021)-510)*.03125;}
}
static void run_sequence(FILE *f,unsigned small,unsigned large,unsigned pattern){
    uint32_t s=64U<<small,l=64U<<large;
    context_t c={.input=make((l+4)*8),.history=make((l/2+4)*8),.previous=make((l/2+4)*8),.current=make((l/2+4)*8),.large=l};
    memset(&c.result,0xa5,sizeof(c.result));
    CHECK(native_vorbis_overlap_init(&plans[small],&plans[large],(double *)c.history.data,l/2,&c.state)==0);
    if(!pattern)ancillary(&c,&plans[small],&plans[large]);
    const unsigned sequence[]={0,0,1,1,0,1,0,0};
    const int64_t exponents[]={INT64_MIN,INT64_MAX,INT64_MAX,INT64_MAX,1074,1074,-788,512};
    for(unsigned step=0;step<8;++step){
        if(step==4){
            for(uint32_t i=0;i<l/2;++i)((double *)c.history.data)[i]=NAN;
            buffer_t history=copy(&c.history);const native_vorbis_window_plan_t *sp=c.state.short_plan,*lp=c.state.long_plan;
            CHECK(native_vorbis_overlap_reset(&c.state)==0);++resets;unchanged(&c.history,&history);destroy(&history);
            CHECK(c.state.previous_size==0&&c.state.previous_exponent==0&&c.state.short_plan==sp&&c.state.long_plan==lp&&c.state.history==(double *)c.history.data&&c.state.history_capacity==l/2);
        }
        uint32_t n=sequence[step]?l:s;
        double *data=(double *)c.input.data;const native_vorbis_window_plan_t *plan=&plans[sequence[step]?large:small];
        memset(c.input.data,0xa5,c.input.bytes);for(uint32_t i=0;i<n;++i)data[i]=sample(pattern,step,i,n,plan);
        memset(c.previous.data,0xa5,c.previous.bytes);memset(c.current.data,0xa5,c.current.bytes);
        native_vorbis_transform_block_t source={.count=n,.exponent=exponents[step],.samples=data};
        native_vorbis_overlap_requirements_t req;CHECK(native_vorbis_overlap_measure(&c.state,n,&req)==0);
        uint32_t a=c.state.previous_size;int64_t old_exponent=c.state.previous_exponent;
        CHECK(req.count==(a?(a+n)/4:0)&&req.history_count==n/2);
        if(!pattern)controls(&c,&source,req.count);
        buffer_t input=copy(&c.input),history=copy(&c.history),previous=copy(&c.previous),current=copy(&c.current);
        unsigned char source_before[sizeof(source)];memcpy(source_before,&source,sizeof(source));
        double *p=req.count?(double *)c.previous.data:NULL,*q=req.count?(double *)c.current.data:NULL;
        CHECK(native_vorbis_overlap_push(&c.state,&source,n,p,req.count,q,req.count,&c.result)==0);
        CHECK(c.result.previous.count==req.count&&c.result.current.count==req.count&&c.result.previous.samples==p&&c.result.current.samples==q);
        CHECK(c.result.previous.exponent==old_exponent&&c.result.current.exponent==source.exponent);
        CHECK(c.state.previous_size==n&&c.state.previous_exponent==source.exponent);
        unchanged(&c.input,&input);CHECK(!memcmp(source_before,&source,sizeof(source)));
        CHECK(!memcmp(c.history.data,data+n/2,n/2*8));
        CHECK(!memcmp(c.history.data+n/2*8,history.data+n/2*8,c.history.bytes-n/2*8));
        CHECK(!memcmp(c.previous.data+req.count*8,previous.data+req.count*8,c.previous.bytes-req.count*8));
        CHECK(!memcmp(c.current.data+req.count*8,current.data+req.count*8,c.current.bytes-req.count*8));
        guards(&c.history);guards(&c.previous);guards(&c.current);check_plans();
        if(pattern==1&&step==3){for(uint32_t i=0;i<req.count;++i){CHECK(bits(p[i])==(bits(q[i])^UINT64_C(0x8000000000000000)));++cancellations;}}
        put32(f,s);put32(f,l);put32(f,pattern);put32(f,step);put32(f,a);put32(f,n);put32(f,req.count);
        put64(f,(uint64_t)c.result.previous.exponent);put64(f,(uint64_t)c.result.current.exponent);
        values(f,data,n);values(f,p,req.count);values(f,q,req.count);values(f,(double *)c.history.data,n/2);++cases;
        destroy(&current);destroy(&previous);destroy(&history);destroy(&input);
    }
    destroy(&c.current);destroy(&c.previous);destroy(&c.history);destroy(&c.input);
}
int main(int argc,char **argv){
    CHECK(argc==2);FILE *f=fopen(argv[1],"wb");CHECK(f);CHECK(fwrite("VOVERL01",1,8,f)==8);prepare(f);put32(f,864);
    for(unsigned s=0;s<8;++s)for(unsigned l=s;l<8;++l)for(unsigned p=0;p<3;++p)run_sequence(f,s,l,p);
    for(unsigned i=0;i<8;++i){destroy(&lookup_copy[i]);destroy(&lookup[i]);}
    CHECK(fclose(f)==0);printf("OVERLAP_CAPTURE cases=%" PRIu64 " refusals=%" PRIu64 " checks=%" PRIu64 " cancellations=%" PRIu64 " resets=%" PRIu64 "\n",cases,refusals,checks,cancellations,resets);return 0;
}
