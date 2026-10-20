# Map2 and mapped-single-entry setup repair proposal

This is source-only preparation for independent CYD/Xtensa and C3/RV32
qualification. Canonical files and previous proposals/campaigns are untouched.
`setup-map2.patch` contains two changes per platform; full exact baseline and
candidate copies are beside it. Neither candidate has been compiled or decoded.

## Public format basis

[Vorbis I, section 3.2.1](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
defines lookup2 as `entries * dimensions` multiplicands, indexed by the original
entry. Unused Huffman entries do not remove their multiplicands. Its
Errata 20150226 defines a single active entry, including a sparse one: its length
must be one, decoding consumes one bit, and either bit returns that entry.
[Xiph v1.3.7 sharedbook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c)
uses original-row offsets in `_book_unquantize` and duplicates the single-entry
fast-table result. These establish the intended format behavior, not target
qualification of this proposal.

## Source diagnosis

Both pinned setup.c sources have the following original line numbers:

| Original location | Defect | Proposed behavior |
| --- | --- | --- |
| `_make_words`, 123-125 | A single declared entry is replaced with flagged scalar zero, without `decpack`; mapped quants remain unread and its second branch is empty. | A single **active** entry uses `decpack(original_index, 0, ...)`, requires length1 and fills both branches. |
| `_make_words`, 128-180 | Packed lookup2 reads a row only when the original Huffman entry is active. A hole shifts every later row and the following setup fields. | Read/discard each unused row, in place, without allocating an all-entry quant table. |
| `repair_vorbis_book_unpack`, 555-566 | Wide lookup2 reads only a contiguous `used_entries * dim` prefix. Sparse original rows cannot match `decpack`'s compact active indices, and remaining quants shift subsequent setup fields. | Read all original rows; retain active rows in original entry order, matching compact used-entry leaves. |

The sparse D4 book in the original books bank selects packed dec_type1. The new
D16/two-bit book requires 33 bits with its flag and selects wide dec_type3.
These are independent source paths. A successful header alone cannot establish
their decoded vector correctness.

## Bounds and preservation

The existing parser validates positive entries/dimensions, their product, each
length, quant width1..16 and the length-list-derived active count before these
paths. A single active entry always uses a four-byte node and a three-word
allocation; the new two-branch write additionally checks capacity>=2. For wide
books, the row-byte multiplication has an explicit INT_MAX bound; `repair_calloc`
checks the active-row allocation against SIZE_MAX. The write offset uses size_t,
and at most `used_entries * dim` values are stored in that allocation. Quant
reads still reach the existing end-of-packet check and cleanup path.

Time remains proportional to the required complete wire quant table. Memory is
the existing active-row allocation, plus scalar loop variables. Discarded rows
allocate nothing. Quant precision, q_min/q_del, sequence handling, leaf packing,
ABI fields and decode/synthesis/MDCT/PCM code are unchanged.

The general unused-row discard is restricted to positive active count. The
existing zero-active behavior, including the n<2 branch and wide zero-byte
allocation rejection, is intentionally preserved. General Huffman population
validation is untouched; this is not an empty-book or general malformed-tree
repair. Source projection checks assert that all bytes outside the two reviewed
functions stay identical after newline normalization, and preserve each file's
actual newline encoding in its candidate copy.

## Qualification still required

`fixture-source-audit.json` pins the existing books and new eight-case matrices.
The planned complete corpus is all17 existing cases plus all8 supplement cases:
25 cases, 350 raw packets and 623360 expected PCM bytes. The supplement covers
sparse/dense wide lookup2 with sequence0/1, and nonzero mapped single-entry versus
dense twin with sequence0/1; its audio exercises both single-entry bit values.
The parent reports actual Xiph acceptance and all four equality groups, while
native FFmpeg refuses lookup2. That reported host evidence is separate from the
source checks performed here; no reference command was executed by this prep.

Keep the current checked baseline and original-vendor panic evidence unchanged.
Root must independently qualify each architecture's candidate with public
checked-only open/decode/close, metadata on every packet, complete consumption,
expected overlap sizes, canaries, nonzero transitions and all actual PCM bytes.
Compare actual PCM to the pinned Xiph reference and the four within-decoder
equality groups. No original-vendor call is a prerequisite for these unsupported
formats. Panic, interruption, missing cases or generic errors cannot qualify a
repair or a negative control.

Useful root-owned controls restore only the packed-skip change, only the wide
row-compaction change, or only the mapped-single branch in otherwise fixed
source. Each must reproduce its named case/phase after earlier prerequisites;
any unrelated failure remains NONPASS. No such controller or target run is
created here.

Coverage limits remain explicit: the eight supplement cases use two-bit quants
and a fully declared single-entry mapped book. A sparse single-active mapped
book, map1 nonzero singleton, wide singleton and 9..16-bit wide storage are not
new runtime evidence from these25 cases. The proposed code handles those through
the same public setup rules, but they must not be described as individually
qualified. There are no allocation-failure, Ogg/EOF/reset, private-state, AAC,
physical-board, radio or full-production claims.
