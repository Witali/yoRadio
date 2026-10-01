# Remaining numeric AAC field accesses — 2026-10-01

Follow-up: the [extended core audit](audits/esp32c3-aac-core-symbolic-20261001/README.md)
adds core, bit-reader, SDK-wrapper, TNS/LTP and scratch-region names across the
same 186 functions, with 63 checked layouts. It also records unresolved optimized
aliases explicitly. Use that export for further memory work; the earlier evidence
below remains unchanged.

## Compiled code

The follow-up audit found private-structure offsets in two older experimental
implementations and four hybrid-output slices in the PC16 allocator. They now
use the shared `aac_sbr_abi.h` definitions:

| Previous expression | Named access |
| --- | --- |
| owner + `0xc984` / `0xc988` | `owner->ps` / `owner->embedded_ps` |
| PS + `0x1a0` … `0x1dc` | Serial, sub-QMF and main delay pointer members |
| PS + `0x1fc`; hybrid + 12 / 16 | `ps->hybrid`, `real_history`, `imag_history` |
| PS + `0x14` | `ps->upper_subband` |
| Frame + `0x11b0`, `0x25b0`, `0x3e38`, `0x39b4` | Low-QMF buffers and high-QMF history members |
| Controller `[4]`, `[6]`, `[1]` | `columns`, `write_offset`, `low_complexity` |
| owner + `0x7678` … `0x93b4` | Checked PS workspace members |
| owner + `0x7b24` / `0x8600` | Packed mantissas / test guard structure after packed storage |
| Hybrid output base + 10 / 20 / 30 words | Four named hybrid-output arrays |

Recovering an enclosing owner now uses `offsetof`, and workspace sizes use
`sizeof`. The header's compile-time checks preserve the original byte layout.
No array was shortened, no new storage is allocated, and codec support and
production defaults remain unchanged.

Numeric sample indices, band counts, loop strides, bit masks, coefficients and
deliberate guard sizes remain numbers where they describe an algorithm rather
than an unidentified field. The intentionally invalid vendor reset location
remains a named constant in the padded bug-reproduction test. Instruction
positions in the SHA-pinned binary patcher identify machine instructions; their
replacement field values already come from compiler-generated layout symbols.

## Verification

Five experimental configurations were rebuilt: PC14 roundtrip, PC16 roundtrip,
PC14 PS writes, PC16 PS writes, and PC16 with the unpacked-value cache. Each ran
the synthetic corpus and retained ABBA HE-AACv2 recording in QEMU.

- **345 paired comparisons**, including bypass/lossless controls;
  **228,956,160 candidate scalar PCM samples**.
- All prior PCM error maxima, counts and per-channel ABBA distributions match.
  This preserves existing precision limitations: the old PC14 synthetic test
  still fails the development gate; this refactor does not qualify it.
- Production adapter path with cache: ten format cases, **328,770 stereo
  output frames**, byte-identical to the previous output.
- The shared RV32 ABI assertions and deliberate layout-drift rejection pass.

Instruction counts include experimental instrumentation. PC14 roundtrip is
unchanged; PC16 roundtrip is slightly lower. PS-write checks add a small amount
of work: PC14 extra instructions versus native are 26.738% / 40.709% (synthetic
HEv2 / ABBA), versus 26.681% / 40.658% before this change. PC16 is 32.731% /
43.046%, versus **32.727% / 43.043% in the immediately preceding ABI refactor**.
Cached PC16 is 50.364% / 60.270%, versus 50.359% / 60.266%. These are emulator
instruction counts, not physical CPU measurements; the experimental performance
optimization work remains open.

Evidence: [logs, configurations, comparisons and exact source snapshots](../tests/results/esp32c3-aac-labels-20261001/).
The first three configurations retain their exact earlier header snapshot;
the later PC16 builds include the added hybrid-output view. Historical results
keep their own source hashes and are not relabeled as fresh runs.

```powershell
python tests/test-aac-labels.py
python tests/test-aac-abi.py --compiler PATH/TO/riscv32-esp-elf-gcc.exe
```

Rebuild the existing `build-qemu-aac-*` configurations with `build.ps1`, passing
their own `-Sdkconfig`, then use the matching `run_aac_*.py` runner. Each saved
result records input hashes, tool paths, QEMU command and configuration hash.
These are emulator images; no board firmware was installed.

## Decompiled binary

The immutable raw Ghidra export is evidence, not compiled decoder source.
The [separate symbolic export](audits/esp32c3-aac-symbolic-20261001/README.md)
imports the verified layouts and names SBR/PS fields throughout its callers and
helpers. Its inventory scans all 186 functions and explicitly retains remaining
numeric-access review candidates. Unidentified core fields are not given
invented meanings. A complete reconstruction of all AAC internals remains
unfinished; this change must not be described as eliminating every numeric
expression from the closed decoder binary.
