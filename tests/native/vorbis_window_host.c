// Guarded window geometry, failure atomicity, and every legal transition.
#include "native_vorbis_window.h"
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t checks, refusals;
#define CHECK(x) do { ++checks; assert(x); } while (0)
static void put32(FILE *f, uint32_t u) {
    unsigned char b[4] = {(unsigned char)u, (unsigned char)(u >> 8),
        (unsigned char)(u >> 16), (unsigned char)(u >> 24)};
    CHECK(fwrite(b, 1, 4, f) == 4);
}
static void put64(FILE *f, uint64_t u) { put32(f, (uint32_t)u); put32(f, (uint32_t)(u >> 32)); }
static void values(FILE *f, const double *data, size_t count) {
    for (size_t i = 0; i < count; ++i) { uint64_t u; memcpy(&u, data + i, 8); put64(f, u); }
}
static double *storage(size_t n) {
    double *p = malloc((n + 4) * sizeof(*p)); CHECK(p); memset(p, 0xa5, (n + 4) * sizeof(*p));
    return p;
}
static void guarded(const double *p, size_t n) {
    const unsigned char *b = (const unsigned char *)p;
    for (size_t i = 0; i < 16; ++i) { CHECK(b[i] == 0xa5); CHECK(b[(n + 2) * 8 + i] == 0xa5); }
}
static double sample(uint32_t i) {
    switch (i % 12) {
        case 0: return DBL_MAX;
        case 1: return -DBL_MAX;
        case 2: return DBL_TRUE_MIN;
        case 3: return -DBL_TRUE_MIN;
        case 4: return 0.0;
        case 5: return -0.0;
        case 6: return 0x1p-1000;
        case 7: return -0x1p800;
        case 8: return 1.0;
        case 9: return -1.0;
        default: return ((int)(i % 1021) - 510) * .03125;
    }
}
static native_vorbis_window_plan_t plans[8];
static double *coefficients[8], *coefficient_copies[8];
static void make_plans(FILE *f) {
    put32(f, 8);
    for (unsigned i = 0; i < 8; ++i) {
        uint32_t n = UINT32_C(64) << i; size_t count = n / 2;
        coefficients[i] = storage(count); double *data = coefficients[i] + 2;
        native_vorbis_window_plan_t p;
        memset(&p, 0xa5, sizeof(p)); unsigned char saved[sizeof(p)]; memcpy(saved, &p, sizeof(p));
#define PREP(N,D,C,P,E) do { \
        CHECK(native_vorbis_window_prepare(N,D,C,P) == (E)); ++refusals; \
        CHECK(memcmp(saved, &p, sizeof(p)) == 0); \
        for (size_t k = 0; k < count * 8; ++k) CHECK(((unsigned char *)data)[k] == 0xa5); \
        guarded(coefficients[i], count); \
    } while (0)
        PREP(n, data, count - 1, &p, -4);
        PREP(n, NULL, count, &p, -1);
        PREP(n, data, SIZE_MAX, &p, -2);
        PREP(n, data, count, NULL, -1);
        const uint32_t bad[] = {0, 1, 63, 65, 8193, UINT32_MAX};
        for (size_t j = 0; j < sizeof(bad) / sizeof(*bad); ++j)
            PREP(bad[j], data, count, &p, -1);
#undef PREP
        CHECK(native_vorbis_window_prepare(n, data, count, &plans[i]) == 0);
        CHECK(plans[i].blocksize == n && plans[i].rise == data);
        coefficient_copies[i] = malloc(count * 8); CHECK(coefficient_copies[i]);
        memcpy(coefficient_copies[i], data, count * 8);
        put32(f, n); values(f, data, count);
    }
}
static void run_case(FILE *f, unsigned small, unsigned large, unsigned flags) {
    uint32_t s = UINT32_C(64) << small, l = UINT32_C(64) << large;
    unsigned w = flags & 1, prev = (flags >> 1) & 1, next = (flags >> 2) & 1;
    native_vorbis_window_shape_t shape;
    CHECK(native_vorbis_window_shape(s, l, w, prev, next, &shape) == 0);
    uint32_t n = shape.blocksize; size_t bytes = n * sizeof(double);
    double *raw_in = storage(n), *raw_out = storage(n), *data = raw_in + 2, *out = raw_out + 2;
    double *input_copy = malloc(bytes), *output_copy = malloc(bytes), *call_input = malloc(bytes);
    CHECK(input_copy && output_copy && call_input);
    for (uint32_t i = 0; i < n; ++i) data[i] = sample(i + flags);
    memcpy(input_copy, data, bytes); memcpy(output_copy, out, bytes);
    native_vorbis_transform_block_t source = {.count = n,
        .exponent = flags & 2 ? INT64_MIN : INT64_MAX, .samples = data}, result;
    memset(&result, 0xa5, sizeof(result)); unsigned char saved[sizeof(result)]; memcpy(saved, &result, sizeof(result));
    const native_vorbis_window_plan_t *left = &plans[w && prev ? large : small];
    const native_vorbis_window_plan_t *right = &plans[w && next ? large : small];
#define APPLY(S,L,R,I,IC,O,OC,D,E) do { \
    const native_vorbis_window_shape_t *checked_shape = (S); \
    const native_vorbis_window_plan_t *checked_left = (L), *checked_right = (R); \
    const native_vorbis_transform_block_t *checked_source = (I); \
    unsigned char shape_before[sizeof(shape)], left_before[sizeof(*left)], \
        right_before[sizeof(*right)], source_before[sizeof(source)]; \
    memcpy(call_input, data, bytes); \
    if (checked_shape) memcpy(shape_before, checked_shape, sizeof(shape_before)); \
    if (checked_left) memcpy(left_before, checked_left, sizeof(left_before)); \
    if (checked_right) memcpy(right_before, checked_right, sizeof(right_before)); \
    if (checked_source) memcpy(source_before, checked_source, sizeof(source_before)); \
    CHECK(native_vorbis_window_apply(S,L,R,I,IC,O,OC,D) == (E)); ++refusals; \
    CHECK(memcmp(saved, &result, sizeof(result)) == 0); CHECK(memcmp(output_copy, out, bytes) == 0); \
    CHECK(memcmp(call_input, data, bytes) == 0); guarded(raw_in, n); guarded(raw_out, n); \
    if (checked_shape) CHECK(memcmp(shape_before, checked_shape, sizeof(shape_before)) == 0); \
    if (checked_left) CHECK(memcmp(left_before, checked_left, sizeof(left_before)) == 0); \
    if (checked_right) CHECK(memcmp(right_before, checked_right, sizeof(right_before)) == 0); \
    if (checked_source) CHECK(memcmp(source_before, checked_source, sizeof(source_before)) == 0); \
} while (0)
    APPLY(NULL,left,right,&source,n,out,n,&result,-1);
    APPLY(&shape,NULL,right,&source,n,out,n,&result,-1);
    APPLY(&shape,left,NULL,&source,n,out,n,&result,-1);
    APPLY(&shape,left,right,NULL,n,out,n,&result,-1);
    APPLY(&shape,left,right,&source,n,NULL,n,&result,-1);
    APPLY(&shape,left,right,&source,n,out,n,NULL,-1);
    APPLY(&shape,left,right,&source,n-1,out,n,&result,-4);
    APPLY(&shape,left,right,&source,n,out,n-1,&result,-4);
    APPLY(&shape,left,right,&source,SIZE_MAX,out,n,&result,-2);
    APPLY(&shape,left,right,&source,n,out,SIZE_MAX,&result,-2);
    native_vorbis_window_shape_t bad_shape = shape; ++bad_shape.right_end;
    APPLY(&bad_shape,left,right,&source,n,out,n,&result,-1);
    native_vorbis_window_plan_t bad_plan = *left; bad_plan.blocksize = 63;
    APPLY(&shape,&bad_plan,right,&source,n,out,n,&result,-1);
    bad_plan = *right; bad_plan.rise = NULL;
    APPLY(&shape,left,&bad_plan,&source,n,out,n,&result,-1);
    native_vorbis_transform_block_t bad_source = source; --bad_source.count;
    APPLY(&shape,left,right,&bad_source,n,out,n,&result,-1);
    bad_source = source; bad_source.samples = NULL;
    APPLY(&shape,left,right,&bad_source,n,out,n,&result,-1);
    const double invalid[] = {NAN, INFINITY, -INFINITY};
    for (unsigned i = 0; i < 3; ++i) {
        data[n - 1] = invalid[i];
        APPLY(&shape,left,right,&source,n,out,n,&result,-2);
        memcpy(data + n - 1, input_copy + n - 1, 8);
    }
#undef APPLY
    CHECK(native_vorbis_window_apply(&shape,left,right,&source,n,out,n,&result) == 0);
    CHECK(result.count == n && result.exponent == source.exponent && result.samples == out);
    CHECK(memcmp(data, input_copy, bytes) == 0); guarded(raw_in, n); guarded(raw_out, n);
    put32(f, s); put32(f, l); put32(f, flags);
    const uint32_t fields[] = {shape.blocksize,shape.left_size,shape.right_size,shape.left_begin,
        shape.left_end,shape.right_begin,shape.right_end};
    for (unsigned i = 0; i < 7; ++i) put32(f, fields[i]);
    put64(f, (uint64_t)result.exponent); values(f, data, n); values(f, out, n);
    for (unsigned i = 0; i < 8; ++i) {
        size_t count = (size_t)32 << i;
        guarded(coefficients[i], count);
        CHECK(memcmp(coefficients[i] + 2, coefficient_copies[i], count * 8) == 0);
    }
    free(call_input); free(input_copy); free(output_copy); free(raw_in); free(raw_out);
}
int main(int argc, char **argv) {
    CHECK(argc == 2); FILE *f = fopen(argv[1], "wb"); CHECK(f);
    CHECK(fwrite("VWINDOW1", 1, 8, f) == 8); make_plans(f); put32(f, 288);
    for (unsigned small = 0; small < 8; ++small)
        for (unsigned large = small; large < 8; ++large)
            for (unsigned flags = 0; flags < 8; ++flags) run_case(f, small, large, flags);
    native_vorbis_window_shape_t shape;
    memset(&shape, 0xa5, sizeof(shape)); unsigned char saved[sizeof(shape)]; memcpy(saved, &shape, sizeof(shape));
    const uint32_t invalid[][5] = {{0,64,0,0,0},{64,63,0,0,0},{128,64,0,0,0},
        {64,8193,0,0,0},{64,64,2,0,0},{64,64,0,2,0},{64,64,0,0,2}};
    for (size_t i = 0; i < sizeof(invalid) / sizeof(*invalid); ++i) {
        const uint32_t *v = invalid[i];
        CHECK(native_vorbis_window_shape(v[0],v[1],v[2],v[3],v[4],&shape) == -1);
        CHECK(memcmp(saved, &shape, sizeof(shape)) == 0); ++refusals;
    }
    CHECK(native_vorbis_window_shape(64,64,0,0,0,NULL) == -1); ++refusals;
    for (unsigned i = 0; i < 8; ++i) { free(coefficients[i]); free(coefficient_copies[i]); }
    CHECK(fclose(f) == 0);
    printf("WINDOW_CAPTURE cases=288 refusals=%" PRIu64 " checks=%" PRIu64 "\n", refusals, checks);
    return 0;
}
