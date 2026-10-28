# Carry complete window products through S16 rounding

The [exact-window representation](CYD_VORBIS_EXACT_WINDOW_DESIGN.md) retains
up to 106 bits of a binary64 sample times a window factor. Narrowing that
product to the existing two-binary64 PCM API would discard its tail again.
The new [API](../idf/components/native_vorbis_pcm_exact/include/native_vorbis_pcm_exact.h)
accepts both complete products and computes

```
clamp_S16(roundTiesToEven((a*2^(Ea+sa) + b*2^(Eb+sb))*32768))
```

Each magnitude is canonical odd and at most 106 bits; zero has all fields
zero. Both signed64 base scales and every product shift in [-2148,1023] are
accepted. Any canonical magnitude is valid, without a factorization proof.
Noncanonical caller objects are INVALID; this is an internal representation
contract, not a new restriction on encoded Vorbis streams. Bool fields are
ordinary well-formed C objects. Sources are immutable and output is disjoint.

## Exact comparison at the final boundary

Normalize each nonzero source magnitude to 106 bits, retaining its scale in
a signed two-word exponent represented by unsigned64 words. The PCM factor
adds 15 and normalization subtracts at most 105, so the total source offset
is bounded by [-2238,1038]. No offset is added into a signed64 base, and no
unbounded exponent difference is converted into a shift count.

Compare the exact sum to a half-integer boundary by adding the negated boundary
as a third normalized 106-bit term. Sort by exponent. A gap of at least two
between the largest and second term makes the largest magnitude strictly
larger than the sum of the smaller two. Otherwise merge the leading pair at
a distance of zero or one, retaining at most 108 bits in two unsigned words.
The remaining signed two-term comparison orders exact top positions, aligning
only when those positions match; that alignment is bounded by the widths.
Exact cancellation exposes the remaining term unchanged. All magnitude
addition, subtraction and carries remain unsigned and bounded.

Sixteen half-grid comparisons locate the nearest signed16 value. Equality
selects the even adjacent integer, including negative boundaries; saturation
occurs after the complete sum is considered. No heap, VLA, __int128, floating
arithmetic, overflowing conversion, per-term clipping or rounding-mode
dependency is introduced. Full 106-bit tails matter: for a genuine product
`(1+2^-52)*(1-2^-53)` at base scale -16, final S16 is 1, while prematurely
rounding the product to binary64 produces an exact half tie and S16 zero.

## Logical slices connect the exact window to PCM

For actual adjacent sizes A and B, the ready interval has (A+B)/4 samples.
Read the previous full window starting at A/2 and the current full window at
(B-A)/4. Previous slopes are (A,min(A,B)); current slopes are (min(A,B),B).
Unused outer slopes do not affect this ready interval. Negative current
indices for a long-to-short transition and previous indices beyond a short
block are exact zero. Int32 origin plus uint32 index is evaluated in int64,
whose range safely covers all possible sums of those argument types.
In C, form the current origin as `((int32_t)B-(int32_t)A)/4` for legal block
sizes. Subtracting uint32 sizes before the cast would wrap on long-to-short
transitions and silently select an unrelated zero region.

The adapter requires successful immutable exact-window views even for count0.
It checks output extents/capacity and both view descriptors, then every selected
read before writing any sample. Under the unchanged-view contract, repeated
reads and scalar conversion in the publication pass cannot fail. Every returned
error therefore leaves output and all inputs unchanged. No block-sized product
array is allocated. The view's existing input/lookup borrows remain alive and
immutable throughout both passes; caller use is serialized.

This adapter does not create a history owner, infer priming/reset decisions,
trim granules, reorder channels or invent a terminal packet. It executes the
new exact-window/106-bit path, distinct from the deferred controller that
would have composed the older rounded overlap and two-binary64 PCM APIs.
Those old APIs, captures and deferred record remain unchanged.

Complete decoder qualification still needs original31 PCM/bound2/all14
relations, preceding gain/IMDCT precision and wider paths, granule/output/raw
integration, resource/performance/native tests and physical acceptance.
The component is not selected by production; task affinities and backends remain.

## Qualification

The [checkpoint](../tests/results/vorbis-pcm-exact-20261028/CHECKPOINT.md) retains
all 478,388 previous PCM outputs and adds 208,411 scalar cases, including every
width1..106, genuine 106-bit midpoint/cancellation tails and 432 direct wide
carry/merge cases. All 864 saved adjacent-block data rows produce 598,992 new
exact adapter outputs and 1,197,984 complete window terms; every one of the
17,962 prior underflow witness identities remains present before addition.
Two independent Fraction/symbolic anchor sets pass 2,033 checks each.

ASan/UBSan, 4,178 refusals / 62,379,152 guard checks and 14 damaged-capture
controls pass. Both new C units have zero Clang warnings/errors and compile
with C/C++ public headers for LX6/RV32IMC. These source objects and host tests
are not native runtime, full task-stack or real-time measurements. The exact
S16 boundary still needs a decoder history owner and full packet integration.
