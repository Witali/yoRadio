# Owned Vorbis codebook parsing and Huffman assignment

The owned quantization layer now implements complete codebook setup parsing,
scalar entropy decoding, and transactional VQ/floor0-LSP handoff in
[codebook.c](../idf/components/native_vorbis_numeric/codebook.c), with an
independent frontier-assignment review recorded below. The
[finite checkpoint](../tests/results/vorbis-codebook-20261025/CHECKPOINT.md)
records actual sanitized host and native emulator checks. No complete stream
decoder or PCM result is qualified by this layer.

The primary sources are [Vorbis I sections 2, 3 and Errata 20150226](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
[Xiph v1.3.7 codebook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/codebook.c)
and [Xiph v1.3.7 sharedbook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c).
Only public source and the specification are involved.

## Format requirements and compatibility decisions

- Assign used entries in original entry order. Skip unused sparse entries.
  Sorting lengths before assignment changes the encoded language.
- Ordered zero runs represent length gaps. Bound lengths at 32, reject runs
  larger than the remaining entries, and require every setup field to exist.
- A singleton must have encoded length 1, consumes one bit, and accepts either
  bit value. The earlier zero-bit claim is explicitly superseded by the erratum.
- Reject overpopulation and nonempty underpopulation, except that singleton.
- Preserve declared entry indexes when compacting or sorting active rows.
  Lookup0 is valid for scalar use but cannot supply a VQ vector.

These rules come from the [current specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).

Zero-active setup metadata is a deliberate reference-compatibility case.
`vorbis_book_init_decode()` succeeds without constructing words when no entries
are active; `vorbis_book_decode()` then returns failure without a symbol.
The owned parser retains empty/all-unused descriptors, and scalar consumption returns INVALID
without changing output or cursor. Do not invent a singleton or entry0. The
specification's general tree-completeness sentence does not explicitly grant
this empty exception. [Xiph sharedbook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c),
[Xiph codebook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/codebook.c).

Dimension0 is retained for scalar lookup0 and metadata-only lookup2; vector
consumers validate positive dimensions. Lookup1/dimension0 remains explicitly
invalid in the current owned quantization API: its greatest-integer-root
definition has no finite result. Xiph instead parses zero lookup values there;
adopting that permissive behavior would be a separate compatibility decision.
Do not turn the reference library's `ilog(dim)+ilog(entries)>24` allocation
restriction into a format limit. [Xiph codebook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/codebook.c).

## Frontier assignment: independent correctness argument

Represent an available prefix by its depth and its prefix bits aligned to the
most significant end of a uint32 key. Maintain one slot at each depth0..32 and
an independent availability bit; numeric key0 is a valid prefix. Initially the
only available slot is the root at depth0 with key0.

For a requested nonzero length L, choose the deepest available depth d<=L.
If none exists, no length-L leaf is possible. Remove that slot, descend its
left branch to depthL, and keep each right sibling as an available prefix at
its depth. Emit the resulting left leaf and its original entry index. Unused
entries do not modify the frontier.

The invariant has three parts:

1. Available prefixes are disjoint subtrees containing exactly the remaining
   unassigned leaves; none is an ancestor of an assigned codeword.
2. At most one available prefix exists at each depth.
3. A deeper available prefix lies to the left of every shallower available
   prefix in binary lexicographic order.

The invariant holds for the root. For the next request, any available prefix
deeper thanL is unusable: its depth-L ancestor already contains an assigned
leaf, so choosing that ancestor would violate prefix freedom. Among the
eligible prefixes, part3 makes the deepest one the leftmost. Its leftmost
depth-L descendant is consequently the smallest valid codeword of lengthL.

Because d was the deepest eligible depth, slots d+1..L were empty before the
split. The new right siblings therefore cannot overwrite another available
prefix. Within the split subtree, deeper right siblings lie left of shallower
right siblings. Existing deeper prefixes remain to its left; existing shallower
prefixes remain to its right. All three invariant parts are preserved. By
induction, the algorithm implements lowest-unused assignment in entry order,
including unsorted lengths.

After assignment, a nonempty frontier proves an incomplete tree. Apply the
explicit singleton and zero-active compatibility cases before interpreting
that final state. A failure to find an eligible prefix proves overpopulation.

For example, lengths `[2,1,2]` produce `00,1,01`. This is an independent small
counterexample to assigning the same entries after a length sort. Useful
depth32 cases include both `[1,2,...,31,32,32]` and the reverse depth order;
these exercise boundary keys and completion without allocating a large tree.

## Representation and decode boundaries

A uint64 availability mask can represent all 33 depths. Splitting sets a right
child with `UINT32_C(1) << (32-depth)` only for depth1..32, so no shift by32 is
needed. Keep length32 operations unsigned, and use uint64 if forming an interval
end that can equal2^32. A length0 value is only the unused-entry marker.

The implementation sorts complete `{key,length,original_entry}` records after assignment. Heapsort
provides bounded auxiliary storage; sorting keys alone would destroy the entry
mapping. Prefix-free words have distinct aligned keys. The assignment uses
fixed33-slot scratch; required row storage is caller-owned and capacity failure
must remain distinct from an invalid stream. No board-specific entry/dimension
cap follows from this representation.

Measurement retains the full uint64 multiplicand count. Materialization first
remeasures and matches the immutable setup layout. INVALID/TRUNCATED precede
RANGE for an unaddressable uint16 storage object, then CAPACITY. On 32-bit
targets, the explicit addressability check uses `SIZE_MAX/sizeof(uint16_t)`;
it is a storage limit, not a bitstream count limit. Every failure preserves
both storage arrays and the output book.

The packet, layout, writable arrays and output book are disjoint. Once the
complete preflight succeeds, quantization copy and length replay follow the
same immutable input. That establishes why the writing replay cannot discover
a new parser failure. The materialized view and its caller-owned storage remain
immutable for their lifetime. Decode validates shape in constant time and then
uses binary search; it does not rescan every codeword on each symbol.

Decode uses the available packet bits, up to32, without requiring a full32-bit
lookahead. A completed short leaf at packet end succeeds; an incomplete leaf
returns truncation. A singleton still needs its one actual bit. A zero-active
book returns INVALID without consuming a bit. A failed setup read is fatal to
setup; later floor/residue code applies its own specified truncation behavior.
For an actual transported packet, pass every octet as `bits=8*bytes`, checking
that multiplication first. The final zero padding is readable under the
transport's octet extent. Shorter explicit bit extents serve internal spans and
controlled truncation tests; they are not an inferred encoded-payload length.
[Vorbis I sections 2.1.8, 2.1.9 and 3.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).

The owned cursor reads LSb-first integers of widths0..64. Truncation sets
sticky end-of-packet while preserving position and output. A zero-width read
at the extent succeeds before EOP is set; after EOP it also returns TRUNCATED.
Invalid arguments preserve the entire cursor and output. Scalar Huffman
failure likewise preserves position/output, with sticky EOP only on truncation.
All scalar output objects are disjoint from cursor, packet and book storage.

VQ prefix decoding checks lookup, dimensions and capacity before reading audio.
A zero prefix is an explicit no-op for a valid positive-dimension VQ book.
For a nonzero prefix, the function decodes through a temporary cursor and commits
that cursor only after exact reconstruction succeeds. Floor0-LSP decoding first
reads exactly `ceil(order/dimensions)` original entry indexes into fixed scratch
of at most255 elements, then applies the existing exact cross-vector recurrence
and final-prefix truncation. An aggregate failure preserves all output and the
original position; truncation alone sets sticky EOP. Capacity retries therefore
cannot consume audio. These wrappers allocate neither heap memory nor a VLA.

The tests bind original lengths to emitted words using independent greedy free
intervals and bit-by-bit tree traversal. Fixed and generated cases include
unsorted and sparse permutations, missing/extra Kraft mass, singleton bits 0/1
and EOP, ordered zero runs, every setup-field truncation, empty descriptors,
dimension0 contexts and output/cursor preservation. A separate host supplement
covers malformed ordered runs/length33, reserved lookup types, every invalid
singleton length and full 16-bit dimension/24-bit sparse metadata. Actual counts
and limits are retained in the checkpoint; this finite suite is not exhaustive
Vorbis conformance or an independent proof of complete synthesis.
