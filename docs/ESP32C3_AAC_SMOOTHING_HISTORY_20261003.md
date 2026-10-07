# Four persistent SBR smoothing rows, 2026-10-03

## Result and scope

The QEMU experiment keeps four previous gain/noise rows in the SBR owner and
creates the fifth row temporarily on the decoding task's existing stack. All
five FIR terms and the pinned decoder's integer arithmetic remain unchanged.
No mantissas, exponents, frequency bands or AAC features are removed.

**The owner allocation saves another 2048 bytes over PC18 high history.**
144 direct FIR cases are bit-exact; 81 paired full-decoder comparisons on eleven
inputs remain within 2 signed-16 PCM LSB against the original decoder. These
full-decoder comparisons include the previously qualified lossy PC18 high-QMF
history. Their sample counts and error counts match the retained five-row PC18
results; that statistical agreement is not a samplewise PCM hash comparison.

This is disabled-by-default **QEMU-only** work. The physical board and production
defaults are unchanged. The previous public HE-AAC network/heap failures remain
open; the smaller owner alone does not prove that the complete radio now fits.

## Actual memory accounting

| Item | Previous five-row PC18 owner | Four-row experiment |
| --- | ---: | ---: |
| Smoothing matrices, stereo | 10240 B | 8192 B |
| Pointer tables, stereo | 160 B | 160 B |
| Owner request | 47980 B | 45932 B |
| Measured unguarded allocator block | 49152 B | 47104 B |
| Cumulative owner-block saving versus native 55296 B | 6144 B | 8192 B |
| Temporary row payload during complex processing | 0 | 1024 B |

The compiled complex wrapper has a **1184-byte stack frame**, including its
1024-byte row payload. Its dispatch function releases its own 32-byte frame
before tail-calling either path. Real-only LC-SBR tail-calls the native envelope
without the large frame. Callee stack requirements remain additional.
Disassembly is retained with the evidence.

The test task already allocates the production decoder stack plus 4096 bytes
for A/B diagnostics. No task stack allocation was increased for this experiment.
**Physical production stack headroom must still be measured** before claiming
the full 2048-byte reduction as a usable whole-radio saving. Allocator figures
are separate from persistent payload, peak stack use and network fragmentation.

## Lifetime and consumer audit

The [earlier smoothing audit](ESP32C3_AAC_SMOOTHING_TABLES_20261001.md) checked
the five-tap standard filter and all owner consumers. This change preserves
the five-entry pointer interface while reducing each physical matrix to four
retained rows. It builds on the
[PC18 high-history owner](ESP32C3_AAC_HIGH_HISTORY_20261003.md).

| Function / access | Treatment |
| --- | --- |
| `init_sbr_dec` | Compiler-derived matrix strides address four rows. The native five-iteration loop only constructs pointers; its fifth pointer is cleared immediately by a wrapper, before any consumer can dereference it. |
| `calc_sbr_envelope` | On startup fills the first four rows. During complex processing a scoped fifth row is available across every envelope in this call. The frame prefix and all opaque workspaces retain their native ABI. |
| `envelope_application` | Unchanged binary reads all five FIR terms, writes current values and rotates all five pointers. A temporary pointer that survives among the first four is copied into the unused persistent row before returning. No stack pointer escapes. |
| `envelope_application_LC` | Uses no smoothing tables. The real-only call site supplies null tables and dispatches directly to native code. |
| `sbr_dec` | Both envelope call relocations, at pinned instruction offsets 0x23c/0xc3a, are redirected in this copied object only. Other decoder calls remain original. |
| `sbr_open`, `sbr_read_data`, `sbr_applied`, `PVMP4AudioDecodeFrame` | Existing checked layout patcher derives channel/tail addresses from the RV32 C layout. New channel size is 22960 bytes. |
| `ps_allocate_decoder`, PS readers | Existing right-channel overlay remains intact. Its new channel base crosses a 4 KiB boundary for the QMF all-pass workspace, so its upper address immediate is patched as well. |
| Repaired reset | Typed `sizeof` clears the reduced matrices; the first four logical row pointers remain valid. Startup/reset repopulates history. Both native reset modes and subsequent PCM are tested. |
| Free / allocation failure | Existing guarded owner registry and cleanup paths retain their owner-base semantics and cover both SBR/control failures. |

The native archive SHA-256 is pinned; all **91** address/stride instruction
patches reconstruct the original words when supplied the original C layout.
Memory offsets come from named `offsetof`/`sizeof` expressions. Patch locations
are instruction offsets in the pinned object, not hardcoded runtime addresses.

The 23-argument envelope interface was cross-checked against native disassembly
and the upstream
[PacketVideo implementation](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/calc_sbr_envelope.cpp).
Source provenance is retained; upstream DSP code is not copied into firmware.

## Qualification

- **144 direct FIR scenarios**, seven calls per scenario: 1/32/48 active bands;
  2/4/6/8/10/32 slots; tone/no-tone; noise/no-noise; smoothing toggled on/off.
  Compare QMF outputs, phase/harmonic counters, current values and four retained
  logical rows. Check per-matrix guards, pointer ownership and removal of every
  temporary pointer. **562464 active QMF scalar values** compared; no differences.
- The previous 24 five-entry table tests remain enabled and pass independently.
- **81 paired decoder comparisons**: six synthetic LC/HE/HEv2 fixtures and five
  original radio ADTS captures, each with controls and three repetitions. Full
  output rates and channels remain checked. Maximum error: **2 LSB**, within the
  current production numerical gate of 3. LC does not allocate an SBR owner.
- 21 lifecycle segments, two allocation-failure paths and six reset fixtures
  pass, including real-only and complex SBR, PS and full owner cleanup. These
  existing controls repeat in each input run.
- The first full run caught a real-only null-table dereference after all direct
  complex-FIR checks had passed. Its panic log and ELF hash are retained. The
  fix dispatches that path before temporary complex storage is installed.

[Complete table](../tests/results/esp32c3-aac-smoothing-history-20261003/TABLES.md)
and [raw logs, layout and snapshots](../tests/results/esp32c3-aac-smoothing-history-20261003/)
retain failed and passing evidence. RMS is collected on the real captures;
synthetic RMS is not claimed.

The incremental QEMU guest-instruction cost relative to five-row PC18 ranges
from **-0.040% to +0.141%** on this corpus. This is a ratio of warm-run counts,
including test guards/counters and different linked instruction encodings. It
does not establish a physical CPU speedup or a universal performance bound.

Remaining gates: production adapter integration, physical stack/CPU/heap,
public HTTP/HTTPS HE-AAC playback, OTA, malformed inputs, sustained streams and
additional bandwidth/coupling/header transitions. The corpus alone is not a
universal proof for all valid bitstreams.

Six new host regression checks and nine existing high-history checks pass.
They re-parse retained evidence, verify hashes, reject missing/corrupt coverage,
reconstruct the original instruction patches and check memory/stack accounting.
A fresh RV32 layout compilation with the new option disabled matches every
previous PC18 layout descriptor.

## Reproduce

Use the exact PowerShell build command saved as
[`build.ps1`](../tests/results/esp32c3-aac-smoothing-history-20261003/build.ps1)
from this worktree. It combines the prior QEMU high-history profile with
`sdkconfig.qemu-aac-smoothing-history.defaults` in a separate build directory.

```powershell
python tools/codec_benchmark/run_aac_smoothing_history.py --dependency-root C:/Work/yoRadio/.idf --qemu <qemu-system-riscv32> --bios <qemu-bios-directory> --wsl --output .build/aac-smoothing-history/synthetic
python tests/test-aac-smoothing-history.py
```

Add `--input <unchanged-recording.aac>` with a separate output directory for
real captures. Omit `--wsl` for a native QEMU executable. These are disposable
QEMU test images, not board firmware artifacts.
