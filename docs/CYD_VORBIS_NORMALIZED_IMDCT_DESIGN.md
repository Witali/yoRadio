# A binary64 entry to the reused Xiph inverse transform

The [existing transform adapter](CYD_VORBIS_TRANSFORM_DESIGN.md) accepts an exact
floor1 limb product. Another floor representation must not manufacture that
product merely to reach the same inverse transform. The public
`native_vorbis_imdct_transform_binary64` entry accepts a borrowed binary64
spectrum and its separate common exponent. It uses the same unchanged Xiph
backward/butterfly/bitreverse bodies; no second transform algorithm is added.

The entry requires exactly N/2 samples, a successful immutable plan, and the
same single N+8-double workspace. All samples must be finite and have magnitude
at most 2^639, the already proved bound of the limb converter. Source and
workspace capacities count doubles. Shapes, addressable byte extents,
capacities and every sample are validated before the first write. Every
returned failure preserves workspace and result; inputs, descriptors and lookup
arrays remain immutable. Aliased/forged storage is outside the borrow contract.

The source exponent is retained unchanged, including both signed64 endpoints.
There is no implicit exponent arithmetic, rescaling, float32 conversion or
clipping. A wholly zero spectrum, including negative zeros, produces canonical
positive zero samples while retaining the caller's exponent. Nonzero spectra
follow ordinary Xiph binary64 arithmetic and can produce signed zeros or
subnormals after cancellation. The old limb API and its existing zero policy
are unchanged.

`RANGE` reports an unsuitable internal representation, not an invalid Vorbis
stream. A caller handling a larger finite spectrum must normalize it or retain
a wider representation. This API does not resolve arbitrary floor0 gain,
mapping/pole policy or its extreme finite spans. No production decoder selection,
task/core/stack setting, deferred scope, window/overlap or PCM gate changes.

The new host suite runs both entries on 1,249 spectra obtained from the exact
limb converter. It covers all 1..1151 magnitude widths at N64 and selected
boundary widths at every other legal block size. All 301,248 resulting time
values must be bit-identical. Another 480 rows exercise full signed64 exponent
endpoints, the finite magnitude boundary and its predecessor, dense/impulse
spectra, signed zeros, normal minima, subnormals and mixed huge/tiny values.
An independent complex FFT oracle is checked against 286 retained
Decimal/rational anchors. The predeclared comparison bound is
`5e-12*L1(input) + 32*N*DBL_TRUE_MIN`. The absolute term explicitly permits
underflow for subnormal inputs; it is a test tolerance, not a universal relative
error guarantee. Normal and subnormal input errors are reported separately.

Each block size also exercises 42 atomic refusal controls: invalid/null
descriptors, shape/lookup mismatch, short capacities, byte-extent overflow,
infinities, quiet/signaling NaNs, over-bound values and retry on the unchanged
workspace. Guarded input/lookup/prefix/output-tail and descriptor snapshots
cover successful calls as well. ASan/UBSan and warnings-as-errors run over all
1,729 rows. These are host representation-entry checks, not native timing,
memory high-water or final audio qualification.

The final host run reports 5,589,927 assertions and 336 refusals, with a maximum
normal-input error/L1 of 2.6506574712925612e-15. The separate subnormal maximum
is 0.49994464825754625 and is covered by the declared absolute underflow term;
it must not be presented as ordinary relative precision. The initial sandbox
attempt stopped at WSL E_ACCESSDENIED before GCC; the first successful run and
the descriptor/metric supplement and final per-refusal snapshot supplement are
retained separately. Every refusal now snapshots the entire real input array
and supplied descriptors immediately before the call and compares them before
restoring injected invalid values. The captured numerical outputs are identical
before and after this test strengthening; the production code did not change.

Source-only GCC15.2 C and C++17 compatibility passes for Xtensa LX6 and RV32IMC,
including the exact new function-pointer type. The first sandbox GCC launch
failed with Windows DLL error623 before compiler execution and is retained.
Clang-Tidy on the frozen conversion and transform units reports zero warnings
and errors. The new host fixture has three warnings for comparing its own
pre-call descriptor byte snapshots, including padding; these checks deliberately
test unchanged object storage rather than equality of independently constructed
objects. No warning is suppressed. None of these source profiles is an SDK
build or target execution.
