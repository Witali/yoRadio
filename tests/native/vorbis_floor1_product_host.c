// Guarded generic floor1 product capture. The integer oracle lives in Python.
#include "native_vorbis_floor1_product.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks, refusals;
#define CHECK(x) do { ++checks; assert(x); } while (0)

static uint32_t read32(FILE *file) {
    unsigned char bytes[4]; CHECK(fread(bytes, 1, 4, file) == 4);
    return (uint32_t)bytes[0] | (uint32_t)bytes[1] << 8 |
        (uint32_t)bytes[2] << 16 | (uint32_t)bytes[3] << 24;
}
static int32_t read_signed(FILE *file) {
    uint32_t bits = read32(file); int32_t value; memcpy(&value, &bits, 4); return value;
}
static void write32(FILE *file, uint32_t value) {
    unsigned char bytes[4] = {(unsigned char)value, (unsigned char)(value >> 8),
        (unsigned char)(value >> 16), (unsigned char)(value >> 24)};
    CHECK(fwrite(bytes, 1, 4, file) == 4);
}
static void write64(FILE *file, uint64_t value) {
    write32(file, (uint32_t)value); write32(file, (uint32_t)(value >> 32));
}
static void layout_write(FILE *file, const native_vorbis_floor1_product_layout_t *value) {
    write32(file, value->bins); write32(file, value->limbs);
    write32(file, value->magnitude_bits); write32(file, (uint32_t)value->exponent);
    write64(file, value->limb_count);
}
static bool same_layout(const native_vorbis_floor1_product_layout_t *a,
                        const native_vorbis_floor1_product_layout_t *b) {
    return a->bins == b->bins && a->limbs == b->limbs &&
        a->magnitude_bits == b->magnitude_bits && a->exponent == b->exponent &&
        a->limb_count == b->limb_count;
}
static void refused(const native_vorbis_residue_layout_t *source,
    const uint32_t *spectrum, size_t source_capacity, uint32_t channel,
    const uint8_t *indices, size_t count, uint32_t *destination,
    size_t destination_capacity, native_vorbis_floor1_product_t *published,
    int expected, const uint32_t *saved, size_t saved_count) {
    unsigned char result_copy[sizeof(*published)];
    memcpy(result_copy, published, sizeof(result_copy));
    int status = native_vorbis_floor1_scale(source, spectrum, source_capacity,
        channel, indices, count, destination, destination_capacity, published);
    CHECK(status == expected); ++refusals;
    CHECK(!memcmp(result_copy, published, sizeof(result_copy)));
    if (destination) CHECK(!memcmp(saved, destination, saved_count * sizeof(*saved)));
}
static void measure_refused(const native_vorbis_residue_layout_t *source,
    const uint8_t *indices, size_t count, int expected) {
    native_vorbis_floor1_product_layout_t output;
    unsigned char saved[sizeof(output)];
    memset(&output, 0x5a, sizeof(output)); memcpy(saved, &output, sizeof(saved));
    CHECK(native_vorbis_floor1_scale_measure(source, indices, count, &output) == expected);
    CHECK(!memcmp(saved, &output, sizeof(saved))); ++refusals;
}
static void controls(const native_vorbis_residue_layout_t *source,
    uint32_t *spectrum, const uint8_t *indices, uint32_t channel,
    uint32_t *destination, native_vorbis_floor1_product_t *published) {
    size_t n = (size_t)published->layout.limb_count;
    uint32_t *saved = malloc((n ? n : 1) * sizeof(*saved)); CHECK(saved);
    if (n) memcpy(saved, destination, n * sizeof(*saved));
    size_t source_count = (size_t)source->limb_count;
#define REF(S,P,C,CH,I,N,O,OC,E) refused(S,P,C,CH,I,N,O,OC,published,E,saved,n)
    REF(source,spectrum,source_count,channel,indices,source->bins-1,destination,n,-1);
    REF(NULL,spectrum,source_count,channel,indices,source->bins,destination,n,-1);
    REF(source,spectrum,source_count,source->channels,indices,source->bins,destination,n,-1);
    REF(source,spectrum,SIZE_MAX,channel,indices,source->bins,destination,n,-2);
    REF(source,spectrum,source_count,channel,indices,source->bins,destination,SIZE_MAX,-2);
    measure_refused(NULL,indices,source->bins,-1);
    measure_refused(source,indices,source->bins-1,-1);
    CHECK(native_vorbis_floor1_scale_measure(source,indices,source->bins,NULL) == -1); ++refusals;
    CHECK(native_vorbis_floor1_scale(source,spectrum,source_count,channel,indices,source->bins,
        destination,n,NULL) == -1); ++refusals;
    if (source->limbs) {
        REF(source,spectrum,source_count-1,channel,indices,source->bins,destination,n,-4);
        REF(source,spectrum,source_count,channel,indices,source->bins,destination,n-1,-4);
        REF(source,NULL,source_count,channel,indices,source->bins,destination,n,-1);
        REF(source,spectrum,source_count,channel,indices,source->bins,NULL,n,-1);
        REF(source,spectrum,source_count,channel,NULL,source->bins,destination,n,-1);
        measure_refused(source,NULL,source->bins,-1);
    }
    native_vorbis_residue_layout_t invalid = *source;
#define BAD(F,V) do { invalid=*source; invalid.F=(V); measure_refused(&invalid,indices,source->bins,-1); } while (0)
    BAD(bins,0); BAD(bins,4097); BAD(channels,0); BAD(channels,256);
    BAD(sample_count,source->sample_count+1); BAD(limb_count,source->limb_count+1);
    BAD(limbs,35); BAD(magnitude_bits,1088);
    if (source->limbs) { BAD(magnitude_bits,0); BAD(limbs,source->limbs-1); }
    else { BAD(exponent,1); BAD(magnitude_bits,1); }
#undef BAD
    // Invalid bytes in an unselected channel must not affect selected output.
    if (source->channels > 1 && source->limbs) {
        uint32_t other = channel ? 0 : 1;
        size_t at = (size_t)other * source->bins * source->limbs;
        size_t words = (size_t)source->bins * source->limbs;
        uint32_t *copy = malloc(words * sizeof(*copy)); CHECK(copy);
        memcpy(copy,spectrum+at,words*sizeof(*copy));
        memset(spectrum+at,0xa5,words*sizeof(*copy));
        CHECK(native_vorbis_floor1_scale(source,spectrum,source_count,channel,indices,
            source->bins,destination,n,published) == 0);
        CHECK(!memcmp(saved,destination,n*sizeof(*saved)));
        memcpy(spectrum+at,copy,words*sizeof(*copy)); free(copy);
    }
    // Canonical full retry after the refusal controls.
    CHECK(native_vorbis_floor1_scale(source,spectrum,source_count,channel,indices,
        source->bins,destination,n,published) == 0);
    CHECK(!n || !memcmp(saved,destination,n*sizeof(*saved)));
#undef REF
    free(saved);
}

int main(int argc, char **argv) {
    CHECK(argc == 3);
    FILE *input = fopen(argv[1],"rb"), *output = fopen(argv[2],"wb"); CHECK(input && output);
    char magic[8]; CHECK(fread(magic,1,8,input)==8 && !memcmp(magic,"F1PROD01",8));
    CHECK(fwrite("F1OUT001",1,8,output)==8);
    uint32_t cases = read32(input); write32(output,cases);
    for (uint32_t row=0; row<cases; ++row) {
        native_vorbis_residue_layout_t source = {.mapping=UINT32_MAX,.classification_count=UINT64_MAX};
        source.bins=read32(input); source.channels=read32(input); uint32_t channel=read32(input);
        source.limbs=read32(input); source.magnitude_bits=read32(input); source.exponent=read_signed(input);
        uint32_t run_controls=read32(input);
        CHECK(source.bins && source.bins<=4096 && source.channels && source.channels<=255 &&
            source.limbs<=34 && source.magnitude_bits<=1087 && channel<source.channels && run_controls<=1);
        source.sample_count=(uint64_t)source.bins*source.channels;
        source.limb_count=source.sample_count*source.limbs;
        unsigned char source_copy[sizeof(source)]; memcpy(source_copy,&source,sizeof(source));
        size_t input_words=(size_t)source.limb_count, max_words=(size_t)source.bins*36;
        uint8_t *curve=malloc((size_t)source.bins+2), *curve_copy=malloc(source.bins); CHECK(curve && curve_copy);
        curve[0]=0x37; curve[source.bins+1]=0xb9;
        CHECK(fread(curve+1,1,source.bins,input)==source.bins); memcpy(curve_copy,curve+1,source.bins);
        uint32_t *data=malloc((input_words+2)*sizeof(*data));
        uint32_t *copy=malloc((input_words?input_words:1)*sizeof(*copy));
        uint32_t *scaled=malloc((max_words+2)*sizeof(*scaled)); CHECK(data && copy && scaled);
        data[0]=scaled[0]=UINT32_C(0x13579bdf);
        data[input_words+1]=scaled[max_words+1]=UINT32_C(0x2468ace0);
        for(size_t i=0;i<input_words;++i)data[i+1]=read32(input);
        if(input_words)memcpy(copy,data+1,input_words*sizeof(*copy));
        for(size_t i=0;i<max_words;++i)scaled[i+1]=UINT32_C(0xa5a5a5a5);
        native_vorbis_floor1_product_layout_t measured;
        unsigned char before_measure[sizeof(measured)];
        memset(&measured,0x5a,sizeof(measured));memcpy(before_measure,&measured,sizeof(measured));
        const uint8_t *indices=source.limbs?curve+1:NULL;
        int measure=native_vorbis_floor1_scale_measure(&source,indices,source.bins,&measured);
        if(measure)CHECK(!memcmp(before_measure,&measured,sizeof(measured)));
        native_vorbis_floor1_product_t result;
        unsigned char before_result[sizeof(result)];
        memset(&result,0x5a,sizeof(result));memcpy(before_result,&result,sizeof(result));
        size_t capacity=measure?max_words:(size_t)measured.limb_count;
        int status=native_vorbis_floor1_scale(&source,source.limbs?data+1:NULL,input_words,channel,
            indices,source.bins,source.limbs?scaled+1:NULL,capacity,&result);
        write32(output,row);write32(output,(uint32_t)measure);
        if(!measure)layout_write(output,&measured);
        write32(output,(uint32_t)status);
        if(!status) {
            CHECK(!measure && same_layout(&result.layout,&measured));
            CHECK(result.samples==(source.limbs?scaled+1:NULL));
            if(run_controls)controls(&source,data+1,indices,channel,scaled+1,&result);
            layout_write(output,&result.layout);
            for(size_t i=0;i<result.layout.limb_count;++i)write32(output,scaled[i+1]);
            for(size_t i=(size_t)result.layout.limb_count;i<max_words;++i)
                CHECK(scaled[i+1]==UINT32_C(0xa5a5a5a5));
        } else {
            CHECK(!memcmp(before_result,&result,sizeof(result)));
            for(size_t i=0;i<max_words;++i)CHECK(scaled[i+1]==UINT32_C(0xa5a5a5a5));
        }
        CHECK(curve[0]==0x37 && curve[source.bins+1]==0xb9 && !memcmp(curve_copy,curve+1,source.bins));
        CHECK(data[0]==UINT32_C(0x13579bdf) && data[input_words+1]==UINT32_C(0x2468ace0));
        CHECK(scaled[0]==UINT32_C(0x13579bdf) && scaled[max_words+1]==UINT32_C(0x2468ace0));
        CHECK(!input_words || !memcmp(copy,data+1,input_words*sizeof(*copy)));
        CHECK(!memcmp(source_copy,&source,sizeof(source)));
        free(curve);free(curve_copy);free(data);free(copy);free(scaled);
    }
    CHECK(fgetc(input)==EOF);write64(output,refusals);write64(output,checks+4);
    CHECK(!fclose(input)); CHECK(!fclose(output));
    printf("FLOOR1_PRODUCT_CAPTURE cases=%" PRIu32 " refusals=%" PRIu64 " checks=%" PRIu64 "\n",cases,refusals,checks);
    return 0;
}
