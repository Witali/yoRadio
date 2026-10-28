// Exact scalar products and copied-descriptor views; no overlap or PCM calls.
#include "native_vorbis_window_exact.h"
#define main unused_rounded_window_main
#include "vorbis_window_host.c"
#undef main
#include <fenv.h>

static uint64_t get_integer(FILE *f,unsigned count) {
    uint64_t value=0;
    for(unsigned i=0;i<count;++i){int c=fgetc(f);CHECK(c!=EOF);value|=(uint64_t)(unsigned char)c<<(i*8);}
    return value;
}
static double from_word(uint64_t word){double d;memcpy(&d,&word,8);return d;}
static uint64_t word_of(double d){uint64_t word;memcpy(&word,&d,8);return word;}
static void product_put(FILE *f,const native_vorbis_window_product_t *p) {
    put64(f,p->low);put64(f,p->high);put64(f,(uint64_t)p->exponent);
    put32(f,(uint32_t)p->shift);put32(f,p->negative);
}
static void failed_put(FILE *f) {
    put64(f,UINT64_C(0xa5a5a5a5a5a5a5a5));put64(f,UINT64_C(0xa5a5a5a5a5a5a5a5));
    put64(f,UINT64_C(0xa5a5a5a5a5a5a5a5));put32(f,UINT32_C(0xa5a5a5a5));put32(f,UINT32_C(0xa5a5a5a5));
}
typedef struct {uint64_t prefix[2];native_vorbis_window_product_t value;uint64_t suffix[2];} product_guard_t;
static void product_guards(const product_guard_t *p) {
    CHECK(p->prefix[0]==UINT64_C(0xa5a5a5a5a5a5a5a5)&&p->prefix[1]==p->prefix[0]);
    CHECK(p->suffix[0]==p->prefix[0]&&p->suffix[1]==p->prefix[0]);
}
static bool same_product(const native_vorbis_window_product_t *a,const native_vorbis_window_product_t *b) {
    return a->low==b->low&&a->high==b->high&&a->exponent==b->exponent&&a->shift==b->shift&&a->negative==b->negative;
}
static void scalar_case(FILE *input,FILE *output,uint32_t index) {
    uint64_t a=get_integer(input,8),b=get_integer(input,8),e=get_integer(input,8);
    int32_t wanted=(int32_t)get_integer(input,4);uint32_t controls=(uint32_t)get_integer(input,4);
    int64_t exponent;memcpy(&exponent,&e,8);double sample_value=from_word(a),factor=from_word(b);
    product_guard_t result;memset(&result,0xa5,sizeof(result));unsigned char before[sizeof(result)];memcpy(before,&result,sizeof(result));
    int status=native_vorbis_window_multiply_exact(sample_value,factor,exponent,&result.value);
    CHECK(status==wanted);product_guards(&result);
    put32(output,index);put64(output,a);put64(output,b);put64(output,e);put32(output,(uint32_t)status);
    if(status){CHECK(!memcmp(before,&result,sizeof(result)));failed_put(output);++refusals;}
    else product_put(output,&result.value);
    if(controls){
        CHECK(native_vorbis_window_multiply_exact(sample_value,factor,exponent,NULL)==-1);++refusals;
        if(!status){
            const int modes[]={FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
            for(unsigned i=0;i<3;++i){
                CHECK(fesetround(modes[i])==0);product_guard_t next;memset(&next,0xa5,sizeof(next));
                CHECK(native_vorbis_window_multiply_exact(sample_value,factor,exponent,&next.value)==0);
                CHECK(same_product(&next.value,&result.value));product_guards(&next);
            }
            CHECK(fesetround(FE_TONEAREST)==0);
        }
    }
    if(status){
        CHECK(native_vorbis_window_multiply_exact(1,1,exponent,&result.value)==0);
        CHECK(result.value.low==1&&result.value.high==0&&result.value.exponent==exponent&&result.value.shift==0&&!result.value.negative);
        product_guards(&result);
    }
}

typedef struct {double *source;double *lookup[8];} borrow_copy_t;
static borrow_copy_t borrow_snapshot(const double *source,uint32_t n) {
    borrow_copy_t result;result.source=malloc((size_t)n*8);CHECK(result.source);memcpy(result.source,source,(size_t)n*8);
    for(unsigned i=0;i<8;++i){size_t bytes=(size_t)32<<i;bytes*=8;
        result.lookup[i]=malloc(bytes);CHECK(result.lookup[i]);memcpy(result.lookup[i],coefficients[i]+2,bytes);}
    return result;
}
static void borrows_unchanged(const double *source,uint32_t n,borrow_copy_t *saved) {
    CHECK(!memcmp(saved->source,source,(size_t)n*8));free(saved->source);
    for(unsigned i=0;i<8;++i){size_t count=(size_t)32<<i;
        CHECK(!memcmp(saved->lookup[i],coefficients[i]+2,count*8));guarded(coefficients[i],count);free(saved->lookup[i]);}
}
static void prepare_refusal(const native_vorbis_window_shape_t *shape,
    const native_vorbis_window_plan_t *left,const native_vorbis_window_plan_t *right,
    const native_vorbis_transform_block_t *source,size_t capacity,
    const double *data,uint32_t n,int wanted,bool null_view) {
    native_vorbis_window_exact_view_t view;memset(&view,0xa5,sizeof(view));
    unsigned char before[sizeof(view)],sb[sizeof(*shape)],lb[sizeof(*left)],rb[sizeof(*right)],ib[sizeof(*source)];
    memcpy(before,&view,sizeof(view));if(shape)memcpy(sb,shape,sizeof(sb));if(left)memcpy(lb,left,sizeof(lb));
    if(right)memcpy(rb,right,sizeof(rb));
    if(source)memcpy(ib,source,sizeof(ib));
    borrow_copy_t saved=borrow_snapshot(data,n);
    CHECK(native_vorbis_window_exact_prepare(shape,left,right,source,capacity,null_view?NULL:&view)==wanted);++refusals;
    CHECK(!memcmp(before,&view,sizeof(view)));if(shape)CHECK(!memcmp(sb,shape,sizeof(sb)));
    if(left)CHECK(!memcmp(lb,left,sizeof(lb)));
    if(right)CHECK(!memcmp(rb,right,sizeof(rb)));
    if(source)CHECK(!memcmp(ib,source,sizeof(ib)));
    borrows_unchanged(data,n,&saved);
}
static void at_refusal(const native_vorbis_window_exact_view_t *view,uint32_t index,
    const double *data,uint32_t n,bool null_result) {
    product_guard_t result;memset(&result,0xa5,sizeof(result));
    unsigned char before[sizeof(result)],vb[sizeof(*view)];memcpy(before,&result,sizeof(result));
    if(view)memcpy(vb,view,sizeof(vb));
    borrow_copy_t saved=borrow_snapshot(data,n);
    CHECK(native_vorbis_window_exact_at(view,index,null_result?NULL:&result.value)==-1);++refusals;
    CHECK(!memcmp(before,&result,sizeof(result)));if(view)CHECK(!memcmp(vb,view,sizeof(vb)));
    borrows_unchanged(data,n,&saved);
}

static void exact_view_case(FILE *output,unsigned small,unsigned large,unsigned flags) {
    uint32_t s=64U<<small,l=64U<<large;
    native_vorbis_window_shape_t shape;CHECK(native_vorbis_window_shape(s,l,flags&1,(flags>>1)&1,(flags>>2)&1,&shape)==0);
    uint32_t n=shape.blocksize;CHECK(n>=64&&n<=8192&&!(n&(n-1)));
    double *raw=storage(n),*data=raw+2;
    for(uint32_t i=0;i<n;++i)data[i]=sample(i+flags);
    double *original=malloc((size_t)n*8);CHECK(original);memcpy(original,data,(size_t)n*8);
    native_vorbis_window_plan_t left=plans[(flags&1)&&(flags&2)?large:small],right=plans[(flags&1)&&(flags&4)?large:small];
    native_vorbis_transform_block_t source={.count=n,.exponent=flags&2?INT64_MIN:INT64_MAX,.samples=data};
#define REF(S,L,R,I,C,E,V) prepare_refusal(S,L,R,I,C,data,n,E,V)
    REF(NULL,&left,&right,&source,n,-1,false);REF(&shape,NULL,&right,&source,n,-1,false);
    REF(&shape,&left,NULL,&source,n,-1,false);REF(&shape,&left,&right,NULL,n,-1,false);
    REF(&shape,&left,&right,&source,n,-1,true);REF(&shape,&left,&right,&source,n-1,-4,false);
    REF(&shape,&left,&right,&source,SIZE_MAX,-2,false);
    native_vorbis_window_shape_t bad_shape=shape;++bad_shape.right_end;
    REF(&bad_shape,&left,&right,&source,n,-1,false);
    native_vorbis_window_plan_t bad_plan=left;bad_plan.blocksize=63;
    REF(&shape,&bad_plan,&right,&source,n,-1,false);bad_plan=right;bad_plan.rise=NULL;
    REF(&shape,&left,&bad_plan,&source,n,-1,false);
    native_vorbis_transform_block_t bad_source=source;--bad_source.count;
    REF(&shape,&left,&right,&bad_source,n,-1,false);bad_source=source;bad_source.samples=NULL;
    REF(&shape,&left,&right,&bad_source,n,-1,false);
    const double invalid_source[]={NAN,INFINITY,-INFINITY};
    for(unsigned i=0;i<3;++i){data[n-1]=invalid_source[i];REF(&shape,&left,&right,&source,n,-2,false);data[n-1]=original[n-1];}
    const double invalid_factor[]={NAN,INFINITY,-INFINITY,-DBL_TRUE_MIN,0x1.0000000000001p0};
    for(unsigned side=0;side<2;++side){
        const native_vorbis_window_plan_t *plan=side?&right:&left;
        double *last=(double *)plan->rise+plan->blocksize/2-1;uint64_t before=word_of(*last);
        for(unsigned i=0;i<5;++i){*last=invalid_factor[i];REF(&shape,&left,&right,&source,n,-2,false);*last=from_word(before);}
    }
#undef REF
    native_vorbis_window_exact_view_t view;CHECK(native_vorbis_window_exact_prepare(&shape,&left,&right,&source,n,&view)==0);
    CHECK(view.source.samples==data&&view.source.count==n&&view.source.exponent==source.exponent);
    CHECK(view.left.rise==left.rise&&view.right.rise==right.rise);
    at_refusal(NULL,0,data,n,false);at_refusal(&view,n,data,n,false);at_refusal(&view,UINT32_MAX,data,n,false);
    at_refusal(&view,0,data,n,true);
    native_vorbis_window_exact_view_t bad_view=view;--bad_view.source.count;at_refusal(&bad_view,0,data,n,false);
    bad_view=view;++bad_view.shape.left_begin;at_refusal(&bad_view,0,data,n,false);
    bad_view=view;bad_view.left.rise=NULL;at_refusal(&bad_view,0,data,n,false);
    // Successful preparation copied descriptors. The original descriptors expire here.
    memset(&shape,0x5a,sizeof(shape));memset(&left,0x5a,sizeof(left));memset(&right,0x5a,sizeof(right));memset(&source,0x5a,sizeof(source));
    unsigned char view_before[sizeof(view)];memcpy(view_before,&view,sizeof(view));
    put32(output,s);put32(output,l);put32(output,flags);
    const uint32_t fields[]={view.shape.blocksize,view.shape.left_size,view.shape.right_size,view.shape.left_begin,
        view.shape.left_end,view.shape.right_begin,view.shape.right_end};
    for(unsigned i=0;i<7;++i)put32(output,fields[i]);
    put64(output,(uint64_t)view.source.exponent);values(output,data,n);
    for(uint32_t i=0;i<n;++i){
        product_guard_t result;memset(&result,0xa5,sizeof(result));
        CHECK(native_vorbis_window_exact_at(&view,i,&result.value)==0);product_guards(&result);
        CHECK(!memcmp(view_before,&view,sizeof(view)));product_put(output,&result.value);
    }
    CHECK(!memcmp(data,original,(size_t)n*8));guarded(raw,n);
    for(unsigned i=0;i<8;++i){size_t count=(size_t)32<<i;guarded(coefficients[i],count);
        CHECK(!memcmp(coefficients[i]+2,coefficient_copies[i],count*8));}
    free(original);free(raw);
}

int main(int argc,char **argv) {
    CHECK(argc==3);FILE *input=fopen(argv[1],"rb"),*output=fopen(argv[2],"wb");CHECK(input&&output);
    unsigned char magic[8];CHECK(fread(magic,1,8,input)==8&&!memcmp(magic,"VWXIN001",8));
    uint32_t rows=(uint32_t)get_integer(input,4);CHECK(rows>17962);
    CHECK(fwrite("VWXOUT01",1,8,output)==8);put32(output,rows);
    for(uint32_t i=0;i<rows;++i)scalar_case(input,output,i);
    CHECK(fgetc(input)==EOF&&!ferror(input));CHECK(fclose(input)==0);
    CHECK(fegetround()==FE_TONEAREST);make_plans(output);put32(output,288);
    for(unsigned small=0;small<8;++small)for(unsigned large=small;large<8;++large)
        for(unsigned flags=0;flags<8;++flags)exact_view_case(output,small,large,flags);
    for(unsigned i=0;i<8;++i){free(coefficients[i]);free(coefficient_copies[i]);}
    CHECK(fclose(output)==0);
    printf("WINDOW_EXACT rows=%" PRIu32 " shapes=288 refusals=%" PRIu64 " checks=%" PRIu64 "\n",rows,refusals,checks);
    return 0;
}
