// Convert lazy exact-window terms without a materialized product block.
#include "native_vorbis_pcm_exact.h"

static native_vorbis_numeric_status_t logical_sample(
    const native_vorbis_window_exact_view_t *view, int32_t begin, uint32_t index,
    native_vorbis_window_product_t *result) {
    int64_t coordinate = (int64_t)begin + index;
    if (coordinate < 0 || (uint64_t)coordinate >= view->shape.blocksize) {
        *result = (native_vorbis_window_product_t){0};
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    return native_vorbis_window_exact_at(view, (uint32_t)coordinate, result);
}

native_vorbis_numeric_status_t native_vorbis_pcm_s16_windows(
    const native_vorbis_window_exact_view_t *previous, int32_t previous_begin,
    const native_vorbis_window_exact_view_t *current, int32_t current_begin,
    uint32_t count, int16_t *output, size_t output_capacity) {
    if (!previous || !current) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (output_capacity > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (output_capacity < count) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (count && !output) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_window_product_t a = {0}, b = {0};
    // Validate both view descriptors even for an entirely out-of-block slice.
    native_vorbis_numeric_status_t status = native_vorbis_window_exact_at(previous, 0, &a);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = native_vorbis_window_exact_at(current, 0, &b);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    for (uint32_t i = 0; i < count; ++i) {
        status = logical_sample(previous, previous_begin, i, &a);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        status = logical_sample(current, current_begin, i, &b);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    }
    // With successful immutable views every repeated read yields the same
    // canonical product, so this publication pass has no fallible decisions.
    for (uint32_t i = 0; i < count; ++i) {
        (void)logical_sample(previous, previous_begin, i, &a);
        (void)logical_sample(current, current_begin, i, &b);
        (void)native_vorbis_pcm_s16_product_pair(&a, &b, output + i);
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}
