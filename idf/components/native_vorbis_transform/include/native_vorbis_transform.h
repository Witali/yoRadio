// Wide floor1 spectrum boundary and reused Xiph inverse MDCT, Vorbis I 4.3.7.
#pragma once
#include "native_vorbis_floor1_product.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t blocksize, log2n;
    uint64_t trig_count, bitrev_count, workspace_count;
} native_vorbis_imdct_requirements_t;

typedef struct {
    uint32_t blocksize, log2n;
    double *trig;
    int *bitrev;
} native_vorbis_imdct_plan_t;

// Each sample represents samples[i]*2^exponent. The scale stays separate;
// neither this representation nor IMDCT clips/converts to PCM. Count is bins
// for conversion and full blocksize for inverse MDCT. Borrowed caller storage.
typedef struct {
    uint32_t count;
    int64_t exponent;
    const double *samples;
} native_vorbis_transform_block_t;

// Legal Vorbis block sizes: powers of two from64 through8192. Lookup storage is
// n+n/4 doubles and n/4 ints. One in-place transform workspace needs n+8 doubles;
// its first8 elements keep upstream rotation-loop pointers inside ONE allocated
// array. They are not a separate prefix object. Failure preserves requirements.
native_vorbis_numeric_status_t native_vorbis_imdct_measure(
    uint32_t blocksize, native_vorbis_imdct_requirements_t *requirements);

// Capacity, pointer and object-byte checks precede writes. After success the
// plan and lookup arrays stay alive/immutable until every use ends. No heap or
// VLA. Lookup arithmetic follows Xiph initialization with integer log2n, binary64
// coefficients and caller storage. Failure preserves plan; provisioned arrays
// are scratch during construction and may change on a later arithmetic error.
// Plan, trig and bitrev are disjoint. New construction storage must also be
// disjoint from arrays still borrowed by any live plan; this is not an atomic
// in-place replacement of an old lookup's storage.
native_vorbis_numeric_status_t native_vorbis_imdct_prepare(
    uint32_t blocksize, double *trig, size_t trig_capacity,
    int *bitrev, size_t bitrev_capacity, native_vorbis_imdct_plan_t *plan);

// Round each signed exact integer S ONCE to binary64(S*2^-512), ties to even,
// retaining source.exponent+512 in int64. This working grid covers all36-limb
// source shapes (magnitude_bits<=1151) without input overflow or underflow.
// No float32 step or early spectral clipping. Zero grids publish exponent0 and
// write count positive zeros. Numeric shape and all signed sample domains are
// validated before output writes; failures preserve output/result. Capacities
// count array elements, not bytes. No forged aliased descriptors/storage.
native_vorbis_numeric_status_t native_vorbis_spectrum_to_binary64(
    const native_vorbis_floor1_product_t *source, size_t limb_capacity,
    double *output, size_t output_capacity,
    native_vorbis_transform_block_t *result);

// Use a successful immutable plan and coherent floor1 product with bins==n/2.
// The unchanged Xiph backward/butterfly/bitreverse bodies run with binary64
// storage/constants. Their normalization is sum(X[k]*cos((2*pi/n)*
// (j+.5+n/4)*(k+.5))), with no extra2/n or4/n factor. Input conversion and all
// resource/domain checks finish before transform writes. Workspace/result are
// preserved on failure; on success result.samples==workspace+8, count==n.
//
// Source, plan/lookup arrays, workspace, descriptors and result are disjoint.
// Keep all borrows alive and immutable while used; serialize workspace reuse.
// Floating arithmetic assumes the normal nearest rounding environment. The
// transform is approximate binary64 arithmetic: cancellation has no universal
// relative or final PCM error guarantee. Floor0 arbitrary gain ranges, window,
// overlap, PCM, SDK/resource and complete decoder gates remain separate.
native_vorbis_numeric_status_t native_vorbis_imdct_transform(
    const native_vorbis_imdct_plan_t *plan,
    const native_vorbis_floor1_product_t *source, size_t limb_capacity,
    double *workspace, size_t workspace_capacity,
    native_vorbis_transform_block_t *result);

// Reuse the same kernel for a caller-normalized binary64 spectrum. Count must
// be n/2 and every sample finite with absolute value <=2^639, the proven input
// bound of the limb conversion route. This is an internal representation
// contract, not a restriction on a codec's accepted values: a caller with a
// wider spectrum needs another representation/normalization route. No scaling,
// clipping or float32 conversion occurs here; exponent is retained unchanged,
// including INT64_MIN/MAX. A wholly zero spectrum (either zero sign) produces
// canonical +0 samples, with that same exponent. Other spectra follow ordinary
// Xiph arithmetic, which may produce signed zeros/subnormals after cancellation.
//
// All input samples, shapes and capacities are checked before any write.
// Failure preserves workspace/result. Source capacity counts doubles and must
// cover count. Workspace has the same n+8 single-array contract as above.
// Source/plan/lookup/workspace/descriptors/result are disjoint and immutable
// borrows remain alive. Normal nearest rounding and the approximate transform
// limitations above apply; this entry does not implement floor0 gain policy.
native_vorbis_numeric_status_t native_vorbis_imdct_transform_binary64(
    const native_vorbis_imdct_plan_t *plan,
    const native_vorbis_transform_block_t *source, size_t source_capacity,
    double *workspace, size_t workspace_capacity,
    native_vorbis_transform_block_t *result);

#ifdef __cplusplus
}
#endif
