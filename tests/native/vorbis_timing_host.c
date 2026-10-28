// Integer metadata only. No decoder, overlap, PCM, or native SDK is executed.
#include "native_vorbis_timing.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

static uint64_t checks,refusals,references;
#define CHECK(x) do { ++checks; assert(x); } while (0)
typedef struct { uint64_t a[2]; native_vorbis_timing_t value; uint64_t z[2]; } state_box_t;
typedef struct { uint64_t a[2]; native_vorbis_timing_event_t value; uint64_t z[2]; } event_box_t;
typedef struct { uint64_t a[2]; native_vorbis_timing_result_t value; uint64_t z[2]; } result_box_t;
static void guard(const uint64_t *a,const uint64_t *z) {
    for(unsigned i=0;i<2;++i){CHECK(a[i]==UINT64_C(0xa5a5a5a5a5a5a5a5));CHECK(z[i]==UINT64_C(0xa5a5a5a5a5a5a5a5));}
}
static uint32_t read32(FILE *f) {unsigned char b[4];CHECK(fread(b,1,4,f)==4);return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;}
static uint64_t read64(FILE *f) {uint64_t low=read32(f);return low|((uint64_t)read32(f)<<32);}
static int64_t signed64(uint64_t u){int64_t v;memcpy(&v,&u,8);return v;}
static void put32(FILE *f,uint32_t u){unsigned char b[4]={(unsigned char)u,(unsigned char)(u>>8),(unsigned char)(u>>16),(unsigned char)(u>>24)};CHECK(fwrite(b,1,4,f)==4);}
static void put64(FILE *f,uint64_t u){put32(f,(uint32_t)u);put32(f,(uint32_t)(u>>32));}
static native_vorbis_timing_t read_state(FILE *f) {
    native_vorbis_timing_t s={0};s.short_size=read32(f);s.long_size=read32(f);s.previous_size=read32(f);
    s.position_known=read32(f);s.end_seen=read32(f);s.bounded_sample_count=read64(f);s.bounded_prediction=read64(f);return s;
}
static native_vorbis_timing_event_t read_event(FILE *f) {
    native_vorbis_timing_event_t e={0};e.blocksize=read32(f);e.granule_position=signed64(read64(f));
    e.end_of_stream=read32(f);e.discontinuity=read32(f);return e;
}
static void state(FILE *f,const native_vorbis_timing_t *s) {
    put32(f,s->short_size);put32(f,s->long_size);put32(f,s->previous_size);put32(f,s->position_known);put32(f,s->end_seen);
    put64(f,s->bounded_sample_count);put64(f,s->bounded_prediction);
}
static void event(FILE *f,const native_vorbis_timing_event_t *e) {
    put32(f,e->blocksize);put64(f,(uint64_t)e->granule_position);put32(f,e->end_of_stream);put32(f,e->discontinuity);
}
static void result(FILE *f,const native_vorbis_timing_result_t *r) {
    put32(f,r->available);put32(f,r->discard_start);put32(f,r->discard_end);put32(f,r->count);
    put32(f,(uint32_t)r->position_kind);put64(f,(uint64_t)r->end_position);
}
static void refused(native_vorbis_timing_t *s,const native_vorbis_timing_event_t *e,native_vorbis_timing_result_t *r) {
    unsigned char sb[sizeof(*s)],eb[sizeof(*e)],rb[sizeof(*r)];
    if(s)memcpy(sb,s,sizeof(sb));
    if(e)memcpy(eb,e,sizeof(eb));
    if(r)memcpy(rb,r,sizeof(rb));
    CHECK(native_vorbis_timing_push(s,e,r)==NATIVE_VORBIS_NUMERIC_INVALID);++refusals;
    if(s)CHECK(!memcmp(sb,s,sizeof(sb)));
    if(e)CHECK(!memcmp(eb,e,sizeof(eb)));
    if(r)CHECK(!memcmp(rb,r,sizeof(rb)));
}
static void invalid_state_controls(native_vorbis_timing_t *s,native_vorbis_timing_event_t *e,native_vorbis_timing_result_t *r) {
    native_vorbis_timing_t bad=*s;
    for(unsigned kind=0;kind<13;++kind){
        bad=*s;
        switch(kind){
            case 0:bad.short_size=63;break;case 1:bad.long_size=8193;break;
            case 2:bad.short_size=8192;bad.long_size=64;break;case 3:bad.previous_size=1;break;
            case 4:bad.position_known=2;break;case 5:bad.end_seen=2;break;
            case 6:bad.bounded_sample_count=NATIVE_VORBIS_TIMING_COUNTER_LIMIT+1;break;
            case 7:bad.bounded_prediction=NATIVE_VORBIS_TIMING_COUNTER_LIMIT+1;break;
            case 8:bad.position_known=0;bad.bounded_prediction=1;break;
            case 9:bad.previous_size=0;bad.position_known=1;break;
            case 10:bad.previous_size=0;bad.end_seen=1;break;
            case 11:bad.previous_size=0;bad.bounded_sample_count=1;break;
            default:bad.previous_size=0;bad.bounded_prediction=1;break;
        }
        refused(&bad,e,r);unsigned char before[sizeof(bad)];memcpy(before,&bad,sizeof(bad));
        CHECK(native_vorbis_timing_reset(&bad)==-1);++refusals;CHECK(!memcmp(before,&bad,sizeof(bad)));
    }
}
static void controls(native_vorbis_timing_t *s) {
    native_vorbis_timing_event_t e={.blocksize=s->short_size,.granule_position=-1};
    native_vorbis_timing_result_t r;memset(&r,0xa5,sizeof(r));
    refused(NULL,&e,&r);refused(s,NULL,&r);refused(s,&e,NULL);
    native_vorbis_timing_event_t bad=e;
    bad.blocksize=0;refused(s,&bad,&r);bad=e;bad.blocksize=63;refused(s,&bad,&r);
    bad=e;bad.granule_position=-2;refused(s,&bad,&r);bad=e;bad.granule_position=INT64_MIN;refused(s,&bad,&r);
    bad=e;bad.end_of_stream=2;refused(s,&bad,&r);bad=e;bad.discontinuity=2;refused(s,&bad,&r);
    invalid_state_controls(s,&e,&r);
    const uint32_t invalid[][2]={{0,64},{63,64},{65,128},{64,8193},{8192,64},{UINT32_MAX,UINT32_MAX}};
    unsigned char before[sizeof(*s)];memcpy(before,s,sizeof(before));
    for(unsigned i=0;i<sizeof(invalid)/sizeof(*invalid);++i){
        CHECK(native_vorbis_timing_init(invalid[i][0],invalid[i][1],s)==-1);++refusals;
        CHECK(!memcmp(before,s,sizeof(before)));
    }
    CHECK(native_vorbis_timing_init(64,64,NULL)==-1);++refusals;
    CHECK(native_vorbis_timing_reset(NULL)==-1);++refusals;
}

// Only this small pinned metadata fragment is reused. Original LP64 long is
// required, and the runner excludes all cases whose signed additions overflow.
_Static_assert(sizeof(long)>=sizeof(int64_t),"LP64 reference fixture required");
static native_vorbis_timing_result_t reference(const native_vorbis_timing_t *s,const native_vorbis_timing_event_t *e) {
    struct {long blocksizes[2];} config={{(long)s->short_size,(long)s->long_size}},*ci=&config;
    struct {int64_t sample_count;} backend={.sample_count=s->previous_size?(int64_t)s->bounded_sample_count:-1},*b=&backend;
    struct {int64_t granulepos;long pcm_current,pcm_returned;int lW,W,eofflag;} decoder={
        .granulepos=s->position_known?(int64_t)s->bounded_prediction:-1,
        .pcm_current=s->previous_size?(long)(s->previous_size+e->blocksize)/4:0,.pcm_returned=0,
        .lW=s->previous_size==s->long_size,.W=e->blocksize==s->long_size,.eofflag=(int)s->end_seen},*v=&decoder;
    struct {int64_t granulepos;int eofflag;} packet={.granulepos=e->granule_position,.eofflag=(int)e->end_of_stream},*vb=&packet;
    int hs=0;
    if(e->discontinuity){b->sample_count=-1;v->granulepos=-1;}
    uint32_t available=(uint32_t)v->pcm_current;
    CHECK(b->sample_count==-1||b->sample_count<=INT64_MAX-(int64_t)available);
    CHECK(v->granulepos==-1||v->granulepos<=INT64_MAX-(int64_t)available);
#include "xiph-granule.inc"
    ++references;
    return (native_vorbis_timing_result_t){.available=available,.discard_start=(uint32_t)v->pcm_returned,
        .discard_end=available-(uint32_t)v->pcm_current,.count=(uint32_t)(v->pcm_current-v->pcm_returned),
        .position_kind=v->granulepos<0?NATIVE_VORBIS_POSITION_UNKNOWN:NATIVE_VORBIS_POSITION_KNOWN,
        .end_position=v->granulepos<0?0:v->granulepos};
}

int main(int argc,char **argv) {
    CHECK(argc==3);FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");CHECK(in&&out);
    unsigned char magic[8];CHECK(fread(magic,1,8,in)==8&&!memcmp(magic,"VTIMIN01",8));
    uint32_t count=read32(in);CHECK(fwrite("VTIMOUT1",1,8,out)==8);put32(out,count);
    state_box_t sb;event_box_t eb;result_box_t rb;memset(&sb,0xa5,sizeof(sb));memset(&eb,0xa5,sizeof(eb));memset(&rb,0xa5,sizeof(rb));
    sb.value=(native_vorbis_timing_t){0};
    for(uint32_t row=0;row<count;++row){
        uint32_t action=read32(in),use_reference=read32(in);native_vorbis_timing_t supplied=read_state(in);eb.value=read_event(in);
        if(action==3)sb.value=supplied;
        native_vorbis_timing_t before=sb.value;native_vorbis_timing_result_t ref={0};memset(&rb.value,0xa5,sizeof(rb.value));
        unsigned char event_before[sizeof(eb.value)];memcpy(event_before,&eb.value,sizeof(eb.value));
        int status;
        if(action==0){status=native_vorbis_timing_init(supplied.short_size,supplied.long_size,&sb.value);CHECK(status==0);controls(&sb.value);}
        else if(action==2){status=native_vorbis_timing_reset(&sb.value);CHECK(status==0);}
        else {CHECK(action==1||action==3);if(use_reference)ref=reference(&before,&eb.value);status=native_vorbis_timing_push(&sb.value,&eb.value,&rb.value);CHECK(status==0);}
        CHECK(!memcmp(event_before,&eb.value,sizeof(eb.value)));guard(sb.a,sb.z);guard(eb.a,eb.z);guard(rb.a,rb.z);
        put32(out,action);put32(out,(uint32_t)status);put32(out,use_reference);state(out,&before);event(out,&eb.value);state(out,&sb.value);
        native_vorbis_timing_result_t empty={0};result(out,action==0||action==2?&empty:&rb.value);result(out,&ref);
    }
    CHECK(fgetc(in)==EOF);CHECK(fclose(in)==0&&fclose(out)==0);
    printf("TIMING_CAPTURE commands=%" PRIu32 " references=%" PRIu64 " refusals=%" PRIu64 " checks=%" PRIu64 "\n",count,references,refusals,checks);
    return 0;
}
