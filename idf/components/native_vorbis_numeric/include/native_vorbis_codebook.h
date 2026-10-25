// Owned packet cursor and complete Vorbis I codebooks (sections 2 and 3).
#pragma once
#include "native_vorbis_quant.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    const uint8_t *data;
    size_t bytes;
    uint64_t bits, position;
    bool end_of_packet;
} native_vorbis_packet_t;

// Explicit valid-bit extent; bits above it are ignored. For transported Vorbis
// packets include every octet (bits=8*bytes, checked), including final padding
// as required by section2.1.8. Shorter extents also support internal/test spans.
// Failed initialization leaves the cursor unchanged. Storage is caller-owned.
native_vorbis_numeric_status_t native_vorbis_packet_init(
    native_vorbis_packet_t *packet, const uint8_t *data, size_t bytes,
    uint64_t bits, uint64_t start_bit);

// LSb-first integer, width0..64. A truncated read sets sticky end_of_packet,
// preserving position and value. Reading zero bits at the end succeeds until
// end_of_packet has been set; every subsequent read then returns TRUNCATED.
// Invalid arguments change neither the cursor nor value. The output value,
// cursor and immutable packet data must not overlap.
native_vorbis_numeric_status_t native_vorbis_packet_read(
    native_vorbis_packet_t *packet, unsigned width, uint64_t *value);

typedef struct {
    uint32_t code, entry, length;
} native_vorbis_codeword_t;

typedef struct {
    native_vorbis_quant_layout_t quantization;
    uint64_t start_bit;
    uint32_t used_entries, maximum_length;
} native_vorbis_codebook_layout_t;

// Immutable materialized view. Words are sorted by their MSb-aligned lexical
// code, retaining original sparse entry numbers. Exactly used_entries words
// and quantization.multiplicand_count uint16 values are required. This is not
// a length-sorted canonical Huffman assignment. Only successfully materialized
// views with unchanged storage may be used; pointers are never vendor handles.
typedef struct {
    native_vorbis_codebook_layout_t layout;
    const native_vorbis_codeword_t *words;
    size_t word_count;
    native_vorbis_quantization_t quantization;
} native_vorbis_codebook_t;

// Start at the 24-bit codebook sync. Parse the complete ordered/unordered/
// sparse length list, validate the tree and measure the complete quantization
// section. No allocation or entries-sized scratch array. Failure preserves
// layout. The singleton erratum requires encoded length1, consumes one bit,
// and accepts either value of that bit during audio decoding.
native_vorbis_numeric_status_t native_vorbis_codebook_measure(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    uint64_t start_bit, native_vorbis_codebook_layout_t *layout);

// Remeasure and match layout before writing caller storage. INVALID/TRUNCATED
// take precedence over RANGE (unaddressable storage), then CAPACITY. Measurement
// still reports the complete uint64 count. Every failure preserves both arrays
// and book. The packet, layout, storage arrays and output book are disjoint,
// and all input memory remains immutable throughout each call. On success the
// book owns nothing; the caller retains both storage arrays for its lifetime.
native_vorbis_numeric_status_t native_vorbis_codebook_materialize(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    const native_vorbis_codebook_layout_t *layout,
    native_vorbis_codeword_t *words, size_t word_capacity,
    uint16_t *multiplicands, size_t multiplicand_capacity,
    native_vorbis_codebook_t *book);

// Read exactly one codeword, returning its original entry number. A short
// prefix sets sticky EOP and leaves position/output unchanged. No allocation,
// read past the declared extent, unused sparse entry or minimum lookahead
// demand. Entry output is disjoint from cursor, book/storage and packet data.
native_vorbis_numeric_status_t native_vorbis_codebook_decode(
    const native_vorbis_codebook_t *book, native_vorbis_packet_t *packet,
    uint32_t *entry);

// Decode one entry and reconstruct its requested prefix exactly. Capacity and
// lookup checks precede audio reads. Prefix0 is a successful no-op for a valid
// positive-dimension VQ book. Every failure preserves output and cursor
// position; truncation alone sets sticky EOP. Output, book/storage and packet
// data/cursor must be disjoint and immutable inputs cannot change mid-call.
native_vorbis_numeric_status_t native_vorbis_codebook_vector(
    const native_vorbis_codebook_t *book, native_vorbis_packet_t *packet,
    size_t prefix, native_vorbis_affine_t *output, size_t capacity);

// Read ceil(order/dimensions) words and reconstruct floor0 LSPs, including the
// cross-vector carry and final partial vector. order1..255. An aggregate failure
// preserves all output and the original cursor position, with sticky EOP only
// on truncation. Capacity retry cannot consume any audio. Fixed bounded scratch
// retains at most255 original entry indexes; there is no heap or VLA.
native_vorbis_numeric_status_t native_vorbis_codebook_floor0_lsp(
    const native_vorbis_codebook_t *book, native_vorbis_packet_t *packet,
    size_t order, native_vorbis_affine_t *output, size_t capacity);

#ifdef __cplusplus
}
#endif
