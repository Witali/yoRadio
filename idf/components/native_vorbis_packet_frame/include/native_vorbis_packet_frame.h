// Exact Vorbis audio front end, through inverse coupling (Vorbis I 4.3.1-5).
#pragma once
#include "native_vorbis_floor_packet.h"
#include "native_vorbis_residue.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    native_vorbis_audio_prefix_t prefix;
    uint32_t floor_count;
    uint64_t floor0_values, floor1_values;
    native_vorbis_residue_layout_t residue_bound;
} native_vorbis_frame_requirements_t;

typedef struct {
    native_vorbis_floor_packet_t state;
    size_t value_offset;
} native_vorbis_frame_floor_t;

typedef struct {
    native_vorbis_frame_floor_t *floors;
    size_t floor_capacity;
    native_vorbis_affine_t *floor0;
    size_t floor0_capacity;
    uint32_t *floor1;
    size_t floor1_capacity;
    uint32_t *spectrum;
    size_t spectrum_capacity;
    uint8_t *classifications;
    size_t classification_capacity;
} native_vorbis_frame_workspace_t;

typedef struct {
    const native_vorbis_setup_t *setup;
    native_vorbis_audio_prefix_t prefix;
    const native_vorbis_frame_floor_t *floors;
    uint32_t floor_count;
    const native_vorbis_affine_t *floor0;
    size_t floor0_count;
    const uint32_t *floor1;
    size_t floor1_count;
    native_vorbis_residue_layout_t spectrum_layout;
    native_vorbis_residue_packet_t residue;
    const uint32_t *spectrum;
    bool implicit_zero, floor_eop;
} native_vorbis_packet_frame_t;

// Read the mode/window prefix through a temporary cursor, without consuming it.
// Return conservative configured floor pools and an all-present residue bound.
// These are upper capacities, not actual packet RAM. Decode remeasures residue
// with original floor flags and may succeed with less storage (unused floors,
// floor EOP, or a zero numeric grid). Failure preserves requirements and packet.
// Setup is a successfully materialized immutable view; its owner stays alive.
native_vorbis_numeric_status_t native_vorbis_frame_measure(
    const native_vorbis_setup_t *setup, const native_vorbis_packet_t *packet,
    native_vorbis_frame_requirements_t *requirements);

// Decode floors in original channel order, residue in submap order and inverse
// coupling in reverse pair order, with exact VQ/limb arithmetic throughout.
// Original floor presence is retained even when coupling requires its residue.
// Floor records index the compact used prefix of floor0 or floor1 by state.type.
// Floor1 values are raw Y; curve synthesis and floor multiplication are later.
// This API does not transform, window, overlap, convert PCM or allocate memory.
//
// Floor EOP is the section4.3.2 whole-frame zero case: clear all floor presence,
// counts and offsets, set floor_eop/implicit_zero, and skip residue/coupling.
// All-unused floors also need no spectrum/classification storage. Their layout
// contains only mapping/bins/channels/sample_count; remaining fields are zero.
// A present floor with an all-zero residue grid still decodes entropy words;
// implicit_zero then describes only residue, not final audio or a pole policy.
// Residue EOP keeps every earlier complete contribution and applies coupling.
//
// On failure preserve result and cursor, except prefix truncation sets sticky
// EOP without moving its position. Nominal floor/residue EOP returns OK. Workspace
// is scratch: bytes may change on failure; all previous frame borrows expire on
// every attempted reuse. Only a successful result may be consumed. Its setup
// and workspace must remain alive and immutable until consumption finishes.
// Packet bytes, setup/storage, workspace arrays/descriptor, cursor and result
// are disjoint. No forged/mutable setup, aliasing buffers or concurrent reuse.
native_vorbis_numeric_status_t native_vorbis_frame_decode(
    const native_vorbis_setup_t *setup, native_vorbis_packet_t *packet,
    const native_vorbis_frame_workspace_t *workspace,
    native_vorbis_packet_frame_t *result);

#ifdef __cplusplus
}
#endif
