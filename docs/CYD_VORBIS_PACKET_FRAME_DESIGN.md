# Exact Vorbis packet front end

`native_vorbis_packet_frame` composes the already qualified exact packet stages:
mode/window prefix, channel floors, residue and inverse coupling. It borrows a
live immutable setup, including the view returned by the setup owner. It does
not expand float tables, allocate memory or select a production decoder.

The [API](../idf/components/native_vorbis_packet_frame/include/native_vorbis_packet_frame.h)
and [implementation](../idf/components/native_vorbis_packet_frame/packet_frame.c)
preserve original packed VQ terms and exact residue limbs through this boundary.
Floor curve synthesis/multiplication, inverse transform, window/overlap and PCM
remain later stages. An implicit zero residue is not a final audio-silence or
active floor0 pole policy.

## Decode order and packet endings

[Vorbis I 4.3.1–4.3.5](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
requires floors in channel order, residue in submap order, and inverse coupling
in reverse pair order. The coordinator retains the original floor-presence
flags. The existing residue layer performs forward nonzero propagation once;
an absent floor can need residue after coupling without becoming a present floor.

Prefix truncation is an error. Result metadata and cursor position remain
unchanged, with sticky EOP set. Floor EOP instead returns the whole-frame zero
case required by section4.3.2: all published floor presence/counts/offsets become
zero, all numeric pools are empty, and residue/coupling are skipped. Every
channel record is initialized before any floor read, including unreached channels.
The last successfully read field/word position is retained. This result still
needs later overlap handling; it does not erase a previous frame's output tail.

Normal all-unused floors also need no spectrum/classification buffers, without
claiming floor EOP. A present floor with a zero numeric residue grid still
consumes mandatory class/stage words. Residue EOP preserves every completed VQ
contribution and applies inverse coupling to that exact partial result. An
active empty entropy book remains INVALID, not an invented EOP or zero vector.
Floor0 order0 consumes its required VQ word but publishes zero coefficients.

## Capacities and lifetimes

Measurement uses a temporary prefix cursor and returns conservative capacities
for the selected mode: channel records, configured floor0 orders/floor1 posts,
and an all-present residue/classification bound. These are maximum reservations,
not measured packet RAM. Decode remeasures residue using actual original floor
flags; the larger conservative classification count is not passed to decode.

Affine coefficients and raw floor1 Y values occupy separate compact pools.
Each channel record carries its type and pool offset. Unused records expose no
values; a whole-frame zero result also resets every offset. The residue view
contains exact two's-complement limbs on the existing common dyadic grid.
Configured counts retain their full format range; caller capacity and object
addressability remain resource outcomes, with no new stream-format cap.

Workspace is scratch. Its contents may change on failure and all previous
frame borrows expire on any attempted reuse. Only a successful result can be
consumed; its workspace and setup owner remain live and immutable until then.
The result descriptor/cursor publish only on success, apart from sticky prefix
EOP. Input bytes, setup, cursor, result and workspace arrays do not overlap;
callers serialize access. No global mutable state or task is introduced.

An eventual floor EOP can still need earlier floor-value scratch: a nonzero
amplitude/flag triggers the lower stage's capacity check before a later EOP is
discovered. The API therefore promises that some packets can use less than the
conservative bound, not that every truncated packet needs no floor scratch.

## Qualification

The [checkpoint](../tests/results/vorbis-packet-frame-20261026/CHECKPOINT.md)
retains two complete sanitized host runs of 1,311 scenarios. All434 original
packets remain unmodified; synthetic cases and exhaustive cuts exercise mixed
submaps, coupling chains, actual-versus-conservative capacities, zero grids,
order0, empty books and the three distinct EOP regions. Independent Python
parsers and exact rational reconstruction compare every field and limb.

Both captures match411520 residue words after inverse coupling,2769 affine
values and2224 raw Y values. There are384 floor-EOP and420 residue-EOP results,
3332 actual-pool capacity refusals and hash-identical full retries. ASan/UBSan
emit no diagnostics. Fixture cleanup was made nonrecursive with explicit
single-level snapshot invariants; both earlier traces and all original checks
remain preserved. A remaining analyzer path assumes inconsistent reciprocal
links in the fixture's allocator list; the checkpoint records the proof and
the raw diagnostic. No suppression or numerical relaxation was added.

GCC source-only compilation produces C and C++ header-probe ELF32 objects for
ESP32/LX6 and ESP32-C3/RV32IMC. Both report static own-function frames of464 B
for measure and544 B for decode with `-O2 -fno-inline`. This is not a whole call
chain, SDK application, target execution or task-stack high-water measurement.
The new coordinator has zero Clang warnings; inherited/helper diagnostics are
recorded separately.

Neither radio application selects this component. Full native qualification,
resource/CPU measurements, numeric-route selection, later synthesis and actual
audio-task wiring remain open. Existing deferred scopes were not resumed.
