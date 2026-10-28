// Actual complete raw-packet public pipeline capture, without private decoders.
#include "vorbis_synthesis_pipeline.h"
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks,packets,pcm_bytes,failures;
#define CHECK(x) do{++checks;assert(x);}while(0)
static uint32_t get32(FILE *f){unsigned char b[4];CHECK(fread(b,1,4,f)==4);return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;}
static uint64_t get64(FILE *f){uint64_t low=get32(f);return low|(uint64_t)get32(f)<<32;}
static int64_t signed64(uint64_t word){int64_t s;memcpy(&s,&word,8);return s;}
static void put32(FILE *f,uint32_t u){unsigned char b[4]={(unsigned char)u,(unsigned char)(u>>8),(unsigned char)(u>>16),(unsigned char)(u>>24)};CHECK(fwrite(b,1,4,f)==4);}
static void put64(FILE *f,uint64_t u){put32(f,(uint32_t)u);put32(f,(uint32_t)(u>>32));}
static void put16(FILE *f,int16_t s){uint16_t u;memcpy(&u,&s,2);unsigned char b[2]={(unsigned char)u,(unsigned char)(u>>8)};CHECK(fwrite(b,1,2,f)==2);}
typedef struct {unsigned char *raw,*data;size_t bytes;} buffer_t;
static buffer_t buffer(size_t bytes){CHECK(bytes<=SIZE_MAX-32);buffer_t b={.raw=malloc(bytes+32),.bytes=bytes};CHECK(b.raw);b.data=b.raw+16;memset(b.raw,0xa5,bytes+32);return b;}
static void guard(const buffer_t *b){for(unsigned i=0;i<16;++i){CHECK(b->raw[i]==0xa5);CHECK(b->data[b->bytes+i]==0xa5);}}
static void drop(buffer_t *b){guard(b);free(b->raw);}
typedef struct {FILE *output;uint32_t next_packet;uint64_t remaining;char error_stage[64];int error_status;} context_t;
static bool packet_callback(void *opaque,const vorbis_synthesis_pipeline_packet_t *p){
    context_t *c=opaque;CHECK(p->packet==c->next_packet&&c->remaining==0);++c->next_packet;++packets;
    put32(c->output,p->packet);put32(c->output,p->blocksize);put32(c->output,p->channels);
    put32(c->output,p->floor0_channels);put32(c->output,p->floor1_channels);put64(c->output,p->consumed_bits);put32(c->output,p->end_of_packet);
    const native_vorbis_timing_result_t *t=&p->synthesis.timing;
    put32(c->output,t->available);put32(c->output,t->discard_start);put32(c->output,t->discard_end);put32(c->output,t->count);
    put32(c->output,(uint32_t)t->position_kind);put64(c->output,(uint64_t)t->end_position);put64(c->output,p->synthesis.pcm_samples);
    CHECK(p->synthesis.channels==p->channels&&p->synthesis.pcm_samples==(uint64_t)t->count*p->channels);
    c->remaining=p->synthesis.pcm_samples;return true;
}
static bool pcm_callback(void *opaque,uint32_t packet,const int16_t *samples,size_t count){
    context_t *c=opaque;CHECK(packet+1==c->next_packet&&count&&count<=128&&count<=c->remaining);
    for(size_t i=0;i<count;++i)put16(c->output,samples[i]);
    c->remaining-=count;pcm_bytes+=count*2;return true;
}
static void error_callback(void *opaque,uint32_t packet,const char *stage,int status,uint32_t channel,uint32_t route){
    context_t *c=opaque;(void)packet;(void)channel;(void)route;
    size_t n=strlen(stage);CHECK(n<sizeof(c->error_stage));memcpy(c->error_stage,stage,n+1);c->error_status=status;
}
static void run_case(FILE *input,FILE *output,uint32_t ordinal){
    uint32_t fields[9];for(unsigned i=0;i<9;++i)fields[i]=get32(input);
    CHECK(fields[0]==ordinal&&fields[5]>0&&fields[5]<=10000);
    buffer_t id=buffer(fields[6]),setup=buffer(fields[7]),audio=buffer(fields[8]);
    CHECK(fread(id.data,1,id.bytes,input)==id.bytes&&fread(setup.data,1,setup.bytes,input)==setup.bytes&&fread(audio.data,1,audio.bytes,input)==audio.bytes);
    buffer_t offsets=buffer(((size_t)fields[5]+1)*4),granules=buffer((size_t)fields[5]*8);
    for(uint32_t i=0;i<=fields[5];++i)((uint32_t *)offsets.data)[i]=get32(input);
    for(uint32_t i=0;i<fields[5];++i)((int64_t *)granules.data)[i]=signed64(get64(input));
    native_vorbis_identification_t identification;
    CHECK(native_vorbis_identification_parse(id.data,id.bytes,(uint64_t)id.bytes*8,&identification)==0);
    CHECK(identification.sample_rate==fields[1]&&identification.channels==fields[2]&&identification.blocksize_0==fields[3]&&identification.blocksize_1==fields[4]);
    const buffer_t *borrows[]={&id,&setup,&audio,&offsets,&granules};buffer_t copies[5];
    for(unsigned i=0;i<5;++i){copies[i]=buffer(borrows[i]->bytes);memcpy(copies[i].data,borrows[i]->data,borrows[i]->bytes);}
    for(unsigned i=0;i<6;++i)put32(output,fields[i]);
    long length_at=ftell(output);CHECK(length_at>=0);put64(output,0);
    long begin=ftell(output);CHECK(begin>=0);context_t context={.output=output};
    vorbis_synthesis_pipeline_callbacks_t callbacks={.context=&context,.packet=packet_callback,.pcm=pcm_callback,.error=error_callback};
    vorbis_synthesis_pipeline_case_t stream={.identification=id.data,.setup=setup.data,.audio=audio.data,
        .identification_bytes=id.bytes,.setup_bytes=setup.bytes,.audio_bytes=audio.bytes,
        .packet_offsets=(uint32_t *)offsets.data,.granules=(int64_t *)granules.data,.packet_count=fields[5]};
    vorbis_synthesis_pipeline_result_t result;int status=vorbis_synthesis_pipeline_run(&stream,&callbacks,&result);
    CHECK(!context.remaining&&status==result.status&&result.live_allocations==0&&result.live_payload_bytes==0&&result.allocations==result.releases);
    CHECK(context.next_packet==result.packets);long end=ftell(output);CHECK(end>=begin);
    CHECK(fseek(output,length_at,SEEK_SET)==0);put64(output,(uint64_t)(end-begin));CHECK(fseek(output,end,SEEK_SET)==0);
    put32(output,(uint32_t)status);put32(output,result.failed_packet);put32(output,result.failed_channel);put32(output,result.failed_route);
    const uint64_t totals[]={result.packets,result.frames,result.pcm_samples,result.floor0_channels,result.floor1_channels,
        result.allocations,result.releases,result.live_allocations,result.live_payload_bytes,result.peak_allocations,result.peak_payload_bytes};
    for(unsigned i=0;i<11;++i)put64(output,totals[i]);
    size_t stage_length=strlen(context.error_stage);put32(output,(uint32_t)stage_length);CHECK(fwrite(context.error_stage,1,stage_length,output)==stage_length);
    if(status)++failures;
    for(unsigned i=0;i<5;++i){guard(borrows[i]);CHECK(!memcmp(borrows[i]->data,copies[i].data,borrows[i]->bytes));drop(&copies[i]);}
    drop(&granules);drop(&offsets);drop(&audio);drop(&setup);drop(&id);
}
// Additional host-only lifecycle tests; the MCU uses only the common helper.
static uint64_t owner_refusals,owner_values,owner_pushes;
static buffer_t lookups[8],lookup_copies[8];
static native_vorbis_window_plan_t owner_plans[8];
typedef struct {
    uint32_t s,l,channels;
    native_vorbis_synthesis_t state;
    native_vorbis_synthesis_requirements_t q;
    buffer_t history,exponents,source,blocks,capacities,pcm;
} owner_t;
static void state_put(FILE *f,const native_vorbis_timing_t *s){
    put32(f,s->short_size);put32(f,s->long_size);put32(f,s->previous_size);put32(f,s->position_known);put32(f,s->end_seen);
    put64(f,s->bounded_sample_count);put64(f,s->bounded_prediction);
}
static void timing_put(FILE *f,const native_vorbis_timing_result_t *t){
    put32(f,t->available);put32(f,t->discard_start);put32(f,t->discard_end);put32(f,t->count);put32(f,(uint32_t)t->position_kind);put64(f,(uint64_t)t->end_position);
}
static void raw_words(FILE *f,const buffer_t *b){
    CHECK(!(b->bytes%8));for(size_t i=0;i<b->bytes;i+=8){uint64_t word;memcpy(&word,b->data+i,8);put64(f,word);}
}
static unsigned plan_index(uint32_t n){unsigned i=0;while(i<8&&(64U<<i)!=n)++i;CHECK(i<8);return i;}
static void owner_open(owner_t *c,uint32_t s,uint32_t l,uint32_t channels){
    memset(c,0,sizeof(*c));c->s=s;c->l=l;c->channels=channels;
    CHECK(native_vorbis_synthesis_measure(s,l,channels,&c->q)==0);
    c->history=buffer(((size_t)c->q.history_samples+2)*8);c->exponents=buffer(((size_t)channels+2)*8);
    c->source=buffer((size_t)channels*l*8);c->blocks=buffer((size_t)channels*sizeof(native_vorbis_transform_block_t));
    c->capacities=buffer((size_t)channels*sizeof(size_t));c->pcm=buffer(((size_t)c->q.max_pcm_samples+4)*2);
    uint64_t nan=UINT64_C(0x7ff8000000000042);
    for(size_t i=0;i<c->history.bytes;i+=8)memcpy(c->history.data+i,&nan,8);
    memset(c->source.data,0,c->source.bytes);memset(c->blocks.data,0,c->blocks.bytes);
    buffer_t h=buffer(c->history.bytes),e=buffer(c->exponents.bytes);memcpy(h.data,c->history.data,h.bytes);memcpy(e.data,c->exponents.data,e.bytes);
    if(channels==255){
        native_vorbis_synthesis_requirements_t q;memset(&q,0xa5,sizeof(q));unsigned char qb[sizeof(q)];memcpy(qb,&q,sizeof(qb));
        const uint32_t invalid[][3]={{0,128,1},{64,63,1},{128,64,1},{64,128,0},{64,128,256}};
        for(unsigned i=0;i<5;++i){CHECK(native_vorbis_synthesis_measure(invalid[i][0],invalid[i][1],invalid[i][2],&q)==-1);++owner_refusals;CHECK(!memcmp(qb,&q,sizeof(qb)));}
        CHECK(native_vorbis_synthesis_measure(s,l,channels,NULL)==-1);++owner_refusals;
        native_vorbis_synthesis_t rejected;memset(&rejected,0xa5,sizeof(rejected));unsigned char before[sizeof(rejected)];memcpy(before,&rejected,sizeof(before));
#define INIT(S,L,H,HC,E,EC,R,W) do{CHECK(native_vorbis_synthesis_init(S,L,channels,H,HC,E,EC,R)==W);++owner_refusals;CHECK(!memcmp(before,&rejected,sizeof(before))&&!memcmp(h.data,c->history.data,h.bytes)&&!memcmp(e.data,c->exponents.data,e.bytes));}while(0)
        const native_vorbis_window_plan_t *sp=&owner_plans[plan_index(s)],*lp=&owner_plans[plan_index(l)];
        INIT(NULL,lp,(double *)c->history.data,(size_t)c->q.history_samples+2,(int64_t *)c->exponents.data,channels+2,&rejected,-1);
        INIT(sp,NULL,(double *)c->history.data,(size_t)c->q.history_samples+2,(int64_t *)c->exponents.data,channels+2,&rejected,-1);
        INIT(sp,lp,(double *)c->history.data,SIZE_MAX,(int64_t *)c->exponents.data,channels+2,&rejected,-2);
        INIT(sp,lp,(double *)c->history.data,(size_t)c->q.history_samples-1,(int64_t *)c->exponents.data,channels+2,&rejected,-4);
        INIT(sp,lp,(double *)c->history.data,(size_t)c->q.history_samples+2,(int64_t *)c->exponents.data,channels-1,&rejected,-4);
        INIT(sp,lp,NULL,(size_t)c->q.history_samples+2,(int64_t *)c->exponents.data,channels+2,&rejected,-1);
        INIT(sp,lp,(double *)c->history.data,(size_t)c->q.history_samples+2,NULL,channels+2,&rejected,-1);
        INIT(sp,lp,(double *)c->history.data,(size_t)c->q.history_samples+2,(int64_t *)c->exponents.data,channels+2,NULL,-1);
#undef INIT
    }
    CHECK(native_vorbis_synthesis_init(&owner_plans[plan_index(s)],&owner_plans[plan_index(l)],channels,
        (double *)c->history.data,(size_t)c->q.history_samples+2,(int64_t *)c->exponents.data,(size_t)channels+2,&c->state)==0);
    CHECK(!memcmp(h.data,c->history.data,h.bytes)&&!memcmp(e.data,c->exponents.data,e.bytes));drop(&e);drop(&h);
}
static void owner_close(owner_t *c){drop(&c->pcm);drop(&c->capacities);drop(&c->blocks);drop(&c->source);drop(&c->exponents);drop(&c->history);}
static void source_blocks(owner_t *c,uint32_t n,int64_t exponent){
    native_vorbis_transform_block_t *blocks=(void *)c->blocks.data;size_t *caps=(void *)c->capacities.data;
    for(uint32_t ch=0;ch<c->channels;++ch){blocks[ch]=(native_vorbis_transform_block_t){.count=n,.exponent=exponent,.samples=(double *)c->source.data+(size_t)ch*c->l};caps[ch]=n;}
}
static native_vorbis_synthesis_result_t owner_push(owner_t *c,const native_vorbis_timing_event_t *event){
    buffer_t h=buffer(c->history.bytes),e=buffer(c->exponents.bytes),p=buffer(c->pcm.bytes),s=buffer(c->source.bytes),b=buffer(c->blocks.bytes),caps=buffer(c->capacities.bytes);
    memcpy(h.data,c->history.data,h.bytes);memcpy(e.data,c->exponents.data,e.bytes);memcpy(p.data,c->pcm.data,p.bytes);
    memcpy(s.data,c->source.data,s.bytes);memcpy(b.data,c->blocks.data,b.bytes);memcpy(caps.data,c->capacities.data,caps.bytes);
    native_vorbis_synthesis_result_t result;unsigned char ev[sizeof(*event)];memcpy(ev,event,sizeof(ev));
    CHECK(native_vorbis_synthesis_push(&c->state,event,(void *)c->blocks.data,(void *)c->capacities.data,c->channels,
        (int16_t *)c->pcm.data,(size_t)c->q.max_pcm_samples,&result)==0);++owner_pushes;owner_values+=result.pcm_samples;
    CHECK(result.channels==c->channels&&result.pcm_samples==(uint64_t)result.timing.count*c->channels);
    CHECK(!memcmp(ev,event,sizeof(ev))&&!memcmp(s.data,c->source.data,s.bytes)&&!memcmp(b.data,c->blocks.data,b.bytes)&&!memcmp(caps.data,c->capacities.data,caps.bytes));
    CHECK(!memcmp(c->pcm.data+(size_t)result.pcm_samples*2,p.data+(size_t)result.pcm_samples*2,p.bytes-(size_t)result.pcm_samples*2));
    uint32_t half=event->blocksize/2,stride=c->l/2;native_vorbis_transform_block_t *blocks=(void *)c->blocks.data;
    for(uint32_t ch=0;ch<c->channels;++ch){
        CHECK(!memcmp((double *)c->history.data+(size_t)ch*stride,blocks[ch].samples+half,(size_t)half*8));
        CHECK(!memcmp(c->history.data+((size_t)ch*stride+half)*8,h.data+((size_t)ch*stride+half)*8,(size_t)(stride-half)*8));
        CHECK(((int64_t *)c->exponents.data)[ch]==blocks[ch].exponent);
    }
    CHECK(!memcmp(c->history.data+(size_t)c->q.history_samples*8,h.data+(size_t)c->q.history_samples*8,16));
    CHECK(!memcmp(c->exponents.data+(size_t)c->channels*8,e.data+(size_t)c->channels*8,16));
    guard(&c->history);guard(&c->exponents);guard(&c->source);guard(&c->blocks);guard(&c->capacities);guard(&c->pcm);
    drop(&caps);drop(&b);drop(&s);drop(&p);drop(&e);drop(&h);return result;
}
static void refusal(owner_t *c,native_vorbis_synthesis_t *state,const native_vorbis_timing_event_t *event,
    const native_vorbis_transform_block_t *blocks,const size_t *caps,size_t bc,int16_t *output,size_t capacity,bool null_result,int wanted){
    const buffer_t *all[]={&c->history,&c->exponents,&c->source,&c->blocks,&c->capacities,&c->pcm};buffer_t saved[6];
    for(unsigned i=0;i<6;++i){saved[i]=buffer(all[i]->bytes);memcpy(saved[i].data,all[i]->data,all[i]->bytes);}
    buffer_t tables[8];for(unsigned i=0;i<8;++i){tables[i]=buffer(lookups[i].bytes);memcpy(tables[i].data,lookups[i].data,tables[i].bytes);}
    native_vorbis_synthesis_result_t result;memset(&result,0xa5,sizeof(result));unsigned char rb[sizeof(result)],sb[sizeof(c->state)],eb[sizeof(*event)];
    memcpy(rb,&result,sizeof(rb));
    if(state)memcpy(sb,state,sizeof(sb));
    if(event)memcpy(eb,event,sizeof(eb));
    CHECK(native_vorbis_synthesis_push(state,event,blocks,caps,bc,output,capacity,null_result?NULL:&result)==wanted);++owner_refusals;
    CHECK(!memcmp(rb,&result,sizeof(rb)));
    if(state)CHECK(!memcmp(sb,state,sizeof(sb)));
    if(event)CHECK(!memcmp(eb,event,sizeof(eb)));
    for(unsigned i=0;i<6;++i){guard(all[i]);CHECK(!memcmp(saved[i].data,all[i]->data,all[i]->bytes));drop(&saved[i]);}
    for(unsigned i=0;i<8;++i){CHECK(!memcmp(tables[i].data,lookups[i].data,tables[i].bytes));drop(&tables[i]);}
}
static void focused_controls(owner_t *c,native_vorbis_timing_event_t *event){
    native_vorbis_transform_block_t *blocks=(void *)c->blocks.data;size_t *caps=(void *)c->capacities.data;
    int16_t *out=(void *)c->pcm.data;size_t capacity=(size_t)c->q.max_pcm_samples;
#define REF(S,E,B,C,BC,O,OC,R,W) refusal(c,S,E,B,C,BC,O,OC,R,W)
    REF(NULL,event,blocks,caps,c->channels,out,capacity,false,-1);REF(&c->state,NULL,blocks,caps,c->channels,out,capacity,false,-1);
    REF(&c->state,event,NULL,caps,c->channels,out,capacity,false,-1);REF(&c->state,event,blocks,NULL,c->channels,out,capacity,false,-1);
    REF(&c->state,event,blocks,caps,c->channels,out,capacity,true,-1);REF(&c->state,event,blocks,caps,c->channels-1,out,capacity,false,-4);
    REF(&c->state,event,blocks,caps,SIZE_MAX,out,capacity,false,-2);REF(&c->state,event,blocks,caps,c->channels,out,SIZE_MAX,false,-2);
    native_vorbis_timing_t preview=c->state.timing;native_vorbis_timing_result_t span;CHECK(native_vorbis_timing_push(&preview,event,&span)==0);
    size_t required=(size_t)span.count*c->channels;CHECK(required);
    REF(&c->state,event,blocks,caps,c->channels,NULL,capacity,false,-1);REF(&c->state,event,blocks,caps,c->channels,out,required-1,false,-4);
    uint32_t last=c->channels-1;size_t saved_cap=caps[last];caps[last]=event->blocksize-1;
    REF(&c->state,event,blocks,caps,c->channels,out,capacity,false,-4);caps[last]=SIZE_MAX;
    REF(&c->state,event,blocks,caps,c->channels,out,capacity,false,-2);caps[last]=saved_cap;
    --blocks[last].count;REF(&c->state,event,blocks,caps,c->channels,out,capacity,false,-1);++blocks[last].count;
    const double *saved_pointer=blocks[last].samples;blocks[last].samples=NULL;REF(&c->state,event,blocks,caps,c->channels,out,capacity,false,-1);blocks[last].samples=saved_pointer;
    native_vorbis_timing_event_t bad=*event;bad.granule_position=-2;REF(&c->state,&bad,blocks,caps,c->channels,out,capacity,false,-1);
    bad=*event;bad.end_of_stream=2;REF(&c->state,&bad,blocks,caps,c->channels,out,capacity,false,-1);
    bad=*event;bad.discontinuity=2;REF(&c->state,&bad,blocks,caps,c->channels,out,capacity,false,-1);
    native_vorbis_synthesis_t bad_state=c->state;bad_state.exponent_capacity=c->channels-1;
    REF(&bad_state,event,blocks,caps,c->channels,out,capacity,false,-4);bad_state=c->state;bad_state.timing.previous_size=63;
    REF(&bad_state,event,blocks,caps,c->channels,out,capacity,false,-1);
    unsigned char before[sizeof(bad_state)];memcpy(before,&bad_state,sizeof(before));CHECK(native_vorbis_synthesis_reset(&bad_state)==-1);++owner_refusals;CHECK(!memcmp(before,&bad_state,sizeof(before)));
    const double malformed[]={NAN,INFINITY,-INFINITY};
    double *sample_value=(double *)c->source.data+(size_t)last*c->l+event->blocksize-1;uint64_t word;memcpy(&word,sample_value,8);
    for(unsigned i=0;i<3;++i){*sample_value=malformed[i];REF(&c->state,event,blocks,caps,c->channels,out,capacity,false,-2);}memcpy(sample_value,&word,8);
    double *history=(double *)c->history.data+(size_t)last*(c->l/2)+c->state.timing.previous_size/2-1;memcpy(&word,history,8);
    for(unsigned i=0;i<3;++i){*history=malformed[i];REF(&c->state,event,blocks,caps,c->channels,out,capacity,false,-2);}memcpy(history,&word,8);
    for(unsigned which=0;which<2;++which){unsigned index=plan_index(which?c->l:c->s);double *factor=(double *)lookups[index].data+(which?c->l:c->s)/2-1;memcpy(&word,factor,8);
        const double invalid[]={NAN,INFINITY,-INFINITY,-DBL_TRUE_MIN,0x1.0000000000001p0};
        for(unsigned i=0;i<5;++i){*factor=invalid[i];REF(&c->state,event,blocks,caps,c->channels,out,capacity,false,-2);}memcpy(factor,&word,8);}
#undef REF
}
static double owner_wave(uint32_t index){
    switch(index%12){case 0:return DBL_MAX;case 1:return -DBL_MAX;case 2:return DBL_TRUE_MIN;case 3:return -DBL_TRUE_MIN;
        case 4:return 0;case 5:return -0.0;case 6:return 0x1p-1000;case 7:return -0x1p800;case 8:return 1;case 9:return -1;
        default:return ((int)(index%1021)-510)*.03125;}
}
static int owner_main(const char *input_name,const char *output_name){
    FILE *input=fopen(input_name,"rb"),*output=fopen(output_name,"wb");CHECK(input&&output);unsigned char magic[8];
    CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VSYNOWNI",8));CHECK(fwrite("VSYNOWNO",1,8,output)==8);put32(output,8);
    for(unsigned i=0;i<8;++i){uint32_t n=64U<<i;lookups[i]=buffer((size_t)n/2*8);lookup_copies[i]=buffer(lookups[i].bytes);
        CHECK(native_vorbis_window_prepare(n,(double *)lookups[i].data,n/2,&owner_plans[i])==0);memcpy(lookup_copies[i].data,lookups[i].data,lookups[i].bytes);
        put32(output,n);raw_words(output,&lookups[i]);}
    uint32_t rows=get32(input);CHECK(rows==864);put32(output,rows);owner_t c;memset(&c,0,sizeof(c));bool live=false;
    for(uint32_t row=0;row<rows;++row){uint32_t ids[7];for(unsigned i=0;i<7;++i)ids[i]=get32(input);int64_t ea=signed64(get64(input)),eb=signed64(get64(input));
        uint32_t n=ids[5];if(ids[3]==0){if(live)owner_close(&c);owner_open(&c,ids[0],ids[1],1);live=true;}
        if(ids[3]==4)CHECK(native_vorbis_synthesis_reset(&c.state)==0);
        CHECK(c.state.timing.previous_size==ids[4]);if(ids[4])CHECK(((int64_t *)c.exponents.data)[0]==ea);
        for(uint32_t i=0;i<n;++i){uint64_t word=get64(input);memcpy(c.source.data+(size_t)i*8,&word,8);}source_blocks(&c,n,eb);
        native_vorbis_timing_event_t event={.blocksize=n,.granule_position=-1};native_vorbis_synthesis_result_t result=owner_push(&c,&event);
        CHECK(result.timing.available==ids[6]&&result.timing.count==ids[6]);
        for(unsigned i=0;i<7;++i)put32(output,ids[i]);
        put64(output,(uint64_t)ea);put64(output,(uint64_t)eb);
        timing_put(output,&result.timing);put32(output,result.channels);put64(output,result.pcm_samples);state_put(output,&c.state.timing);
        CHECK(fwrite(c.source.data,1,(size_t)n*8,output)==(size_t)n*8);raw_words(output,&c.history);raw_words(output,&c.exponents);
        for(uint64_t i=0;i<result.pcm_samples;++i)put16(output,((int16_t *)c.pcm.data)[i]);
    }
    if(live)owner_close(&c);
    live=false;
    CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VTIMIN01",8));uint32_t actions=get32(input);CHECK(actions==20019);put32(output,actions);
    native_vorbis_timing_t current={0};
    for(uint32_t row=0;row<actions;++row){uint32_t action=get32(input);(void)get32(input);native_vorbis_timing_t seed;
        seed.short_size=get32(input);seed.long_size=get32(input);seed.previous_size=get32(input);seed.position_known=get32(input);seed.end_seen=get32(input);
        seed.bounded_sample_count=get64(input);seed.bounded_prediction=get64(input);native_vorbis_timing_event_t event;
        event.blocksize=get32(input);event.granule_position=signed64(get64(input));event.end_of_stream=get32(input);event.discontinuity=get32(input);
        if(action==3){CHECK(live);memset(c.history.data,0,c.history.bytes);memset(c.exponents.data,0,c.exponents.bytes);c.state.timing=seed;current=seed;}
        put32(output,action);state_put(output,&current);put32(output,event.blocksize);put64(output,(uint64_t)event.granule_position);put32(output,event.end_of_stream);put32(output,event.discontinuity);
        native_vorbis_synthesis_result_t result={0};uint64_t hash=UINT64_C(14695981039346656037);
        if(action==0){if(live)owner_close(&c);owner_open(&c,seed.short_size,seed.long_size,1);live=true;memset(c.history.data,0,c.history.bytes);memset(c.exponents.data,0,c.exponents.bytes);}
        else if(action==2)CHECK(native_vorbis_synthesis_reset(&c.state)==0);
        else{CHECK(action==1||action==3);source_blocks(&c,event.blocksize,0);result=owner_push(&c,&event);
            for(uint64_t i=0;i<result.pcm_samples;++i){CHECK(((int16_t *)c.pcm.data)[i]==0);hash*=UINT64_C(1099511628211);hash*=UINT64_C(1099511628211);}}
        current=c.state.timing;state_put(output,&current);timing_put(output,&result.timing);put64(output,result.pcm_samples);put64(output,hash);
    }
    if(live)owner_close(&c);
    put32(output,255);
    for(uint32_t channels=1;channels<=255;++channels){owner_open(&c,64,128,channels);put32(output,channels);
        for(uint32_t step=0;step<3;++step){uint32_t n=step==1?128:64;source_blocks(&c,n,0);native_vorbis_transform_block_t *blocks=(void *)c.blocks.data;
            for(uint32_t ch=0;ch<channels;++ch){blocks[ch].exponent=(ch+step)&1?INT64_MAX:INT64_MIN;
                for(uint32_t i=0;i<n;++i)((double *)c.source.data)[(size_t)ch*c.l+i]=owner_wave(i*37+ch*17+step*11);}
            native_vorbis_timing_event_t event={.blocksize=n,.granule_position=step==1?(channels%3==0?40:-1):(step==2?(channels%3==0?50:channels%5==0?10:-1):-1),
                .end_of_stream=step==2,.discontinuity=step==1&&channels%7==0};
            if(channels==255&&step==2)focused_controls(&c,&event);
            native_vorbis_synthesis_result_t result=owner_push(&c,&event);put32(output,step);timing_put(output,&result.timing);put64(output,result.pcm_samples);
            raw_words(output,&c.history);raw_words(output,&c.exponents);for(uint64_t i=0;i<result.pcm_samples;++i)put16(output,((int16_t *)c.pcm.data)[i]);
        }
        buffer_t h=buffer(c.history.bytes),e=buffer(c.exponents.bytes);memcpy(h.data,c.history.data,h.bytes);memcpy(e.data,c.exponents.data,e.bytes);
        uint64_t nan=UINT64_C(0x7ff8000000000042);memcpy(c.history.data,&nan,8);buffer_t invalid=buffer(c.history.bytes);memcpy(invalid.data,c.history.data,invalid.bytes);
        CHECK(native_vorbis_synthesis_reset(&c.state)==0&&!memcmp(invalid.data,c.history.data,invalid.bytes)&&!memcmp(e.data,c.exponents.data,e.bytes));
        memcpy(c.history.data,h.data,h.bytes);drop(&invalid);drop(&e);drop(&h);state_put(output,&c.state.timing);owner_close(&c);
    }
    CHECK(fgetc(input)==EOF&&!ferror(input));CHECK(fclose(input)==0&&fclose(output)==0);
    for(unsigned i=0;i<8;++i){CHECK(!memcmp(lookups[i].data,lookup_copies[i].data,lookups[i].bytes));drop(&lookup_copies[i]);drop(&lookups[i]);}
    printf("SYNTHESIS_OWNER overlap=864 timing=20019 channels=255 pushes=%" PRIu64 " values=%" PRIu64 " refusals=%" PRIu64 " checks=%" PRIu64 "\n",owner_pushes,owner_values,owner_refusals,checks);return 0;
}
int main(int argc,char **argv){
    if(argc==4&&!strcmp(argv[1],"--owner"))return owner_main(argv[2],argv[3]);
    CHECK(argc==3);FILE *input=fopen(argv[1],"rb"),*output=fopen(argv[2],"wb");CHECK(input&&output);
    unsigned char magic[8];CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VSYNIN01",8));uint32_t count=get32(input);CHECK(count==31);
    CHECK(fwrite("VSYNOUT1",1,8,output)==8);put32(output,count);
    for(uint32_t i=0;i<count;++i)run_case(input,output,i);
    CHECK(fgetc(input)==EOF&&!ferror(input));CHECK(fclose(input)==0&&fclose(output)==0);
    printf("SYNTHESIS_CAPTURE cases=31 packets=%" PRIu64 " pcm_bytes=%" PRIu64 " failed=%" PRIu64 " checks=%" PRIu64 " live=0 bytes=0\n",packets,pcm_bytes,failures,checks);return 0;
}
