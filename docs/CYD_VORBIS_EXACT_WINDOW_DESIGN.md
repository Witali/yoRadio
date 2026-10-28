# Preserve window products before PCM rounding

The existing [window](CYD_VORBIS_WINDOW_DESIGN.md) and
[overlap](CYD_VORBIS_OVERLAP_DESIGN.md) use binary64 slope products. Their
qualification retains 17,962 operands whose nonzero product underflows,
including 13,767 with a separately retained exponent of at least 1074.
For example, the minimum positive binary64 sample times a positive slope may
round to zero before its scale makes the physical contribution appreciable.
Keeping separate scales cannot recover those lost product bits.

The new [API](../idf/components/native_vorbis_window_exact/include/native_vorbis_window_exact.h)
addresses that specific representation loss. It does not change the existing
window curve or kernel, modify their qualified captures, retry the deferred
overlap/PCM controller, or choose a new production decoder.

## Integer product and symbolic scale

Decompose each finite binary64 input into sign, nonnegative integer significand
and power of two. Strip the significand's trailing zero bits so every nonzero
integer is odd. A finite sample may have any magnitude; a window factor must
be in [0,1], including either zero sign. Every NaN/Inf and invalid factor is
checked before zero shortcuts. The two significands have at most 53 bits each.
Portable 32-bit word multiplication with unsigned64 carries retains the full
product of at most 106 bits. No floating multiplication or rounding occurs.

The result stores low/high magnitude words, sign, the source's unmodified
signed64 exponent and a bounded shift. Its meaning is

```
(-1)^negative * (low + 2^64 * high) * 2^(exponent + shift)
```

The exponent sum is symbolic. The normalized sample shift is in [-1074,1023]
and the factor shift in [-1074,0]; their sum fits [-2148,1023] in signed32.
Both signed64 base endpoints therefore remain valid without adding into them.
Zero has every field zero. The magnitude is odd when nonzero, so the
representation is canonical for the supplied base scale. Full underflow and
106-bit tails remain available for later exact addition/rounding.

This exact dyadic boundary does not certify the real transcendental window,
preceding approximate IMDCT/floor arithmetic, or final PCM accuracy. It cannot
reconstruct information already lost at an earlier stage.

## Borrowed view and geometry

The existing prepared rising tables retain the nested-sine window from
[Vorbis I 4.3.1 and 4.3.8](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
The new view follows the same centers, support and descending-table traversal
as the existing owned window and pinned Xiph reference. The outside-support
region is canonical zero, the plateau multiplies by exact unity and each
slope multiplies by its actual stored binary64 coefficient. No table is
recomputed or replaced. The old reference's end-of-right-slope convention
remains, as explained in the earlier window design.

Preparation checks coherent legal-size geometry, pointer/byte extents, the
whole finite source and both whole finite [0,1] lookup arrays before publishing
the view. Failure preserves its actual bytes and every immutable input.
Successful preparation copies descriptors, borrowing only their arrays.
Original descriptors can then expire. The copied view and borrowed arrays
must remain immutable and alive through reads; caller storage is disjoint
from result/view destinations and reuse is serialized.

Reading checks the copied descriptors/index and publishes one scalar product
last. It needs no block-sized output storage, heap, VLA, lock or task. This
removes the need for a materialized window array at this boundary; it is not a
measured whole-decoder RAM/performance improvement. Existing overlap history,
PCM APIs and production task/backends are unchanged.

Next integration must carry exact products into adjacent-block addition and
the final PCM boundary. The existing two-binary64 PCM API cannot silently
accept a 106-bit product; narrowing it first would reintroduce information
loss. Full31 PCM/bound2/all14 relations, certified gain/wider transform paths,
granule/output integration, SDK/resource/runtime and physical gates remain.

## Qualification

The [checkpoint](../tests/results/vorbis-window-exact-20261028/CHECKPOINT.md)
retains all 17,962 original underflow operands, including all 13,767 with
base exponent >=1074, and proves their exact products stay nonzero. No saved
witness is deduplicated. The independent oracle uses binary64 integer ratios
and unbounded multiplication, rather than the C partial-product algorithm.
Its 64,940 scalar rows reach all finite sample exponent fields, every factor
exponent field in [0,1], both operand widths 1..53, 106-bit products and both
shift endpoints. The entire signed64 base scale remains symbolic.

All 587,520 products from 288 window shapes agree exactly with that oracle.
The 8,160 prepared coefficients preserve the existing 70-digit sine-series
bound 2e-15, with maximum error 3.3306690738754696e-16. The full corpus passes
ASan/UBSan, 10,360 refusals / 14,889,244 checks and 13 corruption controls.
Source profiles compile C/C++ for both LX6 and RV32IMC; both new C units have
zero Clang warnings/errors. Source objects are not SDK/native execution or
measurement of the decoder's RAM, task stack, or real-time performance.
