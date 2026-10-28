// New exact-product PCM and window slices only; legacy captures are input DATA.
#include "native_vorbis_pcm_exact.h"
#define main unused_window_fixture_main
#include "vorbis_window_host.c"
#undef main
#include <fenv.h>

static uint32_t get32(FILE *f){unsigned char b[4];CHECK(fread(b,1,4,f)==4);return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;}
static uint64_t get64(FILE *f){uint64_t low=get32(f);return low|(uint64_t)get32(f)<<32;}
static int64_t get_signed(FILE *f){uint64_t u=get64(f);int64_t s;memcpy(&s,&u,8);return s;}
static double from_bits(uint64_t word){double d;memcpy(&d,&word,8);return d;}
static void put16(FILE *f,int16_t value){uint16_t u;memcpy(&u,&value,2);unsigned char b[2]={(unsigned char)u,(unsigned char)(u>>8)};CHECK(fwrite(b,1,2,f)==2);}
typedef struct {unsigned char *raw,*data;size_t bytes;} buffer_t;
// Every buffer in this finite host corpus fits the largest saved PCM batch.
static buffer_t buffer(size_t bytes){CHECK(bytes<=SIZE_MAX-32&&bytes<=(size_t)65540*8+32);buffer_t b={.raw=malloc(bytes+32),.bytes=bytes};CHECK(b.raw);b.data=b.raw+16;memset(b.raw,0xa5,bytes+32);return b;}
static void check_buffer(const buffer_t *b){for(unsigned i=0;i<16;++i){CHECK(b->raw[i]==0xa5);CHECK(b->data[b->bytes+i]==0xa5);}}
static buffer_t snapshot(const buffer_t *b){buffer_t copy=buffer(b->bytes);memcpy(copy.data,b->data,b->bytes);return copy;}
static void unchanged_buffer(const buffer_t *b,const buffer_t *copy){check_buffer(b);CHECK(b->bytes==copy->bytes&&!memcmp(b->data,copy->data,b->bytes));}
static void drop(buffer_t *b){check_buffer(b);free(b->raw);}
static bool product_equal(const native_vorbis_window_product_t *a,const native_vorbis_window_product_t *b){return a->low==b->low&&a->high==b->high&&a->exponent==b->exponent&&a->shift==b->shift&&a->negative==b->negative;}
static void product_put(FILE *f,const native_vorbis_window_product_t *p){put64(f,p->low);put64(f,p->high);put64(f,(uint64_t)p->exponent);put32(f,(uint32_t)p->shift);put32(f,p->negative);}
static native_vorbis_window_product_t product_get(FILE *f){
    native_vorbis_window_product_t p;memset(&p,0xa5,sizeof(p));p.low=get64(f);p.high=get64(f);p.exponent=get_signed(f);
    uint32_t shift=get32(f),negative=get32(f);memcpy(&p.shift,&shift,4);CHECK(negative<=1);p.negative=negative!=0;return p;
}
static bool canonical_product(const native_vorbis_window_product_t *p){
    if(!p->low&&!p->high)return !p->exponent&&!p->shift&&!p->negative;
    return (p->low&1)&&p->high<(UINT64_C(1)<<42)&&p->shift>=-2148&&p->shift<=1023;
}
typedef struct {uint64_t prefix[2];int16_t value;unsigned char suffix[16];} scalar_guard_t;
static int16_t pair_call(const native_vorbis_window_product_t *a,const native_vorbis_window_product_t *b,
    unsigned nulls,int wanted,bool controls){
    scalar_guard_t out;memset(&out,0xa5,sizeof(out));unsigned char before[sizeof(out)],aa[sizeof(*a)],bb[sizeof(*b)];
    memcpy(before,&out,sizeof(out));memcpy(aa,a,sizeof(aa));memcpy(bb,b,sizeof(bb));
    CHECK(native_vorbis_pcm_s16_product_pair(nulls&1?NULL:a,nulls&2?NULL:b,nulls&4?NULL:&out.value)==wanted);
    CHECK(!memcmp(aa,a,sizeof(aa))&&!memcmp(bb,b,sizeof(bb)));
    if(wanted){CHECK(!memcmp(before,&out,sizeof(out)));++refusals;}
    CHECK(out.prefix[0]==UINT64_C(0xa5a5a5a5a5a5a5a5)&&out.prefix[1]==out.prefix[0]);
    for(unsigned i=0;i<16;++i)CHECK(out.suffix[i]==0xa5);
    if(controls){
        for(unsigned mask=1;mask<=4;mask*=2){
            scalar_guard_t failed;memset(&failed,0xa5,sizeof(failed));unsigned char saved[sizeof(failed)];memcpy(saved,&failed,sizeof(saved));
            CHECK(native_vorbis_pcm_s16_product_pair(mask&1?NULL:a,mask&2?NULL:b,mask&4?NULL:&failed.value)==-1);++refusals;
            CHECK(!memcmp(saved,&failed,sizeof(failed))&&!memcmp(aa,a,sizeof(aa))&&!memcmp(bb,b,sizeof(bb)));
        }
        if(!wanted){const int modes[]={FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
            for(unsigned i=0;i<3;++i){CHECK(fesetround(modes[i])==0);int16_t value=0;
                CHECK(native_vorbis_pcm_s16_product_pair(a,b,&value)==0&&value==out.value);}
            CHECK(fesetround(FE_TONEAREST)==0);
            if(product_equal(a,b)){int16_t value=0;CHECK(native_vorbis_pcm_s16_product_pair(a,a,&value)==0&&value==out.value);}
        }else{native_vorbis_window_product_t zero={0};int16_t retry=123;CHECK(native_vorbis_pcm_s16_product_pair(&zero,&zero,&retry)==0&&retry==0);}
    }
    return out.value;
}
static uint32_t legacy_batches(FILE *input,FILE *output){
    unsigned char magic[8];CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VPCMPR01",8));uint32_t rows=get32(input);CHECK(rows==2479);put32(output,rows);
    for(uint32_t row=0;row<rows;++row){uint32_t n=get32(input),controls=get32(input);CHECK(n<=65540);int64_t ea=get_signed(input),eb=get_signed(input);
        buffer_t a=buffer((size_t)n*8),b=buffer((size_t)n*8),out=buffer((size_t)n*2+8);
        for(unsigned side=0;side<2;++side)for(uint32_t i=0;i<n;++i){uint64_t u=get64(input);memcpy((side?b.data:a.data)+(size_t)i*8,&u,8);}
        buffer_t ac=snapshot(&a),bc=snapshot(&b);
        for(uint32_t i=0;i<n;++i){native_vorbis_window_product_t p,q;
            CHECK(native_vorbis_window_multiply_exact(((double *)a.data)[i],1,ea,&p)==0);
            CHECK(native_vorbis_window_multiply_exact(((double *)b.data)[i],1,eb,&q)==0);
            ((int16_t *)out.data)[i]=pair_call(&p,&q,0,0,controls&&(i==0||i+1==n));}
        unchanged_buffer(&a,&ac);unchanged_buffer(&b,&bc);check_buffer(&out);
        for(size_t i=(size_t)n*2;i<out.bytes;++i)CHECK(out.data[i]==0xa5);
        put32(output,n);put64(output,(uint64_t)ea);put64(output,(uint64_t)eb);values(output,(double *)a.data,n);values(output,(double *)b.data,n);
        for(uint32_t i=0;i<n;++i)put16(output,((int16_t *)out.data)[i]);
        drop(&bc);drop(&ac);drop(&out);drop(&b);drop(&a);
    }return rows;
}
static uint32_t scalar_rows(FILE *input,FILE *output){
    uint32_t count=get32(input);CHECK(count>196614);put32(output,count);
    for(uint32_t i=0;i<count;++i){uint32_t controls=get32(input),multiply=get32(input),nulls=get32(input);
        native_vorbis_window_product_t a=product_get(input),b=product_get(input);
        if(multiply){native_vorbis_window_product_t *products[]={&a,&b};
            for(unsigned side=0;side<2;++side){double sample_value=from_bits(get64(input)),factor=from_bits(get64(input));int64_t e=get_signed(input);
                native_vorbis_window_product_t actual;CHECK(native_vorbis_window_multiply_exact(sample_value,factor,e,&actual)==0);
                CHECK(product_equal(&actual,products[side]));*products[side]=actual;}}
        int status=nulls||!canonical_product(&a)||!canonical_product(&b)?-1:0;
        int16_t result=pair_call(&a,&b,nulls,status,controls!=0);
        put32(output,i);product_put(output,&a);product_put(output,&b);put32(output,(uint32_t)status);put16(output,result);
    }return count;
}
static void prepared(uint32_t s,uint32_t l,uint32_t n,unsigned previous_long,unsigned next_long,
    double *data,int64_t e,native_vorbis_window_exact_view_t *view){
    native_vorbis_window_shape_t shape;CHECK(native_vorbis_window_shape(s,l,n==l,previous_long,next_long,&shape)==0&&shape.blocksize==n);
    unsigned left=0,right=0;
    while(left<8&&(64U<<left)!=shape.left_size)++left;
    while(right<8&&(64U<<right)!=shape.right_size)++right;
    CHECK(left<8&&right<8);
    native_vorbis_transform_block_t source={.count=n,.exponent=e,.samples=data};
    CHECK(native_vorbis_window_exact_prepare(&shape,&plans[left],&plans[right],&source,n,view)==0);
}
static void refused_windows(const native_vorbis_window_exact_view_t *a,int32_t ab,
    const native_vorbis_window_exact_view_t *b,int32_t bb,uint32_t count,int16_t *output,size_t capacity,int wanted,
    const buffer_t *aa,const buffer_t *ba,const buffer_t *out){
    buffer_t ac=snapshot(aa),bc=snapshot(ba),oc=snapshot(out);unsigned char av[sizeof(*a)],bv[sizeof(*b)];
    if(a)memcpy(av,a,sizeof(av));
    if(b)memcpy(bv,b,sizeof(bv));
    CHECK(native_vorbis_pcm_s16_windows(a,ab,b,bb,count,output,capacity)==wanted);++refusals;
    if(a)CHECK(!memcmp(av,a,sizeof(av)));
    if(b)CHECK(!memcmp(bv,b,sizeof(bv)));
    unchanged_buffer(aa,&ac);unchanged_buffer(ba,&bc);unchanged_buffer(out,&oc);drop(&oc);drop(&bc);drop(&ac);
}
static native_vorbis_window_product_t logical(const native_vorbis_window_exact_view_t *v,int32_t begin,uint32_t i){
    int64_t coordinate=(int64_t)begin+i;native_vorbis_window_product_t p={0};
    if(coordinate>=0&&(uint64_t)coordinate<v->shape.blocksize)CHECK(native_vorbis_window_exact_at(v,(uint32_t)coordinate,&p)==0);
    return p;
}
static void adapter_row(FILE *input,FILE *output,uint32_t ordinal){
    uint32_t ids[7];for(unsigned i=0;i<7;++i)ids[i]=get32(input);
    uint32_t s=ids[0],l=ids[1],pattern=ids[2],step=ids[3],a=ids[4],n=ids[5],count=ids[6];
    CHECK(s>=64&&l<=8192&&s<=l&&(n==s||n==l)&&(a==0||a==s||a==l)&&count==(a?(a+n)/4:0));
    int64_t ea=get_signed(input),eb=get_signed(input);uint32_t an=a?a:64;
    buffer_t aa=buffer((size_t)an*8),ba=buffer((size_t)n*8),out=buffer((size_t)count*2+8);
    if(!a)memset(aa.data,0,aa.bytes);
    for(unsigned side=0;side<2;++side){uint32_t amount=side?n:a;for(uint32_t i=0;i<amount;++i){uint64_t u=get64(input);memcpy((side?ba.data:aa.data)+(size_t)i*8,&u,8);}}
    buffer_t ac=snapshot(&aa),bc=snapshot(&ba);native_vorbis_window_exact_view_t previous,current;
    if(a)prepared(s,l,a,a==l,n==l,(double *)aa.data,ea,&previous);
    else prepared(64,64,64,0,0,(double *)aa.data,0,&previous);
    prepared(s,l,n,a==l,n==l,(double *)ba.data,eb,&current);
    int32_t ab=(int32_t)a/2,bb=a?((int32_t)n-(int32_t)a)/4:0;
    int16_t *destination=(int16_t *)out.data;
#define REF(A,AB,B,BB,C,O,CAP,E) refused_windows(A,AB,B,BB,C,O,CAP,E,&aa,&ba,&out)
    if(step==1||!count){
        REF(NULL,ab,&current,bb,count,destination,count,-1);REF(&previous,ab,NULL,bb,count,destination,count,-1);
        REF(&previous,ab,&current,bb,count,destination,SIZE_MAX,-2);
        native_vorbis_window_exact_view_t bad=previous;--bad.source.count;
        REF(&bad,ab,&current,bb,count,destination,count,-1);
        if(count){REF(&previous,ab,&current,bb,count,destination,count-1,-4);REF(&previous,ab,&current,bb,count,NULL,count,-1);}
        else CHECK(native_vorbis_pcm_s16_windows(&previous,ab,&current,bb,0,NULL,0)==0);
    }
    if((ordinal==1)||(s==64&&l==8192&&pattern==0&&step==6)){
        buffer_t invalid=snapshot(&ba);native_vorbis_window_exact_view_t bad=current;bad.source.samples=(double *)invalid.data;
        const double malformed[]={NAN,INFINITY,-INFINITY};
        for(unsigned i=0;i<3;++i){((double *)invalid.data)[n/2-1]=malformed[i];
            refused_windows(&previous,ab,&bad,bb,count,destination,count,-2,&aa,&invalid,&out);}
        drop(&invalid);
        buffer_t extremes=buffer(128+8);CHECK(native_vorbis_pcm_s16_windows(&previous,INT32_MIN,&current,INT32_MAX,64,(int16_t *)extremes.data,64)==0);
        for(unsigned i=0;i<64;++i)CHECK(((int16_t *)extremes.data)[i]==0);
        for(size_t i=128;i<extremes.bytes;++i)CHECK(extremes.data[i]==0xa5);
        drop(&extremes);
    }
#undef REF
    unsigned char av[sizeof(previous)],bv[sizeof(current)];memcpy(av,&previous,sizeof(av));memcpy(bv,&current,sizeof(bv));
    CHECK(native_vorbis_pcm_s16_windows(&previous,ab,&current,bb,count,destination,count)==0);
    CHECK(!memcmp(av,&previous,sizeof(av))&&!memcmp(bv,&current,sizeof(bv)));unchanged_buffer(&aa,&ac);unchanged_buffer(&ba,&bc);check_buffer(&out);
    for(size_t i=(size_t)count*2;i<out.bytes;++i)CHECK(out.data[i]==0xa5);
    for(unsigned i=0;i<7;++i)put32(output,ids[i]);
    put64(output,(uint64_t)ea);put64(output,(uint64_t)eb);put32(output,(uint32_t)ab);put32(output,(uint32_t)bb);
    values(output,(double *)aa.data,a);values(output,(double *)ba.data,n);
    for(uint32_t i=0;i<count;++i){native_vorbis_window_product_t p=logical(&previous,ab,i),q=logical(&current,bb,i);
        CHECK(pair_call(&p,&q,0,0,false)==destination[i]);product_put(output,&p);product_put(output,&q);put16(output,destination[i]);}
    for(unsigned i=0;i<8;++i){size_t amount=(size_t)32<<i;guarded(coefficients[i],amount);CHECK(!memcmp(coefficients[i]+2,coefficient_copies[i],amount*8));}
    drop(&bc);drop(&ac);drop(&out);drop(&ba);drop(&aa);
}
int main(int argc,char **argv){
    CHECK(argc==3);FILE *input=fopen(argv[1],"rb"),*output=fopen(argv[2],"wb");CHECK(input&&output);
    unsigned char magic[8];CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VPCMEX01",8));CHECK(fwrite(magic,1,8,output)==8);
    uint32_t batches=legacy_batches(input,output),scalars=scalar_rows(input,output);CHECK(fegetround()==FE_TONEAREST);
    make_plans(output);uint32_t adapters=get32(input);CHECK(adapters==864);put32(output,adapters);
    for(uint32_t i=0;i<adapters;++i)adapter_row(input,output,i);
    CHECK(fgetc(input)==EOF&&!ferror(input));CHECK(fclose(input)==0&&fclose(output)==0);
    for(unsigned i=0;i<8;++i){free(coefficients[i]);free(coefficient_copies[i]);}
    printf("PCM_EXACT batches=%" PRIu32 " scalars=%" PRIu32 " adapters=%" PRIu32 " refusals=%" PRIu64 " checks=%" PRIu64 "\n",batches,scalars,adapters,refusals,checks);return 0;
}
