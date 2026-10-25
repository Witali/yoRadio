# Owned wide Vorbis synthesis: numerical boundary

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
allows a future stable angle implementation to bypass that conversion.
Coefficient-domain accuracy does not prove angle-domain or complete decoded
PCM accuracy.

## Required continuation through public raw operations

The future wider decoder should own its state behind the public raw decoder
operation table, rather than extending an opaque vendor handle. Public
identification/setup bytes and raw audio packet bytes are sufficient inputs.
The synthesis implementation is selected at open and retained for that
handle's lifetime, including mixed floor0/floor1 mappings. Switching isolated
packets between implementations would leave incompatible overlap histories.

The remaining implementation must:

- Preserve original quantization fields, amplitude metadata and sufficient LSP
  precision during owned setup/dequantization, including partial final vectors.
- Decode residue and inverse coupling without a premature int32/Q8 narrowing.
- Compute the floor from the original angles with stable handling near roots,
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
