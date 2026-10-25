# Floor0 arithmetic for an owned wide synthesis path

This component implements the polynomial and amplitude equations from
[Vorbis I 6.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html), with the
straightforward [Xiph v1.3.7 LSP implementation](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/lsp.c)
as an independent source of the parity equations. It is not connected to either
radio application's component list or decoder registration. No vendor callback,
private handle, codebook consumer, packet parser or PCM conversion is replaced.

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
and values outside `[0,pi]`. It retains 1152 fractional phase bits and uses a
2304-bit `2/pi` constant; the bin phase is an integer division of `2*bin/map`.
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

The complete correction still needs owned raw setup, dequantization, residue,
coupling, IMDCT and overlap with adequate precision and
range. It must preserve retry/reset/EOF and public registration contracts and
be qualified against independent reference PCM on both targets. Inserting this
module into the existing int32/Q24 inverse2 callback would not recover
information already lost elsewhere. See the
[remaining floor0 requirements](../../../docs/CYD_VORBIS_FLOOR0_REMAINING.md).

ESP32 and C3 have different arithmetic costs. Software numerical checks and
emulator execution do not measure physical audio throughput, stack/heap
margins, Wi-Fi/TLS coexistence or prolonged radio playback. Production cores,
priorities, stacks, display configuration and audio backends are unchanged.
