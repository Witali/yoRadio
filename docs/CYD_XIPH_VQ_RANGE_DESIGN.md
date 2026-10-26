# Xiph VQ range: measured gap and integration requirements

Status: the range audit and exact-quantization comparison are complete. The
decoder correction and radio integration remain open. This document does not
change the pinned upstream source, the resource port, or either production
application's component selection.

## Specified values and current behavior

[Vorbis I 9.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
defines a packed codebook value as a signed 21-bit mantissa multiplied by
`2^(exponent-788)`, with a ten-bit unsigned exponent. A nonzero magnitude ranges
from `2^-788` through `(2^21-1)*2^235`. This helper does not specify an exponent
clamp. Sections 3.2/3.3 define the lookup1/lookup2 reconstruction and sequence
recurrence.

The pinned [Xiph 1.3.7 implementation](https://github.com/xiph/vorbis/blob/v1.3.7/lib/sharedbook.c)
clamps the adjusted exponent to `[-63,63]` before its `float` return. The current
resource port inherits that arithmetic byte for byte. Concrete scalar witnesses
are:

| Packed word | Specification | Current Xiph |
| --- | --- | --- |
| `0x5a800001` | `2^-64` | `2^-63` |
| `0x6a800001` | `2^64` | `2^63` |
| `0x00000001` | `2^-788` | `2^-63` |

The first two specified values are exactly representable in binary32. Their
difference is therefore not an unavoidable rounding at a float boundary.
Removing the clamp alone is incomplete: a table with minimum `-2^128`, delta
`2^128` and multiplicand1 has exact value0, but converting the two terms to
binary32 first would produce infinities before cancellation. These are table
arithmetic witnesses; this audit does not synthesize or qualify whole streams.

## Reproducible comparison

The [checkpoint](../tests/results/vorbis-xiph-vq-range-20261026/CHECKPOINT.md)
records the actual sanitizer capture, exact rational oracle, raw diagnostics,
the initial compile failure, and the final classified result:

- 14336 scalar words: every exponent and sign, seven selected mantissas,
  including all2048 signed/exponent zero words.
- 8225 direct lookup tables and271626 component values, both lookup types,
  sequence on/off, full dimension65535, and a lookup1 leftover entry.
- All271626 owned affine results match the independent integer recurrence.
- 10764 scalar values differ from the specified rational;1682 of those
  specified rationals are exactly representable in binary32.
- At table level,8201 exact values change because of the field clamp;
  132024 actual float values differ from the exact recurrence using clamped
  fields. These counts overlap. The latter includes ordinary sequence rounding
  and is not independently a claim of decoder nonconformance.

The capture calls the actual generated `_float32_unpack` and dense
`_book_unquantize` functions. It also calls the existing
`native_vorbis_quantization_vector`, retaining original packed words and integer
multipliers. Python reconstructs the exact dyadic values using integers and
`Fraction`; binary32 boundary classification rounds the rational directly with
ties to even, without a binary64 intermediate. Fourteen self-test controls cover
normal/subnormal/overflow/tie boundaries and exact cancellation.

This is not exhaustive over all32-bit packed words. Quantization width is16;
the sparse-map argument isNULL. Multi-entry direct tables deliberately have
dummy all-one length lists, so they are not complete valid Huffman codebooks.
No header, packet, floor, DSP, native target, PCM or radio path executes here.
Ordinary31 PCM qualification remains the earlier independent checkpoint; it was
not rerun because no implementation changed.

## Existing exact components to reuse

For sequence component k, the exact value is
`minimum*(k+1) + delta*sum(multiplicands[0..k])`; without sequence the multipliers
are1 and the current multiplicand. The full format bounds the minimum multiplier
by65535 and the delta multiplier by`65535^2`. A packed mantissa times either
multiplier is below`2^53`; each individual term is exactly representable in
binary64. Adding the terms can still lose a small residual, so a double-valued
table alone is not an exact representation.

- [quant.c](../idf/components/native_vorbis_numeric/quant.c) already retains
  the two original words and the two unsigned integer multipliers. This audit
  proves its recurrence against the Xiph-table cases without another parser or
  quantizer implementation.
- [setup.c](../idf/components/native_vorbis_numeric/setup.c) retains the
  configured graph and original codebook/multiplicand views before expansion.
- [residue.c](../idf/components/native_vorbis_numeric/residue.c) preserves
  residue addition and inverse coupling on a common exact dyadic grid. Its
  maximum34 limbs derives from encoded ranges and eight passes, rather than an
  added format cap. Storage and addressability remain separate resource limits.
- The existing affine floor0 API retains the original LSP terms through phase
  reduction. Its presence does not close the separately deferred Xiph floor0
  amplitude scope or qualify a new decoder integration.

There is no supported lookup1 `indexdiv` overflow finding. For positive legal
dimensions, every product is at most `quantvals^dimensions <= entries <= 0xffffff`.
No speculative integer fix was applied.

## Remaining implementation sequence

1. The [exact setup owner](CYD_VORBIS_SETUP_OWNER_DESIGN.md) now provides the
   immutable lifetime primitive using the existing parser. Host qualification
   retains raw words, actual multiplicands and original active-entry indexes;
   [native preparation remains incomplete](CYD_VORBIS_SETUP_OWNER_TARGET_DEFERRED_20261026.md).
   Qualify its target resource/lifetime behavior and connect it before Xiph
   initialization consumes static books. Full measured requirements stay intact.
2. Define selection of the complete numeric route before float expansion.
   Checking only whether packed exponents fit`[-63,63]` is insufficient to
   prove a final PCM error bound. An exceptional table must not be converted
   back to float before residue addition or coupling. Preserve the ordinary
   Xiph path's measured bit patterns while qualifying the selection contract.
3. Connect existing exact VQ, floor-packet, residue and coupling views with
   transactional capacity/OOM cleanup and complete packet-end semantics.
   Qualify original input consumption, unused tails, sparse indexes, recovery
   and concurrent stream ownership. Deferred gates remain separate.
4. Specify the floor-to-IMDCT representation, scaling, rounding and exceptional
   arithmetic contract. Wide floor0 gains and cancellation across bins mean
   that merely choosing double for`valuelist` or clipping before the transform
   does not solve this boundary. Reuse Xiph's transform if it can satisfy the
   contract; a new transform is not justified by this audit.
5. Verify final unshifted PCM against the original31 cases and their fixed
   bound2/all14 relations, plus independent range/cancellation references.
   Then qualify actual Xtensa stack/heap/watchdog and the audio-task integration
   for all three outputs before production selection.

No maximum packed exponent, valid format restriction, relaxed PCM tolerance,
new transform, or default decoder switch was introduced. Existing deferred
scopes and the board acceptance requirements remain open.
