# Owned Vorbis floor packets and floor1 integer curves

This layer follows the owned [setup graph](VORBIS_SETUP_DESIGN.md). Its
[implementation](../idf/components/native_vorbis_numeric/floor_packet.c)
produces packet-presence state, exact affine floor0 LSP metadata, floor1 raw
and reconstructed Y values, active-post flags and integer dB-table indices.
The five public entry points are declared in
[native_vorbis_floor_packet.h](../idf/components/native_vorbis_numeric/include/native_vorbis_floor_packet.h):
`native_vorbis_floor0_packet`, `native_vorbis_floor1_packet`,
`native_vorbis_floor1_reconstruct`, `native_vorbis_floor1_curve` and
`native_vorbis_floor0_packet_gain`.
Finite qualification is pending actual checks. No residue/spectrum
value is rounded or multiplied here, and this document does not qualify full
floor0 synthesis, a complete stream decoder, PCM, or a physical board.

Primary sources are [Vorbis I sections4.3,6.2,7.2 and9.2](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html),
public Xiph v1.3.7 [floor0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c),
[floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c),
and [codebook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/codebook.c).
Only the public specification/reference and owned interfaces are involved.

## Packet status and ownership

An absent floor and a present floor at the minimum represented amplitude are
different states. Floor0 amplitude0 and floor1 presence0 explicitly select an
unused channel. Floor1 table index0 still represents a nonzero floor near
-140dB; it must never stand in for an unused-floor flag.

Actual EOP during a floor packet is nominal: return unused as though the first
amplitude/presence field were zero. EOP through the preceding audio prefix is
instead fatal for that packet. At the enclosing packet level, section4.3.2
requires floor EOP to zero all channel vectors and skip to overlap/output;
retaining sticky EOP lets that later orchestrator distinguish this condition
from an explicitly absent individual channel.
[Vorbis I sections4.3.1,4.3.2,6.2.2 and7.2.3](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).

Nominal EOP does not grant a general rule that every malformed decode becomes
unused. In particular, an out-of-range floor0 selector is explicitly an
undecodable packet. A scalar decoder's INVALID status for a zero-active book
also differs from actual packet truncation; do not manufacture sticky EOP for
that metadata compatibility case. The public API states the aggregate
cursor/output behavior and empty-book compatibility decision explicitly.
The owned decision is INVALID for active
empty-book consumption in either floor, without a fabricated EOP or zero LSPs.
Retaining an unused descriptor does not promise that it can supply a symbol.

Actual TRUNCATED maps to successful UNUSED with sticky EOP and the cursor at
its last successfully consumed field/codeword. No coefficient or Y-array bytes
are published on that path. Successfully read raw amplitude remains observable;
the unused flag controls later gain. CAPACITY and INVALID roll back the complete
floor cursor/state/output, so capacity retry consumes no packet data.

The reference has two different empty-book behaviors. Its scalar
`vorbis_book_decode()` returns-1 without a symbol for zero used entries, and
floor1 treats that as unused. Floor0 instead calls `vorbis_book_decodev_set()`;
that helper fills zero LSP values and returns success for an empty book. These
are reference compatibility choices, not the specification's actual-EOP rule.
[Xiph codebook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/codebook.c),
[Xiph floor0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c),
[Xiph floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c).

## Floor0 packet syntax and exact values

Read the full0..63-bit raw amplitude field. A zero result consumes no selector
or codeword. For a positive result, read `ilog(number_of_books)` selector bits,
including one bit with a single book and five bits with16 books. A selector
outside the configured list is invalid; reducing the width to
`ilog(number_of_books - 1)` changes the packet language.
[Vorbis I section6.2.2](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).

For positive order, decode whole entropy symbols until enough coefficients
exist. Reconstruct each selected vector's required prefix with the existing
exact affine quantization representation, add the previous full vector's last
scalar to every scalar of the next vector, and preserve the raw packed
minimum/delta words and integer multipliers. A final partial vector consumes
one complete entropy codeword; its unused scalar tail need not be materialized
and has no effect on another vector. No binary64 summation, cosine conversion,
Q-format clipping or unity cap belongs at this packet boundary.

The published packet pseudocode has a numbering inconsistency: its backward
jump names the step containing `last=0`, which would make the subsequent carry
assignment ineffective. The public reference initializes last once before
its vector loop and carries the previous vector's last scalar. The owned layer
follows that meaningful recurrence and the existing exact LSP layer, rather
than treating the inconsistent jump label as an independent numerical oracle.
[Xiph floor0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c).

Setup preserves order0 because the unsigned header field has no normative
minimum. Section6.2.2 still enters its vector-read body before testing whether
enough scalars exist: positive-amplitude order0 therefore consumes one complete
codeword and retains zero LSPs. A prefix0 vector helper is a no-op, so that
helper alone cannot implement this case. For a later curve handoff, the even
order formula's empty products give `p=(1-cos(w))/2`, `q=(1+cos(w))/2`, hence
`D=p+q=1`. This identity does not require constructing an LSP vector; the new
gain handoff can use the existing scaled-denominator gain function directly.
[Vorbis I sections6.2.2 and6.2.3](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).

Rate0 and Bark-map0 are likewise retained header metadata. Reading packet
amplitude, selector and LSPs does not require those fields. General active
curve evaluation with zero-domain mapping remains a separate unresolved
consumer boundary; this packet layer must not silently call it unused or
invent a gain policy. A PRESENT gain handoff requires positive rate/map even
for order0; failure of that consumer-domain check is explicit INVALID. The
existing positive-order wide numerical APIs remain unchanged.

The caller-owned packet state records floor index/type, presence, retained
value count and the selected floor0 book; no per-channel maximum-sized union
or decoder-owned heap is needed. Coefficients/raw Y arrays are supplied by the
caller with explicit capacity. Borrowed setup data and state must belong to
the same setup/floor; all writable arrays, state and packet/cursor storage are
disjoint. Standalone reconstruction and rendering require present-floor inputs
and validate their complete spans before writing output.

## Floor1 decode, prediction and clamping

Presence1 selects range256/128/86/64 for multiplier1/2/3/4. Read both initial
Y values using `ilog(range - 1)` bits. Range86 still uses seven bits: initial
raw values86..127 are representable and must be retained for the prescribed
prediction/guard policy rather than rejected merely on read.

Process partitions and posts in their original setup order. Decode a master
entry only when subclass bits are nonzero; consume its low subclass bits
successively, ignoring unused high bits after the partition's dimension.
A missing subclass book contributes rawY0 without an entropy read. Master and
subclass books are scalar contexts, so dimensions/lookup mappings impose no
additional packet restriction. Preserve full declared-entry indexes, including
24-bit scalar values.
[Xiph floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c).

For each later post, find its nearest lower/higher X coordinates among earlier
original post indexes. Both previously inactive zero-difference posts and
active posts participate in prediction. Reconstruct the signed integer Y with
the specification's wrapped-difference rules. Nonzero difference activates
the current post and both neighbors; a zero difference leaves this post
inactive, but a later nonzero post may activate it. Keep active flags separate
from numeric Y bits.

Section7.2.4 suggests clamping each reconstructed Y to `[0,range)` after the
complete prediction step1. The intended owned policy follows that timing:
use unmodified signed reconstructed values for subsequent predictions, then
clamp every finalY to0..range-1 before rendering. Valid inputs are unchanged.
The reference instead masks prediction values with0x7fff and later guards
multiplied rendering endpoints to0..255. Its abuse-specific masking should not
be mistaken for the normative prediction equations.
[Vorbis I section7.2.4](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html),
[Xiph floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c).

Use signed64 intermediates. Prediction is between its two earlier endpoint Y
values. In the outer unwrap branch the algebra simplifies to either rawY or
`range - 1 - rawY`; the inner branch remains within the ordinary range. With
full24-bit packet codebook entry indexes, every unclamped reconstructed
magnitude is below2^24 and `abs(dy) * dx < 2^40`. The standalone reconstruction
helper also permits arbitrary raw uint32 values: magnitudes remain below2^32
and the corresponding product below2^48 for X coordinates0..32768. Signed64
therefore covers both domains without overflow or a negative signed shift.
Clamping before multiplier gives
maximum table indices255/254/255/252, which fit uint8 exactly.

## Integer curve rendering

Sort post indexes by X for rendering while carrying Y and active flags.
Every active pair defines a segment with its original endpoints. Emit only
the requested bins, retaining that original segment slope when the right
endpoint exceeds the output extent. Write x0..x1-1 and extend the final
endpoint value constantly if its X coordinate is below the requested length.
Do not rescale a short configured domain to the transform length.

The section9.2.7 line algorithm explicitly rounds signed division toward zero.
For independent comparison, each bin can equivalently be evaluated as
`y0 + sign(dy) * floor(abs(dy) * (x-x0) / (x1-x0))`; ordinary mathematical
floor of the signed interpolation is wrong for a descending line. Rendering
length1..4096 includes meaningful endpoint1/2/8/32768 cases: endpoint1 with
two output bins produces the first Y followed by the endpoint tail, while
endpoint32768 with4096 bins produces only the original long-line prefix.
[Vorbis I section9.2.7](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).

Output indices retain the specification's dB-table coordinate without a float
lookup or spectrum multiplication. A future wide spectrum handoff can consume
these indices independently of the residue arithmetic representation.

## Required finite evidence

Tests need absent and truncated cases at every floor field/codeword boundary;
the selector width/reserved values; order0 do-while consumption; odd dimensions,
cross-vector carry and final partial VQ vectors; all63 amplitude bits; exact
packed affine words; scalar master/subclass routing and missing-book zeros;
full65 posts; original-order neighbors and later reactivation; seven-bit
range86 over-range seeds; large24-bit raw differences; clamp timing; ascending,
descending and clipped lines; short-domain constant tails; capacity and
byte-preserving failure; and sticky EOP versus ordinary unused results. The
existing setup/codebook checkpoints cover header validation separately; this
layer's floor-payload cuts should not imply rerunning every setup-header cut
for a large sparse book.

Evidence must separate original finite inputs, actual guarded component
execution, independent exact comparison and offline saved-value replay.
Compiler frame sizes alone are not task-stack high-water measurements.
Public source comparison does not mean a reference executable ran. Floor
packet/indices qualification does not close residue, inverse coupling, wide
spectrum, IMDCT/overlap, stream or PCM gates.
