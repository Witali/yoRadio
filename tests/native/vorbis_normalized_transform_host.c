// Guard the public binary64 entry, retaining the old limb path as a bit oracle.
#include "native_vorbis_transform.h"
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks, refusals, cases, matched;
#define CHECK(x) do { ++checks; assert(x); } while (0)
typedef struct { unsigned char *raw, *data; size_t bytes; } guard_t;
static guard_t create(size_t bytes) {
    CHECK(bytes <= SIZE_MAX - 32);
    guard_t g = {.raw = malloc(bytes + 32), .bytes = bytes}; CHECK(g.raw);
    g.data = g.raw + 16; memset(g.raw, 0xa5, bytes + 32); return g;
}
static void guards(const guard_t *g) {
    for (size_t i = 0; i < 16; ++i) {
        CHECK(g->raw[i] == 0xa5); CHECK(g->data[g->bytes + i] == 0xa5);
    }
}
static guard_t copy(const guard_t *g) {
    guard_t result = create(g->bytes); memcpy(result.data, g->data, g->bytes); return result;
}
static void unchanged(const guard_t *a, const guard_t *b) {
    guards(a); CHECK(a->bytes == b->bytes); CHECK(!memcmp(a->data, b->data, a->bytes));
}
static void destroy(guard_t *g) { guards(g); free(g->raw); memset(g, 0, sizeof(*g)); }
static void put32(FILE *f, uint32_t word) {
    unsigned char b[4] = {(unsigned char)word, (unsigned char)(word >> 8),
        (unsigned char)(word >> 16), (unsigned char)(word >> 24)};
    CHECK(fwrite(b, 1, 4, f) == 4);
}
static void put64(FILE *f, uint64_t word) { put32(f, (uint32_t)word); put32(f, (uint32_t)(word >> 32)); }
static uint64_t bits(double value) { uint64_t result; memcpy(&result, &value, 8); return result; }
static void capture(FILE *f, uint32_t n, uint32_t kind, uint32_t index,
    const native_vorbis_transform_block_t *source, const native_vorbis_transform_block_t *result) {
    put32(f, n); put32(f, kind); put32(f, index); put64(f, (uint64_t)source->exponent);
    for (uint32_t i = 0; i < source->count; ++i) put64(f, bits(source->samples[i]));
    for (uint32_t i = 0; i < result->count; ++i) {
        CHECK(isfinite(result->samples[i])); put64(f, bits(result->samples[i]));
    }
    ++cases;
}
static void refused(const native_vorbis_imdct_plan_t *plan,
    const native_vorbis_transform_block_t *source, size_t count, double *output, size_t capacity,
    native_vorbis_transform_block_t *result, int wanted, const guard_t *input,
    const guard_t *work, const guard_t *before) {
    unsigned char saved[sizeof(*result)];
    if (result) memcpy(saved, result, sizeof(saved));
    unsigned char plan_before[sizeof(*plan)],source_before[sizeof(*source)];
    if (plan) memcpy(plan_before,plan,sizeof(plan_before));
    if (source) memcpy(source_before,source,sizeof(source_before));
    // Snapshot the entire real array immediately before this call, including
    // the injected nonfinite bit pattern. Check before controls() restores it.
    guard_t input_before=copy(input);
    CHECK(native_vorbis_imdct_transform_binary64(plan, source, count, output, capacity, result) == wanted);
    if (result) CHECK(!memcmp(saved, result, sizeof(saved)));
    if (plan) CHECK(!memcmp(plan_before,plan,sizeof(plan_before)));
    if (source) CHECK(!memcmp(source_before,source,sizeof(source_before)));
    unchanged(input,&input_before);destroy(&input_before);
    unchanged(work, before); ++refusals;
}
static void controls(native_vorbis_imdct_plan_t *plan, native_vorbis_transform_block_t *source,
    guard_t *input, guard_t *work, native_vorbis_transform_block_t *result) {
    guard_t before = copy(work); uint32_t n = plan->blocksize; size_t count = source->count;
    double *output = (double *)work->data;
#define REF(P,S,C,O,W,E) refused(P,S,C,O,W,result,E,input,work,&before)
    REF(NULL,source,count,output,n+8,-1); REF(plan,NULL,count,output,n+8,-1);
    REF(plan,source,count-1,output,n+8,-4); REF(plan,source,count,output,n+7,-4);
    REF(plan,source,SIZE_MAX,output,n+8,-2); REF(plan,source,count,output,SIZE_MAX,-2);
    REF(plan,source,count,NULL,n+8,-1);
    refused(plan,source,count,output,n+8,NULL,-1,input,work,&before);
    native_vorbis_imdct_plan_t bad_plan = *plan;
    bad_plan.blocksize=63; REF(&bad_plan,source,count,output,n+8,-1);
    bad_plan=*plan; ++bad_plan.log2n; REF(&bad_plan,source,count,output,n+8,-1);
    bad_plan=*plan; bad_plan.trig=NULL; REF(&bad_plan,source,count,output,n+8,-1);
    bad_plan=*plan; bad_plan.bitrev=NULL; REF(&bad_plan,source,count,output,n+8,-1);
    native_vorbis_transform_block_t bad_source = *source;
    --bad_source.count; REF(plan,&bad_source,count,output,n+8,-1);
    bad_source=*source; bad_source.samples=NULL; REF(plan,&bad_source,count,output,n+8,-1);
    const uint64_t invalid[] = {UINT64_C(0x7ff0000000000000),UINT64_C(0xfff0000000000000),
        UINT64_C(0x7ff8000000000001),UINT64_C(0x7ff0000000000001),
        UINT64_C(0x67e0000000000001),UINT64_C(0xe7e0000000000001),
        UINT64_C(0x7fefffffffffffff)};
    double *values=(double *)input->data, saved=values[count-1];
    for (size_t i=0;i<sizeof(invalid)/sizeof(*invalid);++i) {
        memcpy(&values[count-1],&invalid[i],8);
        REF(plan,source,count,output,n+8,-2);
    }
    values[count-1]=saved;
    // A failed call never consumes the immutable input and the same workspace
    // remains usable without repair. Successful retry is checked by the caller.
    destroy(&before);
#undef REF
}
static void run(FILE *f, native_vorbis_imdct_plan_t *plan, guard_t *input, guard_t *work,
    uint32_t kind, uint32_t index, int64_t exponent, int run_controls,
    const native_vorbis_floor1_product_t *limb, guard_t *oldwork) {
    uint32_t n=plan->blocksize;
    native_vorbis_transform_block_t source={.count=n/2,.exponent=exponent,.samples=(double *)input->data};
    unsigned char source_before[sizeof(source)]; memcpy(source_before,&source,sizeof(source));
    native_vorbis_transform_block_t result; memset(&result,0xa5,sizeof(result));
    guard_t input_before=copy(input),work_before=copy(work);
    if (run_controls) controls(plan,&source,input,work,&result);
    CHECK(native_vorbis_imdct_transform_binary64(plan,&source,n/2,(double *)work->data,n+8,&result)==0);
    CHECK(result.count==n && result.exponent==exponent && result.samples==(double *)work->data+8);
    CHECK(!memcmp(source_before,&source,sizeof(source)));
    unchanged(input,&input_before);
    for (size_t i=0;i<8;++i) CHECK(bits(((double *)work->data)[i])==0);
    CHECK(!memcmp(work->data+(n+8)*8,work_before.data+(n+8)*8,work->bytes-(n+8)*8));
    int nonzero=0;
    for (uint32_t i=0;i<source.count;++i) nonzero |= source.samples[i]!=0.0;
    if (!nonzero) for (uint32_t i=0;i<n;++i) CHECK(bits(result.samples[i])==0);
    if (limb) {
        native_vorbis_transform_block_t old;
        CHECK(native_vorbis_imdct_transform(plan,limb,(size_t)limb->layout.limb_count,
            (double *)oldwork->data,n+8,&old)==0);
        CHECK(old.exponent==exponent && old.count==n);
        if (nonzero) {
            CHECK(!memcmp(old.samples,result.samples,n*sizeof(double))); matched+=n;
        } else for (uint32_t i=0;i<n;++i) CHECK(old.samples[i]==0.0);
    }
    capture(f,n,kind,index,&source,&result);
    guards(work); destroy(&work_before); destroy(&input_before);
}
static void signed_integer(uint32_t *words, uint32_t limbs, uint32_t width, uint32_t pattern) {
    // Endpoint, unit, high bit and zero values exercise the old rounding route.
    memset(words,0,limbs*4);
    uint32_t absolute=pattern%4;
    if (absolute==0) {
        for (uint32_t bit=0;bit<width;++bit) words[bit/32] |= UINT32_C(1)<<(bit%32);
    } else if (absolute==1) words[0]=1;
    else if (absolute==2) words[(width-1)/32]=UINT32_C(1)<<((width-1)%32);
    if (pattern&4) {
        uint64_t carry=1;
        for (uint32_t i=0;i<limbs;++i) {
            uint64_t value=(uint64_t)~words[i]+carry; words[i]=(uint32_t)value; carry=value>>32;
        }
    }
}
int main(int argc, char **argv) {
    CHECK(argc==2); FILE *f=fopen(argv[1],"wb"); CHECK(f);
    CHECK(fwrite("VNORM001",1,8,f)==8);
    const uint32_t selected[]={1,31,32,33,52,53,54,55,63,64,65,1079,1134,1151};
    const int64_t exponents[]={INT64_MIN,INT64_MAX,-788,0,512};
    for (uint32_t shift=0;shift<8;++shift) {
        uint32_t n=64U<<shift,bins=n/2;
        native_vorbis_imdct_requirements_t need;
        CHECK(native_vorbis_imdct_measure(n,&need)==0);
        guard_t trig=create((size_t)need.trig_count*8),rev=create((size_t)need.bitrev_count*sizeof(int));
        native_vorbis_imdct_plan_t plan;
        CHECK(native_vorbis_imdct_prepare(n,(double *)trig.data,(size_t)need.trig_count,
            (int *)rev.data,(size_t)need.bitrev_count,&plan)==0);
        guard_t trig_before=copy(&trig),rev_before=copy(&rev);
        unsigned char plan_before[sizeof(plan)]; memcpy(plan_before,&plan,sizeof(plan));
        guard_t input=create(bins*8),work=create((n+12)*8),oldwork=create((n+12)*8);
        guard_t limbs=create((size_t)bins*36*4);
        for (uint32_t width=1;width<=1151;++width) {
            int chosen=shift==0;
            for (size_t k=0;k<sizeof(selected)/sizeof(*selected);++k) chosen |= width==selected[k];
            if (!chosen) continue;
            uint32_t count=(width+32)/32;
            uint32_t *words=(uint32_t *)limbs.data;
            for (uint32_t i=0;i<bins;++i) signed_integer(words+i*count,count,width,i%8);
            native_vorbis_floor1_product_t exact={.layout={.bins=bins,.limbs=count,.magnitude_bits=width,
                .exponent=width&1?INT32_MIN:INT32_MAX,.limb_count=(uint64_t)bins*count},.samples=words};
            native_vorbis_transform_block_t converted;
            CHECK(native_vorbis_spectrum_to_binary64(&exact,(size_t)exact.layout.limb_count,
                (double *)input.data,bins,&converted)==0);
            run(f,&plan,&input,&work,0,width,converted.exponent,width==1,&exact,&oldwork);
        }
        double *values=(double *)input.data;
        for (uint32_t pattern=0;pattern<12;++pattern) {
            for (uint32_t i=0;i<bins;++i) {
                double sign=i&1?-1.0:1.0;
                switch (pattern) {
                    case 0: values[i]=sign*0.0; break;
                    case 1: values[i]=sign*0x1p639; break;
                    case 2: values[i]=i==bins-1?0x1p639:0.0; break;
                    case 3: values[i]=sign*DBL_TRUE_MIN; break;
                    case 4: values[i]=sign*DBL_MIN; break;
                    case 5: values[i]=i==0?0x1p639:sign*DBL_TRUE_MIN; break;
                    case 6: values[i]=((int)(i%11)-5)/8.0; break;
                    case 7: values[i]=sign*nextafter(0x1p639,0.0); break;
                    case 8: values[i]=i==0?DBL_TRUE_MIN:0.0; break;
                    case 9: values[i]=sign*0x1p-512; break;
                    case 10: values[i]=i==0?-0.0:0.0; break;
                    default: values[i]=sign*(1.0+(double)(i%31)/64.0); break;
                }
            }
            for (size_t k=0;k<sizeof(exponents)/sizeof(*exponents);++k)
                run(f,&plan,&input,&work,1,pattern,exponents[k],pattern==0&&k==0,NULL,&oldwork);
        }
        unchanged(&trig,&trig_before); unchanged(&rev,&rev_before);
        CHECK(!memcmp(plan_before,&plan,sizeof(plan)));
        destroy(&limbs);destroy(&oldwork);destroy(&work);destroy(&input);
        destroy(&rev_before);destroy(&trig_before);destroy(&rev);destroy(&trig);
    }
    CHECK(fclose(f)==0);
    printf("NORMALIZED_CAPTURE cases=%" PRIu64 " matched=%" PRIu64 " refusals=%" PRIu64 " checks=%" PRIu64 "\n",
        cases,matched,refusals,checks);
    return 0;
}
