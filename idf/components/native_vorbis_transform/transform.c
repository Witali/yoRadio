// Reuse the Xiph inverse-transform arithmetic with caller-owned binary64 data.
#include "native_vorbis_transform.h"
#include <float.h>
#include <math.h>
#include <string.h>

_Static_assert(sizeof(double) == sizeof(uint64_t) && DBL_MANT_DIG == 53 &&
    DBL_MAX_EXP == 1024 && FLT_RADIX == 2, "binary64 storage required");
_Static_assert(sizeof(int) == sizeof(int32_t), "32-bit Xiph bitreverse entries required");

typedef struct {
    int n, log2n;
    double *trig;
    int *bitrev;
} native_vorbis_xiph_mdct_lookup_t;

// Specialize types/constants; the included function bodies stay unchanged.
#define mdct_lookup native_vorbis_xiph_mdct_lookup_t
#define mdct_backward native_vorbis_xiph_mdct_backward
#define DATA_TYPE double
#define REG_TYPE double
#define STIN static inline
#define cPI3_8 .38268343236508977175
#define cPI2_8 .70710678118654752441
#define cPI1_8 .92387953251128675613
#define MULT_NORM(x) (x)
#define HALVE(x) ((x)*.5)
#include "xiph_backward.inc"
#undef HALVE
#undef MULT_NORM
#undef cPI1_8
#undef cPI2_8
#undef cPI3_8
#undef STIN
#undef REG_TYPE
#undef DATA_TYPE
#undef mdct_backward
#undef mdct_lookup

native_vorbis_numeric_status_t native_vorbis_imdct_measure(
    uint32_t blocksize, native_vorbis_imdct_requirements_t *requirements) {
    if (!requirements || blocksize < 64 || blocksize > 8192 || (blocksize & (blocksize - 1)))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t log2n = 0;
    for (uint32_t value = blocksize; value > 1; value >>= 1) ++log2n;
    *requirements = (native_vorbis_imdct_requirements_t){.blocksize = blocksize, .log2n = log2n,
        .trig_count = blocksize + blocksize / 4, .bitrev_count = blocksize / 4,
        .workspace_count = blocksize + 8};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_imdct_prepare(
    uint32_t blocksize, double *trig, size_t trig_capacity,
    int *bitrev, size_t bitrev_capacity, native_vorbis_imdct_plan_t *plan) {
    if (!plan) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_imdct_requirements_t needed;
    native_vorbis_numeric_status_t status = native_vorbis_imdct_measure(blocksize, &needed);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (trig_capacity > SIZE_MAX / sizeof(*trig) || bitrev_capacity > SIZE_MAX / sizeof(*bitrev))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    if (trig_capacity < needed.trig_count || bitrev_capacity < needed.bitrev_count)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!trig || !bitrev) return NATIVE_VORBIS_NUMERIC_INVALID;
    // Same expressions as Xiph mdct_init; pi is the nearest binary64 M_PI.
    const double pi = 0x1.921fb54442d18p+1;
    uint32_t n = blocksize, n2 = n / 2;
    for (uint32_t i = 0; i < n / 4; ++i) {
        trig[i * 2] = cos((pi / n) * (4 * i));
        trig[i * 2 + 1] = -sin((pi / n) * (4 * i));
        trig[n2 + i * 2] = cos((pi / (2 * n)) * (2 * i + 1));
        trig[n2 + i * 2 + 1] = sin((pi / (2 * n)) * (2 * i + 1));
    }
    for (uint32_t i = 0; i < n / 8; ++i) {
        trig[n + i * 2] = cos((pi / n) * (4 * i + 2)) * .5;
        trig[n + i * 2 + 1] = -sin((pi / n) * (4 * i + 2)) * .5;
    }
    uint32_t mask = n / 2 - 1;
    uint32_t msb = n / 4;
    for (uint32_t i = 0; i < n / 8; ++i) {
        uint32_t acc = 0;
        for (uint32_t j = 0; (msb >> j) != 0; ++j)
            if ((msb >> j) & i) acc |= 1U << j;
        bitrev[i * 2] = (int)((~acc & mask) - 1);
        bitrev[i * 2 + 1] = (int)acc;
    }
    for (size_t i = 0; i < needed.trig_count; ++i)
        if (!isfinite(trig[i])) return NATIVE_VORBIS_NUMERIC_RANGE;
    *plan = (native_vorbis_imdct_plan_t){.blocksize = n, .log2n = needed.log2n,
        .trig = trig, .bitrev = bitrev};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_imdct_transform(
    const native_vorbis_imdct_plan_t *plan,
    const native_vorbis_floor1_product_t *source, size_t limb_capacity,
    double *workspace, size_t workspace_capacity,
    native_vorbis_transform_block_t *result) {
    if (!plan || !source || !result) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_imdct_requirements_t needed;
    native_vorbis_numeric_status_t status = native_vorbis_imdct_measure(plan->blocksize, &needed);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (plan->log2n != needed.log2n || !plan->trig || !plan->bitrev ||
        source->layout.bins != plan->blocksize / 2) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (workspace_capacity > SIZE_MAX / sizeof(*workspace)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (workspace_capacity < needed.workspace_count) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!workspace) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_transform_block_t converted;
    status = native_vorbis_spectrum_to_binary64(source, limb_capacity, workspace + 8,
        workspace_capacity - 8, &converted);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    for (size_t i = 0; i < 8; ++i) workspace[i] = 0.0;
    double *data = workspace + 8;
    if (!source->layout.limbs) {
        for (size_t i = 0; i < plan->blocksize; ++i) data[i] = 0.0;
    } else {
        native_vorbis_xiph_mdct_lookup_t lookup = {.n = (int)plan->blocksize,
            .log2n = (int)plan->log2n, .trig = plan->trig, .bitrev = plan->bitrev};
        native_vorbis_xiph_mdct_backward(&lookup, data, data);
    }
    *result = (native_vorbis_transform_block_t){.count = plan->blocksize,
        .exponent = converted.exponent, .samples = data};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_imdct_transform_binary64(
    const native_vorbis_imdct_plan_t *plan,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    double *workspace, size_t workspace_capacity,
    native_vorbis_transform_block_t *result) {
    if (!plan || !source || !result) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_imdct_requirements_t needed;
    native_vorbis_numeric_status_t status = native_vorbis_imdct_measure(plan->blocksize, &needed);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (plan->log2n != needed.log2n || !plan->trig || !plan->bitrev ||
        source->count != plan->blocksize / 2) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (source_capacity > SIZE_MAX / sizeof(*source->samples) ||
        workspace_capacity > SIZE_MAX / sizeof(*workspace)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (source_capacity < source->count || workspace_capacity < needed.workspace_count)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!source->samples || !workspace) return NATIVE_VORBIS_NUMERIC_INVALID;
    int nonzero = 0;
    for (uint32_t i = 0; i < source->count; ++i) {
        double value = source->samples[i];
        if (!isfinite(value) || fabs(value) > 0x1p639) return NATIVE_VORBIS_NUMERIC_RANGE;
        nonzero |= value != 0.0;
    }
    for (size_t i = 0; i < 8; ++i) workspace[i] = 0.0;
    double *data = workspace + 8;
    if (!nonzero) {
        for (uint32_t i = 0; i < plan->blocksize; ++i) data[i] = 0.0;
    } else {
        memcpy(data, source->samples, source->count * sizeof(*data));
        native_vorbis_xiph_mdct_lookup_t lookup = {.n = (int)plan->blocksize,
            .log2n = (int)plan->log2n, .trig = plan->trig, .bitrev = plan->bitrev};
        native_vorbis_xiph_mdct_backward(&lookup, data, data);
    }
    *result = (native_vorbis_transform_block_t){.count = plan->blocksize,
        .exponent = source->exponent, .samples = data};
    return NATIVE_VORBIS_NUMERIC_OK;
}
