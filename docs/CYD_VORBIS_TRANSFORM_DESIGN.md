# Reusing the Xiph inverse transform on a wide spectrum

The [reuse-first numerical decision](VORBIS_WIDE_NUMERIC_DESIGN.md) remains in
force. The complete unchanged Xiph decoder has already passed the original31
cases. The later [VQ range audit](CYD_XIPH_VQ_RANGE_DESIGN.md) demonstrates why
some encoded values cannot be expanded to the original float tables: packed
exponent clamping changes exactly representable values, and overflowing terms
can lose finite cancellation before residue/coupling. Exact setup, residue and
floor1 stages now preserve those inputs. Their wider transform boundary needs
an explicit representation, rather than another decode algorithm.

## Algorithm and provenance

[Vorbis I section4.3.7](https://xiph.org/vorbis/doc/Vorbis_I_spec.html) calls for
inverse MDCT after the floor/residue product. `native_vorbis_transform` reuses
the existing Xiph libvorbis1.3.7 butterfly, bitreverse and backward function
bodies, byte-for-byte. `tools/generate-vorbis-imdct64.py --check` verifies the
extracted ranges against pinned `mdct.c`, SHA256
`e32b379d7a3d9253524abae3c41c5ac2486bf166cf65996efc4e68db1b164993`.
The complete Xiph license is copied alongside the generated include.

The specialization supplies binary64 DATA_TYPE/REG_TYPE and the same three
cPI decimal constants without their float suffix. The allocating initializer,
clear and unused forward transform are not included. Caller storage replaces
lookup allocation; trigonometric expressions remain those of Xiph init, with
nearest binary64 pi and integer log2 for the eight legal powers64–8192.
The constructor's bitreverse mask and high bit use n/2-1 and n/4, identical
to the original power-of-two shifts without a variable shift-count dependency.

Orientation and normalization are:

```
time[j] = sum(spectrum[k] * cos((2*pi/N)*(j+.5+N/4)*(k+.5)))
```

There is no additional2/N or4/N factor in the backward transform. The original
lookup scale4/N belongs to its forward transform.

## One explicit rounding boundary

For each signed exact product integer S at common source exponent E, form:

```
working[k] = round_binary64(S[k] * 2^-512)   // nearest, ties to even
time_exponent = int64(E) + 512
physical_time[j] = working_time[j] * 2^time_exponent
```

The input is never converted wholesale to double before scaling. The converter
uses the absolute integer's high53 bits, guard and sticky bits, including carry
into the next exponent, then constructs the final binary64 bits by memcpy.
Negative two's-complement inputs and positive/negative midpoint ties share the
same magnitude rounding. Zero is canonical positive zero. Every source sample's
strict signed magnitude domain is checked before the first output write.

All current exact floor1 products fit at most36 words. The converter accepts
every coherent36-word signed domain up to1151 magnitude bits; actual format
bounds are smaller. Nonzero working inputs lie from2^-512 through2^639,
entirely inside binary64's normal range. Original signed32 exponents, including
their extrema, remain in int64 metadata instead of imposing a new accepted
exponent cap. A zero numeric grid uses exponent0 and materialized positive zeros.

This is an approximate binary64 transform after an exact front end, not an
exact cosine computation. The copied DAG grows by less than2^24 in the worst
case over N<=8192 before rounding: initial rotation<=2, first/generic butterfly
stages<=4 each, terminal32-butterfly<=64, bitreverse<=3 and final rotation<=2.
Even the1151-bit helper domain retains ample overflow margin below2^1024.
Cancellation can produce tiny/subnormal values or zero. It does not have a
universal relative-error or final PCM guarantee; independent normwise error
tests and the unchanged full-decoder PCM gates remain necessary.

## Storage, pointers and failure

Lookup storage is N+N/4 doubles and N/4 ints. One in-place working array has
N+8 doubles, and the original transform receives workspace+8 for both input
and output. The leading padding is part of that same allocated array. This
keeps the original pre-rotation loops' final in-7/in-8 pointers inside their
object, without changing the arithmetic or pretending separate struct arrays
are contiguous. Other upstream pointers stay inside the output or one-past.

At N8192, lookup plus workspace requires155712 bytes (binary64/int32), excluding
source limbs, setup, owners and other radio state. This is a resource cost,
not a claimed memory optimization or physical real-time result. A caller can
reuse one workspace across channels after consuming each result.

Measure preserves its result on failure. Prepare checks sizes/capacities before
writes and publishes the plan last; its provisioned lookup arrays are scratch
during construction. They must be disjoint from each other, the plan and any
arrays still borrowed by a live old plan. There is no in-place old-plan
replacement guarantee. After success plan/arrays stay alive and immutable.

Conversion and transform validate capacities, object-byte addressability and
all source domains before writes. Any returned failure preserves output,
workspace and result. The transform cannot return an error after successful
conversion. Source, lookup, workspace and descriptors are disjoint; reuse is
externally serialized. No heap, VLA, new task or changed production affinity is
introduced. Normal nearest floating arithmetic, no-fast-math and disabled
floating contraction are part of the numerical contract.

## Remaining decoder work

Arbitrary per-bin floor0 logarithmic gain spans and pole/indeterminate domains
remain a separate representation problem; this floor1 boundary does not close
them. Windowing, overlap/history, final PCM conversion, public raw ownership,
retry/reset, actual audio-task integration and full native resource gates are
also still required. The original31 PCM bound2 and all14 relations are retained.
Host/source-profile results do not requalify production or deferred scopes.

For the next floor0 boundary, even a signed64 linear exponent is insufficient
for every finite gain. With order1, positive rate/map, exact LSP phi=2^-788,
amplitude_bits1/raw1/offset1 and bin0, section6.2.3 gives
D=(1-cos(phi))^2>0 and log2(G)=(.11512925/ln(2))*(1/(1-cos(phi))-1)>2^1574.
This is finite, not a pole. Relative precision in that logarithm does not imply
relative precision after exponentiation. Retain raw amplitude/LSP provenance,
classify undefined mapping/pole domains separately, and provide an ordinary
normalized-vector route plus a wider finite fallback. Do not turn the new
floor1 grid or an int64 exponent into a floor0 format restriction. Completing
window/overlap and checking all original31 PCM cases remains the next
end-to-end milestone; it will not by itself prove this extreme range.
