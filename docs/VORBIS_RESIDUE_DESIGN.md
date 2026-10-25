# Owned Vorbis residue packets and exact accumulation

This stage follows the owned [setup](VORBIS_SETUP_DESIGN.md) and
[floor-packet](VORBIS_FLOOR_PACKET_DESIGN.md) boundaries. Its
[implementation](../idf/components/native_vorbis_numeric/residue.c) covers
residue 0/1/2 packet grammar,
exact additive vector reconstruction, exact inverse coupling and the storage
required for those vectors. The three public APIs are declared in
[native_vorbis_residue.h](../idf/components/native_vorbis_numeric/include/native_vorbis_residue.h):
`native_vorbis_residue_measure`, `native_vorbis_residue_packet` and
`native_vorbis_residue_inverse_coupling`. The
[host and emulator checkpoint](../tests/results/vorbis-residue-20261025/CHECKPOINT.md)
records the finite qualification. Floor multiplication, inverse transforms, PCM and a complete stream
decoder remain separate dependencies.

Primary sources are [Vorbis I section 8](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html),
public Xiph v1.3.7 [res0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c)
and [codebook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/codebook.c).
The owned code uses public materialized setup/codebook/quantization views;
there are no vendor decoder handles or private decoder layouts.

## Channel bundles and interval geometry

Each submap supplies an ordered channel bundle. Bundle order is ascending
original stream-channel order, and a skipped channel still has a returned
zero vector. For types 0/1, independently skip channels marked do-not-decode.
Type 2 skips only when every bundle channel is marked: otherwise its single
interleaved vector includes every bundle channel, including individually
flagged channels. An empty submap bundle consumes no packet data.

The API takes the original boolean floor-presence bytes, with exactly one byte
per stream channel, and owns the specification's single forward-order nonzero
propagation through coupling pairs. Input flags remain unchanged. That forward
pass and inverse coupling are different operations; an unordered graph closure
is not the specified substitution.

For a per-channel length `bins`, the actual residue domain is `bins` for
types 0/1 and `bins * bundle_channels` for type 2. Clip both begin and end to
that domain, use an empty interval when end is no greater than begin, and
decode only whole partitions. Prefix/suffix bins and the last incomplete
partition remain zero. No power-of-two partition rule or channel-alignment
rule is added. [Vorbis I sections 8.2, 8.5 and 8.6](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).

Type 2 operates on absolute interleaved scalar positions: flat index `t`
addresses bundle channel `t % bundle_channels` and bin `t / bundle_channels`.
The configured begin and partition size belong to this flat domain, not to
each channel separately. With three channels and begin 1, the first three
scalars go to channel 1/bin 0, channel 2/bin 0 and channel 0/bin 1. Replacing this
with a channel-row offset changes both scatter positions and, for some
dimensions, entropy-word consumption.

## Classification and stage traversal

Classification codewords are read in pass 0, once per classword group and
effective channel, in original bundle order. They are reused in later passes.
The earliest partition uses the most significant of the configured number of
base-classification digits: extracting remainders fills digit positions from
dimension-1 down to 0. A final partial group uses its leading digits and never
requires padded classification storage.

The setup inequality is one-sided: classification_count raised to phrasebook
dimension must not exceed its declared entries. Oversized phrasebooks remain
valid. During packet decode the normative modulo/division loop uses exactly
that many digits and discards a remaining high quotient; an extra
`entry < classification_count^dimension` restriction is not imposed.

Traverse all eight passes, then classword groups, partition positions and
effective channels in that order. Read classification codewords in pass 0 even
when every cascade byte is 0. A pass with no selected stage book adds nothing
but does not change the established classword syntax. For each selected stage,
the setup already ensures a positive-dimension VQ book and partition size
divisible by its dimension. Sequence accumulation resets at each VQ entry;
there is no floor0-style carry between residue entries.

Classification count 1 is a useful exact shortcut: every digit is 0, even for a
65535-dimensional phrasebook or an oversized entry. Classword reads are still
required at their normal group boundaries, but later passes need no stored
digits for this case. For classification count >= 2, the 24-bit declared entry
bound already limits a valid phrasebook dimension to 23 or less.

## Partition scatter and EOP frontier

For type 0 with partition size `n` and VQ dimension `d`, let `step=n/d`.
Vector number `i` sends component `j` to `partition_offset+i+j*step`.
Types 1/2 place successive vector components consecutively, with type 2 then
using the absolute flat scatter above. A complete VQ word produces exactly
one scalar contribution to each of its destinations; no partial entropy word
or partial VQ vector is published.

Actual packet EOP is nominal and returns all contributions from complete VQ
words decoded so far, including earlier words in the current type 0 partition.
It does not turn already decoded residue into an unused/zero floor. Prior
passes, partitions and channels retain their complete contributions. An empty
active entropy book is INVALID, distinct from actual EOP; it does not invent
a zero VQ vector or a sticky EOP.

The packet API requires its supplied layout to match a fresh measurement.
RANGE/CAPACITY refusal occurs before cursor reads or scratch/output writes.
An adequately provisioned call dry-runs the selected entropy words first;
INVALID preserves cursor, numeric output and state, while scratch may have
changed as documented. A successful dry run then zeroes and replays the same
immutable packet, publishing exactly the valid complete-word prefix on EOP.
A pre-existing sticky EOP stops an attempted entropy read before checking an
active book; a no-read call preserves that flag without claiming a new stop.

## Public reference differences

The owned choices follow the normative packet grammar where the public
reference implements narrower common-encoder behavior:

- Xiph stops when a decoded phrasebook entry is at least the classification
  power. The owned path keeps the specified low-dimension modulo digits.
- Xiph uses the highest cascade stage as its pass count, so all-zero cascades
  read no classwords. The owned path still performs the specified pass 0 reads.
- Xiph residue 0 batches all vector entry IDs for a partition before adding any
  values. On a later-word EOP it discards the current partition's earlier words.
  The owned path publishes every complete word as the normative loop does.
- Xiph's type 2 VQ helper starts at channel 0 and `offset / channels`, with a
  channel-row end bound. The owned path supports unaligned flat begin and
  partition sizes without rounding those coordinates.
- Xiph treats scalar empty-book failure like its other decode-stop cases,
  while empty residue VQ helpers add nothing and return success. The owned
  path treats active empty-book consumption as INVALID in either context.

These are explicit compatibility decisions; source comparison must not claim
that the reference executable ran. [Xiph res0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c),
[Xiph codebook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/codebook.c).

## Exact numeric storage

The existing affine quantization representation preserves packed minimum and
delta words and their integer multipliers. A residue vector adds contributions
from different books, so one affine pair cannot represent every accumulated
bin. The intended output instead uses a common exact dyadic grid and a dynamic
number of uint32 limbs, measured from the potential stage books in the selected
mapping. All assigned, nonempty bundles contribute to that numeric format,
even when the current flags skip them or their clipped interval has no complete
partition. Unassigned submaps are ignored. All submaps use one point position
so later cross-submap coupling does not require a lossy conversion. Numeric
format is independent of floor flags; reusable classification capacity depends
on their propagated activity.

The conservative planner uses the following exact integer bounds. For each
nonzero packed mantissa `m` with exponent `E`, its lowest bit is
`E + ctz(m)` and its exclusive top is `E + bit_length(m)`. A book's `top` is
the greater of its nonzero term tops. Let `k` be its dimensions for sequence 1,
otherwise 1, and let `W = k * (minimum_nonzero + delta_nonzero *
((1 << value_bits) - 1))`. The book's scalar upper exponent is
`top + ceil_log2(W)`. Across mapped stage books, take the greatest scalar upper
exponent and add 3 for eight passes; subtract the common lowest bit to obtain
`magnitude_bits`. The limb count is `ceil((magnitude_bits + 1) / 32)`, including
the sign. No floating logarithm or inspection of decoded packet values enters
this measurement.

An unpacked packed value has a 21-bit mantissa and binary exponent -788..235.
For a sequenced vector component `k<=65535`, its affine multipliers satisfy
`M=k`, `D<=k*65535`, so `M+D<2^32`. Each vector scalar therefore has magnitude
below 2^288. A bin receives at most one scalar per pass; eight passes give a
residue magnitude below 2^291. Every value is an integer multiple of 2^-788,
so its signed integer coefficient fits 1080 bits. A universal 34-word uint32
representation provides 1088 bits; ordinary selected books can use fewer limbs.

Inverse coupling does not multiply this range by the number of coupling steps.
Each branch retains the magnitude operand in one output and gives the other
output magnitude `abs(abs(m)-abs(a))`. The global maximum absolute component
cannot increase, even through repeated legal coupling pairs. This bound ends
before floor multiplication: the separate floor0 logarithmic-gain range is
not made finite merely by choosing a residue integer format.

Zero packed mantissas represent exact zero regardless of their sign/exponent
bits. When the planner finds no nonzero packed minimum/delta terms, it uses a
canonical zero-limb view with exponent, magnitude and limb count 0, avoiding a
numeric array. It does not scan multiplicands to discover every other
identically-zero book: a nonzero delta with all stored q values 0 can retain a
conservative nonzero width. The zero-width optimization never removes required
classification/stage entropy reads, empty-book checks or EOP behavior. A zero
numeric footprint and classification scratch requirements are separate
measurements.

Avoid a full 65535-component temporary or calling the scalar quantizer for every
component of a sequenced vector: repeated prefix reconstruction would be
quadratic. An incremental entry walk can retain the lookup1 quotient, component
number and exact running multipliers, producing each scalar once without
modifying the existing quantization API or rounding an intermediate.

Caller-owned output and classification scratch need measured addressability
and capacity checks. Full legal 255-channel vectors can exceed MCU memory;
resource failure is not an additional bitstream-format cap. Sequential
submaps may reuse scratch sized for their largest bundle. The decoder must
zero every returned vector, including skipped channels and uncoded tails,
rather than rely on the caller's previous buffer contents.

Each planar sample occupies `limbs` consecutive uint32 words, least significant
first, and represents a two's-complement integer multiplied by `2^exponent`.
Its offset is `((channel * bins) + bin) * limbs`. Inverse coupling traverses
the original mapping pairs in reverse order and modifies this grid in place.
It checks the complete shape, capacity and strict measured signed domain
before any write. In particular, a claimed `abs(value) < 2^magnitude_bits`
excludes the negative power-of-two boundary as well as the positive boundary;
ordinary sign-extension checks alone are not sufficient for that strict test.

## Required finite evidence

Named cases need all three scatter formats, several active/skipped channels,
type 2 any-active/all-inactive behavior, nonaligned type 2 begin/grouping, clipped
and reversed intervals, incomplete partition tails, most-significant-first
classification digits and final partial groups, oversized phrasebook entries,
all eight passes, all-zero cascades, zero-mantissa stage books, dimensions up to
65535, sequence resets and varied quantization layouts, active empty books,
and every meaningful classword/VQ-word EOP frontier. Numeric checks must compare
exact limb coefficients and zero extension, including cancellation and signed
boundary values. No finite residue campaign alone closes the complete stream,
floor multiplication, transform, PCM, radio or physical-device gates.
