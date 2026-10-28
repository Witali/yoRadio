// Persistent public decoder lifetime, capacity, allocation and PCM qualification.
#include "native_vorbis_decoder.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks,undersized,measure_calls,open_refusals,replace_refusals,process_refusals,other_refusals;
#define CHECK(x) do{++checks;assert(x);}while(0)
static uint32_t get32(FILE *f){unsigned char b[4];CHECK(fread(b,1,4,f)==4);return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;}
static uint64_t get64(FILE *f){uint64_t low=get32(f);return low|(uint64_t)get32(f)<<32;}
static int64_t as_signed(uint64_t u){int64_t s;memcpy(&s,&u,8);return s;}
static void put32(FILE *f,uint32_t u){unsigned char b[4]={(unsigned char)u,(unsigned char)(u>>8),(unsigned char)(u>>16),(unsigned char)(u>>24)};CHECK(fwrite(b,1,4,f)==4);}
static void put64(FILE *f,uint64_t u){put32(f,(uint32_t)u);put32(f,(uint32_t)(u>>32));}
static void put16(FILE *f,int16_t s){uint16_t u;memcpy(&u,&s,2);unsigned char b[2]={(unsigned char)u,(unsigned char)(u>>8)};CHECK(fwrite(b,1,2,f)==2);}
static uint64_t hash_bytes(const void *pointer,size_t bytes,uint64_t hash){const unsigned char *p=pointer;for(size_t i=0;i<bytes;++i)hash=(hash^p[i])*UINT64_C(1099511628211);return hash;}
typedef struct {unsigned char *raw,*data;size_t bytes;} buffer_t;
static buffer_t buffer(size_t bytes){CHECK(bytes<=SIZE_MAX-32);buffer_t b={.raw=malloc(bytes+32),.bytes=bytes};CHECK(b.raw);b.data=b.raw+16;memset(b.raw,0xa5,bytes+32);return b;}
static void guard(const buffer_t *b){for(unsigned i=0;i<16;++i){CHECK(b->raw[i]==0xa5);CHECK(b->data[b->bytes+i]==0xa5);}}
static buffer_t snapshot(const buffer_t *b){buffer_t c=buffer(b->bytes);memcpy(c.data,b->data,b->bytes);return c;}
static void unchanged(const buffer_t *b,const buffer_t *saved){guard(b);CHECK(b->bytes==saved->bytes&&!memcmp(b->data,saved->data,b->bytes));}
static void drop(buffer_t *b){guard(b);free(b->raw);}

typedef union allocation allocation_t;
union allocation {max_align_t alignment;struct {allocation_t *next,*previous;size_t bytes;uint64_t tag;} value;};
typedef struct {
    allocation_t *head;size_t attempts,allocations,releases,live,bytes,peak_live,peak_bytes,fail_at,failed_size,failures,budget;
    size_t *requests,request_capacity;
    native_vorbis_decoder_t **observed,*old;
    unsigned release_mode;
} allocator_t;
static unsigned char *payload(allocation_t *a){return (unsigned char *)(a+1)+16;}
static allocation_t *allocation_of(void *p){return (allocation_t *)((unsigned char *)p-16)-1;}
static void allocation_guard(allocation_t *a){
    CHECK(a->value.tag==UINT64_C(0xdec0deab12cd34ef));unsigned char *p=payload(a);
    for(unsigned i=0;i<16;++i){CHECK((p-16)[i]==0xa5);CHECK(p[a->value.bytes+i]==0xa5);}
}
static void allocations_guard(const allocator_t *a){for(allocation_t *p=a->head;p;p=p->value.next)allocation_guard(p);}
static void *owned_allocate(void *opaque,size_t bytes){
    allocator_t *a=opaque;CHECK(bytes>0&&bytes<=SIZE_MAX-sizeof(allocation_t)-32);++a->attempts;
    if(a->attempts>a->request_capacity){size_t capacity=a->request_capacity?a->request_capacity*2:64;CHECK(capacity>=a->attempts&&capacity<=SIZE_MAX/sizeof(*a->requests));
        void *next=realloc(a->requests,capacity*sizeof(*a->requests));CHECK(next);a->requests=next;a->request_capacity=capacity;}
    a->requests[a->attempts-1]=bytes;
    if(a->fail_at==a->attempts||(a->budget&&(a->bytes>a->budget||bytes>a->budget-a->bytes))){++a->failures;a->failed_size=bytes;return NULL;}
    allocation_t *p=malloc(sizeof(*p)+32+bytes);CHECK(p);memset((unsigned char *)(p+1),0xa5,bytes+32);
    p->value.next=a->head;p->value.previous=NULL;p->value.bytes=bytes;p->value.tag=UINT64_C(0xdec0deab12cd34ef);
    if(a->head)a->head->value.previous=p;
    a->head=p;++a->allocations;++a->live;a->bytes+=bytes;
    if(a->live>a->peak_live)a->peak_live=a->live;
    if(a->bytes>a->peak_bytes)a->peak_bytes=a->bytes;
    return payload(p);
}
static void owned_release(void *opaque,void *pointer){
    allocator_t *a=opaque;CHECK(pointer);allocation_t *p=allocation_of(pointer);allocation_guard(p);
    if(a->release_mode==1)CHECK(a->observed&&!*a->observed);
    if(a->release_mode==2)CHECK(a->observed&&*a->observed&&*a->observed!=a->old);
    if(a->release_mode==3)CHECK(a->observed&&*a->observed==a->old);
    if(p->value.previous)p->value.previous->value.next=p->value.next;else{CHECK(a->head==p);a->head=p->value.next;}
    if(p->value.next)p->value.next->value.previous=p->value.previous;
    CHECK(a->live&&a->bytes>=p->value.bytes);--a->live;a->bytes-=p->value.bytes;++a->releases;p->value.tag=0;free(p);
}
static void cleared(native_vorbis_decoder_t **d,allocator_t *a){
    a->observed=d;a->release_mode=1;native_vorbis_decoder_clear(d);CHECK(!*d&&!a->head&&!a->live&&!a->bytes&&a->allocations==a->releases);
    size_t releases=a->releases;native_vorbis_decoder_clear(d);native_vorbis_decoder_clear(NULL);CHECK(a->releases==releases);a->release_mode=0;
    free(a->requests);a->requests=NULL;a->request_capacity=0;
}
static bool info_equal(const native_vorbis_decoder_info_t *a,const native_vorbis_decoder_info_t *b){
    const native_vorbis_identification_t *x=&a->identification,*y=&b->identification;
    const native_vorbis_timing_t *p=&a->timing,*q=&b->timing;
    return x->channels==y->channels&&x->sample_rate==y->sample_rate&&x->bitrate_maximum_bits==y->bitrate_maximum_bits&&
        x->bitrate_nominal_bits==y->bitrate_nominal_bits&&x->bitrate_minimum_bits==y->bitrate_minimum_bits&&x->blocksize_0==y->blocksize_0&&x->blocksize_1==y->blocksize_1&&
        p->short_size==q->short_size&&p->long_size==q->long_size&&p->previous_size==q->previous_size&&p->position_known==q->position_known&&p->end_seen==q->end_seen&&
        p->bounded_sample_count==q->bounded_sample_count&&p->bounded_prediction==q->bounded_prediction&&a->end_of_stream==b->end_of_stream;
}
static native_vorbis_decoder_info_t info(native_vorbis_decoder_t *d,allocator_t *a){
    native_vorbis_decoder_info_t result;size_t attempts=a->attempts,releases=a->releases;
    CHECK(native_vorbis_decoder_info(d,&result)==0&&a->attempts==attempts&&a->releases==releases);return result;
}
typedef struct {native_vorbis_decoder_result_t result;buffer_t pcm;size_t allocations,*requests;} baseline_t;
typedef struct {uint32_t fields[9];buffer_t id,setup,audio,offsets,granules;baseline_t *baseline;size_t open_allocations,*open_requests;} case_t;
static case_t read_case(FILE *f,uint32_t ordinal){
    case_t c={0};for(unsigned i=0;i<9;++i)c.fields[i]=get32(f);CHECK(c.fields[0]==ordinal&&c.fields[5]==14);
    c.id=buffer(c.fields[6]);c.setup=buffer(c.fields[7]);c.audio=buffer(c.fields[8]);
    CHECK(fread(c.id.data,1,c.id.bytes,f)==c.id.bytes&&fread(c.setup.data,1,c.setup.bytes,f)==c.setup.bytes&&fread(c.audio.data,1,c.audio.bytes,f)==c.audio.bytes);
    c.offsets=buffer(((size_t)c.fields[5]+1)*4);c.granules=buffer((size_t)c.fields[5]*8);
    for(uint32_t i=0;i<=c.fields[5];++i)((uint32_t *)c.offsets.data)[i]=get32(f);
    for(uint32_t i=0;i<c.fields[5];++i)((int64_t *)c.granules.data)[i]=as_signed(get64(f));
    c.baseline=calloc(c.fields[5],sizeof(*c.baseline));CHECK(c.baseline);return c;
}
static int open_case(native_vorbis_decoder_t **d,allocator_t *a,const case_t *c,bool lifetime){
    buffer_t id=snapshot(&c->id),setup=snapshot(&c->setup),descriptor=buffer(sizeof(native_vorbis_setup_allocator_t));
    native_vorbis_setup_allocator_t *callbacks=(void *)descriptor.data;*callbacks=(native_vorbis_setup_allocator_t){.context=a,.allocate=owned_allocate,.release=owned_release};
    a->observed=d;int status=native_vorbis_decoder_replace(d,id.data,id.bytes,(uint64_t)id.bytes*8,setup.data,setup.bytes,(uint64_t)setup.bytes*8,callbacks);
    CHECK(!memcmp(id.data,c->id.data,id.bytes)&&!memcmp(setup.data,c->setup.data,setup.bytes));
    if(lifetime){memset(id.data,0xdb,id.bytes);memset(setup.data,0xdc,setup.bytes);}
    memset(descriptor.data,0,descriptor.bytes);drop(&descriptor);drop(&setup);drop(&id);allocations_guard(a);return status;
}
static native_vorbis_decoder_packet_t packet_for(const case_t *c,uint32_t index){
    const uint32_t *offsets=(void *)c->offsets.data;size_t bytes=offsets[index+1]-offsets[index];
    return (native_vorbis_decoder_packet_t){.data=c->audio.data+offsets[index],.bytes=bytes,.bits=(uint64_t)bytes*8,
        .granule_position=((int64_t *)c->granules.data)[index],.end_of_stream=index+1==c->fields[5]};
}
static native_vorbis_decoder_requirements_t measure(native_vorbis_decoder_t *d,allocator_t *a,const native_vorbis_decoder_packet_t *packet){
    native_vorbis_decoder_info_t before=info(d,a);native_vorbis_decoder_requirements_t q;size_t calls=a->attempts,frees=a->releases;
    buffer_t raw=buffer(packet->bytes);if(raw.bytes)memcpy(raw.data,packet->data,raw.bytes);
    unsigned char pb[sizeof(*packet)];memcpy(pb,packet,sizeof(pb));
    CHECK(native_vorbis_decoder_measure(d,packet,&q)==0&&a->attempts==calls&&a->releases==frees);++measure_calls;
    native_vorbis_decoder_info_t after=info(d,a);CHECK(info_equal(&before,&after)&&!memcmp(pb,packet,sizeof(pb))&&(!raw.bytes||!memcmp(raw.data,packet->data,raw.bytes)));drop(&raw);return q;
}
static void failed_process(native_vorbis_decoder_t *d,allocator_t *a,const native_vorbis_decoder_packet_t *packet,
    buffer_t *output,size_t capacity,int wanted,bool no_allocation){
    buffer_t saved=snapshot(output),raw=buffer(packet->bytes);if(raw.bytes)memcpy(raw.data,packet->data,raw.bytes);
    native_vorbis_decoder_result_t result;memset(&result,0xa5,sizeof(result));unsigned char rb[sizeof(result)],pb[sizeof(*packet)];
    memcpy(rb,&result,sizeof(rb));memcpy(pb,packet,sizeof(pb));native_vorbis_decoder_info_t before=info(d,a);size_t calls=a->attempts,frees=a->releases;
    CHECK(native_vorbis_decoder_process(d,packet,(int16_t *)output->data,capacity,&result)==wanted);
    CHECK(!memcmp(rb,&result,sizeof(rb))&&!memcmp(pb,packet,sizeof(pb)));unchanged(output,&saved);
    native_vorbis_decoder_info_t after=info(d,a);CHECK(info_equal(&before,&after));if(no_allocation)CHECK(a->attempts==calls&&a->releases==frees);
    CHECK(!raw.bytes||!memcmp(raw.data,packet->data,raw.bytes));allocations_guard(a);drop(&raw);drop(&saved);
}
static native_vorbis_decoder_result_t successful(native_vorbis_decoder_t *d,allocator_t *a,const native_vorbis_decoder_packet_t *packet,
    buffer_t *output,const baseline_t *baseline,bool capacity_sweep){
    buffer_t raw=buffer(packet->bytes);memcpy(raw.data,packet->data,raw.bytes);native_vorbis_decoder_packet_t actual=*packet;actual.data=raw.data;
    native_vorbis_decoder_requirements_t q=measure(d,a,&actual);native_vorbis_decoder_requirements_t repeated=measure(d,a,&actual);
    CHECK(q.blocksize==repeated.blocksize&&q.channels==repeated.channels&&q.pcm_samples==repeated.pcm_samples);
    CHECK(q.pcm_samples<=output->bytes/2-4);
    if(capacity_sweep&&q.pcm_samples){
        size_t capacities[3]={0,(size_t)q.pcm_samples/2,(size_t)q.pcm_samples-1};
        for(unsigned i=0;i<3;++i){bool duplicate=false;for(unsigned j=0;j<i;++j)duplicate|=capacities[j]==capacities[i];
            if(!duplicate){failed_process(d,a,&actual,output,capacities[i],-5,true);++undersized;}}
    }
    buffer_t before=snapshot(output);native_vorbis_decoder_result_t result;
    CHECK(native_vorbis_decoder_process(d,&actual,q.pcm_samples?(int16_t *)output->data:NULL,(size_t)q.pcm_samples,&result)==0);
    CHECK(result.blocksize==q.blocksize&&result.channels==q.channels&&result.synthesis.pcm_samples==q.pcm_samples&&
        result.synthesis.timing.available==q.timing.available&&result.synthesis.timing.discard_start==q.timing.discard_start&&
        result.synthesis.timing.discard_end==q.timing.discard_end&&result.synthesis.timing.count==q.timing.count&&
        result.synthesis.timing.position_kind==q.timing.position_kind&&result.synthesis.timing.end_position==q.timing.end_position);
    size_t bytes=(size_t)q.pcm_samples*2;CHECK(!memcmp(output->data+bytes,before.data+bytes,output->bytes-bytes));
    CHECK(!memcmp(raw.data,packet->data,raw.bytes));guard(output);guard(&raw);
    if(baseline)CHECK(bytes==baseline->pcm.bytes&&!memcmp(output->data,baseline->pcm.data,bytes));
    memset(raw.data,0xed,raw.bytes);drop(&raw);drop(&before);allocations_guard(a);return result;
}
static buffer_t output_for(const case_t *c){return buffer(((size_t)c->fields[4]/2*c->fields[2]+4)*2);}
static void build_baseline(case_t *c){
    allocator_t a={0};native_vorbis_decoder_t *d=NULL;CHECK(open_case(&d,&a,c,true)==0);c->open_allocations=a.attempts;buffer_t output=output_for(c);
    c->open_requests=malloc(c->open_allocations*sizeof(*c->open_requests));CHECK(c->open_requests);memcpy(c->open_requests,a.requests,c->open_allocations*sizeof(*c->open_requests));
    for(uint32_t i=0;i<c->fields[5];++i){native_vorbis_decoder_packet_t packet=packet_for(c,i);size_t calls=a.attempts;
        c->baseline[i].result=successful(d,&a,&packet,&output,NULL,false);c->baseline[i].allocations=a.attempts-calls;
        if(c->baseline[i].allocations){c->baseline[i].requests=malloc(c->baseline[i].allocations*sizeof(size_t));CHECK(c->baseline[i].requests);
            memcpy(c->baseline[i].requests,a.requests+calls,c->baseline[i].allocations*sizeof(size_t));}
        c->baseline[i].pcm=buffer((size_t)c->baseline[i].result.synthesis.pcm_samples*2);memcpy(c->baseline[i].pcm.data,output.data,c->baseline[i].pcm.bytes);}
    cleared(&d,&a);drop(&output);
}
static uint64_t packet_hash(const baseline_t *p,uint64_t hash){return hash_bytes(p->pcm.data,p->pcm.bytes,hash);}
static void info_put(FILE *f,const native_vorbis_decoder_info_t *info){
    native_vorbis_decoder_info_t empty={0};if(!info)info=&empty;
    put32(f,info->identification.channels);put32(f,info->identification.sample_rate);put32(f,info->identification.blocksize_0);put32(f,info->identification.blocksize_1);
    const native_vorbis_timing_t *t=&info->timing;put32(f,t->short_size);put32(f,t->long_size);put32(f,t->previous_size);put32(f,t->position_known);put32(f,t->end_seen);
    put64(f,t->bounded_sample_count);put64(f,t->bounded_prediction);put32(f,info->end_of_stream);
}
static void event(FILE *f,uint32_t kind,uint32_t stream,uint32_t packet,size_t ordinal,size_t bytes,
    const native_vorbis_decoder_info_t *before,const native_vorbis_decoder_info_t *after,uint32_t spans){
    put32(f,kind);put32(f,stream);put32(f,packet);put64(f,ordinal);put64(f,bytes);info_put(f,before);info_put(f,after);put32(f,spans);
}
static void recovery_span(FILE *f,const case_t *c,uint32_t packet,const native_vorbis_decoder_result_t *result,const buffer_t *actual){
    size_t bytes=(size_t)result->synthesis.pcm_samples*2;CHECK(bytes==c->baseline[packet].pcm.bytes);
    put32(f,c->fields[0]);put32(f,packet);put32(f,(uint32_t)bytes);CHECK(fwrite(actual->data,1,bytes,f)==bytes);
}
static void event_end(FILE *f,uint64_t hash,const allocator_t *a,const allocator_t *b){
    put64(f,hash);put64(f,a->live+(b?b->live:0));put64(f,a->allocations+(b?b->allocations:0));put64(f,a->releases+(b?b->releases:0));
}
static void replay_prefix(native_vorbis_decoder_t *d,allocator_t *a,const case_t *c,uint32_t count,buffer_t *output){
    for(uint32_t i=0;i<count;++i){native_vorbis_decoder_packet_t packet=packet_for(c,i);(void)successful(d,a,&packet,output,&c->baseline[i],false);}
}
static void open_sweeps(const case_t *c,FILE *log){
    for(size_t ordinal=1;ordinal<=c->open_allocations;++ordinal){allocator_t a={.fail_at=ordinal};native_vorbis_decoder_t *d=NULL;
        CHECK(open_case(&d,&a,c,false)==-4&&!d&&a.failures==1&&!a.live&&!a.head&&a.allocations==a.releases);size_t bytes=a.failed_size;
        CHECK(bytes==c->open_requests[ordinal-1]);event(log,0,c->fields[0],0,ordinal,bytes,NULL,NULL,2);
        a.fail_at=0;CHECK(open_case(&d,&a,c,true)==0);buffer_t output=output_for(c);
        for(uint32_t i=0;i<2;++i){native_vorbis_decoder_packet_t packet=packet_for(c,i);native_vorbis_decoder_result_t result=successful(d,&a,&packet,&output,&c->baseline[i],false);recovery_span(log,c,i,&result,&output);}
        uint64_t hash=packet_hash(&c->baseline[1],packet_hash(&c->baseline[0],UINT64_C(14695981039346656037)));
        cleared(&d,&a);drop(&output);event_end(log,hash,&a,NULL);++open_refusals;
    }
}
typedef struct {allocation_t *allocation;buffer_t bytes;} allocation_copy_t;
static allocation_copy_t *owned_snapshot(const allocator_t *a){
    allocation_copy_t *saved=calloc(a->live,sizeof(*saved));CHECK(saved);size_t i=0;
    for(allocation_t *p=a->head;p;p=p->value.next){saved[i].allocation=p;saved[i].bytes=buffer(p->value.bytes);memcpy(saved[i].bytes.data,payload(p),p->value.bytes);++i;}
    CHECK(i==a->live);return saved;
}
static void owned_unchanged(const allocator_t *a,allocation_copy_t *saved,size_t count){
    CHECK(a->live==count);for(size_t i=0;i<count;++i){allocation_guard(saved[i].allocation);CHECK(!memcmp(saved[i].bytes.data,payload(saved[i].allocation),saved[i].bytes.bytes));drop(&saved[i].bytes);}free(saved);
}
static void replacement_sweeps(const case_t *c,FILE *log){
    for(size_t ordinal=1;ordinal<=c->open_allocations;++ordinal){allocator_t old={0},candidate={.fail_at=ordinal};native_vorbis_decoder_t *d=NULL;
        CHECK(open_case(&d,&old,c,true)==0);buffer_t output=output_for(c);replay_prefix(d,&old,c,3,&output);
        native_vorbis_decoder_t *saved_handle=d;native_vorbis_decoder_info_t before=info(d,&old);size_t live=old.live;allocation_copy_t *snapshot=owned_snapshot(&old);
        candidate.observed=&d;candidate.old=d;candidate.release_mode=3;
        CHECK(open_case(&d,&candidate,c,false)==-4&&d==saved_handle&&candidate.failures==1&&!candidate.live&&!candidate.head);
        native_vorbis_decoder_info_t after=info(d,&old);CHECK(info_equal(&before,&after));owned_unchanged(&old,snapshot,live);
        size_t bytes=candidate.failed_size;CHECK(bytes==c->open_requests[ordinal-1]);event(log,1,c->fields[0],3,ordinal,bytes,&before,&after,3);
        native_vorbis_decoder_packet_t packet=packet_for(c,3);native_vorbis_decoder_result_t result=successful(d,&old,&packet,&output,&c->baseline[3],false);recovery_span(log,c,3,&result,&output);
        candidate.fail_at=0;candidate.release_mode=0;old.observed=&d;old.old=d;old.release_mode=2;
        CHECK(open_case(&d,&candidate,c,true)==0&&!old.live&&!old.head&&old.allocations==old.releases);
        free(old.requests);old.requests=NULL;old.request_capacity=0;
        for(uint32_t i=0;i<2;++i){packet=packet_for(c,i);result=successful(d,&candidate,&packet,&output,&c->baseline[i],false);recovery_span(log,c,i,&result,&output);}
        uint64_t hash=packet_hash(&c->baseline[1],packet_hash(&c->baseline[0],packet_hash(&c->baseline[3],UINT64_C(14695981039346656037))));
        cleared(&d,&candidate);drop(&output);event_end(log,hash,&old,&candidate);++replace_refusals;
    }
}
static void process_sweeps(const case_t *c,FILE *log){
    for(uint32_t packet_index=0;packet_index<c->fields[5];++packet_index)for(size_t ordinal=1;ordinal<=c->baseline[packet_index].allocations;++ordinal){
        allocator_t a={0};native_vorbis_decoder_t *d=NULL;CHECK(open_case(&d,&a,c,true)==0);buffer_t output=output_for(c);
        replay_prefix(d,&a,c,packet_index,&output);native_vorbis_decoder_packet_t packet=packet_for(c,packet_index);
        native_vorbis_decoder_requirements_t q=measure(d,&a,&packet);native_vorbis_decoder_info_t before=info(d,&a);a.fail_at=a.attempts+ordinal;
        failed_process(d,&a,&packet,&output,(size_t)q.pcm_samples,-4,false);CHECK(a.failures==1);size_t bytes=a.failed_size;a.fail_at=0;
        native_vorbis_decoder_info_t after=info(d,&a);CHECK(bytes==c->baseline[packet_index].requests[ordinal-1]);
        event(log,2,c->fields[0],packet_index,ordinal,bytes,&before,&after,packet_index+1<c->fields[5]?2:1);
        native_vorbis_decoder_result_t result=successful(d,&a,&packet,&output,&c->baseline[packet_index],false);recovery_span(log,c,packet_index,&result,&output);
        uint64_t hash=packet_hash(&c->baseline[packet_index],UINT64_C(14695981039346656037));
        if(packet_index+1<c->fields[5]){packet=packet_for(c,packet_index+1);result=successful(d,&a,&packet,&output,&c->baseline[packet_index+1],false);recovery_span(log,c,packet_index+1,&result,&output);hash=packet_hash(&c->baseline[packet_index+1],hash);}
        cleared(&d,&a);drop(&output);event_end(log,hash,&a,NULL);++process_refusals;
    }
}
static void failed_measure(native_vorbis_decoder_t *d,allocator_t *a,const native_vorbis_decoder_packet_t *packet,int status){
    native_vorbis_decoder_requirements_t q;memset(&q,0xa5,sizeof(q));unsigned char saved[sizeof(q)];memcpy(saved,&q,sizeof(q));
    native_vorbis_decoder_info_t before=info(d,a);size_t calls=a->attempts,frees=a->releases;
    CHECK(native_vorbis_decoder_measure(d,packet,&q)==status&&!memcmp(saved,&q,sizeof(q)));
    native_vorbis_decoder_info_t after=info(d,a);CHECK(info_equal(&before,&after)&&a->attempts==calls&&a->releases==frees);++other_refusals;
}
static void basic_failures(native_vorbis_decoder_t *d,allocator_t *a,const case_t *c,buffer_t *output){
    native_vorbis_decoder_packet_t p=packet_for(c,0);p.bits=0;failed_measure(d,a,&p,-3);failed_process(d,a,&p,output,0,-3,true);++other_refusals;
    p=packet_for(c,0);p.granule_position=-2;failed_measure(d,a,&p,-1);failed_process(d,a,&p,output,0,-1,true);++other_refusals;
    p=packet_for(c,0);p.data=NULL;p.bytes=0;p.bits=0;failed_measure(d,a,&p,-3);failed_process(d,a,&p,output,0,-3,true);++other_refusals;
    native_vorbis_decoder_info_t sentinel;memset(&sentinel,0xa5,sizeof(sentinel));unsigned char saved[sizeof(sentinel)];memcpy(saved,&sentinel,sizeof(saved));
    CHECK(native_vorbis_decoder_info(NULL,&sentinel)==-1&&!memcmp(saved,&sentinel,sizeof(saved))&&native_vorbis_decoder_info(d,NULL)==-1&&native_vorbis_decoder_reset(NULL)==-1);
    native_vorbis_decoder_requirements_t q;CHECK(native_vorbis_decoder_measure(NULL,&p,&q)==-1&&native_vorbis_decoder_measure(d,NULL,&q)==-1&&native_vorbis_decoder_measure(d,&p,NULL)==-1);
    native_vorbis_decoder_result_t result;CHECK(native_vorbis_decoder_process(NULL,&p,NULL,0,&result)==-1&&native_vorbis_decoder_process(d,NULL,NULL,0,&result)==-1&&native_vorbis_decoder_process(d,&p,NULL,0,NULL)==-1);
}
static void packet_put(FILE *f,uint32_t packet,const native_vorbis_decoder_result_t *r,const buffer_t *output){
    put32(f,packet);put32(f,r->blocksize);put32(f,r->channels);put32(f,r->floor0_channels);put32(f,r->floor1_channels);put64(f,r->consumed_bits);put32(f,r->end_of_packet);
    const native_vorbis_timing_result_t *t=&r->synthesis.timing;
    put32(f,t->available);put32(f,t->discard_start);put32(f,t->discard_end);put32(f,t->count);put32(f,t->position_kind);put64(f,(uint64_t)t->end_position);put64(f,r->synthesis.pcm_samples);
    for(uint64_t i=0;i<r->synthesis.pcm_samples;++i)put16(f,((int16_t *)output->data)[i]);
}
static void primary(const case_t *c,FILE *capture,FILE *log){
    for(unsigned j=0;j<6;++j)put32(capture,c->fields[j]);
    long length_offset=ftell(capture);CHECK(length_offset>=0);put64(capture,0);long begin=ftell(capture);CHECK(begin>=0);
    allocator_t a={0};native_vorbis_decoder_t *d=NULL;CHECK(open_case(&d,&a,c,true)==0);buffer_t output=output_for(c);basic_failures(d,&a,c,&output);
    uint64_t frames=0,samples=0,floor0=0,floor1=0;
    for(uint32_t i=0;i<c->fields[5];++i){native_vorbis_decoder_packet_t p=packet_for(c,i);native_vorbis_decoder_result_t r=successful(d,&a,&p,&output,&c->baseline[i],true);
        packet_put(capture,i,&r,&output);frames+=r.synthesis.timing.count;samples+=r.synthesis.pcm_samples;floor0+=r.floor0_channels;floor1+=r.floor1_channels;}
    long end=ftell(capture);CHECK(end>=begin&&fseek(capture,length_offset,SEEK_SET)==0);put64(capture,(uint64_t)(end-begin));CHECK(fseek(capture,end,SEEK_SET)==0);
    native_vorbis_decoder_packet_t p=packet_for(c,0);failed_measure(d,&a,&p,-11);failed_process(d,&a,&p,&output,output.bytes/2,-11,true);++other_refusals;
    native_vorbis_decoder_info_t before=info(d,&a);CHECK(before.end_of_stream);size_t calls=a.attempts,frees=a.releases;
    CHECK(native_vorbis_decoder_reset(d)==0&&a.attempts==calls&&a.releases==frees);native_vorbis_decoder_info_t after=info(d,&a);
    CHECK(!after.end_of_stream&&!after.timing.previous_size&&!after.timing.position_known&&!after.timing.end_seen&&!after.timing.bounded_sample_count&&!after.timing.bounded_prediction);
    event(log,3,c->fields[0],0,0,0,&before,&after,c->fields[5]);uint64_t hash=UINT64_C(14695981039346656037);
    for(uint32_t i=0;i<c->fields[5];++i){p=packet_for(c,i);native_vorbis_decoder_result_t r=successful(d,&a,&p,&output,&c->baseline[i],false);recovery_span(log,c,i,&r,&output);hash=packet_hash(&c->baseline[i],hash);}
    CHECK(a.attempts==calls&&a.releases==frees);cleared(&d,&a);event_end(log,hash,&a,NULL);drop(&output);
    put32(capture,0);for(unsigned j=0;j<3;++j)put32(capture,UINT32_MAX);
    put64(capture,c->fields[5]);put64(capture,frames);put64(capture,samples);put64(capture,floor0);put64(capture,floor1);
    put64(capture,a.allocations);put64(capture,a.releases);put64(capture,a.live);put64(capture,a.bytes);put64(capture,a.peak_live);put64(capture,a.peak_bytes);put32(capture,0);
}
static void gap(const case_t *c,FILE *log){
    allocator_t a={0};native_vorbis_decoder_t *d=NULL;CHECK(open_case(&d,&a,c,true)==0);buffer_t output=output_for(c);replay_prefix(d,&a,c,3,&output);
    native_vorbis_decoder_info_t before=info(d,&a);native_vorbis_decoder_packet_t p=packet_for(c,3);p.discontinuity=true;p.granule_position=-1;
    native_vorbis_decoder_result_t r=successful(d,&a,&p,&output,&c->baseline[3],false);native_vorbis_decoder_info_t after=info(d,&a);
    CHECK(!after.timing.position_known&&!after.end_of_stream);event(log,4,c->fields[0],3,0,0,&before,&after,2);recovery_span(log,c,3,&r,&output);
    p=packet_for(c,4);r=successful(d,&a,&p,&output,&c->baseline[4],false);recovery_span(log,c,4,&r,&output);
    uint64_t hash=packet_hash(&c->baseline[4],packet_hash(&c->baseline[3],UINT64_C(14695981039346656037)));cleared(&d,&a);event_end(log,hash,&a,NULL);drop(&output);
}
static void independent(const case_t *a_case,const case_t *b_case,FILE *log){
    allocator_t a={0},b={0};native_vorbis_decoder_t *ad=NULL,*bd=NULL;CHECK(open_case(&ad,&a,a_case,true)==0&&open_case(&bd,&b,b_case,true)==0);
    buffer_t ao=output_for(a_case),bo=output_for(b_case);event(log,5,a_case->fields[0],b_case->fields[0],0,0,NULL,NULL,28);uint64_t hash=UINT64_C(14695981039346656037);
    for(uint32_t i=0;i<14;++i){native_vorbis_decoder_info_t before=info(bd,&b);native_vorbis_decoder_packet_t p=packet_for(a_case,i);
        native_vorbis_decoder_result_t r=successful(ad,&a,&p,&ao,&a_case->baseline[i],false);native_vorbis_decoder_info_t after=info(bd,&b);CHECK(info_equal(&before,&after));
        recovery_span(log,a_case,i,&r,&ao);hash=packet_hash(&a_case->baseline[i],hash);before=info(ad,&a);p=packet_for(b_case,i);r=successful(bd,&b,&p,&bo,&b_case->baseline[i],false);
        after=info(ad,&a);CHECK(info_equal(&before,&after));recovery_span(log,b_case,i,&r,&bo);hash=packet_hash(&b_case->baseline[i],hash);}
    cleared(&ad,&a);cleared(&bd,&b);event_end(log,hash,&a,&b);drop(&ao);drop(&bo);
}
static void cross_replace(const case_t *old_case,const case_t *new_case,FILE *log){
    allocator_t a={0},b={0};native_vorbis_decoder_t *d=NULL;CHECK(open_case(&d,&a,old_case,true)==0);buffer_t ao=output_for(old_case);replay_prefix(d,&a,old_case,3,&ao);
    native_vorbis_decoder_info_t before=info(d,&a);a.observed=&d;a.old=d;a.release_mode=2;CHECK(open_case(&d,&b,new_case,true)==0&&!a.live&&a.allocations==a.releases);
    native_vorbis_decoder_info_t after=info(d,&b);CHECK(!after.timing.previous_size&&!after.end_of_stream&&after.identification.channels==new_case->fields[2]);
    event(log,6,old_case->fields[0],new_case->fields[0],0,0,&before,&after,2);buffer_t bo=output_for(new_case);uint64_t hash=UINT64_C(14695981039346656037);
    for(uint32_t i=0;i<2;++i){native_vorbis_decoder_packet_t p=packet_for(new_case,i);native_vorbis_decoder_result_t r=successful(d,&b,&p,&bo,&new_case->baseline[i],false);recovery_span(log,new_case,i,&r,&bo);hash=packet_hash(&new_case->baseline[i],hash);}
    cleared(&d,&b);free(a.requests);event_end(log,hash,&a,&b);drop(&ao);drop(&bo);
}
static void http_eof(const case_t *c,FILE *log){
    allocator_t a={0},b={0};native_vorbis_decoder_t *ad=NULL,*bd=NULL;CHECK(open_case(&ad,&a,c,true)==0&&open_case(&bd,&b,c,true)==0);buffer_t ao=output_for(c),bo=output_for(c);
    for(uint32_t i=0;i<13;++i){native_vorbis_decoder_packet_t p=packet_for(c,i);p.end_of_stream=false;
        (void)successful(ad,&a,&p,&ao,&c->baseline[i],false);(void)successful(bd,&b,&p,&bo,&c->baseline[i],false);}
    native_vorbis_decoder_info_t before=info(ad,&a);CHECK(!before.end_of_stream);native_vorbis_decoder_packet_t empty={.granule_position=-1};
    failed_measure(ad,&a,&empty,-3);failed_process(ad,&a,&empty,&ao,ao.bytes/2,-3,true);++other_refusals;native_vorbis_decoder_info_t after=info(ad,&a);CHECK(info_equal(&before,&after));
    event(log,7,c->fields[0],13,0,0,&before,&after,2);native_vorbis_decoder_packet_t p=packet_for(c,13);p.granule_position=-1;p.end_of_stream=false;
    native_vorbis_decoder_result_t ar=successful(ad,&a,&p,&ao,NULL,false),br=successful(bd,&b,&p,&bo,NULL,false);
    CHECK(ar.synthesis.pcm_samples==br.synthesis.pcm_samples&&!memcmp(ao.data,bo.data,(size_t)ar.synthesis.pcm_samples*2));
    size_t bytes=(size_t)ar.synthesis.pcm_samples*2;uint64_t hash=UINT64_C(14695981039346656037);
    for(unsigned i=0;i<2;++i){put32(log,c->fields[0]);put32(log,13);put32(log,(uint32_t)bytes);CHECK(fwrite(i?bo.data:ao.data,1,bytes,log)==bytes);hash=hash_bytes(i?bo.data:ao.data,bytes,hash);}
    cleared(&ad,&a);cleared(&bd,&b);event_end(log,hash,&a,&b);drop(&ao);drop(&bo);
}
typedef struct {case_t stream;buffer_t active,prime;uint64_t active_bits,prime_bits;int status;uint32_t extreme;} supplement_t;
static supplement_t read_supplement(FILE *f,uint32_t index){
    supplement_t s={0};case_t *c=&s.stream;c->fields[0]=index;for(unsigned i=1;i<5;++i)c->fields[i]=get32(f);s.status=(int32_t)get32(f);s.extreme=get32(f);
    c->id=buffer(get32(f));c->setup=buffer(get32(f));s.active=buffer(get32(f));s.prime=buffer(get32(f));s.active_bits=get64(f);s.prime_bits=get64(f);
    CHECK(fread(c->id.data,1,c->id.bytes,f)==c->id.bytes&&fread(c->setup.data,1,c->setup.bytes,f)==c->setup.bytes&&fread(s.active.data,1,s.active.bytes,f)==s.active.bytes&&fread(s.prime.data,1,s.prime.bytes,f)==s.prime.bytes);return s;
}
static void numeric_supplement(supplement_t *s,FILE *log){
    allocator_t a={0};native_vorbis_decoder_t *d=NULL;case_t *c=&s->stream;CHECK(open_case(&d,&a,c,true)==0);buffer_t output=output_for(c);
    native_vorbis_decoder_packet_t p={.data=s->prime.data,.bytes=s->prime.bytes,.bits=s->prime_bits,.granule_position=-1};
    native_vorbis_decoder_result_t r=successful(d,&a,&p,&output,NULL,false);CHECK(!r.synthesis.pcm_samples);native_vorbis_decoder_info_t before=info(d,&a);
    p.data=s->active.data;p.bytes=s->active.bytes;p.bits=s->active_bits;p.end_of_stream=true;native_vorbis_decoder_requirements_t q=measure(d,&a,&p);
    put32(log,c->fields[0]);put32(log,(uint32_t)s->status);info_put(log,&before);
    if(s->status){failed_process(d,&a,&p,&output,(size_t)q.pcm_samples,s->status,false);failed_process(d,&a,&p,&output,(size_t)q.pcm_samples,s->status,false);other_refusals+=2;
        native_vorbis_decoder_info_t after=info(d,&a);info_put(log,&after);CHECK(info_equal(&before,&after)&&!after.end_of_stream);
        p.data=s->prime.data;p.bytes=s->prime.bytes;p.bits=s->prime_bits;p.end_of_stream=false;r=successful(d,&a,&p,&output,NULL,false);
        for(uint64_t i=0;i<r.synthesis.pcm_samples;++i)CHECK(!((int16_t *)output.data)[i]);
    }else{r=successful(d,&a,&p,&output,NULL,false);native_vorbis_decoder_info_t after=info(d,&a);CHECK(after.end_of_stream);info_put(log,&after);}
    put64(log,r.synthesis.pcm_samples);for(uint64_t i=0;i<r.synthesis.pcm_samples;++i)put16(log,((int16_t *)output.data)[i]);
    cleared(&d,&a);put64(log,a.allocations);put64(log,a.releases);put64(log,a.live);drop(&output);
}
static void extreme_supplement(supplement_t *s,FILE *log){
    case_t *c=&s->stream;CHECK(c->fields[2]==255&&c->fields[3]==8192&&c->fields[4]==8192);allocator_t small={.budget=1024*1024};native_vorbis_decoder_t *d=NULL;
    CHECK(open_case(&d,&small,c,true)==-4&&!d&&!small.live&&small.allocations==small.releases&&small.failures==1);put32(log,c->fields[0]);put32(log,(uint32_t)-4);
    put64(log,small.budget);put64(log,small.failed_size);put64(log,small.allocations);put64(log,small.releases);put64(log,small.live);free(small.requests);++other_refusals;
    allocator_t a={.budget=64*1024*1024};CHECK(open_case(&d,&a,c,true)==0);buffer_t output=output_for(c);
    native_vorbis_decoder_packet_t p={.data=s->prime.data,.bytes=s->prime.bytes,.bits=s->prime_bits,.granule_position=-1};
    native_vorbis_decoder_result_t r=successful(d,&a,&p,&output,NULL,false);CHECK(!r.synthesis.pcm_samples);r=successful(d,&a,&p,&output,NULL,true);
    CHECK(r.channels==255&&r.blocksize==8192&&r.synthesis.pcm_samples==UINT64_C(4096)*255);put64(log,r.synthesis.pcm_samples);
    for(uint64_t i=0;i<r.synthesis.pcm_samples;++i){CHECK(!((int16_t *)output.data)[i]);put16(log,((int16_t *)output.data)[i]);}
    size_t calls=a.attempts,frees=a.releases;CHECK(native_vorbis_decoder_reset(d)==0&&a.attempts==calls&&a.releases==frees);cleared(&d,&a);
    put64(log,a.allocations);put64(log,a.releases);put64(log,a.live);put64(log,a.peak_bytes);drop(&output);
}
static void case_drop(case_t *c){
    for(uint32_t i=0;i<c->fields[5];++i){drop(&c->baseline[i].pcm);free(c->baseline[i].requests);}free(c->baseline);free(c->open_requests);
    drop(&c->id);drop(&c->setup);drop(&c->audio);drop(&c->offsets);drop(&c->granules);
}
int main(int argc,char **argv){
    CHECK(argc==4);FILE *input=fopen(argv[1],"rb"),*capture=fopen(argv[2],"wb"),*log=fopen(argv[3],"wb");CHECK(input&&capture&&log);
    char magic[8];CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VSYNIN01",8)&&get32(input)==31);case_t cases[31];
    for(uint32_t i=0;i<31;++i){cases[i]=read_case(input,i);build_baseline(&cases[i]);}
    CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VDECSUP1",8)&&get32(input)==14);supplement_t supplements[14];for(uint32_t i=0;i<14;++i)supplements[i]=read_supplement(input,i);CHECK(fgetc(input)==EOF&&fclose(input)==0);
    CHECK(fwrite("VSYNOUT1",1,8,capture)==8);put32(capture,31);CHECK(fwrite("VDECCTL1",1,8,log)==8);put32(log,31);
    uint64_t events=31+4;
    for(uint32_t i=0;i<31;++i){case_t *c=&cases[i];put32(log,i);put64(log,c->open_allocations);for(size_t j=0;j<c->open_allocations;++j)put64(log,c->open_requests[j]);
        events+=2*c->open_allocations;put32(log,c->fields[5]);for(uint32_t j=0;j<c->fields[5];++j){put64(log,c->baseline[j].allocations);events+=c->baseline[j].allocations;
            for(size_t k=0;k<c->baseline[j].allocations;++k)put64(log,c->baseline[j].requests[k]);}}
    put64(log,events);
    for(uint32_t i=0;i<31;++i){primary(&cases[i],capture,log);open_sweeps(&cases[i],log);replacement_sweeps(&cases[i],log);process_sweeps(&cases[i],log);}
    gap(&cases[0],log);independent(&cases[0],&cases[20],log);cross_replace(&cases[0],&cases[20],log);http_eof(&cases[0],log);
    put32(log,13);for(unsigned i=0;i<13;++i)numeric_supplement(&supplements[i],log);put32(log,1);extreme_supplement(&supplements[13],log);
    for(unsigned i=0;i<31;++i)case_drop(&cases[i]);
    for(unsigned i=0;i<14;++i){drop(&supplements[i].stream.id);drop(&supplements[i].stream.setup);drop(&supplements[i].active);drop(&supplements[i].prime);}
    put64(log,checks);put64(log,undersized);put64(log,measure_calls);put64(log,open_refusals);put64(log,replace_refusals);put64(log,process_refusals);put64(log,other_refusals);
    CHECK(fclose(capture)==0&&fclose(log)==0);printf("DECODER_CAPTURE cases=31 packets=434 pcm_bytes=738560 open=%"PRIu64" replace=%"PRIu64" process=%"PRIu64" undersized=%"PRIu64" measures=%"PRIu64" other=%"PRIu64" checks=%"PRIu64" live=0 bytes=0\n",open_refusals,replace_refusals,process_refusals,undersized,measure_calls,other_refusals,checks);return 0;
}
