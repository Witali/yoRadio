// Internal selected LibBF foundation; this does not certify transcendental gain.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "libbf.h"

#ifdef __cplusplus
extern "C" {
#endif

// Conservative, analytically checked ENGINE resources, never a Vorbis format cap.
#define NATIVE_VORBIS_BIGFLOAT_MAX_BITS UINT32_C(1048576)
#define NATIVE_VORBIS_BIGFLOAT_MAX_TOP INT32_C(1048576)
#define NATIVE_VORBIS_BIGFLOAT_MAX_WORDS UINT32_C(32768)

typedef enum {
    NATIVE_VORBIS_BIGFLOAT_OK = 0,
    NATIVE_VORBIS_BIGFLOAT_INVALID = -1,
    NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT = -2,
    NATIVE_VORBIS_BIGFLOAT_NO_MEMORY = -3,
    NATIVE_VORBIS_BIGFLOAT_ARITHMETIC = -4,
    NATIVE_VORBIS_BIGFLOAT_CAPACITY = -5
} native_vorbis_bigfloat_status_t;

typedef enum {
    NATIVE_VORBIS_BIGFLOAT_DOWN = 0,
    NATIVE_VORBIS_BIGFLOAT_UP = 1
} native_vorbis_bigfloat_round_t;

typedef struct {
    void *opaque;
    void *(*allocate)(void *opaque, size_t bytes);
    void (*release)(void *opaque, void *allocation);
} native_vorbis_bigfloat_allocator_t;

typedef struct {
    uint64_t attempts, failures;
    size_t live_allocations, live_bytes, peak_allocations, peak_bytes;
    bool allocation_failed, ntt_initialized;
} native_vorbis_bigfloat_stats_t;

typedef struct {
    // Internal fields: callers must not modify or shallow-copy a live context.
    bf_context_t engine;
    native_vorbis_bigfloat_allocator_t allocator;
    native_vorbis_bigfloat_stats_t accounting;
    uint64_t cookie;
} native_vorbis_bigfloat_context_t;

// Context/callback storage outlives all initialized numbers and cache storage.
// Operations on a context are serialized. Copies of the allocator descriptor
// are retained; allocations must be fresh, aligned and disjoint as malloc.
// Allocation failure is sticky until clear_failure; cleanup never allocates.
// Stats and allocation-free exports remain available while failure is latched.
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_context_init(
    native_vorbis_bigfloat_context_t *context,
    const native_vorbis_bigfloat_allocator_t *allocator);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_clear_failure(
    native_vorbis_bigfloat_context_t *context);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_stats(
    const native_vorbis_bigfloat_context_t *context,
    native_vorbis_bigfloat_stats_t *result);
// Clear every number first. End clears engine caches; a remaining live number
// returns INVALID. The context becomes inactive only on successful end.
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_context_end(
    native_vorbis_bigfloat_context_t *context);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_init(
    native_vorbis_bigfloat_context_t *context, bf_t *number);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_clear(
    native_vorbis_bigfloat_context_t *context, bf_t *number);

// All numbers are initialized by this API in this context. Inputs stay immutable.
// Destinations may alias an operand. Failure preserves the destination's actual
// fields/storage. Disjoint output descriptors/buffers stay immutable when borrowed.
// Exact dyadic input is signed M*2^exponent, LE32 magnitude with nonzero top word;
// low even words are accepted. Zero is count0/exponent0/negativefalse. Exponents
// outside the checked engine envelope return retryable ENGINE_LIMIT.
// Arithmetic/round precision is2..MAX_BITS;0/1 and unknown rounding modes are
// INVALID. No upstream transcendental, constant, signed-si or float64 exporter
// is part of this selected API. Well-formed objects and ordinary C bool objects
// are preconditions; caller descriptors/buffers and live context storage are
// disjoint unless destination/operand aliasing is explicitly allowed above.
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_set_u64(
    native_vorbis_bigfloat_context_t *context, bf_t *destination, uint64_t value);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_import(
    native_vorbis_bigfloat_context_t *context, bf_t *destination,
    const uint32_t *words, size_t count, int64_t exponent, bool negative);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_copy(
    native_vorbis_bigfloat_context_t *context, bf_t *destination, const bf_t *source);

#define NATIVE_VORBIS_BIGFLOAT_BINARY_DECL(name) \
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_##name( \
    native_vorbis_bigfloat_context_t *context, bf_t *destination, \
    const bf_t *left, const bf_t *right, uint32_t precision, \
    native_vorbis_bigfloat_round_t rounding)
NATIVE_VORBIS_BIGFLOAT_BINARY_DECL(add);
NATIVE_VORBIS_BIGFLOAT_BINARY_DECL(sub);
NATIVE_VORBIS_BIGFLOAT_BINARY_DECL(mul);
NATIVE_VORBIS_BIGFLOAT_BINARY_DECL(div);
#undef NATIVE_VORBIS_BIGFLOAT_BINARY_DECL
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_sqrt(
    native_vorbis_bigfloat_context_t *context, bf_t *destination,
    const bf_t *source, uint32_t precision, native_vorbis_bigfloat_round_t rounding);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_round(
    native_vorbis_bigfloat_context_t *context, bf_t *destination,
    const bf_t *source, uint32_t precision, native_vorbis_bigfloat_round_t rounding);

// Allocation-free measures/exports. Canonical dyadic output has odd nonzero M,
// little-endian uint32 words and signed binary exponent. Canonical zero has all
// output fields zero. Floor output is signed arbitrary-limb INTEGER magnitude;
// it never narrows the integer part into bf_t.expn or int64. An input with tiny
// negative value therefore exports integer -1. All output bytes/metadata remain
// unchanged on every failure, including CAPACITY. Successful exports initialize
// exactly count words; unused caller capacity is not written.
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_measure_dyadic(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source, size_t *count);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_export_dyadic(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source,
    uint32_t *words, size_t capacity, size_t *count, int64_t *exponent, bool *negative);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_measure_floor(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source, size_t *count);
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_export_floor(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source,
    uint32_t *words, size_t capacity, size_t *count, bool *negative);

#ifdef __cplusplus
}
#endif
