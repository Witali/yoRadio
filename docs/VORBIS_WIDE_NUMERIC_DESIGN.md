# Owned wide Vorbis synthesis: numerical boundary

## Reuse-first decision, 2026-10-25

The user approved testing a ready complete upstream decoder before continuing
custom synthesis. The [branch audit](CYD_OGG_VORBIS_BRANCH_AUDIT_20261025.md)
confirms that basic Ogg/Vorbis playback is already implemented through the
Espressif package. A complete source-buildable Xiph port is an investigation
into the retained failures, not a prerequisite for adding that existing feature.

The approved experiment pins the upstream source and dependencies, compiles an
essentially unchanged decode path for ESP32, adapts only public input/output
and platform integration, and runs the original failing corpus. Its PCM, memory
and target execution evidence is recorded below. Emulator results do not establish
physical real-time performance. Preserve the existing tests and owned numeric
components as diagnostics; do not add a new custom IMDCT or synthesis stage
until the ready implementation has been evaluated. Any required deviations
must address a demonstrated requirement, without discarding failing cases or
weakening the declared standard/conformance criteria. Deferred scopes stay
deferred, and production selection changes require their own completed gates.

The numerical analysis below records requirements and implemented components;
it does not make a complete custom rewrite mandatory.

The [unchanged Xiph ESP32 evaluation](../tests/results/vorbis-xiph-20261025/CHECKPOINT.md)
now completes all 31 original cases, 434 audio packets and 738560 PCM bytes.
Every signed16 sample is bit-identical to the retained Xiph reference, and all
14 original relations pass at the unchanged bound2 (observed maximum0).
Only IDF build/type configuration and the public raw fixture were adapted;
upstream C/header arithmetic remains byte-identical to the pinned releases.
This finite gate is complete. Continue with allocation-failure recovery,
large-book scratch/stack bounds, remaining format/range coverage and production
integration gates. Unchecked realloc and entry-sized stack scratch are concrete
open source-review findings. Neither the isolated QEMU resource observations
nor this corpus qualifies physical performance or universal standard coverage.
Do not resume custom IMDCT/synthesis merely because the earlier repair failed.

Full floor0 correctness requires a precision and range design for the complete
synthesis path. The public low-memory implementation stores Q4 amplitude and
Q24 LSP values; the current bridge delegates residue, coupling, IMDCT, overlap
and PCM conversion to the pinned archive. A new inverse2 callback cannot
recover information already narrowed before or after that callback. The
[existing remaining-work note](CYD_VORBIS_FLOOR0_REMAINING.md) records these
limits without inferring opaque backend behavior.

[Vorbis I 4.3.6](https://xiph.org/vorbis/doc/Vorbis_I_spec.html) explicitly
discusses roughly 48-bit residue dynamics and an effective 48-by-24-bit floor
product. Its movable binary point option motivates the owned scaled numerical
core. The complete implementation must preserve sufficient precision through
the transform and overlap; early clipping of a spectral bin is not a substitute
for final PCM conversion.

## First implemented component

[native_vorbis_numeric](../idf/components/native_vorbis_numeric/README.md)
provides independent floor0 polynomial/gain arithmetic. Its
[public API](../idf/components/native_vorbis_numeric/include/native_vorbis_floor0.h)
has no vendor structures or callbacks. It is not added to either production
application's component list.

`native_vorbis_floor0_denominator()` evaluates the even/odd polynomial using
normalized binary64 mantissas and signed32 exponents. The products cannot
underflow merely because the order is large, and their nonnegative sum avoids
cancellation. `native_vorbis_floor0_gain_from_denominator()` preserves the
scaled denominator through amplitude scaling and square root, returning a
scaled **log2 gain**. There is no fixed Q24 output or unity ceiling. The full
0..63-bit raw amplitude and 0..255 offset are retained; a stable deficit formula
handles wide amplitude differences near unity. Ordinary binary64 rounding
remains, and poles/indeterminate arithmetic have explicit result kinds rather
than an invented PCM policy.

The exact supplied-coefficient domain and the approximate cosine/Bark helpers
are separate test layers. In particular, a tiny nonzero angle can round
`2*cos(angle)` to exactly 2. The scaled-denominator entry point deliberately
allows the original-angle implementation to bypass that conversion.
Coefficient-domain accuracy does not prove angle-domain or complete decoded
PCM accuracy.

The original-angle entry points now compute the same polynomial directly at
`theta=pi*bin/map`. The identity
`abs(2*cos(theta)-2*cos(phi)) = 4*abs(sin((phi+theta)/2)*sin((phi-theta)/2))`
avoids subtracting rounded cosines. Both endpoint factors use corresponding
half-angle squares. Phase reduction uses exact integer products/division,
2304 fractional bits and a 4096-bit `2/pi` constant; all finite binary64 LSPs
are accepted. Negative, tiny and very large angles do not require a floating
periodic remainder. A small sine remains scaled instead of underflowing during
halving or squaring. This solves a numerical layer; preserving the original
setup/dequantization inputs and propagating the floor through wide synthesis
remain separate requirements.

The [angle checkpoint](../tests/results/vorbis-floor0-angles-20261025/CHECKPOINT.md)
retains 2376 sanitized host cases, 28 metadata controls and 200 SDK/QEMU cases
per architecture. Its oracle independently derives pi with directed Chudnovsky
intervals and evaluates the direct cosine polynomial at Decimal800..1184.
A separate exact-rational Machin/continued-fraction certificate verifies all
72 constant limbs and the nonzero phase separation; it makes no libm/complete
floating error claim. Separate replay accepts every host and all 400 native
results computed from the supplied angles under the predeclared bounds. The preceding
60541-operation coefficient output is byte-identical. These checks establish
the standalone numerical layer, not setup preservation, wide synthesis or PCM.
Those historical results used the smaller preceding phase grid; the newer grid
also supports exact affine VQ values described below.

The [owned quantization section and lazy VQ/LSP reconstruction](VORBIS_QUANTIZATION_DESIGN.md)
retain original packed minimum/delta words and integer multipliers. The affine
floor APIs reduce both individually exact terms separately, before any floating
sum. This preserves small terms and cancellation across the packed exponent
range. The [owned codebook layer](VORBIS_CODEBOOK_DESIGN.md) now parses complete
descriptors, decodes their audio words and feeds exact VQ/LSP reconstruction.
The [complete setup graph and audio prefix](VORBIS_SETUP_DESIGN.md) now retain
all descriptors and select packet modes/windows. The
[floor-packet layer](VORBIS_FLOOR_PACKET_DESIGN.md) and
[exact residue/coupling layer](VORBIS_RESIDUE_DESIGN.md) now decode those audio
portions separately. They still require frame orchestration, floor application
and synthesis before replacing a production decoder.
Raw zero-valued floor0 metadata is retained by setup; active arithmetic
for those domains remains an explicit subsequent requirement.

## Required continuation through public raw operations

The future wider decoder should own its state behind the public raw decoder
operation table, rather than extending an opaque vendor handle. Public
identification/setup bytes and raw audio packet bytes are sufficient inputs.
The synthesis implementation is selected at open and retained for that
handle's lifetime, including mixed floor0/floor1 mappings. Switching isolated
packets between implementations would leave incompatible overlap histories.

The remaining implementation must:

- Compose the existing prefix/floor/residue/coupling components into a frame
  decoder, retaining amplitude metadata, partial final vectors and the distinct
  nominal floor/residue EOP behavior across channels and submaps.
- Connect the exact shared-grid residue/coupling output to floor application
  without premature int32/Q8 narrowing or cancellation loss.
- Feed the original-angle floor APIs without narrowing setup/dequantized LSPs,
  preserving range through floor multiplication, IMDCT and overlap.
- Convert and clip only at the requested final PCM boundary.
- Keep capacity refusals before state advancement and preserve the registered
  open/process/info/reset/close, EOF, generation and ownership contracts.
- Verify allocation failure/recovery and lifetime behavior, then integrate with
  existing audio owners without changing their core affinity or priorities.

The complete original/equivalent corpus and existing independent reference
outputs remain required. Tests for the numerical component do not close G6 or
requalify the historical wide/sequence1/floor0 PCM failures. The other deferred
work items remain deferred; this component changes none of their sources.

## Hardware and resource qualification

ESP32 and C3 have different arithmetic costs, and double arithmetic needs its
own target measurements. Caller-owned workspaces and constant-size numerical
locals avoid per-bin allocation, but do not prove that the entire wider decoder
fits alongside codebooks, network/TLS, display and audio buffers. Separate
target compiler frames, complete task stack/heap measurements and actual audio
throughput are distinct evidence. Emulator execution cannot establish physical
real-time behavior or Wi-Fi/TLS coexistence.

The CYD stream owner remains on core0 and decode/output on core1. C3 remains
single-core. Display/pins, USB/reset behavior and all three CYD audio backends
retain their existing implementations. Final all-backend builds and physical
acceptance remain required after the full source set is ready.
