# Public owned-book consumer baseline: SDK exact, host UBSan NONPASS

This is a finite public-source/owned-array diagnostic. It is not a production
repair, vendor decoder qualification, PCM/conformance result or physical test.
The original C arithmetic and every original failure are retained.

## Actual scope and independent expectations

The selected raw setup data contain34 unchanged book-case selections and two
separately labelled unit-only zero-float variants. There are36 cases,123 valid
codeword/tolerance probes and365 vector calls. Widths2/9/16, decode types1/2/3,
D16 map1 singleton q_pack0, sparse/dense rows and both sequence flags are covered.
Integer books use point0/residue−8/floor0−24. The two fractional floor0 books
use only their exactly representable points−8/−24. Preferred singleton zero and
nonpreferred-one tolerance controls are distinguished; the latter do not assert
full normative singleton support or full-decoder acceptance.

An independent LSB raw-book/Fraction oracle retains all encoded fields and
canonical q_del scaling (`q_del >>= q_bits`, `q_delp += q_bits`). Every selected
scaled product and complete expected vector is exactly representable signed32.
No gain, fitting, trimming, point change or weakened comparison is applied.
Only declared minimum/delta32 fields change in the two additive unit cases;
no full-stream/carrier validity or reference PCM claim is made for those units.

Public Tremor revision0ad0141e864cfbb130db4f22e279d421832e7336 and complete
original C/header/BSD license are retained. Original codebook.c SHA256 is
`0cfcbdadd7a491bc6bb7c24a2e7d3ed6ce9fb9360122b93631d205fcdf5ac749`.
The port changes only decode_map local linkage/name and explicit byte-pointer
arithmetic; multiply/shifts/sequence logic remains unchanged. Canonical CYD
setup6b36 and ABIe60 are exact. A general LP64 host does not run that ILP32 ABI:
its independent valid owned prefix arrays use public consumer declarations only.
Actual canonical publication is a separate SDK test.

## Actual source controls and data generation

Source02 readiness is
`6d009ae122974c4993ab88e8befc350f40077d9095d14e85f784c8a9ef40e6bc`.
Its immutable source01 history is retained; source02 only selects the existing
WSL non-PIE sanitizer profile before measurement. A peer-found draft
sanitizer/numerical-exit classification issue was corrected before source01
freeze; it is not an invented actual failed test run.

All26 construction/protocol/scope tests passed in actual terminal0/chunk720789
(0.052s). Actual materialization terminated0/chunkd8ce61. Independent root
readback bf0de3 recovered all36 complete raw C arrays, all123 probe rows and365
expected point vectors, with exactly the two declared additive unit edits.
Generated runtime readiness is
`c5b554bc0df7c566742c0d9ceeb157fdf81116d93426c22e73adf04af9d8cc77`.
Raw contract.json SHA256 is
`a50a9350ac681f58d18774455127714b8d2ce195430b873c746d7b2b79374c48`;
its distinct canonical model digest is
`92a9c6ba03892f6e6637b5e6cf5889e5cf0defe92e6d5357e40120acad66d8ff`.
The full generated header SHA256 is
`0e7fe555d413f82419a7688e549cb6d153cf5867fc67a0e2ec5c394a5735ce67`.

## Actual host baseline: complete campaign, sanitizer NONPASS

WSL GCC13.3.0 SHA256
`1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26`
compiled the consumer-only unit without diagnostics. Flags retain ASan and
UBSan, no recovery, full warnings as errors, frame pointers and the existing
non-PIE profile. Each of365 calls ran in a distinct bounded child. All366 child
commands, including compilation, reached a normal terminal status; the outer
campaign finished exit1 in actual terminal chunk708824, session34175.

All331 available vectors are sanitizer-clean and equal every independent
Fraction component. The remaining34 calls stop at UBSan and have no vector;
full numerical comparison and host sanitizer qualification therefore remain
false. They are preserved as NONPASS, never expected passing controls.

| Case | First observed oversized public shift | Missing vectors |
| --- | --- | --- |
| 32: existing floor0 zero minimum | q_minp−9999 at point−8/−24:9991/9975 | 4 |
| 34: unit-only zero delta | q_delp−9997 at point0/−8/−24:9997/9989/9973 | 15 |
| 35: unit-only zero minimum/delta | minimum shift9999/9991/9975 | 15 |

The raw public unpack helper represents zero magnitude with point−9999. The
consumer still uses point differences as32-bit shift counts with no magnitude
guard. A zero operand does not make a shift count of32 or more defined C.
For case35, the first minimum failure prevents reaching the later delta shift;
its source path is distinct from an observed executed instruction. These facts
diagnose the retained public source. The effect on any opaque vendor code is
unknown; no historical PCM cause or overflow mechanism is inferred.

Host report SHA256:
`8289faff1ab23e749035ba912feefc58263c39b06f26f87689dd04fcb528c999`.
Actual outer receipt SHA256:
`79adf7db0e86d0c5ae78e084143ad37746b1277ea0aa3237f759b946e48be22f`.
Root bac678 rechecked every actual child log length/hash. Root factual summary
SHA256 is`23739ac9796722e3fdeff1c6f9f1a2467f9c3b4aced934eec7bc3e6d6f646732`.

## Actual SDK/Xtensa baseline: complete publication and exact365 vectors

The separate sealed controller readiness is
`1d500f7ae44334cc62110da70a0243ec39faf5fa43bc4c585c23b1b94bb68f1f`.
SDK6.0.2 HEAD7101770dc6db2667b3c477cc31365dd1acd6db4e compiled the unchanged
unit/owned parser/public consumer for classic ESP32 ILP32,240MHz,SMP,app_main
core0/stack16384. No vendor codec archive or full-stream decoder is linked.
Actual compiler argv/macros, repeated include dependencies, frozen configured
inputs, own ELF32/machine94, nm/map and generated link commands are retained.
DIO40MHz/4MB is an isolated QEMU fixture profile, not a production firmware export.

All14 commands terminated0. All36 canonical publications,365 complete Fraction
vectors and439 protocol records passed. Every owned array/quantized row/field,
exact bit consumption, guard and normal clear/free was checked. Compiler
warnings/errors are0. QMP greeting/capabilities, quit acknowledgement, non-guest
host SHUTDOWN, stdout EOF, reader join and actual process exit0 were verified
before protocol qualification. COMPLETE alone is not an acceptance criterion.

The direct root command finished0 in actual terminal chunkba4727, session90202.
SDK report SHA256:
`8988baa98cc0c72a494dd70eec229860fb953cba63ce58a38b4f0caa155bab74`.
Actual direct terminal record SHA256:
`e9a08762a422ffbf5c501a5d34c7323ae82bb1e5fa4ec64ad501cf18af62005c`.
Root fact inspection49cfc0 confirms all365 exact vectors and complete owned
lifecycle. Actual target equality does not prove portable public C: host UBSan
NONPASS remains. Publication, full vector comparison and sanitizer coverage are
recorded as separate facts.

## Boundaries and next step

The separate zero-guard analysis/proposal is source-only. This baseline archive
contains no applied guarded consumer and no invented successor execution. A
future separate port can handle q_min0 and q_del0 before shifts, retaining the
nonzero paths, q_bits scaling, sequence, ABI, sentinels and all original inputs.
It must preserve331 existing vectors, make all34 zero-field vectors available
and exact under ASan/UBSan, and separately retain identical SDK publications.

Historical singleton/native refusals and wide/floor0/sequence1 numerical
NONPASS remain record-only and unchanged. Their old target PCM is not replayed
or requalified. No vendor backend, synthesis, PCM, production radio integration,
fullG6 or full-standard result follows. Deferred Ogg/EOF/reset/OOM/AAC work is
untouched. No board/COM/flashing/reset/network/audio operation occurred. CYD
production stream core0/decode-output core1 and their priorities/stacks are
unchanged; this sequential unit's own app_main core0 does not qualify G5.
