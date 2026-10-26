# Native exact floor1 product qualification

2026-10-26. Parent implementation: `62bc12a9dd376e86fd11644ab50377e9ca6ac21d`.
**ESP32 LX6 and ESP32-C3 native arithmetic captures and independent replay
PASS. Both original controller CLIs retain a terminal1 summary-print failure
after completing their native work.** The corrected final source changes only
that console-summary expression; no native fixture, parser or arithmetic changed.

## What runs

The isolated project exercises the public generic floor1 scale measurement and
product APIs. Setup ownership, packet/frame decoding, Xiph DSP, floor0,
transforms, PCM, radio, production firmware and previously deferred targets do
not execute. Linked-symbol checks retain both generic APIs and exclude decoder,
owner and renamed unexecuted host-fixture main symbols.

The complete1663-row host corpus supplies the selected scalar inputs. Each
endpoint row becomes two256-coefficient batches and each1792-bin pattern row
becomes seven256-coefficient batches. All original selected scalar positions
are retained exactly once. Every batch preserves the original curve's common
factor-grid extrema. Three additional small3-channel calls cover selected
channels0/1/2. Native call shapes differ from host metadata; this is not complete
host-shape/control parity. Synthetic1087-bit shapes also cover the arithmetic
helper beyond the encoded residue's1079-bit bound.

| Per architecture | Actual result |
| --- | ---: |
| Calls | 2957 |
| Coefficients | All256 |
| Magnitude widths | All1–1087 |
| Signed endpoint combinations | 556544 |
| Exact output samples | 619564 |
| Exact uint32 output words | 11817093 |
| Maximum limbs | 36 |
| Refused rows | 23 |
| Refusal controls | 713 |
| Runtime assertions | 14627821 |
| Ordered protocol events | 101481 |

Both exact word sequences hash to
`cd525fee0961ec7378f53bde7fe8155447c956d282c312c3a24ba6257747c9ae`.
The digest supplements per-word comparison; it does not replace it.

## Runtime and evidence

ESP32 uses SDK6.0.2 revision
`7101770dc6db2667b3c477cc31365dd1acd6db4e`, dual-core LX6, coordinator core0
and priority3/16384-byte worker core1. C3 uses SDK6.1.0 revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`, RV32IMC, coordinator/worker core0
with the same worker priority and stack. Existing production task settings
are untouched. Task watchdog initialization and IDLE checks remain enabled;
new fixture code yields after every bounded output chunk and every row.

Peak wide input plus output storage is approximately72KiB before small guards,
scratch and SDK overhead. Input data is regenerated for exact immutability
comparisons. Capacity/null/RANGE/shape refusals preserve output and published
metadata, and complete retries succeed. No physical heap benefit or real-time
audio performance is inferred.

Each profile's six actual child commands return0: SDK head/clean, build,
symbols, image merge and QEMU. The SDK child receipt also records terminal0.
Raw logs, ELF32 machine types94/243, selected images/SDK configuration, actual
compile rows and individual `.su` records are retained. Source hashes match
executed snapshots. A supplementary replay verifies every native limb again,
checks SDK head/clean afterward, captures compiler identity/dependencies and
rechecks installed tool hashes. All ten supplementary commands return0.
Compiler frames are not complete call-chain or task high-water measurements.

The output protocol uses canonical lossless run-length encoding within
contiguous128-word chunks. The pure reader expands every word and compares it
against exact rational decimal-to-binary32 table conversion and Python integer
products. Native panic, watchdog, heap, stack, torn/duplicate/missing events,
wrong fields/core, altered data or extra terminal events fail. Pure protocol
tests pass both target profiles and reject28 explicit corrupted/partial
transcripts over nine representative cases each.

## Preserved failures

- `failed-build01/`: first ESP32 SDK attempt stops at compilation because the
  generated descriptor array lacks its closing delimiter. No QEMU runs. The
  generator was corrected and its complete-array regression check added.
- `esp32/` and `esp32c3/`: every SDK/QEMU command and every numerical comparison
  completes, and PASS is saved. The outer Python CLI subsequently returns1:
  its final `dict` console summary supplies `passed` twice and raises TypeError.
  Original reports and their errors are unchanged. The fixed source removes
  only that duplicate console-summary keyword. These original CLIs are not
  relabelled clean.
- `replay01/`: the supplementary resolver mistakenly checks system
  `powershell.exe` for the `pwsh.exe` tool alias. It fails identity validation;
  no native test changes or reruns occur. `replay02/` fixes only that alias and
  completes a clean independent replay and post-run checks.

`outcomes.json` distinguishes these failures from successful native child
execution. The replay receipt explicitly retains original outer exit1.
No failed scope is hidden or declared successful by dropping cases.

## Archive and verification

`captures.zip`:263 members,18124487 compressed bytes,126339632 uncompressed
bytes. SDK/build caches are excluded; selected declared build outputs remain.

- Archive SHA256: `e2366f3078c20b9b2928e897c60eae5b5223403b9345ac621a0a41c6aff70ee7`.
- Manifest SHA256: `419e6cf04799b672b31f82352aea411a731d7c5d11cf6120b0b0e9a11b2f388b`.

The private installation path of PowerShell7 is intentionally replaced by an
explicit tool alias in command/tool metadata; its exact executable SHA256 is
retained and rechecked. Other SDK/project/QEMU arguments remain explicit.
Raw artifacts require local privacy inspection before publication.

Run `python -B tests/verify-vorbis-floor1-product-native-checkpoint.py`.
It verifies pinned inventory/member/source hashes, regenerates the entire
finite model/header, compares every limb on both architectures, verifies raw
command/SDK receipts, actual ELF/images/configuration and supplementary checks,
and repeats the28 protocol corruption controls. Only pinned current local
pure readers execute; no archived Python, children or extraction execute.

This closes the isolated generic arithmetic gate only. The owner/frame,
floor0/transform/PCM, full decoder/resource/audio-task, production, physical
acceptance and all previous deferred gates remain open.
