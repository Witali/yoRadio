// Preserve exact window products on demand, without an output-block allocation.
#include "native_vorbis_window_exact.h"
#include <math.h>

static bool legal_size(uint32_t value) {
    return value >= 64 && value <= 8192 && !(value & (value - 1));
}

static bool coherent_shape(const native_vorbis_window_shape_t *shape) {
    if (!legal_size(shape->blocksize) || !legal_size(shape->left_size) ||
        !legal_size(shape->right_size) || shape->left_size > shape->blocksize ||
        shape->right_size > shape->blocksize) return false;
    uint32_t left = shape->blocksize / 4 - shape->left_size / 4;
    uint32_t right = 3 * shape->blocksize / 4 - shape->right_size / 4;
    return shape->left_begin == left && shape->left_end == left + shape->left_size / 2 &&
        shape->right_begin == right && shape->right_end == right + shape->right_size / 2;
}

static bool coherent_descriptors(const native_vorbis_window_shape_t *shape,
    const native_vorbis_window_plan_t *left, const native_vorbis_window_plan_t *right,
    const native_vorbis_transform_block_t *source) {
    return shape && left && right && source && coherent_shape(shape) &&
        left->blocksize == shape->left_size && right->blocksize == shape->right_size &&
        left->rise && right->rise && source->count == shape->blocksize && source->samples;
}

native_vorbis_numeric_status_t native_vorbis_window_exact_prepare(
    const native_vorbis_window_shape_t *shape,
    const native_vorbis_window_plan_t *left,
    const native_vorbis_window_plan_t *right,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    native_vorbis_window_exact_view_t *view) {
    if (!view || !coherent_descriptors(shape, left, right, source))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (source_capacity > SIZE_MAX / sizeof(*source->samples)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (source_capacity < source->count) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    for (uint32_t i = 0; i < source->count; ++i)
        if (!isfinite(source->samples[i])) return NATIVE_VORBIS_NUMERIC_RANGE;
    for (uint32_t i = 0; i < left->blocksize / 2; ++i)
        if (!isfinite(left->rise[i]) || left->rise[i] < 0 || left->rise[i] > 1)
            return NATIVE_VORBIS_NUMERIC_RANGE;
    for (uint32_t i = 0; i < right->blocksize / 2; ++i)
        if (!isfinite(right->rise[i]) || right->rise[i] < 0 || right->rise[i] > 1)
            return NATIVE_VORBIS_NUMERIC_RANGE;
    *view = (native_vorbis_window_exact_view_t){
        .shape = *shape, .left = *left, .right = *right, .source = *source};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_window_exact_at(
    const native_vorbis_window_exact_view_t *view, uint32_t index,
    native_vorbis_window_product_t *result) {
    if (!view || !result || !coherent_descriptors(
        &view->shape, &view->left, &view->right, &view->source) || index >= view->shape.blocksize)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (index < view->shape.left_begin || index >= view->shape.right_end) {
        *result = (native_vorbis_window_product_t){0};
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    double factor = 1;
    if (index < view->shape.left_end) factor = view->left.rise[index - view->shape.left_begin];
    else if (index >= view->shape.right_begin) factor = view->right.rise[view->shape.right_end - index - 1];
    return native_vorbis_window_multiply_exact(view->source.samples[index], factor,
        view->source.exponent, result);
}
