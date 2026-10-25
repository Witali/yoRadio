// Owned exact residue0/1/2 and inverse coupling, Vorbis I sections4.3/8.
#pragma once
#include "native_vorbis_setup.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t mapping, bins, channels, limbs, magnitude_bits;
    int32_t exponent;
    uint64_t sample_count, limb_count, classification_count;
} native_vorbis_residue_layout_t;

typedef struct {
    uint64_t classwords, vectors, values;
    uint32_t stopped_on_eop;
} native_vorbis_residue_packet_t;

// Measure one complete mapping's planar spectrum and reusable classification
// scratch. floor_present has exactly setup.channels boolean bytes, before the
// single forward-order coupling propagation; inputs remain unchanged. bins is
// 1..4096. All mapped submaps are decoded in their original order, and bundle
// channels retain ascending original channel indexes.
//
// Each sample is a little-significance-first two's-complement integer occupying
// limbs uint32 elements, multiplied by 2^exponent. Its absolute integer value is
// strictly below 2^magnitude_bits. The common binary point covers every potential
// stagebook in every nonempty mapped bundle, permitting exact inverse coupling
// across submaps. No floating rounding or int32 clipping occurs. Width depends
// on encoded books, not a new format cap: the universal bound is34 limbs.
//
// Planar offset=((channel*bins)+bin)*limbs. Counts use uint64; caller capacity
// and object-byte addressability are separate resource checks. When all mapped
// stagebook minimum/delta mantissas are zero, the planner recognizes an exact
// zero domain: limbs/magnitude_bits/exponent/limb_count are0. The encoded
// value_bits bound is conservative; it does not scan q storage to find further
// zero-valued books. In the recognized zero domain,
// every logical sample is implicitly zero and output=NULL/capacity0 is valid.
// Entropy reads and classification scratch may still be required in that case.
// Classification bytes hold only actual partitions and are reused per submap;
// classifications1 needs none, even when its phrase dimension is65535.
// Failure preserves layout. Setup must be a successfully materialized immutable
// view; all borrowed storage has the same owner and remains alive.
native_vorbis_numeric_status_t native_vorbis_residue_measure(
    const native_vorbis_setup_t *setup, uint32_t mapping, size_t bins,
    const uint8_t *floor_present, size_t flag_count,
    native_vorbis_residue_layout_t *layout);

// Decode the residue portion of a packet after its floor portion. layout must
// match a fresh measure with these exact inputs. Capacity/RANGE refusal precedes
// scratch/output writes and audio reads. A dry run validates the selected entropy
// words before zeroing/replaying output; INVALID preserves cursor/output/state.
// Scratch contents may change after an adequately provisioned decode starts.
// All input storage, cursor, layout, scratch, output and state are disjoint.
//
// Genuine EOP returns OK plus stopped_on_eop1 and publishes every earlier full
// VQ word, including earlier words in the same residue0 partition. The cursor
// commits its last full codeword position and sticky EOP. A pre-existing sticky
// EOP stops any attempted entropy read before book consumption; no-read calls
// preserve it with stopped_on_eop0. Active empty books are INVALID when reached
// before EOP. Uncoded/skipped/tail samples are zeroed, never left stale.
//
// Follow normative base-digit reduction for declared classword entries, including
// entries >= classifications^dimension; ignore the leftover high quotient. Pass0
// still consumes classwords with all-zero cascades. Type2 scatters each absolute
// flat index by %bundle_channels and /bundle_channels without alignment limits.
// No heap, VLA, full VQ row, expanded classification map or floating arithmetic.
native_vorbis_numeric_status_t native_vorbis_residue_packet(
    const native_vorbis_setup_t *setup,
    const native_vorbis_residue_layout_t *layout,
    const uint8_t *floor_present, size_t flag_count,
    native_vorbis_packet_t *packet,
    uint8_t *classifications, size_t classification_capacity,
    uint32_t *output, size_t limb_capacity,
    native_vorbis_residue_packet_t *state);

// Apply all mapping coupling pairs in reverse order in place, on the common
// exact grid. Every sign branch is exact, including tiny nonzero differences
// left after cancellation. Inverse coupling does not increase the global maximum
// absolute sample, so no per-step growth factor or saturation is needed.
// Validate complete shape/capacity and the measured signed sample domain before
// writes. Failure preserves the entire output. The source must be decoded using
// this same setup/layout; all inputs remain immutable during the call.
native_vorbis_numeric_status_t native_vorbis_residue_inverse_coupling(
    const native_vorbis_setup_t *setup,
    const native_vorbis_residue_layout_t *layout,
    uint32_t *output, size_t limb_capacity);

#ifdef __cplusplus
}
#endif
