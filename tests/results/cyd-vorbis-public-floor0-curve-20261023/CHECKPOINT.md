# CYD public floor0 curve checkpoint — 2026-10-23

The isolated PORTED public Tremor floor0 function completed an actual ESP32
SDK/QEMU owned-array experiment. This closes the planned public integer-curve
experiment for these six fixtures. It does not establish vendor decoder
behavior, PCM accuracy, complete Vorbis conformance or radio integration.

## Actual scope

The experiment calls public `vorbis_lsp_to_curve` on owned arrays derived
from the six unchanged original even6/odd5 raw floor0 fixtures. There are
84 packets, 168 channel calls and 58,368 complete half-block output bins
(233,472 signed32 bytes), with half-blocks32/128/1024. All original call
inputs and checksums equal the earlier original-public contract. Independent
C-array readback recovered 168 descriptors and 5,208 words before execution.
The Q24 LSP, Q4 amplitude and residue Q8 units are explicit; output is Q24,
not PCM. Canaries, input preservation, complete tails, bounded outputs and
five bounded multiply controls are mandatory. No vendor codec, opaque handle,
MDCT, audio device, COM port or physical board is involved.

Actual runtime03 contract SHA256:
`1f8817117df942c4d6564614e71a90147a9faa6e782ff945830dc11d5b9f6e3d`.
Actual runtime03 readiness:
`97de1886431efe1302f1125f223752800eaa83b599168dda41d31a0442cd0e65`.
Capture03 report:
`d00a30f91d37f998af97f63cd9433e140e8d72f6c9a126de58ee260c929354cd`.
Direct tool terminal: session43646, chunk `f26f66`, exit0.

All22 owned commands returned0. The actual three translation units, GCC
macros/dependency closure, link/map/nm and explicit compiled source agree.
SDK6.0.2, Xtensa ELF94, ILP32/little-endian, GNU23,240MHz and normal SMP are
recorded. The unit runs on main core0 with stack16384. Production stream
core0 and decoder/output core1 bindings are unchanged. The passing build
has zero compiler warning/error diagnostics.

QEMU is owned, snapshot-only and has no NIC/audio/display/monitor. Its
actual greeting, capability acknowledgement, COMPLETE, owner quit request,
non-guest host SHUTDOWN, quit acknowledgement and exit0 are retained.
The exact captured helper enforces EOF and reader joining; this older helper
does not emit separate EOF/join booleans. None is invented. The strict
protocol revalidated all3,992 events and all168 full curves.

## Original public source and explicit portability

Public Tremor revision `0ad0141e864cfbb130db4f22e279d421832e7336` was fetched
from android.googlesource.com. The actual HTTP200 record, complete87-file
source tree, copyright/license and archive identity are retained. Archive
SHA256 is `d5e655ab1ad537049ade9703477200a6ec15d7919cae11678ea841f018936743`.

Original floor0.c is retained byte-exact at SHA256
`d0372c1dbf4c95231927619a7a1a660bdf421d63b332966f5fe33b9572c002f2`.
The compiled source is explicitly `PORTED_PUBLIC_TREMOR_FLOOR0`, SHA256
`e1836251d072154691f87a74ea6cdae88d2cf2dd106fbc99908ec71f1f1a8e5a`.
Both negative-constant shifts `(-140<<12)` become `-(140<<12)`, and the unused
`inyq` declaration is removed. No warning suppression, algorithm, table,
clamp, input, unit or compile-option change is added. The exact diff is
`32ea414dedfd4ebe90d3b5d6a78752aeb6049eae25ba9353de73297d8c8b8cfd`.
Other legacy C integer semantics are not declared universally portable.

Attempt01 ended1 before build/QEMU because the evidence collector froze a
configured SDK header after its dependency binding. Attempt02 fixed only
that ordering and ended1 at strict SDK compilation: original public source
contained a negative left shift and an unused local. Both complete original
failed histories remain unchanged. Only the explicit port passed attempt03.

## Separate binary64 diagnostic

A separately reviewed comparator bound actual capture03, its exact direct
terminal/controller, full168 persisted curve files and actual Q24/Q4 inputs.
It normally imports unchanged SHA-pinned protocol and formula helpers.
Its actual wrapper ended0 (chunk `72085a`); diagnostic SHA256:
`be554d0dd64630216d27736130f8e523daf118e005e9fd2ebb66d9970d414a6b`.

The diagnostic retained2,688 active-bin comparisons. Its mathematical
binary64 path requests positive dB at147 points; public-function gain
estimates at those points range from0.9999999403953552 to1.0. Across all
active points the public estimate ranges from0.012980222702026367 to1.0.
These are finite observations of public integer mapping/lookup/rounding/
clamp versus our mathematical Bark path. There is no equality threshold,
amplitude fitting, PCM policy or attribution to opaque vendor internals.

The floor0 and wide PCM regressions remain NONPASS under the unchanged
project criterion of2 S16 LSB; that criterion is not a normative Vorbis
tolerance. Remaining G1–G8, other formats, callback/ownership/concurrency,
radio integration, resource and physical acceptance gates stay open.
Existing Ogg/reset/OOM, FLAC target-error and AAC deferrals remain in force.
