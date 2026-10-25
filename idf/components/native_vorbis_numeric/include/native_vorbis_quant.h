// Owned quantization fields and exact VQ reconstruction, Vorbis I 3.2/6.2.2.
#pragma once
#include "native_vorbis_floor0.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t dimensions, entries, lookup_type;
    uint32_t minimum_bits, delta_bits, value_bits, sequence_p;
    uint64_t multiplicand_count;
    uint64_t start_bit, multiplicand_bit, end_bit;
} native_vorbis_quant_layout_t;

// Immutable view. Materialization copies raw unsigned multiplicands to storage
// owned by the caller; it never expands entries*dimensions into floating rows.
typedef struct {
    native_vorbis_quant_layout_t layout;
    const uint16_t *multiplicands;
    size_t storage_count;
} native_vorbis_quantization_t;

// Complete 16-bit dimensions / 24-bit entry metadata. Lookup0/2 may have zero
// dimensions/entries at this layer; Huffman and consuming-context validation
// are separate. Lookup1 requires positive dimensions. No floating integer root.
native_vorbis_numeric_status_t native_vorbis_quantization_count(
    uint32_t dimensions, uint32_t entries, uint32_t lookup_type, uint64_t *count);

// Start immediately after codeword lengths, at the four-bit lookup type.
// packet_bits is an explicit valid bit extent within packet_bytes. On success
// retain original packed words and the complete uint64 required multiplicand
// count (even when unaddressable on a 32-bit target). On any failure leave
// layout unchanged. This does not validate the earlier Huffman length list.
native_vorbis_numeric_status_t native_vorbis_quantization_measure(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    uint64_t start_bit, uint32_t dimensions, uint32_t entries,
    native_vorbis_quant_layout_t *layout);

// Remeasure and match the layout before writing. CAPACITY leaves storage/book
// unchanged; layout supplies the required uint64 count for allocation/retry.
// Truncation/invalid metadata takes precedence over insufficient capacity.
// Packet, writable storage, layout and output book must not overlap. The packet
// and view/storage must remain immutable during calls; the caller owns lifetime.
native_vorbis_numeric_status_t native_vorbis_quantization_materialize(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    const native_vorbis_quant_layout_t *layout,
    uint16_t *storage, size_t capacity, native_vorbis_quantization_t *book);

// Decode a VQ entry's prefix without a Huffman/packet read. Entry indexes refer
// to declared rows (including unused sparse rows); the entropy layer must never
// produce an unused row. Prefix <= dimensions. Prefix0 is a successful no-op
// for a valid positive-dimension VQ book and accepts output=NULL/capacity0.
// Lookup0 returns NO_LOOKUP. All requested values are validated before writes.
// Output must not overlap the book or its storage. No allocation or VLA.
native_vorbis_numeric_status_t native_vorbis_quantization_vector(
    const native_vorbis_quantization_t *book, uint32_t entry, size_t prefix,
    native_vorbis_affine_t *output, size_t capacity);

// One component, including sequence accumulation, without allocating the full
// vector. component < dimensions. This supports large dimensions even when a
// complete output row would not fit target RAM. Failure leaves output unchanged.
native_vorbis_numeric_status_t native_vorbis_quantization_scalar(
    const native_vorbis_quantization_t *book, uint32_t entry, uint32_t component,
    native_vorbis_affine_t *output);

// Reconstruct floor0 LSPs from the already decoded entry indexes of one selected
// book. Codebook sequence resets for each entry; a separate last-LSP carry is
// retained across entries as in Xiph floor0.c. order1..255; entry_count must be
// exactly ceil(order/dimensions), and the final vector is truncated to its used
// prefix. No unused tail or following entry is read. Every failure preserves
// output, including late invalid entries/multiplicands and insufficient space.
// Entry indexes remain immutable during both passes; output must be disjoint
// from entries, the book and the multiplicand storage.
native_vorbis_numeric_status_t native_vorbis_floor0_lsp_from_entries(
    const native_vorbis_quantization_t *book, const uint32_t *entries,
    size_t entry_count, size_t order, native_vorbis_affine_t *output,
    size_t capacity);

#ifdef __cplusplus
}
#endif
