// Owned Vorbis I identification/setup and audio packet prefix, sections4/6/7/8.
#pragma once
#include "native_vorbis_codebook.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t channels, sample_rate;
    uint32_t bitrate_maximum_bits, bitrate_nominal_bits, bitrate_minimum_bits;
    uint32_t blocksize_0, blocksize_1;
} native_vorbis_identification_t;

// Parse the complete type1 header (version0). Positive full uint32 rate and
// channels1..255; block sizes64..8192 in ascending order. Bitrate hints retain
// their signed32 bit patterns, including unspecified/nonpositive values.
// Explicit bit extents follow the packet cursor contract. Failure preserves id.
native_vorbis_numeric_status_t native_vorbis_identification_parse(
    const uint8_t *data, size_t bytes, uint64_t bits,
    native_vorbis_identification_t *id);

typedef struct {
    native_vorbis_identification_t identification;
    uint64_t end_bit, codeword_count, multiplicand_count;
    uint32_t book_count, time_count, floor_count, residue_count, mapping_count, mode_count;
    uint32_t configuration_count, floor_table, residue_table, mapping_table, mode_table;
} native_vorbis_setup_layout_t;

typedef struct {
    native_vorbis_codebook_t *books;
    size_t book_capacity;
    native_vorbis_codeword_t *words;
    size_t word_capacity;
    uint16_t *multiplicands;
    size_t multiplicand_capacity;
    uint32_t *configuration;
    size_t configuration_capacity;
} native_vorbis_setup_storage_t;

// Immutable, successfully materialized view only. Four caller-owned arrays
// retain their lifetimes; this component allocates/frees nothing. Configuration
// uses deterministic uint32 records/offsets, compact in actual descriptor counts.
// Getters below hide its record layout. No maximum-sized union per descriptor,
// expanded codebook rows or classifications^dimensions decode map is allocated.
typedef struct {
    native_vorbis_setup_layout_t layout;
    const native_vorbis_codebook_t *books;
    const uint32_t *configuration;
    size_t book_count, configuration_count;
} native_vorbis_setup_t;

// Complete type5 header, all256 books and64 floor/residue/mapping/mode counts.
// Validate all lengths, framing and consuming-context links before publishing
// layout. uint64 counts preserve requirements even if not addressable on MCU.
// Failure preserves layout. Header order/comment ownership belongs to raw open.
native_vorbis_numeric_status_t native_vorbis_setup_measure(
    const uint8_t *data, size_t bytes, uint64_t bits,
    const native_vorbis_identification_t *identification,
    native_vorbis_setup_layout_t *layout);

// Remeasure/match before touching any storage. Malformed/truncated data takes
// precedence over unaddressable storage (RANGE), then CAPACITY. All failures
// preserve every storage byte and output setup. Packet, layout, storage descriptor,
// four writable arrays and output setup are disjoint; input bytes stay immutable.
native_vorbis_numeric_status_t native_vorbis_setup_materialize(
    const uint8_t *data, size_t bytes, uint64_t bits,
    const native_vorbis_setup_layout_t *layout,
    const native_vorbis_setup_storage_t *storage, native_vorbis_setup_t *setup);

typedef struct {
    uint32_t order, rate, bark_map_size, amplitude_bits, amplitude_offset, book_count;
    const uint32_t *books;
} native_vorbis_floor0_setup_t;

typedef struct {
    uint32_t partition_count, class_count, multiplier, range_bits, post_count;
    const uint32_t *partitions, *class_offsets, *x;
} native_vorbis_floor1_setup_t;

typedef struct {
    uint32_t dimensions, subclass_bits, masterbook, book_count;
    const uint32_t *books;
} native_vorbis_floor1_class_t;

typedef struct {
    uint32_t type, begin, end, partition_size, classifications, classbook, stage_book_count;
    const uint32_t *cascades, *book_offsets, *books;
} native_vorbis_residue_setup_t;

typedef struct {
    uint32_t submap_count, coupling_count, channels;
    const uint32_t *coupling_pairs, *mux, *submaps;
} native_vorbis_mapping_setup_t;

typedef struct { uint32_t blockflag, mapping; } native_vorbis_mode_setup_t;

// All getters preserve output on failure. Views borrow immutable configuration.
// Scalar book IDs retain original declared indexes; missing floor1 master/subbook
// is UINT32_MAX. Mapping submaps are triples{ignored time byte,floor,residue};
// coupling_pairs contains successive magnitude/angle IDs. Residue book_offsets
// are relative to its books array; select a stage by popcount of earlier cascade
// bits. Consumers must not treat either ignored/missing field as an active link.
native_vorbis_numeric_status_t native_vorbis_setup_floor_type(
    const native_vorbis_setup_t *setup, uint32_t index, uint32_t *type);
native_vorbis_numeric_status_t native_vorbis_setup_floor0(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_floor0_setup_t *floor);
native_vorbis_numeric_status_t native_vorbis_setup_floor1(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_floor1_setup_t *floor);
native_vorbis_numeric_status_t native_vorbis_setup_floor1_class(
    const native_vorbis_setup_t *setup, const native_vorbis_floor1_setup_t *floor,
    uint32_t index, native_vorbis_floor1_class_t *class_info);
native_vorbis_numeric_status_t native_vorbis_setup_residue(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_residue_setup_t *residue);
native_vorbis_numeric_status_t native_vorbis_setup_mapping(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_mapping_setup_t *mapping);
native_vorbis_numeric_status_t native_vorbis_setup_mode(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_mode_setup_t *mode);

typedef struct {
    uint32_t mode, blockflag, previous_window, next_window, mapping, blocksize;
} native_vorbis_audio_prefix_t;

// Read packet type0, mode and long-block window flags using this setup. A single
// mode reads zero mode bits; short blocks read no window flags. Failure preserves
// output/cursor position; truncation sets sticky EOP. Output/cursor/packet data
// and all setup/storage are disjoint and immutable inputs cannot change mid-call.
native_vorbis_numeric_status_t native_vorbis_audio_prefix(
    const native_vorbis_setup_t *setup, native_vorbis_packet_t *packet,
    native_vorbis_audio_prefix_t *prefix);

#ifdef __cplusplus
}
#endif
