# Owned Vorbis codebooks and wide floor0 arithmetic

This component implements the polynomial and amplitude equations from
[Vorbis I 6.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html), with the
straightforward [Xiph v1.3.7 LSP implementation](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/lsp.c)
as an independent source of the parity equations. It is not connected to either
radio application's component list or decoder registration. No vendor callback,
private handle, existing decoder state or PCM conversion is replaced.

## Complete codebooks and packet reads

The [codebook API](include/native_vorbis_codebook.h) parses a complete descriptor
from its public sync field through ordered/unordered/sparse codeword lengths
and quantization values. A fixed33-slot frontier assigns the lowest unused
lexical prefix in original entry order; lengths are not sorted before assignment.
Caller-owned active words retain original sparse indexes and are sorted together
for binary-search decoding. Materialization validates the full packet and both
required capacities before writing. There is no heap or entries-sized scratch
array inside the component.

The sticky-EOP packet cursor reads integers0..64 bits. A decoder can consume a
complete short word at packet end without demanding maximum-length lookahead.
The2015 singleton erratum requires length1 and one consumed bit, accepting0/1.
Empty descriptors follow the public Xiph setup behavior but provide no symbol.
For transported Vorbis packets the valid extent includes every final octet and
its padding; shorter explicit extents support controlled/internal spans.

Audio codewords can feed exact VQ prefixes or complete floor0 LSP reconstruction,
including cross-vector carry and a partial final vector. Aggregate failures
preserve output and cursor position; truncation sets sticky EOP. Capacity retry
consumes no audio. The [design](../../../docs/VORBIS_CODEBOOK_DESIGN.md) states
the immutable-view, storage, range, empty-book and dimension0 contracts.

This completes the per-codebook layer. The complete setup parser below now
provides the other descriptors; floor/residue packet handling, synthesis and
registered raw lifetime integration remain required for production use.

The [codebook checkpoint](../../../tests/results/vorbis-codebook-20261025/CHECKPOINT.md)
retains 382 sanitized host cases/719 API controls, 318030 setup cuts and 31580
payload cuts. Separate exact comparison accepts all 400 SDK/QEMU cases,
including 26990 affine values. The parser and quantization have zero warnings
in separate cross-target Clang-Tidy analyses; the checkpoint records the
remaining bounded floor0 warning and the finite scope of every check.
A separate host supplement adds 140 malformed fixtures/290 guarded assertions
and checks the complete 16-bit dimension/24-bit sparse-entry boundary without
allocating a declared-entry-sized row table.

## Identification, complete setup and audio prefix

The [setup API](include/native_vorbis_setup.h) reads complete type1/type5 header
packets, retains all signed bitrate hint bit patterns and the full positive
uint32 sample rate, and validates the configured graph. It supports 256 books,
64 time/floor/residue/mapping/mode descriptors, both floors, all three residues
and mapping0 with up to 256 coupling pairs. It validates scalar/VQ book contexts,
floor1's normative 65 unique posts, bounded integer classification capacity,
residue vector dimensions and every declared link/reserved field.

Four caller-owned arrays hold book views, active Huffman words, original
multiplicands and compact uint32 configuration records. Only actual descriptor
counts consume configuration space. The conservative full-format pool bound is
112960 words; it may exceed a target's available RAM. Measurement preserves full
requirements, while materialization distinguishes invalid input, unaddressable
objects and capacity shortage before any write. There is no expanded residue
classification map or maximum-sized descriptor union.

Typed getters expose floor, class, residue, mapping and mode views. Audio-prefix
decode reads packet type, mode and long-block window flags transactionally;
short blocks read no window flags and a single mode needs zero mode bits.
The [setup design](../../../docs/VORBIS_SETUP_DESIGN.md) documents the exact
representation, immutable lifetimes, scope and consuming-context decisions.

Unsigned floor0 order/rate/Bark-map metadata, including zero, is preserved here;
active zero-domain curve behavior is a separate unresolved synthesis requirement.
This differs from Xiph's header-time rejection and does not invent a constant
floor. A mapping's ignored time byte may be nonzero; a reversed/oversized residue
range remains metadata for later empty-range/clamping behavior. Header ordering,
comment handling and raw ownership remain part of the future decoder open path.

The [setup checkpoint](../../../tests/results/vorbis-setup-20261025/CHECKPOINT.md)
retains all 300 sanitized host rows/60 controls and every header/prefix cutoff,
including 43 malformed inputs and two retained encoder-header cases. Separate
exact comparison accepts all 400 SDK/QEMU rows, 1310 book configurations and
42580 configuration words. Setup/codebook/quantization have zero cross-target
Clang-Tidy warnings; the existing bounded floor0 warning remains documented.

## Numerical contract

The [API](include/native_vorbis_floor0.h) separates four operations:

1. Compute the polynomial denominator from supplied binary64 cosine
   coefficients and `w`, all in `[-2,2]`, for orders 1 through 255.
2. Evaluate amplitude and gain from a nonnegative scaled denominator. This
   entry point also accepts a denominator from the original-angle path,
   without first rounding angles to cosines.
3. Provide separate Bark mapping and approximate libm cosine helpers.
4. Evaluate the denominator and gain directly from finite binary64 LSP angles
   at mathematical `theta = pi * bin / bark_map_size`.

Products, squares and their positive sum use normalized mantissas and signed
32-bit exponents. Empty products equal one, zero factors stay zero, and a
nonzero tiny product is not converted to binary64 zero. The odd polynomial
factor `4-w*w` is evaluated as `(2-w)*(2+w)` to avoid cancellation in the square.
The representation retains the range of every nonzero product of up to 255
binary64 differences. It does not make ordinary floating rounding exact.

The output is a **scaled logarithm**:
`log2(linear_gain) = mantissa * 2^exponent`. Even that logarithm can exceed
ordinary binary64 range for a very small polynomial denominator. Keeping its
scale avoids premature infinity or a unity ceiling. The module does not convert
this result to a fixed spectrum, linear gain or PCM.

Raw amplitude retains the full 0..63-bit field and the full 0..255 offset.
Division precedes multiplication, so no uint64 product overflows and no Q4
truncation occurs. Near a unit denominator, a deficit/square-root identity
preserves tiny differences that would disappear if `raw/max` rounded to one
before subtraction. Binary64 rounding remains; exact rational output for every
wide amplitude is not promised. The specification's literal `0.11512925` is
used, rather than silently replacing it with a different exponential constant.

An absent floor is distinct from unity gain. Exact zero denominators produce
explicit pole/indeterminate kinds; these are arithmetic results, not invented
PCM or stream-error policies. No epsilon classifies a near-root as a pole.
Invalid arguments leave outputs unchanged. Functions use caller-owned storage,
no heap, no variable-length arrays and no mutable global state.

## Precision boundaries and integration

Cosine preparation is explicitly approximate. For example, a tiny nonzero
angle can round `2*cos(angle)` to exactly 2 and lose information. Exact
coefficient-domain checks cannot qualify the original angle-domain curve. The
original-angle APIs avoid this conversion: they form cosine differences as
products of half-angle sines, retaining their scale. A fixed-size integer phase
reduction supports all finite binary64 angles, including subnormals, negatives
and values outside `[0,pi]`. It now retains 2304 fractional phase bits and uses a
4096-bit `2/pi` constant; the bin phase is an integer division of `2*bin/map`.
No rounded binary64 multiple of pi is subtracted. Small sines stay scaled, so
halving a subnormal cannot silently turn an LSP into zero. This is still rounded
numerical arithmetic, not an exact symbolic curve.

Bark mapping uses floating half-rate for
odd declared rates, and exact cardinal cosine points are retained for Bark
indices with cosine 0 or ±1/2.

The [original-angle checkpoint](../../../tests/results/vorbis-floor0-angles-20261025/CHECKPOINT.md)
retains the actual host and native results. Denominator acceptance uses relative
error `2e-12`; composed log2 gain uses absolute error
`2e-12 * max(1, abs(reference))`. Near-zero gain relative errors are retained
and can be large; the tests do not promise a relative bound or an exact sign
through an approximate denominator. Very large scaled logarithms likewise do
not imply a universal absolute error bound. Exact supplied-D amplitude tests
remain a separate layer.

The [quantization API](include/native_vorbis_quant.h) now preserves original
packed minimum/delta and integer multiplicands, reconstructing exact symbolic
VQ values and floor0 LSP carries without an early floating sum. Its affine floor
entry points reduce the two exact terms separately. It supports lazy vector
prefixes and single components with caller-owned storage and transactional
capacity/error behavior. The [quantization design](../../../docs/VORBIS_QUANTIZATION_DESIGN.md)
defines the field/range/ownership boundary. Complete descriptors and their audio
codewords now enter through the codebook API, and the setup parser supplies
the complete configured graph. Full floor/residue audio parsing remains.

The [quantization checkpoint](../../../tests/results/vorbis-quantization-20261025/CHECKPOINT.md)
retains actual 6572 host cases/79834 exact values and 200 SDK/QEMU cases per
architecture. Separate replay accepts all 15036 native affine values and 184
floor comparisons. Both earlier host binary output streams remain identical.
The enlarged phase grid has a separate exact-rational certificate; complete
libm/codec/PCM/physical qualification remains outside that proof.

The complete correction still needs header-order/comment handling, floor/residue
audio decoding, coupling, IMDCT and overlap with adequate precision and
range. It must preserve retry/reset/EOF and public registration contracts and
be qualified against independent reference PCM on both targets. Inserting this
module into the existing int32/Q24 inverse2 callback would not recover
information already lost elsewhere. See the
[remaining floor0 requirements](../../../docs/CYD_VORBIS_FLOOR0_REMAINING.md).

ESP32 and C3 have different arithmetic costs. Software numerical checks and
emulator execution do not measure physical audio throughput, stack/heap
margins, Wi-Fi/TLS coexistence or prolonged radio playback. Production cores,
priorities, stacks, display configuration and audio backends are unchanged.
