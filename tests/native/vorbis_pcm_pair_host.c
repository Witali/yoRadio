// Exact pair-to-S16 capture and immediate refusal snapshots.
#include "native_vorbis_pcm.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks, refusals;
#define CHECK(x) do { ++checks; assert(x); } while (0)
typedef struct { unsigned char *raw, *data; size_t bytes; } guard_t;
static guard_t create(size_t bytes) {
    CHECK(bytes <= SIZE_MAX - 32); guard_t g = {.raw = malloc(bytes + 32), .bytes = bytes}; CHECK(g.raw);
    g.data = g.raw + 16; memset(g.raw, 0xa5, bytes + 32); return g;
}
static void validate(const guard_t *g) {
    for (size_t i = 0; i < 16; ++i) { CHECK(g->raw[i] == 0xa5); CHECK(g->data[g->bytes + i] == 0xa5); }
}
static guard_t copy(const guard_t *g) {
    guard_t result = create(g->bytes); memcpy(result.data, g->data, g->bytes); return result;
}
static void unchanged(const guard_t *g, const guard_t *before) {
    validate(g); CHECK(g->bytes == before->bytes); CHECK(!memcmp(g->data, before->data, g->bytes));
}
static void destroy(guard_t *g) { validate(g); free(g->raw); memset(g, 0, sizeof(*g)); }
static uint32_t read32(FILE *f) {
    unsigned char b[4]; CHECK(fread(b, 1, 4, f) == 4);
    return (uint32_t)b[0] | (uint32_t)b[1] << 8 | (uint32_t)b[2] << 16 | (uint32_t)b[3] << 24;
}
static uint64_t read64(FILE *f) { uint64_t low = read32(f); return low | (uint64_t)read32(f) << 32; }
static int64_t read_signed(FILE *f) { uint64_t u = read64(f); int64_t s; memcpy(&s, &u, 8); return s; }
static void put32(FILE *f, uint32_t u) {
    unsigned char b[4] = {(unsigned char)u,(unsigned char)(u >> 8),(unsigned char)(u >> 16),(unsigned char)(u >> 24)};
    CHECK(fwrite(b, 1, 4, f) == 4);
}
static void put64(FILE *f, uint64_t u) { put32(f, (uint32_t)u); put32(f, (uint32_t)(u >> 32)); }
static void put16(FILE *f, int16_t value) {
    uint16_t word; memcpy(&word, &value, 2);
    unsigned char b[2] = {(unsigned char)word,(unsigned char)(word >> 8)}; CHECK(fwrite(b, 1, 2, f) == 2);
}
static void refused(const native_vorbis_transform_block_t *a, size_t ac,
    const native_vorbis_transform_block_t *b, size_t bc, int16_t *output, size_t oc, int wanted,
    const guard_t *input_a, const guard_t *input_b, const guard_t *destination) {
    guard_t a_before = copy(input_a), b_before = copy(input_b), out_before = copy(destination);
    unsigned char ad[sizeof(*a)], bd[sizeof(*b)];
    if (a) memcpy(ad, a, sizeof(ad));
    if (b) memcpy(bd, b, sizeof(bd));
    CHECK(native_vorbis_pcm_s16_pair(a,ac,b,bc,output,oc) == wanted); ++refusals;
    if (a) CHECK(!memcmp(ad, a, sizeof(ad)));
    if (b) CHECK(!memcmp(bd, b, sizeof(bd)));
    unchanged(input_a,&a_before); unchanged(input_b,&b_before); unchanged(destination,&out_before);
    destroy(&out_before); destroy(&b_before); destroy(&a_before);
}
static void controls(native_vorbis_transform_block_t *a, native_vorbis_transform_block_t *b,
    guard_t *aa, guard_t *bb, guard_t *out) {
    uint32_t n = a->count; int16_t *destination = (int16_t *)out->data;
#define REF(A,AC,B,BC,O,OC,E) refused(A,AC,B,BC,O,OC,E,aa,bb,out)
    REF(NULL,n,b,n,destination,n,-1); REF(a,n,NULL,n,destination,n,-1);
    REF(a,SIZE_MAX,b,n,destination,n,-2); REF(a,n,b,SIZE_MAX,destination,n,-2);
    REF(a,n,b,n,destination,SIZE_MAX,-2);
    native_vorbis_transform_block_t bad = *a; bad.count = n + 1;
    REF(&bad,n,b,n,destination,n,-1);
    if (n) {
        REF(a,n-1,b,n,destination,n,-4); REF(a,n,b,n-1,destination,n,-4);
        REF(a,n,b,n,destination,n-1,-4); REF(a,n,b,n,NULL,n,-1);
        bad = *a; bad.samples = NULL; REF(&bad,n,b,n,destination,n,-1);
        bad = *b; bad.samples = NULL; REF(a,n,&bad,n,destination,n,-1);
        uint64_t invalid[] = {UINT64_C(0x7ff0000000000000),UINT64_C(0xfff0000000000000),
            UINT64_C(0x7ff8000000000001),UINT64_C(0x7ff0000000000001)};
        for (unsigned side = 0; side < 2; ++side) {
            unsigned char *last = (side ? bb : aa)->data + (n-1)*8; unsigned char saved[8]; memcpy(saved,last,8);
            for (unsigned i = 0; i < 4; ++i) {
                memcpy(last,&invalid[i],8); REF(a,n,b,n,destination,n,-2);
            }
            memcpy(last,saved,8);
        }
    } else CHECK(native_vorbis_pcm_s16_pair(a,0,b,0,NULL,0) == 0);
#undef REF
}
int main(int argc, char **argv) {
    CHECK(argc == 3); FILE *in = fopen(argv[1],"rb"), *out = fopen(argv[2],"wb"); CHECK(in && out);
    unsigned char magic[8]; CHECK(fread(magic,1,8,in) == 8 && !memcmp(magic,"VPCMPR01",8));
    CHECK(fwrite(magic,1,8,out) == 8); uint32_t rows = read32(in); put32(out,rows);
    for (uint32_t row = 0; row < rows; ++row) {
        uint32_t n = read32(in), test_controls = read32(in); int64_t ea = read_signed(in), eb = read_signed(in);
        guard_t aa = create((size_t)n*8), bb = create((size_t)n*8), output = create((size_t)n*2+8);
        for (uint32_t side = 0; side < 2; ++side) {
            unsigned char *data = side ? bb.data : aa.data;
            for (uint32_t i = 0; i < n; ++i) { uint64_t word = read64(in); memcpy(data+i*8,&word,8); }
        }
        native_vorbis_transform_block_t a = {.count=n,.exponent=ea,.samples=n?(const double *)aa.data:NULL};
        native_vorbis_transform_block_t b = {.count=n,.exponent=eb,.samples=n?(const double *)bb.data:NULL};
        unsigned char ad[sizeof(a)], bd[sizeof(b)]; memcpy(ad,&a,sizeof(a)); memcpy(bd,&b,sizeof(b));
        guard_t a_before = copy(&aa), b_before = copy(&bb);
        if (test_controls) controls(&a,&b,&aa,&bb,&output);
        CHECK(native_vorbis_pcm_s16_pair(&a,n,&b,n,(int16_t *)output.data,n) == 0);
        unchanged(&aa,&a_before); unchanged(&bb,&b_before);
        CHECK(!memcmp(ad,&a,sizeof(a)) && !memcmp(bd,&b,sizeof(b)));
        for (size_t i = (size_t)n*2; i < output.bytes; ++i) CHECK(output.data[i] == 0xa5);
        put32(out,n); put64(out,(uint64_t)ea); put64(out,(uint64_t)eb);
        for (uint32_t side = 0; side < 2; ++side) {
            unsigned char *data = side ? bb.data : aa.data;
            for (uint32_t i = 0; i < n; ++i) { uint64_t word; memcpy(&word,data+i*8,8); put64(out,word); }
        }
        for (uint32_t i = 0; i < n; ++i) put16(out,((int16_t *)output.data)[i]);
        destroy(&b_before); destroy(&a_before); destroy(&output); destroy(&bb); destroy(&aa);
    }
    CHECK(fgetc(in) == EOF); CHECK(fclose(in) == 0); CHECK(fclose(out) == 0);
    printf("PCM_PAIR_CAPTURE rows=%" PRIu32 " refusals=%" PRIu64 " checks=%" PRIu64 "\n",rows,refusals,checks);
    return 0;
}
