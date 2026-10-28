// Vorbis sin(sin^2) window and Xiph-compatible transition coordinates.
#include "native_vorbis_window.h"
#include <float.h>
#include <math.h>

_Static_assert(DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024 && FLT_RADIX == 2,
    "binary64 arithmetic required");

static int legal_size(uint32_t n) {
    return n >= 64 && n <= 8192 && !(n & (n - 1));
}

native_vorbis_numeric_status_t native_vorbis_window_prepare(
    uint32_t blocksize, double *coefficients, size_t capacity,
    native_vorbis_window_plan_t *plan) {
    if (!plan || !legal_size(blocksize)) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (capacity > SIZE_MAX / sizeof(*coefficients)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (capacity < blocksize / 2) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!coefficients) return NATIVE_VORBIS_NUMERIC_INVALID;
    const double pi = 0x1.921fb54442d18p+1;
    for (uint32_t i = 0; i < blocksize / 2; ++i) {
        double inner = sin((pi / blocksize) * (i + .5));
        coefficients[i] = sin((pi / 2) * inner * inner);
    }
    *plan = (native_vorbis_window_plan_t){.blocksize = blocksize, .rise = coefficients};
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_window_shape_t coordinates(uint32_t n, uint32_t p, uint32_t q) {
    uint32_t left = n / 4 - p / 4, right = 3 * n / 4 - q / 4;
    return (native_vorbis_window_shape_t){.blocksize = n, .left_size = p, .right_size = q,
        .left_begin = left, .left_end = left + p / 2,
        .right_begin = right, .right_end = right + q / 2};
}

native_vorbis_numeric_status_t native_vorbis_window_shape(
    uint32_t short_size, uint32_t long_size, unsigned current_long,
    unsigned previous_long, unsigned next_long,
    native_vorbis_window_shape_t *shape) {
    if (!shape || !legal_size(short_size) || !legal_size(long_size) ||
        short_size > long_size || current_long > 1 || previous_long > 1 || next_long > 1)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t n = current_long ? long_size : short_size;
    uint32_t p = current_long && previous_long ? long_size : short_size;
    uint32_t q = current_long && next_long ? long_size : short_size;
    *shape = coordinates(n, p, q);
    return NATIVE_VORBIS_NUMERIC_OK;
}

static int coherent_shape(const native_vorbis_window_shape_t *shape) {
    if (!legal_size(shape->blocksize) || !legal_size(shape->left_size) ||
        !legal_size(shape->right_size) || shape->left_size > shape->blocksize ||
        shape->right_size > shape->blocksize) return 0;
    native_vorbis_window_shape_t expected = coordinates(
        shape->blocksize, shape->left_size, shape->right_size);
    return shape->left_begin == expected.left_begin && shape->left_end == expected.left_end &&
        shape->right_begin == expected.right_begin && shape->right_end == expected.right_end;
}

native_vorbis_numeric_status_t native_vorbis_window_apply(
    const native_vorbis_window_shape_t *shape,
    const native_vorbis_window_plan_t *left,
    const native_vorbis_window_plan_t *right,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    double *output, size_t output_capacity,
    native_vorbis_transform_block_t *result) {
    if (!shape || !left || !right || !source || !result || !coherent_shape(shape) ||
        left->blocksize != shape->left_size || right->blocksize != shape->right_size ||
        !left->rise || !right->rise || source->count != shape->blocksize)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (source_capacity > SIZE_MAX / sizeof(*source->samples) ||
        output_capacity > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (source_capacity < shape->blocksize || output_capacity < shape->blocksize)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!source->samples || !output) return NATIVE_VORBIS_NUMERIC_INVALID;
    for (uint32_t i = 0; i < shape->blocksize; ++i)
        if (!isfinite(source->samples[i])) return NATIVE_VORBIS_NUMERIC_RANGE;
    uint32_t i = 0;
    for (; i < shape->left_begin; ++i) output[i] = 0.0;
    for (; i < shape->left_end; ++i)
        output[i] = source->samples[i] * left->rise[i - shape->left_begin];
    for (; i < shape->right_begin; ++i) output[i] = source->samples[i];
    for (; i < shape->right_end; ++i)
        output[i] = source->samples[i] * right->rise[shape->right_end - i - 1];
    for (; i < shape->blocksize; ++i) output[i] = 0.0;
    *result = (native_vorbis_transform_block_t){.count = shape->blocksize,
        .exponent = source->exponent, .samples = output};
    return NATIVE_VORBIS_NUMERIC_OK;
}
