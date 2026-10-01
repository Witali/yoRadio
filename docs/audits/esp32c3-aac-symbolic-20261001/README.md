# AAC decompilation with named structure fields

This is a separate analysis of the same pinned binary as the
[immutable raw export](../esp32c3-aac-full-20261001/README.md). All **186 functions**
are present at the same addresses and with the same machine-code body sizes.
Neither the library archive nor the analysis ELF has been modified.

The ESP32-C3 compiler supplies **23 checked type layouts** through DWARF debug
metadata. The importer assigns verified pointer roles to **33 functions**;
propagation changes the readable output of **36 functions**. For example:

```c
// Before:
*(int *)(owner + 0xc984)
*(int *)(ps + 0x1fc)
*(int *)(frame + 0x11b0)

// Named fields in the corresponding typed views:
owner->ps
ps->hybrid
frame->low_real[0][0]
```

The analysis additionally names PS configuration/IID/ICC parameters, SBR frame
control, inverse-filter settings, harmonics, envelope/noise data and frequency
tables inside the runtime header's opaque regions. These are analysis views,
with compile-time size checks; they allocate nothing and do not authorize
shrinking any buffer. The original channel view is selected because this ELF
does not contain the experimental relocated/packed layouts.

Field order was cross-checked with the pinned binary's readers, setters and
callers and the PacketVideo reference headers at revision
`437ced8a14944bf5450df50c5e7e7a6dfe20ea40`. Native changes take precedence: notably,
Espressif's `sbr_applied` has **ten arguments**, with controller/core in positions
8/9, unlike the eight-argument reference. The type map records these native
positions. Ghidra keeps inferred types for unverified parameters and returns.

## What remains numeric

[`access-review.json`](access-review.json) scans every function and preserves
line-numbered numeric-access candidates. The lexical count falls from **2256
to 1733**. These numbers are **not a count of bad addresses**: valid sample-array
indices, vector strides and casts appear alongside unidentified core fields.
The scanner cannot infer field semantics or reliably classify optimized pointer
aliases. Unknown core/configuration and scratch subregions still require manual
reconstruction before a source replacement can use them.

Two exports retain Ghidra type-propagation warnings: `ps_bstr_decoding` and
`sbr_reset_dec`. The known out-of-bounds vendor reset remains visible in the
original binary's export (as a bogus `core[2]` access after typing). Its tested
repair is in the runtime adapter; changing an analysis label does not fix the
archive. The analysis ELF must never be run or flashed.

This remains **inferred pseudocode, not compilable recovered source**, and does
not claim to eliminate every numeric field access in the closed library. The
compiled-source changes and paired decoder tests are described in the
[offset audit](../../ESP32C3_AAC_LABELS_20261001.md).

## Reproduce

Use the analysis ELF and `functions.txt` prepared by the raw audit. Create a
fresh output folder so existing type inference cannot affect the result.

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
$compiler = 'C:/Work/yoRadio/.idf/tools-v6.0.2/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-gcc.exe'
& $python tools/codec_benchmark/prepare_aac_symbolic.py `
  --compiler $compiler --output .build/aac-symbolic-repeat
$env:JAVA_HOME = 'C:/Program Files/Eclipse Adoptium/jdk-25.0.3.9-hotspot'
& 'C:/Work/r36sx_disasm/ghidra_12.0.4_PUBLIC/support/analyzeHeadless.bat' `
  .build/aac-symbolic-repeat aac-symbolic `
  -import .build/aac-full-20261001/aac-full.elf `
  -processor RISCV:LE:32:default -cspec gcc -max-cpu 2 -analysisTimeoutPerFile 300 `
  -scriptPath tools/codec_benchmark `
  -postScript ApplyAacTypes.java .build/aac-symbolic-repeat .build/aac-full-20261001/functions.txt
& $python tools/codec_benchmark/audit_aac_symbolic.py `
  --raw docs/audits/esp32c3-aac-full-20261001/pseudocode `
  --symbolic .build/aac-symbolic-repeat/pseudocode `
  --output .build/aac-symbolic-repeat/access-review.json
& $python tests/test-aac-symbolic.py --compiler $compiler
```

Successful import requires the pinned ELF hash, all type sizes/member offsets
and all requested parameter slots. Only then does the importer invoke the
exporter. Inspect the headless log and `applied-types.json`; Ghidra can return
exit code zero after a script error. The retained provenance covers the exact
export, compiler metadata, log and tool/header snapshots. Documentation prose
is maintained separately from those hashes.
