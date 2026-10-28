// DEFERRED, UNQUALIFIED WIP. See docs/CYD_VORBIS_EXTENDED_DEFERRED_20261028.md.
// Independent host driver. MPFR point probes are a separate compile selection.
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks;
#define CHECK(x) do {++checks;assert(x);} while(0)
typedef struct {const char *text;size_t length,at;} reader_t;
static void token(reader_t *r,const char **text,size_t *length){while(r->at<r->length&&(r->text[r->at]==' '||r->text[r->at]=='\n'||r->text[r->at]=='\r'))++r->at;size_t begin=r->at;while(r->at<r->length&&r->text[r->at]!=' '&&r->text[r->at]!='\n'&&r->text[r->at]!='\r')++r->at;*text=r->text+begin;*length=r->at-begin;CHECK(*length);}
static uint64_t decimal(reader_t *r,bool *negative){const char *p;size_t n;token(r,&p,&n);size_t at=0;*negative=p[0]=='-';if(*negative)++at;CHECK(at<n);uint64_t value=0;for(;at<n;++at){CHECK(p[at]>='0'&&p[at]<='9'&&value<=(UINT64_MAX-(unsigned)(p[at]-'0'))/10);value=value*10+(unsigned)(p[at]-'0');}return value;}
static uint64_t positive(reader_t *r){bool negative;uint64_t value=decimal(r,&negative);CHECK(!negative);return value;}
static int64_t signed_decimal(reader_t *r){bool negative;uint64_t value=decimal(r,&negative);CHECK(value<=(negative?UINT64_C(1)<<63:INT64_MAX));if(negative){if(value==UINT64_C(1)<<63)return INT64_MIN;return -(int64_t)value;}return (int64_t)value;}
static void finish(reader_t *r){while(r->at<r->length){CHECK(r->text[r->at]==' '||r->text[r->at]=='\n'||r->text[r->at]=='\r');++r->at;}}
typedef struct {uint32_t *words;size_t count;int64_t exponent;bool negative;} dyadic_t;
static dyadic_t read_dyadic(reader_t *r){dyadic_t a={0};a.negative=positive(r)!=0;a.exponent=signed_decimal(r);const char *p;size_t n;token(r,&p,&n);CHECK(n<=262144);a.count=(n+7)/8;a.words=calloc(a.count,4);CHECK(a.words);for(size_t i=0;i<n;++i){unsigned char c=(unsigned char)p[n-i-1];unsigned v=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:16;CHECK(v<16);a.words[i/8]|=(uint32_t)v<<(4*(i%8));}while(a.count&&!a.words[a.count-1])--a.count;return a;}
typedef struct {uint32_t id,precision;bool sweep;char operation[12];dyadic_t endpoints[4];} primitive_t;
static primitive_t read_primitive(reader_t *r){primitive_t row={0};row.id=(uint32_t)positive(r);const char *p;size_t n;token(r,&p,&n);CHECK(n<sizeof(row.operation));memcpy(row.operation,p,n);row.precision=(uint32_t)positive(r);row.sweep=positive(r)!=0;for(unsigned i=0;i<4;++i)row.endpoints[i]=read_dyadic(r);return row;}
static void primitive_drop(primitive_t *p){for(unsigned i=0;i<4;++i)free(p->endpoints[i].words);}

#ifdef VC_GAIN_MPFR_PROBES
#include <mpfr.h>
static void mpfr_dyadic(mpfr_t d,const dyadic_t *a){mpz_t z;mpz_init(z);mpz_import(z,a->count,-1,4,0,0,a->words);if(a->negative)mpz_neg(z,z);CHECK(mpfr_set_z_2exp(d,z,(mpfr_exp_t)a->exponent,MPFR_RNDN)==0);mpz_clear(z);}
static void mpfr_wire(const mpfr_t value){mpz_t z;mpz_init(z);mpfr_exp_t exponent=mpfr_get_z_2exp(z,value);if(!mpz_sgn(z))exponent=0;else{mp_bitcnt_t bits=mpz_scan1(z,0);mpz_tdiv_q_2exp(z,z,bits);exponent+=(mpfr_exp_t)bits;}printf(" ");mpz_out_str(stdout,16,z);printf(" %"PRId64,(int64_t)exponent);mpz_clear(z);}
static void reference_probes(reader_t *r,uint32_t count){
    printf("VCREF_BEGIN 1 %"PRIu32"\n",count);
    for(uint32_t i=0;i<count;++i){primitive_t p=read_primitive(r);if(strcmp(p.operation,"pi")&&strcmp(p.operation,"ln2")&&strcmp(p.operation,"sin")&&strcmp(p.operation,"cos")){primitive_drop(&p);continue;}
        mpfr_prec_t precision=(mpfr_prec_t)(p.precision*4<2048?2048:p.precision*4);mpfr_t value,lo,hi;mpfr_inits2(precision,value,lo,hi,(mpfr_ptr)0);
        if(!strcmp(p.operation,"pi")){mpfr_const_pi(lo,MPFR_RNDD);mpfr_const_pi(hi,MPFR_RNDU);}
        else if(!strcmp(p.operation,"ln2")){mpfr_const_log2(lo,MPFR_RNDD);mpfr_const_log2(hi,MPFR_RNDU);}
        else{mpfr_dyadic(value,&p.endpoints[0]);if(!strcmp(p.operation,"sin")){mpfr_sin(lo,value,MPFR_RNDD);mpfr_sin(hi,value,MPFR_RNDU);}else{mpfr_cos(lo,value,MPFR_RNDD);mpfr_cos(hi,value,MPFR_RNDU);}}
        printf("VCREF_ROW %"PRIu32" %"PRId64,p.id,(int64_t)precision);mpfr_wire(lo);mpfr_wire(hi);printf("\n");CHECK(fflush(stdout)==0);mpfr_clears(value,lo,hi,(mpfr_ptr)0);primitive_drop(&p);
    }
    finish(r);mpfr_free_cache();printf("VCREF_END 0\n");
}
#else
#include "native_vorbis_certified_gain.h"

static uint64_t refusals,capacity_refusals,guards,negatives;
typedef union allocation allocation_t;
union allocation {max_align_t align;struct {allocation_t *next,*previous;size_t bytes;} record;};
typedef struct {allocation_t *head;uint64_t attempts,allocations,releases,fail_at;size_t live,bytes,peak,failed_bytes;} ledger_t;
static unsigned char *payload(allocation_t *a){return (unsigned char *)(a+1)+16;}
static void allocation_guard(allocation_t *a){unsigned char *p=payload(a);for(unsigned i=0;i<16;++i){CHECK((p-16)[i]==0xa5);CHECK(p[a->record.bytes+i]==0xa5);}}
static void *allocate(void *opaque,size_t bytes){ledger_t *a=opaque;CHECK(bytes&&bytes<=SIZE_MAX-sizeof(allocation_t)-32);++a->attempts;if(a->attempts==a->fail_at){a->failed_bytes=bytes;return NULL;}allocation_t *p=malloc(sizeof(*p)+32+bytes);CHECK(p);memset(p+1,0xa5,bytes+32);p->record.next=a->head;p->record.previous=NULL;p->record.bytes=bytes;if(a->head)a->head->record.previous=p;a->head=p;++a->allocations;++a->live;a->bytes+=bytes;if(a->bytes>a->peak)a->peak=a->bytes;return payload(p);}
static void release(void *opaque,void *pointer){ledger_t *a=opaque;CHECK(pointer);allocation_t *p=(allocation_t *)((unsigned char *)pointer-16)-1;allocation_guard(p);if(p->record.previous)p->record.previous->record.next=p->record.next;else{CHECK(a->head==p);a->head=p->record.next;}if(p->record.next)p->record.next->record.previous=p->record.previous;CHECK(a->live&&a->bytes>=p->record.bytes);--a->live;a->bytes-=p->record.bytes;++a->releases;free(p);}
static native_vorbis_bigfloat_stats_t stats(native_vorbis_bigfloat_context_t *context,ledger_t *a){native_vorbis_bigfloat_stats_t s;CHECK(native_vorbis_bigfloat_stats(context,&s)==0&&s.attempts>=a->attempts&&s.live_allocations==a->live&&s.live_bytes==a->bytes&&s.peak_bytes==a->peak);for(allocation_t *p=a->head;p;p=p->record.next)allocation_guard(p);return s;}
typedef struct {bf_t fields;unsigned char *bytes;size_t count;} number_snapshot_t;
static number_snapshot_t number_snapshot(const bf_t *v){number_snapshot_t s={.count=(size_t)v->len*sizeof(*v->tab)};memcpy(&s.fields,v,sizeof(*v));s.bytes=malloc(s.count?s.count:1);CHECK(s.bytes);if(s.count)memcpy(s.bytes,v->tab,s.count);return s;}
static void number_unchanged(const bf_t *v,const number_snapshot_t *s){CHECK(!memcmp(v,&s->fields,sizeof(*v)));if(s->count)CHECK(!memcmp(v->tab,s->bytes,s->count));}
static void number_snapshot_drop(number_snapshot_t *s){free(s->bytes);}
typedef struct {unsigned char bytes[sizeof(native_vorbis_gain_result_t)];number_snapshot_t values[4];} gain_snapshot_t;
static gain_snapshot_t gain_snapshot(const native_vorbis_gain_result_t *r){gain_snapshot_t s;memcpy(s.bytes,r,sizeof(*r));const bf_t *v[4]={&r->denominator.lo,&r->denominator.hi,&r->log2_gain.lo,&r->log2_gain.hi};for(unsigned i=0;i<4;++i)s.values[i]=number_snapshot(v[i]);return s;}
static void gain_unchanged(const native_vorbis_gain_result_t *r,const gain_snapshot_t *s){CHECK(!memcmp(r,s->bytes,sizeof(*r)));const bf_t *v[4]={&r->denominator.lo,&r->denominator.hi,&r->log2_gain.lo,&r->log2_gain.hi};for(unsigned i=0;i<4;++i)number_unchanged(v[i],&s->values[i]);}
static void gain_snapshot_drop(gain_snapshot_t *s){for(unsigned i=0;i<4;++i)number_snapshot_drop(&s->values[i]);}
static void magnitude(const uint32_t *words,size_t count){if(!count){printf("0");return;}printf("%"PRIx32,words[count-1]);for(size_t i=count-1;i;--i)printf("%08"PRIx32,words[i-1]);}
typedef struct {uint32_t *words;size_t count;int64_t exponent;bool negative;} number_wire_t;
static number_wire_t number_wire(native_vorbis_bigfloat_context_t *c,const bf_t *value){number_wire_t w={0};CHECK(native_vorbis_bigfloat_measure_dyadic(c,value,&w.count)==0);w.words=malloc((w.count+2)*4);CHECK(w.words);memset(w.words,0xa5,(w.count+2)*4);size_t count=SIZE_MAX;CHECK(native_vorbis_bigfloat_export_dyadic(c,value,w.count?w.words:NULL,w.count,&count,&w.exponent,&w.negative)==0&&count==w.count);for(size_t i=w.count*4;i<(w.count+2)*4;++i)CHECK(((unsigned char *)w.words)[i]==0xa5);return w;}
static void number_print(const number_wire_t *w){printf(" %u %"PRId64" ",w->negative,w->exponent);magnitude(w->words,w->count);}
typedef struct {native_vorbis_gain_kind_t kind;bool has_denominator,has_log;uint32_t precision;number_wire_t values[4];uint32_t *lower,*upper;native_vorbis_gain_floor_result_t floor;} gain_wire_t;
static gain_wire_t gain_wire(native_vorbis_gain_workspace_t *w,ledger_t *a,const native_vorbis_gain_result_t *result,bool capacities){
    gain_snapshot_t before=gain_snapshot(result);native_vorbis_bigfloat_stats_t old=stats(&w->arithmetic,a);gain_wire_t out={.kind=result->kind,.has_denominator=result->has_denominator,.has_log=result->has_log,.precision=result->precision};
    const bf_t *values[4]={&result->denominator.lo,&result->denominator.hi,&result->log2_gain.lo,&result->log2_gain.hi};for(unsigned i=0;i<4;++i)out.values[i]=number_wire(&w->arithmetic,values[i]);
    if(result->has_log){native_vorbis_gain_floor_requirements_t needed;CHECK(native_vorbis_gain_floor_measure(w,result,&needed)==0);size_t lb=(needed.lower_words+2)*4,ub=(needed.upper_words+2)*4;out.lower=malloc(lb);out.upper=malloc(ub);CHECK(out.lower&&out.upper);memset(out.lower,0xa5,lb);memset(out.upper,0xa5,ub);
        if(capacities){size_t tests[4][2]={{0,needed.upper_words},{needed.lower_words?needed.lower_words-1:0,needed.upper_words},{needed.lower_words,0},{needed.lower_words,needed.upper_words?needed.upper_words-1:0}};
            for(unsigned i=0;i<4;++i){if(tests[i][0]>=needed.lower_words&&tests[i][1]>=needed.upper_words)continue;bool duplicate=false;for(unsigned j=0;j<i;++j)duplicate|=tests[j][0]==tests[i][0]&&tests[j][1]==tests[i][1];if(duplicate)continue;
                native_vorbis_gain_floor_result_t output={.lower_words=SIZE_MAX,.upper_words=SIZE_MAX,.lower_negative=true,.upper_negative=true,.equal=true};unsigned char saved[sizeof(output)];memcpy(saved,&output,sizeof(output));
                CHECK(native_vorbis_gain_floor_export(w,result,out.lower,tests[i][0],out.upper,tests[i][1],&output)==-5&&!memcmp(saved,&output,sizeof(output)));
                for(size_t j=0;j<lb;++j)CHECK(((unsigned char *)out.lower)[j]==0xa5);for(size_t j=0;j<ub;++j)CHECK(((unsigned char *)out.upper)[j]==0xa5);++capacity_refusals;}}
        CHECK(native_vorbis_gain_floor_export(w,result,needed.lower_words?out.lower:NULL,needed.lower_words,needed.upper_words?out.upper:NULL,needed.upper_words,&out.floor)==0&&out.floor.lower_words==needed.lower_words&&out.floor.upper_words==needed.upper_words);
        for(size_t i=needed.lower_words*4;i<lb;++i)CHECK(((unsigned char *)out.lower)[i]==0xa5);for(size_t i=needed.upper_words*4;i<ub;++i)CHECK(((unsigned char *)out.upper)[i]==0xa5);
    }
    native_vorbis_bigfloat_stats_t after=stats(&w->arithmetic,a);CHECK(after.attempts==old.attempts&&after.live_bytes==old.live_bytes);gain_unchanged(result,&before);gain_snapshot_drop(&before);return out;
}
static void gain_print(const gain_wire_t *w){printf(" %u %u %u %"PRIu32,w->kind,w->has_denominator,w->has_log,w->precision);for(unsigned i=0;i<4;++i)number_print(&w->values[i]);printf(" %u ",w->floor.lower_negative);magnitude(w->lower,w->floor.lower_words);printf(" %u ",w->floor.upper_negative);magnitude(w->upper,w->floor.upper_words);printf(" %u",w->floor.equal);}
static void gain_wire_drop(gain_wire_t *w){for(unsigned i=0;i<4;++i)free(w->values[i].words);free(w->lower);free(w->upper);}
typedef struct {native_vorbis_gain_workspace_t workspace;native_vorbis_gain_result_t result;ledger_t allocation;} gain_session_t;
static int seed(gain_session_t *s){native_vorbis_gain_input_t in={.amplitude={.raw_amplitude=1,.amplitude_bits=8,.amplitude_offset=60},.bark_map_size=1};return native_vorbis_gain_enclose(&s->workspace,&in,16,&s->result);}
static void gain_session_init(gain_session_t *s){memset(s,0,sizeof(*s));native_vorbis_bigfloat_allocator_t allocator={.opaque=&s->allocation,.allocate=allocate,.release=release};CHECK(native_vorbis_gain_workspace_init(&s->workspace,&allocator)==0);memset(&allocator,0,sizeof(allocator));CHECK(native_vorbis_gain_result_init(&s->workspace,&s->result)==0&&seed(s)==0&&s->result.has_log);}
static void gain_session_end(gain_session_t *s){uint64_t attempts=s->allocation.attempts;CHECK(native_vorbis_gain_result_clear(&s->workspace,&s->result)==0&&native_vorbis_gain_workspace_end(&s->workspace)==0&&s->allocation.attempts==attempts&&!s->allocation.live&&!s->allocation.bytes&&s->allocation.allocations==s->allocation.releases);}
typedef struct {uint32_t id;native_vorbis_gain_input_t input;native_vorbis_affine_t *angles;} gain_input_t;
static gain_input_t read_gain(reader_t *r){gain_input_t g={0};g.id=(uint32_t)positive(r);g.input.order=(size_t)positive(r);g.input.bark_index=(uint32_t)positive(r);g.input.bark_map_size=(uint32_t)positive(r);g.input.amplitude.amplitude_bits=(uint32_t)positive(r);g.input.amplitude.raw_amplitude=positive(r);g.input.amplitude.amplitude_offset=(uint32_t)positive(r);CHECK(g.input.order<=255);if(g.input.order){g.angles=calloc(g.input.order,sizeof(*g.angles));CHECK(g.angles);for(size_t i=0;i<g.input.order;++i){g.angles[i].minimum_bits=(uint32_t)positive(r);g.angles[i].delta_bits=(uint32_t)positive(r);g.angles[i].minimum_multiplier=(uint32_t)positive(r);g.angles[i].delta_multiplier=(uint32_t)positive(r);}}g.input.angles=g.angles;return g;}
static int gain_call(gain_session_t *s,const gain_input_t *g,uint32_t precision){native_vorbis_gain_input_t input=g->input;size_t bytes=g->input.order*sizeof(*g->angles);native_vorbis_affine_t *copy=bytes?malloc(bytes):NULL;CHECK(!bytes||copy);if(bytes)memcpy(copy,g->angles,bytes);input.angles=copy;unsigned char saved[sizeof(input)];memcpy(saved,&input,sizeof(input));int status=native_vorbis_gain_enclose(&s->workspace,&input,precision,&s->result);CHECK(!memcmp(saved,&input,sizeof(input))&&(!bytes||!memcmp(copy,g->angles,bytes)));if(bytes)memset(copy,0xdb,bytes);free(copy);memset(&input,0xdc,sizeof(input));return status;}
static void gain_rows(reader_t *r,uint32_t count,uint32_t precision,bool sweep,bool warm){
    printf("VCG_BEGIN 1 %u %"PRIu32" %"PRIu32" %u %u\n",LIMB_BITS,precision,count,sweep,warm);CHECK(fflush(stdout)==0);gain_session_t shared;if(!sweep){gain_session_init(&shared);gain_wire_t seed_wire=gain_wire(&shared.workspace,&shared.allocation,&shared.result,false);printf("VCG_SEED 0");gain_print(&seed_wire);printf("\n");gain_wire_drop(&seed_wire);}
    for(uint32_t i=0;i<count;++i){gain_input_t input=read_gain(r);gain_session_t local;gain_session_t *s=sweep?&local:&shared;if(sweep)gain_session_init(s);if(warm){CHECK(gain_call(s,&input,precision)==0&&seed(s)==0);}
        gain_snapshot_t before=gain_snapshot(&s->result);native_vorbis_bigfloat_stats_t old=stats(&s->workspace.arithmetic,&s->allocation);uint64_t callbacks=s->allocation.attempts;int status=gain_call(s,&input,precision);if(status){gain_unchanged(&s->result,&before);++negatives;}
        native_vorbis_bigfloat_stats_t after=stats(&s->workspace.arithmetic,&s->allocation);uint64_t attempts=s->allocation.attempts-callbacks;gain_wire_t current=gain_wire(&s->workspace,&s->allocation,&s->result,true);printf("VCG_ROW %"PRIu32" %d",input.id,status);gain_print(&current);printf(" %"PRIu64" %"PRIu64" %zu\n",attempts,after.attempts-old.attempts,s->allocation.peak);CHECK(fflush(stdout)==0);gain_snapshot_drop(&before);
        if(sweep){CHECK(status==0);gain_session_end(s);for(uint64_t ordinal=1;ordinal<=attempts;++ordinal){gain_session_init(s);if(warm)CHECK(gain_call(s,&input,precision)==0&&seed(s)==0);gain_snapshot_t saved=gain_snapshot(&s->result);s->allocation.fail_at=s->allocation.attempts+ordinal;
                CHECK(gain_call(s,&input,precision)==-3);gain_unchanged(&s->result,&saved);native_vorbis_bigfloat_stats_t failed=stats(&s->workspace.arithmetic,&s->allocation);CHECK(failed.allocation_failed&&s->allocation.failed_bytes);uint64_t blocked=s->allocation.attempts;CHECK(gain_call(s,&input,precision)==-3&&s->allocation.attempts==blocked);gain_unchanged(&s->result,&saved);
                s->allocation.fail_at=0;CHECK(native_vorbis_gain_clear_failure(&s->workspace)==0);gain_wire_t preserved=gain_wire(&s->workspace,&s->allocation,&s->result,false);CHECK(gain_call(s,&input,precision)==0);gain_wire_t recovered=gain_wire(&s->workspace,&s->allocation,&s->result,false);CHECK(recovered.kind==current.kind&&recovered.has_log==current.has_log&&recovered.has_denominator==current.has_denominator);
                printf("VCG_OOM %"PRIu32" %"PRIu64" %zu",input.id,ordinal,s->allocation.failed_bytes);gain_print(&preserved);gain_print(&recovered);gain_wire_drop(&preserved);gain_wire_drop(&recovered);gain_snapshot_drop(&saved);gain_session_end(s);printf(" %"PRIu64" %"PRIu64" %zu %zu\n",s->allocation.allocations,s->allocation.releases,s->allocation.live,s->allocation.bytes);CHECK(fflush(stdout)==0);++refusals;}}
        gain_wire_drop(&current);free(input.angles);
    }
    if(!sweep)gain_session_end(&shared);finish(r);printf("VCG_END %"PRIu32" %"PRIu64" %"PRIu64" %"PRIu64" %"PRIu64" 0 0\n",count,negatives,refusals,capacity_refusals,checks);
}

#endif

int main(int argc,char **argv){CHECK(argc==2);FILE *file=fopen(argv[1],"rb");CHECK(file&&fseek(file,0,SEEK_END)==0);long n=ftell(file);CHECK(n>=0&&fseek(file,0,SEEK_SET)==0);char *text=malloc(n?(size_t)n:1);CHECK(text&&fread(text,1,(size_t)n,file)==(size_t)n&&fclose(file)==0);reader_t r={.text=text,.length=(size_t)n};const char *magic;size_t length;token(&r,&magic,&length);
#ifdef VC_GAIN_MPFR_PROBES
    CHECK(length==6&&!memcmp(magic,"VCINT1",6));uint32_t count=(uint32_t)positive(&r);reference_probes(&r,count);
#else
    if(length==7&&!memcmp(magic,"VCGAIN1",7)){uint32_t count=(uint32_t)positive(&r),precision=(uint32_t)positive(&r);bool sweep=positive(&r)!=0,warm=positive(&r)!=0;gain_rows(&r,count,precision,sweep,warm);}
    else CHECK(false);
#endif
    free(text);return 0;
}
