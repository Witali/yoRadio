// Directed enclosure at one exact supplied Bark index; Vorbis I 6.2.3.
#pragma once
#include "native_vorbis_floor0.h"
#include "native_vorbis_interval.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NATIVE_VORBIS_GAIN_FINITE = 0,
    NATIVE_VORBIS_GAIN_ABSENT = 1,
    NATIVE_VORBIS_GAIN_UNITY = 2,
    NATIVE_VORBIS_GAIN_POLE = 3,
    NATIVE_VORBIS_GAIN_INDETERMINATE = 4,
    NATIVE_VORBIS_GAIN_NEEDS_PRECISION = 5,
    NATIVE_VORBIS_GAIN_UNDEFINED_MAPPING = 6
} native_vorbis_gain_kind_t;

typedef struct {
    native_vorbis_floor0_amplitude_t amplitude;
    const native_vorbis_affine_t *angles;
    size_t order;
    uint32_t bark_index, bark_map_size;
} native_vorbis_gain_input_t;

typedef struct {
    // Private ownership fields; do not copy a live workspace.
    native_vorbis_bigfloat_context_t arithmetic;
    native_vorbis_interval_t pi, ln2;
    uint32_t cached_precision;
    size_t result_owners;
    uint64_t cookie;
} native_vorbis_gain_workspace_t;

typedef struct {
    // Owned endpoints belong to the workspace until result_clear.
    native_vorbis_interval_t denominator, log2_gain;
    native_vorbis_gain_kind_t kind;
    bool has_denominator, has_log;
    uint32_t precision;
    native_vorbis_gain_workspace_t *owner;
    uint64_t cookie;
} native_vorbis_gain_result_t;

typedef struct { size_t lower_words, upper_words; } native_vorbis_gain_floor_requirements_t;
typedef struct {
    size_t lower_words, upper_words;
    bool lower_negative, upper_negative, equal;
} native_vorbis_gain_floor_result_t;

// Fresh workspace/result storage and valid malloc-like aligned callbacks are
// preconditions. The allocator descriptor is copied. Serialize each workspace;
// no global state, task or production decoder selection is changed.
native_vorbis_bigfloat_status_t native_vorbis_gain_workspace_init(
    native_vorbis_gain_workspace_t *workspace,
    const native_vorbis_bigfloat_allocator_t *allocator);
native_vorbis_bigfloat_status_t native_vorbis_gain_clear_failure(
    native_vorbis_gain_workspace_t *workspace);
// Refuse before cleanup while a result is live. No allocation during cleanup.
native_vorbis_bigfloat_status_t native_vorbis_gain_workspace_end(
    native_vorbis_gain_workspace_t *workspace);
native_vorbis_bigfloat_status_t native_vorbis_gain_result_init(
    native_vorbis_gain_workspace_t *workspace, native_vorbis_gain_result_t *result);
// Releases this result's ownership; call result_init before using it again.
native_vorbis_bigfloat_status_t native_vorbis_gain_result_clear(
    native_vorbis_gain_workspace_t *workspace, native_vorbis_gain_result_t *result);

// Order is always validated as an eight-bit encoded field (0..255). All
// encoded affine words/multipliers are accepted exactly. Active order0 has
// D=1. Zero raw amplitude is absent and does not read LSPs or mapping metadata.
// Active map0 is an undefined mapping outcome, not an invented format error;
// it does not read LSP entries or require a nonnull angle pointer.
// For an active positive map, supplied index<size and immutable order<=255
// affine entries are caller obligations. This API does not calculate Bark maps.
//
// Successful finite results enclose mathematical log2 gain using the exact
// specification decimal 11512925/100000000. No standalone enormous exp2(gain)
// is constructed. Both endpoint floors may differ; callers must refine or keep
// their uncertainty. A finite enclosure is not a universal PCM error claim.
//
// Precision is a requested working resource, not a guarantee of retained gain
// fraction bits. NEEDS_PRECISION preserves uncertainty. Negative resource/API
// statuses preserve every old result field and endpoint allocation byte. The
// workspace's private constant caches/scratch may change. OOM stays latched;
// clear_failure explicitly before retrying from original exact input. No input
// borrow is retained after return. Result, input and workspace storage must be
// disjoint; caller-owned inputs stay immutable throughout each call.
native_vorbis_bigfloat_status_t native_vorbis_gain_enclose(
    native_vorbis_gain_workspace_t *workspace, const native_vorbis_gain_input_t *input,
    uint32_t precision, native_vorbis_gain_result_t *result);

// Allocation-free integer floor exports, never narrowed to int64. Preflight
// both capacities before writing either buffer/metadata. All caller output
// storage is disjoint from the result/workspace and from each other. Unused
// capacity is not written. Successful zero integers have count0/negativefalse.
native_vorbis_bigfloat_status_t native_vorbis_gain_floor_measure(
    const native_vorbis_gain_workspace_t *workspace, const native_vorbis_gain_result_t *result,
    native_vorbis_gain_floor_requirements_t *requirements);
native_vorbis_bigfloat_status_t native_vorbis_gain_floor_export(
    const native_vorbis_gain_workspace_t *workspace, const native_vorbis_gain_result_t *result,
    uint32_t *lower, size_t lower_capacity, uint32_t *upper, size_t upper_capacity,
    native_vorbis_gain_floor_result_t *output);

#ifdef __cplusplus
}
#endif
