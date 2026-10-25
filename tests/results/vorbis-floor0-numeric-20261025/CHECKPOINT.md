# Owned scaled floor0 numerical core, 2026-10-25

The new [component](../../../idf/components/native_vorbis_numeric/README.md)
implements the even/odd polynomial and amplitude equations in
[Vorbis I 6.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html). Products retain
normalized mantissas and separate exponents, and the result is a scaled
**log2 gain**. There is no unity ceiling, fixed Q24 spectrum or premature
conversion to ordinary linear gain. Raw amplitude metadata retains all63 bits,
with a stable deficit identity near unity. The separate scaled-denominator
entry point permits a later stable original-angle path to bypass cosine
rounding. The component remains outside both radio application component lists.

## Actual numerical checks

The host campaign passes60541 operations with ASan/UBSan, including60471
numerical comparisons and49 metadata/output-preservation controls. It compiles
the complete actual C module and public header. All168 retained owned unit
inputs are included as58368 scalar bins; these are mathematical inputs, not
new carrier, raw-decoder or reference-PCM qualification.

The independent oracle uses Decimal120 direct products and square roots,
rather than the component's scaled-product implementation. The policy is fixed
before component measurement:

| Layer | Acceptance |
| --- | --- |
| Supplied binary64 coefficient denominator | relative error ≤2e-12 |
| Scaled log2 gain | absolute error ≤2e-12 × max(1, absolute expected value) |
| 63-bit amplitude deficit-one at D=1 | negative, nonzero, relative error ≤2e-12 |
| Approximate cosine helpers | absolute error ≤4e-15 |
| Host Bark map | every integer bin equal |

All60541 operations are measured; no numerical rejection or nonmeasurement
error is omitted from the result. Maximum host denominator relative error is
2.685e-15; maximum gain relative error, including near-zero cases, is2.0491e-13.
The full report also retains absolute errors for extremely large scaled
logarithms; the policy is not a universal absolute2e-12 bound. Host approximation
checks cover1145 cosine values and25542 exact Bark integer bins.
Host report SHA256:
`8fa58dd5520887ce1bedb63ebd01e175e0a7b182908bf64fd729a86b9903539a`.
Actual host terminal `0e4f96` exits0, including all4 owned Linux commands and
confirmed session/child/process-group cleanup.

Both native whole-component captures complete327 cases,347 events and16 finite
API groups. All9 commands and the SDK child complete normally, with0 compiler
warnings. ESP32 uses SDK6.0.2/machine94/core1; C3 uses pinnedSDK6.1/machine243/
core0; both coordinators use core0. Actual terminal chunks `89303a` and
`33c2a6` exit0. Capture reports intentionally keep numerical-qualified false:
they record guarded values, not independent mathematical acceptance.

The separate checker then regenerates every original Decimal expectation and
accepts all654 native coefficient/gain results. Its actual terminal `4c1bc7`
exits0 and its report SHA256 is
`eede6c5d8d71703cc6086d7432194721ef87ab97c10fa977cd78a2ad0fd0f9f9`.
It reuses explicitly pinned pure oracle/protocol definitions and launches no
SDK, compiler, QEMU, codec or reference-decoder process. Thirteen pure
literal-readback/event tests also pass; they are parser tests, not synthetic
mathematical or native qualification.

## Limits and continuation

The coefficient-domain calculation and approximate cosine preparation are
distinct. A tiny angle can round to a cosine coefficient2; this component does
not claim that such rounding preserves the original angle-domain curve. Native
API groups check finite helper behavior, cardinal points and bounds; they do
not independently qualify every native Bark/cosine output. No pole or
indeterminate result invents a PCM/stream policy.

The isolated compiler `.su` files report a maximum own-function frame208 bytes
on each target. This excludes callee/libm frames, complete task high-water and
physical throughput. No heap or order-sized stack allocation is introduced by
the component's source. Production task cores/priorities/stacks, display and
all three CYD audio backends are unchanged. Test images are emulator fixtures,
not production firmware hand-offs.

Stable angle evaluation, owned residue/coupling, IMDCT/overlap, final PCM and
public raw lifetime/retry/reset/integration remain required by the
[wide design](../../../docs/VORBIS_WIDE_NUMERIC_DESIGN.md). The earlier full31
PCM NONPASS is retained and is not requalified by these tests. Full floor0,
G6/G8, deferred scopes, radio/resource and physical acceptance remain open.
Saved executable/build identities do not provide complete binary semantics or
SDK dependency closure.
