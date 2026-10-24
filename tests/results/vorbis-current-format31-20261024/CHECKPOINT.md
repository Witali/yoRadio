# Current-source complete31 Vorbis checkpoint, 2026-10-24

All 31 public raw cases complete on the current canonical repair, but the full
numerical result remains **NONPASS** at the unchanged project bound of 2 signed16
units. This checkpoint refreshes execution evidence; it does not fix or waive
the remaining wide/floor0 errors.

## Complete current-source execution

The frozen current setup, output, ABI and floor1 renderer are compiled with
ESP-IDF 6.0.2 / Xtensa / machine94. The coordinator stays on core0 and the worker
on core1, priority3, configured stack16384. The original caller, 31-case
contract, 155 materialized arrays, raw inputs, source map and reference binding
are unchanged. All 434 packets / 738560 PCM bytes and 964 protocol records are
retained, including all SS/SL/LS/LL transitions and original/equivalent floor0
cases. Open/decode/close, complete consumption, persistent public metadata,
output capacities, canaries and both nonzero channels are checked.

All ten owned commands terminate successfully. Current `floor1_render.h` is
frozen, and the selected ELF has open/decode/floor1 wrapper symbols. Generated
Ninja flags, linker rule expansion and the owned `ninja -t commands` listing
all select `--wrap=floor1_inverse2`. The listing records a recipe; it is not an
independent observation of linker execution. The successful SDK build and ELF
are separate observations. No original-vendor PCM oracle is claimed.

Capture02 report SHA256:
`cf653b83aeeeae3f201158d169a7d40b936f574edcf818d97345b0b09a4964d8`.
Actual direct terminal: chunk `555f9a`, exit0.

## Numerical measurement and retained failures

The separate adapter completes every original zero-lag L/R signed16 sample,
packet comparison and all 14 declared relations. It revalidates retained
qualified Xiph WAV/framemd5 and actual historical child receipts across the
three original reference scopes. Original dual-reference NONPASS and native
lookup2 refusals stay preserved. No new reference decoder is executed. No
trimming, resampling, gain fitting, shifted or swapped acceptance is used.

| Cases | Count | Maximum absolute signed16 error |
| --- | ---: | --- |
| Original codebooks | 8 | 1 |
| Wide D16 sparse/dense, sequence0/1 | 4 | 65535 |
| Mapped single/twin D2 | 4 | 1 |
| Floor1/residue0 controls | 3 | 1 |
| Even floor0, original and equivalent | 6 | 40664 / 1649 / 40664 per representation |
| Odd floor0, original and equivalent | 6 | 65535 |

Fifteen cases satisfy the limit; sixteen do not. Xiph satisfies all 14
relations; current target satisfies 12 and fails the two wide sparse/dense
equalities. The full31 result and old25 projection remain rejected.
Numerical report SHA256:
`b16bac9ad06b67d0fd143cef91e30a72f010cf078527990989b4316860c6d7fe`.
Actual numerical terminal: chunk `b90832`, exit1 after complete measurement.

A separate complete byte comparison confirms that all 31 current PCM vectors
and all 434 packet slices equal their retained old target vectors. Its selected
source/report/PCM bytes remain unchanged and its actual wrapper exits0. This is
current/retained-target parity, not numerical qualification or a vendor-cause
diagnosis. The new floor1 renderer does not resolve these corpus failures.

## Checks and scope

Eight actual CMake-P phase/pin/recipe tests, eight synthetic link-recipe selection
tests and nine current numeric-binding tests pass. The last two suites test
selection and evidence binding; they do not create synthetic whole31 PCM or
qualify a decoder. The first capture attempt selected the wrong SDK Python
argument and stopped during SDK environment activation, before compiler/QEMU.
Its failure and frozen files are preserved. The same reviewed source succeeds
with the installed SDK virtualenv in capture02.

The offline verifier uses saved bytes, independently recomputes signed16 and
relation results, and distinguishes complete numerical NONPASS from incomplete
input/process failures. Any explicitly reused pure helper is named and
hash-bound. Executables omitted with identity records provide no full binary
semantics or dependency closure. Its first invocation rejected the deliberately
omitted host Python executable because the host-input branch incorrectly
required a saved body. The corrected branch permits identity-only records only
for the recorded Python/CMake tools; missing source bodies still fail. Initial
publication receipts, manifest and checker/collector sources are retained in the
[verification history](../vorbis-current-format31-verification-20261024/README.md).
The original failed checker result is not decoder qualification.
Production source and task bindings are
unchanged; the bridge remains isolated. Full G1/G4/G5/G6, remaining wide/
sequence1/floor0 correctness, deferred work, radio integration, resources and
physical acceptance remain open. See
[floor0 precision/range requirements](../../../docs/CYD_VORBIS_FLOOR0_REMAINING.md)
and the [transfer plan](../../../docs/ESP32_CYD_C3_TRANSFER_PLAN.md).
