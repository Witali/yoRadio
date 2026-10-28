// Persistent public raw-packet decoding above the owned Vorbis components.
#pragma once
#include "native_vorbis_setup_owner.h"
#include "native_vorbis_synthesis.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct native_vorbis_decoder native_vorbis_decoder_t;

typedef enum {
    NATIVE_VORBIS_DECODER_OK = 0,
    NATIVE_VORBIS_DECODER_INVALID = -1,
    NATIVE_VORBIS_DECODER_RANGE = -2,
    NATIVE_VORBIS_DECODER_TRUNCATED = -3,
    NATIVE_VORBIS_DECODER_NO_MEMORY = -4,
    NATIVE_VORBIS_DECODER_OUTPUT_CAPACITY = -5,
    NATIVE_VORBIS_DECODER_NEEDS_WIDER = -6,
    NATIVE_VORBIS_DECODER_NEEDS_PRECISION = -7,
    NATIVE_VORBIS_DECODER_UNDEFINED_MAPPING = -8,
    NATIVE_VORBIS_DECODER_UNDEFINED_POLE = -9,
    NATIVE_VORBIS_DECODER_UNDEFINED_INDETERMINATE = -10,
    NATIVE_VORBIS_DECODER_END_OF_STREAM = -11,
    NATIVE_VORBIS_DECODER_NUMERIC_FAILURE = -12
} native_vorbis_decoder_status_t;

typedef struct {
    const uint8_t *data;
    size_t bytes;
    uint64_t bits;
    int64_t granule_position; // -1 means unknown; a transport-provided position.
    bool end_of_stream, discontinuity;
} native_vorbis_decoder_packet_t;

typedef struct {
    uint32_t blocksize, channels;
    uint64_t pcm_samples; // Interleaved S16 elements, not bytes or frames.
    native_vorbis_timing_result_t timing;
} native_vorbis_decoder_requirements_t;

typedef struct {
    uint32_t blocksize, channels, floor0_channels, floor1_channels;
    uint64_t consumed_bits;
    bool end_of_packet;
    native_vorbis_synthesis_result_t synthesis;
} native_vorbis_decoder_result_t;

typedef struct {
    native_vorbis_identification_t identification;
    native_vorbis_timing_t timing;
    bool end_of_stream;
} native_vorbis_decoder_info_t;

// *decoder starts NULL or is an exclusively owned live handle from this API.
// Read complete type1/type5 packets through the existing exact setup owner.
// Header ordering, comment header, BOS and container validation belong to the
// transport; the public raw SDK likewise configures Vorbis with these two
// headers. No incoming header or allocator descriptor is retained by reference.
//
// Copy allocator callbacks/context and construct a separate candidate. On any
// failure preserve the old handle, setup, state and all its borrows; on success
// publish the new handle, then release the old one via its saved allocator.
// The context must outlive all its handles. Only positive-size allocation and
// non-NULL release calls are made. All returned storage is fresh, aligned and
// disjoint, as malloc promises. Callbacks cannot reenter this handle's API.
// Replacement temporarily needs both handles' storage. No format cap is added
// when a resource request cannot be satisfied; report NO_MEMORY or byte RANGE.
// Writable handle storage, input packets and allocator descriptor are disjoint
// from each other and candidate/old allocations. Callbacks cannot modify the
// caller's handle directly. The same disjointness applies to snapshot outputs.
native_vorbis_decoder_status_t native_vorbis_decoder_replace(
    native_vorbis_decoder_t **decoder,
    const uint8_t *identification, size_t identification_bytes, uint64_t identification_bits,
    const uint8_t *setup, size_t setup_bytes, uint64_t setup_bits,
    const native_vorbis_setup_allocator_t *allocator);

// Read-only prefix/timing preflight. Derive blocksize from the actual packet;
// compute exact output trimming on a timing copy without allocation or state
// advancement. Success does not validate the later floor/residue/numeric data.
// Failure preserves requirements. The first priming packet needs zero output.
native_vorbis_decoder_status_t native_vorbis_decoder_measure(
    const native_vorbis_decoder_t *decoder,
    const native_vorbis_decoder_packet_t *packet,
    native_vorbis_decoder_requirements_t *requirements);

// Decode one complete raw packet through the proven frame/floor/IMDCT/synthesis
// path. Packet and output storage, descriptors, result and every owner allocation
// are disjoint and stay alive/immutable where borrowed. Packet bytes are not
// retained after return. Use ordinary nearest floating rounding, as IMDCT does.
// Output capacity counts interleaved S16 elements; a zero span permits NULL.
//
// Exact PCM capacity is checked BEFORE scratch growth or numerical work. Every
// failure preserves setup, committed history/timing/EOS, output and result.
// Internal scratch/capacities may change; no scratch/frame borrow escapes. The
// caller may retry unchanged packet/metadata after providing memory/capacity.
// All channels complete numerical preparation before synthesis commits anything.
// Successful result is published after that infallible final publication; no
// post-commit callbacks can turn success into a retryable failure.
//
// The supplied granule/EOS/gap metadata is passed unchanged to timing. No
// synthetic final packet or zero-input flush is invented. After a successful
// EOS packet, measure/process return END_OF_STREAM until reset or replacement.
// HTTP EOF is not packet EOS. Reset is distinct from discontinuity, which keeps
// overlap while reanchoring timing according to the existing public policy.
//
// Noncandidate floor0 routes remain typed incomplete mathematical domains,
// not a claim that a valid stream may be rejected. This candidate is unselected
// by production until those routes and container/audio-task gates are complete.
// No packet-local switch to another decoder with incompatible history.
native_vorbis_decoder_status_t native_vorbis_decoder_process(
    native_vorbis_decoder_t *decoder,
    const native_vorbis_decoder_packet_t *packet,
    int16_t *output, size_t output_capacity,
    native_vorbis_decoder_result_t *result);

// Snapshot only committed metadata. No allocation; failure preserves info.
native_vorbis_decoder_status_t native_vorbis_decoder_info(
    const native_vorbis_decoder_t *decoder, native_vorbis_decoder_info_t *info);

// Hard restart the same setup without allocation. Clear terminal EOS and prime
// again; history bytes remain unread until replaced by the next priming block.
// Failure preserves committed state. Retained scratch/lookups can be reused.
native_vorbis_decoder_status_t native_vorbis_decoder_reset(native_vorbis_decoder_t *decoder);

// Clear the caller's handle before callbacks, then release every allocation
// through the original allocator. NULL arguments are no-ops. Callers serialize
// all use against replace/reset/clear; the owner adds no lock or task.
void native_vorbis_decoder_clear(native_vorbis_decoder_t **decoder);

#ifdef __cplusplus
}
#endif
