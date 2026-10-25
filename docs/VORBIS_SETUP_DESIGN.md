# Owned Vorbis identification and setup parsing

This layer adds the configuration and audio-prefix boundary above the owned
codebook implementation. The public API is in
[native_vorbis_setup.h](../idf/components/native_vorbis_numeric/include/native_vorbis_setup.h).
The [finite checkpoint](../tests/results/vorbis-setup-20261025/CHECKPOINT.md)
records 300 sanitized host rows and 400 native emulator rows with separate
exact comparison. This document records the independent format audit; no
completed stream decoder, floor/residue synthesis, PCM output or hardware
qualification follows from this configuration/prefix layer.

The primary specification is [Vorbis I sections 4, 6, 7 and 8](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).
The public reference comparisons use Xiph v1.3.7
[info.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/info.c),
[floor0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c),
[floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c),
[res0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c), and
[mapping0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/mapping0.c).
Reference allocation limits are not automatically format limits.

## Identification and packet boundaries

Identification consumes the complete type1 header prefix, including its six
ASCII `vorbis` signature bytes. Version must be0, channels1..255, and sample
rate a positive full-width uint32 value. Block exponents are6..13 and ordered;
the resulting block sizes are64..8192. Three bitrate hints retain their signed
32-bit patterns: nonpositive or inconsistent hints do not invalidate a header.
The framing bit must be1. [Xiph info.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/info.c).

Setup similarly checks type5 and its signature. Its ordered sections are books,
time transforms, floors, residues, mappings and modes, followed by framing1.
Counts cover all256 books and all64 entries in each other section. Every time
transform is0; accepted floor types are0/1, residue types0/1/2 and mapping type0.
Mode window/transform types are0, with a valid mapping index. These checks must
not depend on whether a descriptor is eventually selected by a mode.
[Xiph info.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/info.c).

All header reads require their bits to exist. The byte transport supplies
`8 * packet_bytes` meaningful bits, including unused padding bits. Explicit
shorter bit extents are an internal/testing facility. No exact-end check is
added after the required framing bit; trailing packet bits are ignored, as by
the public reference. Header sequence, the comment packet and transport/BOS
ownership remain responsibilities of the enclosing stream-open layer.

The audio-prefix API consumes type0, `ilog(mode_count - 1)` mode bits, and two
window flags only for a long-block mode. A single mode consumes zero mode bits;
short blocks consume no window flags. It publishes mode, mapping, block size
and flags together. An invalid mode/type or truncation cannot publish a partial
prefix or advance the caller's position; truncation records sticky EOP. EOP at
this boundary discards the audio packet, unlike nominal EOP during later floor
or residue work. [Vorbis I section4.3.1](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).

## Floor context checks

Floor0 retains order, its own rate and Bark map size, amplitude width/offset,
and1..16 book IDs. Its rate need not equal identification rate. Every selected
book must have a VQ lookup and positive dimension. Amplitude width0..63 and
offset0..255 remain valid; width0 always yields an absent floor. No bound ties
Bark map size to transform length. [Xiph floor0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c).

There is an explicit normative/reference distinction: section6.2.1 describes
unsigned order/rate/map fields without stating positive minima. Xiph
`floor0_unpack()` rejects all three when zero. This descriptor layer preserves
all encoded unsigned values, including zero: an unused or always-absent floor
does not need active curve arithmetic. The existing owned numerical floor0
APIs still require positive order/rate/map. Supporting an active zero-domain
curve is a separate unresolved consumer boundary; the header parser does not
invent a constant-floor or division-by-zero policy, and retaining these fields
does not qualify their active synthesis.
[Xiph floor0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c).

Floor1 stores its0..31 partition class IDs, all classes0..maximum ID even when
some intervening classes are unused, multiplier1..4 and range width0..15.
With zero partitions it encodes no classes. Each class dimension is1..8,
subclass width0..3, and has exactly `1 << subclass_width` subclass book slots.
Masterbook is read only when subclass width is positive. Encoded subclass0
means no book; other values name declared books0..254. Preserve the missing
marker independently of book0. Both master/subclass books are scalar contexts:
lookup0 or dimension0 is not rejected solely for use here.
[Xiph floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c).

The two implicit X posts are0 and `1 << range_bits`. Every other post is read
in partition/class order. All posts must be distinct. **65 total posts,
including the two implicit posts, is a normative maximum** in section7.2.2;
it is not merely the reference's `VIF_POSIT=63` allocation policy. Reject a
larger count even if the compact storage could hold it. Range width0 is valid
with only implicit posts; any additional zero-valued post then duplicates an
endpoint. X coordinates need not fit the current transform half-length: curve
rendering later extends or truncates the configured domain.
[Vorbis I section7.2.2 and7.2.3](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html),
[Xiph floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c).

## Residue context checks

Retain24-bit begin/end, partition size1..2^24, classifications1..64,
classbook ID,8-bit cascades and each active stage book ID in declared order.
All three residue types share this header. Stage books need a VQ lookup and
positive dimension. The partition size must be divisible by each active
stage dimension: sections8.3 and8.4 require whole VQ vectors per partition,
and type2 applies type1 to an interleaved bundle. This requirement does not
imply a power-of-two restriction. [Vorbis I sections8.3..8.6](https://www.xiph.org/vorbis/doc/Vorbis_I_spec.html).

The scalar classification book needs a positive dimension and
`classifications ^ classbook_dimension <= declared_book_entries`.
Declared entries, rather than active sparse entries, define that inequality.
Oversized books are permitted; equality is not required. Compute the power
with bounded integer multiplication: before multiplying by classifications,
test against `entries / classifications`. Classifications1 needs no
dimension-length loop. Store at most the resulting bounded scalar count,
not an expanded classifications-to-partitions decode map.
[Xiph res0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c).

No setup requirement rejects begin>=end or end beyond the transform's actual
vector extent. Keep the raw coordinates. The public inverse clamps end to
available samples and does no residue work when the remaining interval is
nonpositive. For type2 the available vector extent includes the interleaved
channel count. A later decoder must preserve this empty-interval behavior
without unsigned subtraction underflow. The setup layer adds no sample-rate,
block-size or partition-power policy cap.
[Xiph res0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c).

## Mapping and link checks

Mapping0 has1..16 submaps and either no coupling or1..256 ordered coupling
steps. Each magnitude/angle ID uses `ilog(channels - 1)` bits, is in range,
and differs from its partner. A mono stream therefore cannot use coupling,
including the zero-width read case. Do not add pair uniqueness or acyclic
graph requirements. With several submaps, every channel mux ID must be below
the submap count; otherwise its implicit mux is0.
[Xiph mapping0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/mapping0.c).

The mapping reserved two bits must be zero. In contrast, each submap's unused
8-bit time placeholder is read and discarded without a zero requirement.
Retaining that byte in the compact record is harmless, but it is not an active
time-transform link. Every floor/residue link and each mode mapping ID must
be in range. Unused submaps and repeated links remain legal.
[Xiph mapping0.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/mapping0.c).

## Caller-owned representation and transaction

The setup descriptor borrows four separately addressable caller-owned arrays:
book views, active codewords, uint16 quantization multiplicands and a uint32
configuration pool. Configuration offsets count uint32 elements. The pool
contains actual-size records and index tables; typed getters return immutable
borrowed views. The floor1 class getter requires a floor1 view obtained from
the same setup object; views from different owners cannot be mixed. There is
no maximum-sized union per floor/residue/mapping,
expanded VQ row table, or exponentially sized classification decode map.

Each floor/residue/mapping/mode section starts with a reserved table of absolute
record offsets. Floor0 records retain their seven leading scalars and book IDs.
Floor1 appends its actual class records before its main record, with absolute
class offsets and explicit missing-book markers; the main record retains
partitions and all X posts. Residue records retain cascades, relative offsets
into a packed active-book list and that list. Mapping records retain ordered
coupling pairs, a mux value per channel (implicit zeros are materialized), and
time/floor/residue triples. Modes retain just blockflag and mapping. All
offsets use pool elements rather than byte addresses, so relocation does not
depend on pointer width.

Book counts, codeword requirements and multiplicand requirements are measured
without narrowing first. Configuration size is bounded by the encoded format;
actual descriptor counts determine its footprint. Full legal maxima can exceed
an MCU's available memory: a caller may decline an allocation, but that is a
resource/capacity result rather than a new format restriction. The same public
shape works on ESP32 and ESP32-C3; their available heap and worker placement
remain platform concerns outside this parser.

A conservative record bound is112,960 uint32 elements:64 times at most294
floor units,647 residue units,818 mapping units and2 mode units, plus four
64-element offset tables. Some floor maxima cannot occur together, so this
is an upper bound rather than a required allocation. It proves uint32 offsets
are sufficient without pretending that roughly452KB fits every target.
Across256 books, declared codeword counts are below2^32 and multiplicand
counts below2^48; uint64 aggregate requirements therefore cannot overflow
from format fields alone. Array object-byte addressability still needs its
own check on32-bit targets.

Measure validates the entire header and consuming-context links before
publishing its layout. Materialize remeasures immutable input and matches the
supplied layout before touching storage, then checks addressable object sizes
and capacities for all four arrays. Malformed/truncated input takes precedence
over RANGE and then CAPACITY. Every failure preserves all storage bytes and
the output descriptor. Inputs, storage metadata, writable arrays and output
must be disjoint and remain immutable where documented during the call.

After successful preflight, deterministic replay writes exactly the measured
records. The parser uses fixed bounded scratch rather than a heap or packet-
sized stack array: book facts cover256 declarations, and floor1 scratch covers
its65 posts,31 partitions and16 classes. Compiler frame measurements, when
available, describe only the measured functions; they cannot prove complete
task-stack or callee/libm bounds. Getter inputs must be successfully
materialized immutable views; this API is not a parser for arbitrary forged
configuration arrays.

The existing codebook zero-active and scalar dimension0 compatibility choices
remain documented in [VORBIS_CODEBOOK_DESIGN.md](VORBIS_CODEBOOK_DESIGN.md).
Setup checks a book in its actual consuming context. It does not reject an
unused declaration simply because no symbol can be decoded from it.

## Required qualification scope

Independent tests need exact section/view comparisons; invalid signatures,
reserved types and links; all count boundaries; floor1 post count/uniqueness;
all header bit cuts; missing master/subclass fields; floor0 raw round trips
including zero metadata; safe classification powers; stage dimension
divisibility; reversed
residue bounds; nonzero ignored time bytes; mono and high-channel coupling;
single-mode zero-bit audio mode and long-window truncations; capacity/RANGE
precedence; forged measured-layout rejection; and byte-preserving failure.

Host sanitizers and native ESP32/ESP32-C3 captures qualify only the actually
run finite corpus. Public-reference agreement is a separate source comparison;
no reference executable or production audio path has been exercised by this
design audit. Full packet floor1/residue decode, inverse coupling, numeric
spectrum handoff, IMDCT/overlap and real PCM comparison remain subsequent
dependencies.
