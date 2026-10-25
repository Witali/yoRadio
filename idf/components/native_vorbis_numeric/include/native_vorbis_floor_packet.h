// Owned floor0/floor1 audio decode and integer floor1 curve, Vorbis I 6/7/9.
#pragma once
#include "native_vorbis_setup.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t floor_index, type, present, value_count, selected_book;
    native_vorbis_floor0_amplitude_t amplitude;
} native_vorbis_floor_packet_t;

// Decode one mapped channel floor through a temporary cursor. A zero amplitude/
// flag or genuine read truncation is OK with present0/value_count0; truncation
// commits sticky EOP and the last successfully read field/word position. No
// coefficient/Y bytes are published for UNUSED. Floor0 retains any amplitude
// successfully read before a later EOP; present, not amplitude alone, decides
// whether it is used. Floor1 amplitude is all zero; selected_book is UINT32_MAX
// except when a floor0 selector has been decoded successfully; it then holds
// the selected global codebook ID, not the selector within this floor.
//
// After a nonzero amplitude/flag, CAPACITY precedes further audio reads and
// preserves cursor, state and every output byte. Other INVALID/RANGE errors do
// the same. Active empty books are INVALID, without invented EOP or zero LSPs;
// zero-active setup compatibility does not promise a decodable symbol.
//
// All input views are unmodified, successfully materialized setup data owned by
// the same handle; the caller owns all lifetime/storage. Cursor, packet bytes,
// setup/storage, state and writable output arrays are disjoint. No heap/VLA.
native_vorbis_numeric_status_t native_vorbis_floor0_packet(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    native_vorbis_packet_t *packet, native_vorbis_affine_t *coefficients,
    size_t capacity, native_vorbis_floor_packet_t *state);

native_vorbis_numeric_status_t native_vorbis_floor1_packet(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    native_vorbis_packet_t *packet, uint32_t *raw_y,
    size_t capacity, native_vorbis_floor_packet_t *state);

// Full unsigned scalar values remain separate from active flags. Perform every
// original-order prediction before clamping all final Y values to [0,range),
// as suggested in section7.2.4; a later nonzero post can activate its neighbors.
// raw_count equals this floor's post_count (2..65). The arithmetic helper also
// accepts full uint32 supplied values, including endpoints, beyond values a
// real packet can encode. Signed64 products prevent narrowing/wrapping.
// Both destination arrays require capacity>=raw_count. Failure preserves both.
native_vorbis_numeric_status_t native_vorbis_floor1_reconstruct(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    const uint32_t *raw_y, size_t raw_count, uint32_t *final_y,
    uint8_t *active, size_t capacity);

// Render only inverse-dB table indexes, preserving the original segment slope
// when the write span is clipped and extending the last endpoint to bins.
// final_y/active are reconstructed present-floor data, not an unused floor.
// Index0 represents a present quiet floor, not silence. Values remain separate
// from wide-spectrum multiplication. bins1..4096; all arrays disjoint.
// Every input value/flag is checked before writes; failure preserves indices.
native_vorbis_numeric_status_t native_vorbis_floor1_curve(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    const uint32_t *final_y, const uint8_t *active, size_t count,
    uint8_t *indices, size_t bins, size_t capacity);

// Connect a decoded floor0 to the existing wide gain arithmetic at one Bark bin.
// UNUSED returns ABSENT without using coefficients or zero-domain curve fields.
// PRESENT requires positive rate/map and a valid bin. Order0 still consumes one
// codeword during packet decode, retains zero coefficients, and has exact D=1
// from the even-order empty products; positive orders use the affine-angle API.
// No early LSP rounding, linear gain, fixed spectrum or PCM conversion is added.
// State/coefficients must belong to this floor/setup; failure preserves gain.
native_vorbis_numeric_status_t native_vorbis_floor0_packet_gain(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    const native_vorbis_floor_packet_t *state,
    const native_vorbis_affine_t *coefficients, size_t count,
    uint32_t bin, native_vorbis_floor0_gain_t *gain);

#ifdef __cplusplus
}
#endif
