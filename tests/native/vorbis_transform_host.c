// Guarded spectrum conversion and reused IMDCT capture; oracle is independent Python.
#include "native_vorbis_transform.h"
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks, refusals, live_blocks, live_bytes;
#define CHECK(x) do { ++checks; assert(x); } while (0)
typedef struct { unsigned char *raw, *data; size_t bytes; } guard_t;
static guard_t create(size_t bytes) {
    CHECK(bytes <= SIZE_MAX - 32);
    guard_t value = {.raw = malloc(bytes + 32), .bytes = bytes}; CHECK(value.raw);
    value.data = value.raw + 16; memset(value.raw, 0xa5, bytes + 32);
    ++live_blocks; live_bytes += bytes; return value;
}
static void validate(const guard_t *value) {
    for (size_t i = 0; i < 16; ++i) {
        CHECK(value->raw[i] == 0xa5); CHECK(value->data[value->bytes + i] == 0xa5);
    }
}
static void destroy(guard_t *value) {
    validate(value); CHECK(live_blocks && live_bytes >= value->bytes);
    --live_blocks; live_bytes -= value->bytes; free(value->raw); memset(value, 0, sizeof(*value));
}
static guard_t clone(const guard_t *source) {
    guard_t result = create(source->bytes); memcpy(result.data, source->data, source->bytes); return result;
}
static void unchanged(const guard_t *value, const guard_t *copy) {
    validate(value); validate(copy); CHECK(value->bytes == copy->bytes);
    CHECK(memcmp(value->data, copy->data, value->bytes) == 0);
}
static uint32_t read32(FILE *file) {
    unsigned char b[4]; CHECK(fread(b, 1, 4, file) == 4);
    return (uint32_t)b[0] | (uint32_t)b[1] << 8 | (uint32_t)b[2] << 16 | (uint32_t)b[3] << 24;
}
static int32_t signed32(uint32_t word) { int32_t result; memcpy(&result, &word, 4); return result; }
static void put32(FILE *file, uint32_t word) {
    unsigned char b[4] = {(unsigned char)word, (unsigned char)(word >> 8),
        (unsigned char)(word >> 16), (unsigned char)(word >> 24)};
    CHECK(fwrite(b, 1, 4, file) == 4);
}
static void put64(FILE *file, uint64_t word) { put32(file, (uint32_t)word); put32(file, (uint32_t)(word >> 32)); }
static void doubles(FILE *file, const double *values, size_t count) {
    for (size_t i = 0; i < count; ++i) { uint64_t bits; memcpy(&bits, &values[i], 8); put64(file, bits); }
}
static void block(FILE *file, const native_vorbis_transform_block_t *value) {
    put32(file, value->count); put64(file, (uint64_t)value->exponent); doubles(file, value->samples, value->count);
}

typedef struct {
    native_vorbis_imdct_requirements_t requirements;
    native_vorbis_imdct_plan_t plan;
    unsigned char plan_copy[sizeof(native_vorbis_imdct_plan_t)];
    guard_t trig, bitrev, trig_copy, bitrev_copy;
} plan_t;
static plan_t plans[8];
static void lookups_unchanged(void) {
    for (unsigned i = 0; i < 8; ++i) {
        CHECK(memcmp(plans[i].plan_copy,&plans[i].plan,sizeof(plans[i].plan))==0);
        unchanged(&plans[i].trig, &plans[i].trig_copy);
        unchanged(&plans[i].bitrev, &plans[i].bitrev_copy);
    }
}
static void prepare_refused(plan_t *p, uint32_t n, size_t tc, size_t bc,
                            unsigned nulls, int wanted) {
    // Constructor candidates use separate storage; old live lookup borrows
    // remain disjoint even for calls expected to fail before any write.
    guard_t trig=create(p->trig.bytes),bitrev=create(p->bitrev.bytes);
    guard_t trig_before=clone(&trig),bitrev_before=clone(&bitrev);
    native_vorbis_imdct_plan_t plan;
    unsigned char saved[sizeof(plan)]; memset(&plan, 0xa5, sizeof(plan)); memcpy(saved, &plan, sizeof(plan));
    CHECK(native_vorbis_imdct_prepare(n, nulls&1?NULL:(double *)trig.data, tc,
        nulls&2?NULL:(int *)bitrev.data, bc, nulls&4?NULL:&plan) == wanted);
    CHECK(memcmp(saved, &plan, sizeof(plan)) == 0); ++refusals;
    unchanged(&p->trig, &p->trig_copy); unchanged(&p->bitrev, &p->bitrev_copy);
    CHECK(memcmp(p->plan_copy,&p->plan,sizeof(p->plan))==0);
    unchanged(&trig,&trig_before);unchanged(&bitrev,&bitrev_before);
    destroy(&bitrev_before);destroy(&trig_before);destroy(&bitrev);destroy(&trig);
}
static void make_plans(FILE *file) {
    put32(file, 8);
    for (unsigned i = 0; i < 8; ++i) {
        plan_t *p = &plans[i]; uint32_t n = UINT32_C(64) << i;
        CHECK(native_vorbis_imdct_measure(n, &p->requirements) == 0);
        native_vorbis_imdct_requirements_t *r = &p->requirements;
        p->trig = create((size_t)r->trig_count * sizeof(double));
        p->bitrev = create((size_t)r->bitrev_count * sizeof(int));
        CHECK(native_vorbis_imdct_prepare(n, (double *)p->trig.data, (size_t)r->trig_count,
            (int *)p->bitrev.data, (size_t)r->bitrev_count, &p->plan) == 0);
        CHECK(p->plan.blocksize == n && p->plan.log2n == r->log2n &&
            p->plan.trig == (double *)p->trig.data && p->plan.bitrev == (int *)p->bitrev.data);
        p->trig_copy = clone(&p->trig); p->bitrev_copy = clone(&p->bitrev);
        memcpy(p->plan_copy,&p->plan,sizeof(p->plan));
        put32(file, n); put32(file, r->log2n); put64(file, r->trig_count);
        put64(file, r->bitrev_count); put64(file, r->workspace_count);
        doubles(file, p->plan.trig, (size_t)r->trig_count);
        for (size_t j = 0; j < r->bitrev_count; ++j) put32(file, (uint32_t)p->plan.bitrev[j]);
        prepare_refused(p,n,(size_t)r->trig_count-1,(size_t)r->bitrev_count,0,-4);
        prepare_refused(p,n,(size_t)r->trig_count,(size_t)r->bitrev_count-1,0,-4);
        prepare_refused(p,n,(size_t)r->trig_count,(size_t)r->bitrev_count,1,-1);
        prepare_refused(p,n,(size_t)r->trig_count,(size_t)r->bitrev_count,2,-1);
        prepare_refused(p,n,SIZE_MAX,(size_t)r->bitrev_count,0,-2);
        prepare_refused(p,n,(size_t)r->trig_count,SIZE_MAX,0,-2);
        prepare_refused(p,n,(size_t)r->trig_count,(size_t)r->bitrev_count,4,-1);
    }
    const uint32_t bad[] = {0,1,63,65,1023,8193,UINT32_MAX};
    for (size_t i = 0; i < sizeof(bad)/sizeof(*bad); ++i) {
        native_vorbis_imdct_requirements_t result;
        unsigned char before[sizeof(result)]; memset(&result,0xa5,sizeof(result)); memcpy(before,&result,sizeof(result));
        CHECK(native_vorbis_imdct_measure(bad[i],&result) == -1);
        CHECK(memcmp(before,&result,sizeof(result)) == 0); ++refusals;
        prepare_refused(&plans[0],bad[i],80,16,0,-1);
    }
    CHECK(native_vorbis_imdct_measure(64,NULL) == -1); ++refusals;
    lookups_unchanged();
}
static void conversion_refused(const native_vorbis_floor1_product_t *source, size_t capacity,
    double *output, size_t output_capacity, native_vorbis_transform_block_t *result,
    int wanted, const guard_t *destination, const guard_t *saved) {
    unsigned char before[sizeof(*result)]; memcpy(before,result,sizeof(before));
    CHECK(native_vorbis_spectrum_to_binary64(source,capacity,output,output_capacity,result) == wanted);
    CHECK(memcmp(before,result,sizeof(before)) == 0); ++refusals;
    unchanged(destination,saved);
}
static void conversion_controls(native_vorbis_floor1_product_t *source, guard_t *output,
    native_vorbis_transform_block_t *result) {
    guard_t saved = clone(output); size_t count = (size_t)source->layout.limb_count;
    double *destination = (double *)output->data; size_t bins = source->layout.bins;
#define REF(S,C,O,N,E) conversion_refused(S,C,O,N,result,E,output,&saved)
    REF(NULL,count,destination,bins,-1); REF(source,count,NULL,bins,-1);
    REF(source,count,destination,bins-1,-4); REF(source,SIZE_MAX,destination,bins,-2);
    REF(source,count,destination,SIZE_MAX,-2);
    CHECK(native_vorbis_spectrum_to_binary64(source,count,destination,bins,NULL) == -1); ++refusals;
    native_vorbis_floor1_product_t invalid = *source;
    invalid.layout.bins=0; REF(&invalid,count,destination,bins,-1);
    invalid=*source; invalid.layout.bins=4097; REF(&invalid,count,destination,bins,-1);
    invalid=*source; ++invalid.layout.limb_count; REF(&invalid,count,destination,bins,-1);
    invalid=*source; invalid.layout.limbs=37; REF(&invalid,count,destination,bins,-1);
    invalid=*source; invalid.layout.magnitude_bits=1152; REF(&invalid,count,destination,bins,-1);
    if (source->layout.limbs) {
        REF(source,count-1,destination,bins,-4);
        invalid=*source; invalid.samples=NULL; REF(&invalid,count,destination,bins,-1);
        invalid=*source; invalid.layout.magnitude_bits=0; REF(&invalid,count,destination,bins,-1);
    } else {
        invalid=*source; invalid.layout.exponent=1; REF(&invalid,count,destination,bins,-1);
    }
    CHECK(native_vorbis_spectrum_to_binary64(source,count,destination,bins,result) == 0);
    unchanged(output,&saved); destroy(&saved);
#undef REF
}
static void transform_refused(const native_vorbis_imdct_plan_t *plan,
    const native_vorbis_floor1_product_t *source,size_t capacity,double *workspace,size_t wc,
    native_vorbis_transform_block_t *result,int wanted,const guard_t *work,const guard_t *saved) {
    unsigned char before[sizeof(*result)]; memcpy(before,result,sizeof(before));
    CHECK(native_vorbis_imdct_transform(plan,source,capacity,workspace,wc,result) == wanted);
    CHECK(memcmp(before,result,sizeof(before)) == 0); ++refusals; unchanged(work,saved);
}
static void transform_controls(plan_t *plan,native_vorbis_floor1_product_t *source,
    guard_t *work,native_vorbis_transform_block_t *result) {
    guard_t saved=clone(work); size_t capacity=(size_t)source->layout.limb_count;
    double *workspace=(double *)work->data; size_t wc=(size_t)plan->requirements.workspace_count;
#define REF(P,S,C,W,N,E) transform_refused(P,S,C,W,N,result,E,work,&saved)
    REF(NULL,source,capacity,workspace,wc,-1); REF(&plan->plan,NULL,capacity,workspace,wc,-1);
    REF(&plan->plan,source,capacity,NULL,wc,-1); REF(&plan->plan,source,capacity,workspace,wc-1,-4);
    REF(&plan->plan,source,capacity,workspace,SIZE_MAX,-2); REF(&plan->plan,source,SIZE_MAX,workspace,wc,-2);
    CHECK(native_vorbis_imdct_transform(&plan->plan,source,capacity,workspace,wc,NULL) == -1); ++refusals;
    native_vorbis_imdct_plan_t invalid=plan->plan;
    ++invalid.log2n; REF(&invalid,source,capacity,workspace,wc,-1);
    invalid=plan->plan; invalid.blocksize=63; REF(&invalid,source,capacity,workspace,wc,-1);
    invalid=plan->plan; invalid.trig=NULL; REF(&invalid,source,capacity,workspace,wc,-1);
    invalid=plan->plan; invalid.bitrev=NULL; REF(&invalid,source,capacity,workspace,wc,-1);
    native_vorbis_floor1_product_t bad=*source;
    ++bad.layout.bins; REF(&plan->plan,&bad,capacity,workspace,wc,-1);
    if(source->layout.limbs) {
        REF(&plan->plan,source,capacity-1,workspace,wc,-4);
        bad=*source; bad.samples=NULL; REF(&plan->plan,&bad,capacity,workspace,wc,-1);
    }
    CHECK(native_vorbis_imdct_transform(&plan->plan,source,capacity,workspace,wc,result) == 0);
    unchanged(work,&saved); destroy(&saved); lookups_unchanged();
#undef REF
}
static void tail_unchanged(const guard_t *value,size_t used) {
    CHECK(used <= value->bytes);
    for(size_t i=used;i<value->bytes;++i) CHECK(value->data[i] == 0xa5);
    validate(value);
}
static void run_case(FILE *input,FILE *output,uint32_t index) {
    uint32_t kind=read32(input),n=read32(input),bins=read32(input),limbs=read32(input),width=read32(input);
    int32_t exponent=signed32(read32(input)); uint32_t controls=read32(input);
    CHECK(kind<=1 && bins>=1 && bins<=4096 && limbs<=36 && controls<=1);
    uint64_t words=(uint64_t)bins*limbs; CHECK(words <= SIZE_MAX/4);
    guard_t samples=create((size_t)words*4);
    for(size_t i=0;i<(size_t)words;++i) ((uint32_t *)samples.data)[i]=read32(input);
    guard_t sample_copy=clone(&samples),converted=create(((size_t)bins+3)*sizeof(double));
    native_vorbis_floor1_product_t source={.layout={bins,limbs,width,exponent,words},
        .samples=words?(const uint32_t *)samples.data:NULL};
    unsigned char source_before[sizeof(source)]; memcpy(source_before,&source,sizeof(source));
    native_vorbis_transform_block_t result;
    unsigned char result_before[sizeof(result)]; memset(&result,0xa5,sizeof(result)); memcpy(result_before,&result,sizeof(result));
    int status=native_vorbis_spectrum_to_binary64(&source,(size_t)words,(double *)converted.data,bins,&result);
    put32(output,index); put32(output,kind); put32(output,(uint32_t)status);
    if(!status) {
        CHECK(result.count==bins && result.samples==(double *)converted.data);
        CHECK(result.exponent==(limbs?(int64_t)exponent+512:0)); block(output,&result);
        tail_unchanged(&converted,(size_t)bins*sizeof(double));
        if(controls) conversion_controls(&source,&converted,&result);
    } else {
        CHECK(status==-1 && memcmp(result_before,&result,sizeof(result))==0);
        tail_unchanged(&converted,0);
    }
    if(kind) {
        CHECK(n>=64 && n<=8192 && !(n&(n-1)) && bins==n/2);
        unsigned plan_index=0; for(uint32_t value=n;value>64;value>>=1) ++plan_index;
        plan_t *plan=&plans[plan_index]; size_t wc=(size_t)plan->requirements.workspace_count;
        guard_t work=create((wc+3)*sizeof(double));
        native_vorbis_transform_block_t time;
        unsigned char before[sizeof(time)]; memset(&time,0xa5,sizeof(time)); memcpy(before,&time,sizeof(time));
        int ts=native_vorbis_imdct_transform(&plan->plan,&source,(size_t)words,(double *)work.data,wc,&time);
        put32(output,(uint32_t)ts);
        if(!ts) {
            CHECK(time.count==n && time.samples==(double *)work.data+8 && time.exponent==result.exponent);
            for(size_t i=0;i<8;++i) CHECK(((double *)work.data)[i]==0.0);
            for(size_t i=0;i<n;++i) CHECK(isfinite(time.samples[i]));
            block(output,&time); tail_unchanged(&work,wc*sizeof(double));
            if(controls) transform_controls(plan,&source,&work,&time);
        } else {
            CHECK(ts==status && ts==-1 && memcmp(before,&time,sizeof(time))==0);
            tail_unchanged(&work,0);
        }
        destroy(&work);
    }
    CHECK(memcmp(source_before,&source,sizeof(source))==0);
    unchanged(&samples,&sample_copy); lookups_unchanged();
    destroy(&converted); destroy(&sample_copy); destroy(&samples);
}
int main(int argc,char **argv) {
    CHECK(argc==3); FILE *input=fopen(argv[1],"rb"),*output=fopen(argv[2],"wb"); CHECK(input && output);
    unsigned char magic[8]; CHECK(fread(magic,1,8,input)==8 && memcmp(magic,"VTRANS01",8)==0);
    CHECK(fwrite("VTROUT01",1,8,output)==8); uint32_t count=read32(input); put32(output,count); make_plans(output);
    for(uint32_t i=0;i<count;++i) run_case(input,output,i);
    CHECK(fgetc(input)==EOF && !ferror(input));
    for(unsigned i=0;i<8;++i) {
        destroy(&plans[i].bitrev_copy); destroy(&plans[i].trig_copy); destroy(&plans[i].bitrev); destroy(&plans[i].trig);
    }
    CHECK(live_blocks==0 && live_bytes==0); uint64_t final_checks=checks+5;
    put64(output,refusals); put64(output,final_checks);
    CHECK(fclose(input)==0 && fclose(output)==0);
    printf("TRANSFORM_CAPTURE cases=%"PRIu32" refusals=%"PRIu64" checks=%"PRIu64" live=0 bytes=0\n",count,refusals,checks);
    return 0;
}
