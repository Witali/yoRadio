// Portable text corpus: exact output plus transactional allocation refusals.
#include "native_vorbis_bigfloat.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks,refusals,exports,capacity_refusals,aliases,guard_cases;
static size_t peak_bytes;
#define CHECK(x) do {++checks;assert(x);} while(0)
typedef union allocation allocation_t;
union allocation {max_align_t align;struct {allocation_t *next,*previous;size_t bytes;} value;};
typedef struct {allocation_t *head;uint64_t attempts,allocations,releases,failed_at;size_t live,bytes,peak,failed_bytes;} allocator_t;
static unsigned char *payload(allocation_t *a){return (unsigned char *)(a+1)+16;}
static void allocation_guard(allocation_t *a){unsigned char *p=payload(a);for(unsigned i=0;i<16;++i){CHECK((p-16)[i]==0xa5);CHECK(p[a->value.bytes+i]==0xa5);}}
static void *allocate(void *opaque,size_t bytes){
    allocator_t *a=opaque;CHECK(bytes&&bytes<=SIZE_MAX-sizeof(allocation_t)-32);++a->attempts;
    if(a->failed_at==a->attempts){a->failed_bytes=bytes;return NULL;}
    allocation_t *p=malloc(sizeof(*p)+32+bytes);CHECK(p);memset(p+1,0xa5,32+bytes);p->value.next=a->head;p->value.previous=NULL;p->value.bytes=bytes;
    if(a->head)a->head->value.previous=p;
    a->head=p;++a->allocations;++a->live;a->bytes+=bytes;if(a->bytes>a->peak)a->peak=a->bytes;
    if(a->bytes>peak_bytes)peak_bytes=a->bytes;
    return payload(p);
}
static void release(void *opaque,void *pointer){
    allocator_t *a=opaque;CHECK(pointer);allocation_t *p=(allocation_t *)((unsigned char *)pointer-16)-1;allocation_guard(p);
    if(p->value.previous)p->value.previous->value.next=p->value.next;else{CHECK(a->head==p);a->head=p->value.next;}
    if(p->value.next)p->value.next->value.previous=p->value.previous;
    CHECK(a->live&&a->bytes>=p->value.bytes);--a->live;a->bytes-=p->value.bytes;++a->releases;free(p);
}
static native_vorbis_bigfloat_stats_t stats(native_vorbis_bigfloat_context_t *c,allocator_t *a){
    // Sticky failure can block later engine growth before the supplied callback.
    native_vorbis_bigfloat_stats_t s;CHECK(native_vorbis_bigfloat_stats(c,&s)==0&&s.attempts>=a->attempts&&s.live_allocations==a->live&&s.live_bytes==a->bytes&&s.peak_bytes==a->peak);
    for(allocation_t *p=a->head;p;p=p->value.next)allocation_guard(p);
    return s;
}
typedef struct {int negative;int64_t exponent;size_t count;uint32_t *words;} operand_t;
typedef struct {uint32_t id,precision;int direction;bool sweep;char operation[12];operand_t a,b;} row_t;
typedef struct {bf_t fields;unsigned char *bytes;size_t count;} snapshot_t;
static snapshot_t snapshot(const bf_t *value){
    snapshot_t s={.count=(size_t)value->len*sizeof(*value->tab)};memcpy(&s.fields,value,sizeof(*value));s.bytes=malloc(s.count?s.count:1);CHECK(s.bytes);if(s.count)memcpy(s.bytes,value->tab,s.count);
    return s;
}
static void unchanged(const bf_t *value,const snapshot_t *s){CHECK(!memcmp(value,&s->fields,sizeof(*value)));if(s->count)CHECK(!memcmp(value->tab,s->bytes,s->count));}
static void snapshot_drop(snapshot_t *s){free(s->bytes);}
typedef struct {size_t count,floor_count;uint32_t *words,*floor_words;int64_t exponent;bool negative,floor_negative;} wire_t;
static wire_t wire(native_vorbis_bigfloat_context_t *c,allocator_t *a,const bf_t *value,bool capacities){
    snapshot_t source=snapshot(value);native_vorbis_bigfloat_stats_t before=stats(c,a);wire_t w={0};CHECK(native_vorbis_bigfloat_measure_dyadic(c,value,&w.count)==0&&native_vorbis_bigfloat_measure_floor(c,value,&w.floor_count)==0);
    CHECK(w.count<=NATIVE_VORBIS_BIGFLOAT_MAX_WORDS&&w.floor_count<=NATIVE_VORBIS_BIGFLOAT_MAX_WORDS);
    size_t bytes=(w.count+2)*4,floor_bytes=(w.floor_count+2)*4;w.words=malloc(bytes);w.floor_words=malloc(floor_bytes);CHECK(w.words&&w.floor_words);memset(w.words,0xa5,bytes);memset(w.floor_words,0xa5,floor_bytes);
    if(capacities){
        size_t options[2]={0,w.count?w.count-1:0};
        for(unsigned i=0;i<2&&w.count;++i){if(i&&options[i]==options[0])continue;size_t count=SIZE_MAX;int64_t exponent=INT64_MIN;bool negative=true;
            CHECK(native_vorbis_bigfloat_export_dyadic(c,value,w.words,options[i],&count,&exponent,&negative)==-5&&count==SIZE_MAX&&exponent==INT64_MIN&&negative);
            for(size_t j=0;j<bytes;++j)CHECK(((unsigned char *)w.words)[j]==0xa5);
            ++capacity_refusals;}
        options[1]=w.floor_count?w.floor_count-1:0;
        for(unsigned i=0;i<2&&w.floor_count;++i){if(i&&options[i]==options[0])continue;size_t count=SIZE_MAX;bool negative=true;
            CHECK(native_vorbis_bigfloat_export_floor(c,value,w.floor_words,options[i],&count,&negative)==-5&&count==SIZE_MAX&&negative);
            for(size_t j=0;j<floor_bytes;++j)CHECK(((unsigned char *)w.floor_words)[j]==0xa5);
            ++capacity_refusals;}
    }
    size_t count=SIZE_MAX,floor_count=SIZE_MAX;w.exponent=INT64_MIN;w.negative=w.floor_negative=true;
    CHECK(native_vorbis_bigfloat_export_dyadic(c,value,w.count?w.words:NULL,w.count,&count,&w.exponent,&w.negative)==0&&count==w.count);
    CHECK(native_vorbis_bigfloat_export_floor(c,value,w.floor_count?w.floor_words:NULL,w.floor_count,&floor_count,&w.floor_negative)==0&&floor_count==w.floor_count);
    if(!w.count)CHECK(!w.negative&&!w.exponent);else CHECK(w.words[0]&1);
    if(!w.floor_count)CHECK(!w.floor_negative);
    for(size_t i=w.count*4;i<bytes;++i)CHECK(((unsigned char *)w.words)[i]==0xa5);
    for(size_t i=w.floor_count*4;i<floor_bytes;++i)CHECK(((unsigned char *)w.floor_words)[i]==0xa5);
    native_vorbis_bigfloat_stats_t after=stats(c,a);CHECK(after.attempts==before.attempts&&after.failures==before.failures);unchanged(value,&source);snapshot_drop(&source);++exports;return w;
}
static void wire_drop(wire_t *w){free(w->words);free(w->floor_words);}
static bool wire_equal(const wire_t *a,const wire_t *b){return a->count==b->count&&a->floor_count==b->floor_count&&a->negative==b->negative&&a->floor_negative==b->floor_negative&&a->exponent==b->exponent&&
    !memcmp(a->words,b->words,a->count*4)&&!memcmp(a->floor_words,b->floor_words,a->floor_count*4);}
static void magnitude(const uint32_t *words,size_t count){if(!count){printf("0");return;}printf("%"PRIx32,words[count-1]);for(size_t i=count-1;i;--i)printf("%08"PRIx32,words[i-1]);}
static void wire_print(const wire_t *w){printf(" %u %"PRId64" ",w->negative,w->exponent);magnitude(w->words,w->count);printf(" %u ",w->floor_negative);magnitude(w->floor_words,w->floor_count);}
typedef struct {native_vorbis_bigfloat_context_t context;allocator_t allocation;bf_t a,b,d;} session_t;
static void import_operand(session_t *s,bf_t *d,const operand_t *o){CHECK(native_vorbis_bigfloat_import(&s->context,d,o->words,o->count,o->count?o->exponent:0,o->count&&o->negative)==0);}
static void session_init(session_t *s,const row_t *row){
    memset(s,0,sizeof(*s));native_vorbis_bigfloat_allocator_t callbacks={.opaque=&s->allocation,.allocate=allocate,.release=release};
    CHECK(native_vorbis_bigfloat_context_init(&s->context,&callbacks)==0);memset(&callbacks,0,sizeof(callbacks));
    CHECK(native_vorbis_bigfloat_init(&s->context,&s->a)==0&&native_vorbis_bigfloat_init(&s->context,&s->b)==0&&native_vorbis_bigfloat_init(&s->context,&s->d)==0);
    import_operand(s,&s->a,&row->a);import_operand(s,&s->b,&row->b);uint32_t sentinel=13;CHECK(native_vorbis_bigfloat_import(&s->context,&s->d,&sentinel,1,-3,false)==0);(void)stats(&s->context,&s->allocation);
}
static void session_end(session_t *s){
    CHECK(native_vorbis_bigfloat_clear(&s->context,&s->d)==0&&native_vorbis_bigfloat_clear(&s->context,&s->b)==0&&native_vorbis_bigfloat_clear(&s->context,&s->a)==0);
    uint64_t attempts=s->allocation.attempts;CHECK(native_vorbis_bigfloat_context_end(&s->context)==0&&s->allocation.attempts==attempts&&!s->allocation.head&&!s->allocation.live&&!s->allocation.bytes&&s->allocation.allocations==s->allocation.releases);
}
static int operation(session_t *s,const row_t *row,bf_t *d){
    native_vorbis_bigfloat_context_t *c=&s->context;native_vorbis_bigfloat_round_t rounding=row->direction<0?NATIVE_VORBIS_BIGFLOAT_DOWN:NATIVE_VORBIS_BIGFLOAT_UP;
    if(!strcmp(row->operation,"add"))return native_vorbis_bigfloat_add(c,d,&s->a,&s->b,row->precision,rounding);
    if(!strcmp(row->operation,"sub"))return native_vorbis_bigfloat_sub(c,d,&s->a,&s->b,row->precision,rounding);
    if(!strcmp(row->operation,"mul"))return native_vorbis_bigfloat_mul(c,d,&s->a,&s->b,row->precision,rounding);
    if(!strcmp(row->operation,"div"))return native_vorbis_bigfloat_div(c,d,&s->a,&s->b,row->precision,rounding);
    if(!strcmp(row->operation,"sqrt"))return native_vorbis_bigfloat_sqrt(c,d,&s->a,row->precision,rounding);
    if(!strcmp(row->operation,"round"))return native_vorbis_bigfloat_round(c,d,&s->a,row->precision,rounding);
    if(!strcmp(row->operation,"floor")||!strcmp(row->operation,"copy"))return native_vorbis_bigfloat_copy(c,d,&s->a);
    if(!strcmp(row->operation,"import"))return native_vorbis_bigfloat_import(c,d,row->a.words,row->a.count,row->a.count?row->a.exponent:0,row->a.count&&row->a.negative);
    if(!strcmp(row->operation,"u64")){CHECK(row->a.count<=2&&!row->a.negative&&!row->a.exponent);uint64_t value=row->a.count?row->a.words[0]:0;if(row->a.count==2)value|=(uint64_t)row->a.words[1]<<32;
        return native_vorbis_bigfloat_set_u64(c,d,value);}
    CHECK(false);return -99;
}
static int wanted_status(const row_t *r){bool zero=!r->b.count;return ((!strcmp(r->operation,"div")&&zero)||(!strcmp(r->operation,"sqrt")&&r->a.count&&r->a.negative))?-4:0;}
static void run_case(const row_t *row){
    session_t s;session_init(&s,row);snapshot_t a=snapshot(&s.a),b=snapshot(&s.b),d=snapshot(&s.d);native_vorbis_bigfloat_stats_t before=stats(&s.context,&s.allocation);
    int status=operation(&s,row,&s.d);CHECK(status==wanted_status(row));unchanged(&s.a,&a);unchanged(&s.b,&b);if(status)unchanged(&s.d,&d);
    native_vorbis_bigfloat_stats_t after=stats(&s.context,&s.allocation);uint64_t attempts=after.attempts-before.attempts;wire_t result=wire(&s.context,&s.allocation,&s.d,true);
    printf("BFROW %"PRIu32" %d",row->id,status);wire_print(&result);printf(" %"PRIu64" %u %u %zu\n",attempts,before.ntt_initialized,after.ntt_initialized,s.allocation.peak);
    CHECK(fflush(stdout)==0);
    if(!status&&strcmp(row->operation,"import")&&strcmp(row->operation,"u64")){
        CHECK(operation(&s,row,&s.a)==0);wire_t aliased=wire(&s.context,&s.allocation,&s.a,false);CHECK(wire_equal(&result,&aliased));wire_drop(&aliased);++aliases;
        if(!strcmp(row->operation,"add")||!strcmp(row->operation,"sub")||!strcmp(row->operation,"mul")||!strcmp(row->operation,"div")){
            import_operand(&s,&s.a,&row->a);import_operand(&s,&s.b,&row->b);CHECK(operation(&s,row,&s.b)==0);aliased=wire(&s.context,&s.allocation,&s.b,false);CHECK(wire_equal(&result,&aliased));wire_drop(&aliased);++aliases;}
    }
    snapshot_drop(&a);snapshot_drop(&b);snapshot_drop(&d);session_end(&s);
    if(row->sweep)for(uint64_t ordinal=1;ordinal<=attempts;++ordinal){
        session_init(&s,row);snapshot_t sa=snapshot(&s.a),sb=snapshot(&s.b),sd=snapshot(&s.d);s.allocation.failed_at=s.allocation.attempts+ordinal;
        CHECK(operation(&s,row,&s.d)==-3);unchanged(&s.a,&sa);unchanged(&s.b,&sb);unchanged(&s.d,&sd);native_vorbis_bigfloat_stats_t failed=stats(&s.context,&s.allocation);CHECK(failed.allocation_failed&&failed.failures>=1&&s.allocation.failed_bytes);
        uint64_t sticky_attempts=s.allocation.attempts;CHECK(operation(&s,row,&s.d)==-3&&s.allocation.attempts==sticky_attempts);unchanged(&s.d,&sd);
        s.allocation.failed_at=0;CHECK(native_vorbis_bigfloat_clear_failure(&s.context)==0);wire_t preserved=wire(&s.context,&s.allocation,&s.d,false);CHECK(preserved.count==1&&preserved.words[0]==13&&preserved.exponent==-3&&!preserved.negative);
        CHECK(operation(&s,row,&s.d)==status);wire_t recovered=wire(&s.context,&s.allocation,&s.d,false);CHECK(wire_equal(&result,&recovered));
        printf("BFOOM %"PRIu32" %"PRIu64" %zu",row->id,ordinal,s.allocation.failed_bytes);wire_print(&preserved);wire_print(&recovered);
        wire_drop(&preserved);wire_drop(&recovered);snapshot_drop(&sa);snapshot_drop(&sb);snapshot_drop(&sd);session_end(&s);
        printf(" %"PRIu64" %"PRIu64" %zu\n",s.allocation.allocations,s.allocation.releases,s.allocation.live);CHECK(fflush(stdout)==0);++refusals;
    }
    wire_drop(&result);
}
static void guards(void){
    uint32_t a_word=7,b_word=3;row_t row={.precision=53,.direction=-1,.a={.count=1,.words=&a_word},.b={.count=1,.words=&b_word}};strcpy(row.operation,"add");session_t a,b;session_init(&a,&row);session_init(&b,&row);
    snapshot_t sa=snapshot(&a.d),sb=snapshot(&b.d);native_vorbis_bigfloat_stats_t before=stats(&a.context,&a.allocation);uint32_t precisions[3]={0,1,NATIVE_VORBIS_BIGFLOAT_MAX_BITS+1};
    for(unsigned i=0;i<3;++i){CHECK(native_vorbis_bigfloat_add(&a.context,&a.d,&a.a,&a.b,precisions[i],NATIVE_VORBIS_BIGFLOAT_DOWN)==(i==2?-2:-1));unchanged(&a.d,&sa);++guard_cases;}
    CHECK(native_vorbis_bigfloat_add(&a.context,&a.d,&a.a,&a.b,53,(native_vorbis_bigfloat_round_t)2)==-1);unchanged(&a.d,&sa);++guard_cases;
    CHECK(native_vorbis_bigfloat_copy(&a.context,&a.d,&b.a)==-1&&native_vorbis_bigfloat_add(&a.context,&a.d,&a.a,&b.b,53,NATIVE_VORBIS_BIGFLOAT_UP)==-1);unchanged(&a.d,&sa);unchanged(&b.d,&sb);guard_cases+=2;
    uint32_t zero=0,one=1;
    CHECK(native_vorbis_bigfloat_import(&a.context,&a.d,&zero,1,0,false)==-1&&native_vorbis_bigfloat_import(&a.context,&a.d,NULL,0,1,false)==-1&&native_vorbis_bigfloat_import(&a.context,&a.d,NULL,0,0,true)==-1);unchanged(&a.d,&sa);guard_cases+=3;
    CHECK(native_vorbis_bigfloat_import(&a.context,&a.d,&one,NATIVE_VORBIS_BIGFLOAT_MAX_WORDS+1,0,false)==-2&&native_vorbis_bigfloat_import(&a.context,&a.d,&one,1,INT64_MIN,false)==-2&&native_vorbis_bigfloat_import(&a.context,&a.d,&one,1,INT64_MAX,false)==-2);unchanged(&a.d,&sa);guard_cases+=3;
    size_t count=SIZE_MAX;int64_t exponent=INT64_MIN;bool negative=true;uint32_t output[4]={1,2,3,4};
    CHECK(native_vorbis_bigfloat_export_dyadic(&a.context,&a.a,output,SIZE_MAX/4+1,&count,&exponent,&negative)==-2&&count==SIZE_MAX&&exponent==INT64_MIN&&negative&&output[0]==1&&output[3]==4);++guard_cases;
    CHECK(native_vorbis_bigfloat_export_floor(&a.context,&a.a,output,SIZE_MAX/4+1,&count,&negative)==-2&&count==SIZE_MAX&&negative&&output[0]==1&&output[3]==4);++guard_cases;
    CHECK(native_vorbis_bigfloat_add(&a.context,NULL,&a.a,&a.b,53,NATIVE_VORBIS_BIGFLOAT_DOWN)==-1&&native_vorbis_bigfloat_copy(NULL,&a.d,&a.a)==-1&&native_vorbis_bigfloat_measure_dyadic(&a.context,&a.a,NULL)==-1);unchanged(&a.d,&sa);guard_cases+=3;
    native_vorbis_bigfloat_stats_t after=stats(&a.context,&a.allocation);CHECK(after.attempts==before.attempts);CHECK(operation(&a,&row,&a.d)==0);wire_t actual=wire(&a.context,&a.allocation,&a.d,true);CHECK(actual.count==1&&actual.words[0]==5&&actual.exponent==1&&!actual.negative);wire_drop(&actual);unchanged(&b.d,&sb);
    CHECK(native_vorbis_bigfloat_context_end(&a.context)==-1);++guard_cases;wire_t still=wire(&a.context,&a.allocation,&a.d,false);CHECK(still.count==1&&still.words[0]==5&&still.exponent==1);wire_drop(&still);
    snapshot_drop(&sa);snapshot_drop(&sb);session_end(&a);session_end(&b);printf("BFGUARD %"PRIu64"\n",guard_cases);
}
typedef struct {const char *text;size_t length,at;} reader_t;
static void token(reader_t *r,const char **start,size_t *length){while(r->at<r->length&&(r->text[r->at]==' '||r->text[r->at]=='\n'||r->text[r->at]=='\r'))++r->at;size_t begin=r->at;while(r->at<r->length&&r->text[r->at]!=' '&&r->text[r->at]!='\n'&&r->text[r->at]!='\r')++r->at;*start=r->text+begin;*length=r->at-begin;CHECK(*length);}
static uint64_t decimal(reader_t *r,bool *negative){const char *p;size_t length;token(r,&p,&length);size_t at=0;*negative=p[0]=='-';if(*negative)++at;CHECK(at<length);uint64_t value=0;for(;at<length;++at){CHECK(p[at]>='0'&&p[at]<='9'&&value<=(UINT64_MAX-(unsigned)(p[at]-'0'))/10);value=value*10+(unsigned)(p[at]-'0');}return value;}
static uint64_t positive(reader_t *r){bool negative;uint64_t value=decimal(r,&negative);CHECK(!negative);return value;}
static int64_t signed_decimal(reader_t *r){bool negative;uint64_t value=decimal(r,&negative);CHECK(value<=(negative?UINT64_C(1)<<63:INT64_MAX));if(negative){if(value==UINT64_C(1)<<63)return INT64_MIN;return -(int64_t)value;}return (int64_t)value;}
static operand_t operand(reader_t *r){operand_t out={0};out.negative=(int)positive(r);CHECK(out.negative<=1);out.exponent=signed_decimal(r);const char *p;size_t length;token(r,&p,&length);CHECK(length&&length<=NATIVE_VORBIS_BIGFLOAT_MAX_WORDS*8);
    out.count=(length+7)/8;out.words=calloc(out.count,4);CHECK(out.words);for(size_t i=0;i<length;++i){unsigned char ch=(unsigned char)p[length-1-i];unsigned value=ch>='0'&&ch<='9'?ch-'0':ch>='a'&&ch<='f'?ch-'a'+10:16;CHECK(value<16);out.words[i/8]|=(uint32_t)value<<(4*(i%8));}
    while(out.count&&!out.words[out.count-1])--out.count;
    return out;
}
int native_vorbis_bigfloat_fixture_run(const char *text,size_t length){
    CHECK(text);checks=refusals=exports=capacity_refusals=aliases=guard_cases=0;peak_bytes=0;reader_t r={.text=text,.length=length};const char *p;size_t n;token(&r,&p,&n);CHECK(n==8&&!memcmp(p,"VBFCASE1",8));uint64_t cases=positive(&r);CHECK(cases<=10000);
    printf("BFBEGIN 1 %u %"PRIu64"\n",LIMB_BITS,cases);
    CHECK(fflush(stdout)==0);
    for(uint32_t i=0;i<cases;++i){row_t row={0};row.id=(uint32_t)positive(&r);CHECK(row.id==i);token(&r,&p,&n);CHECK(n<sizeof(row.operation));memcpy(row.operation,p,n);row.operation[n]=0;
        uint64_t precision=positive(&r);CHECK(precision<=UINT32_MAX);row.precision=(uint32_t)precision;row.direction=(int)signed_decimal(&r);CHECK(row.direction==1||row.direction==-1);row.sweep=positive(&r)!=0;row.a=operand(&r);row.b=operand(&r);
        run_case(&row);free(row.a.words);free(row.b.words);}
    while(r.at<r.length){CHECK(r.text[r.at]==' '||r.text[r.at]=='\r'||r.text[r.at]=='\n');++r.at;}guards();
    printf("BFEND %"PRIu64" %"PRIu64" %"PRIu64" %"PRIu64" %"PRIu64" %"PRIu64" %zu 0 0\n",cases,refusals,exports,capacity_refusals,aliases,checks,peak_bytes);return 0;
}
#ifndef ESP_PLATFORM
int main(int argc,char **argv){CHECK(argc==2);FILE *f=fopen(argv[1],"rb");CHECK(f&&fseek(f,0,SEEK_END)==0);long end=ftell(f);CHECK(end>=0&&fseek(f,0,SEEK_SET)==0);size_t bytes=(size_t)end;char *text=malloc(bytes?bytes:1);CHECK(text&&fread(text,1,bytes,f)==bytes&&fclose(f)==0);int result=native_vorbis_bigfloat_fixture_run(text,bytes);free(text);return result;}
#endif
