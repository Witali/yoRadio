# AAC decompilation evidence

Read the [analysis and proposals](../../ESP32C3_AAC_DECOMPILATION_RAM_20260930.md)
first. The firmware and decoder binary have not been modified.

- [provenance.json](provenance.json): binary identities, allocation arithmetic,
  reference hashes, scope, warnings and candidate estimates.
- [pseudocode/manifest.json](pseudocode/manifest.json): 176 functions, addresses,
  direct calls, completion and warning flags. Adjacent `.c` files are **Ghidra
  pseudocode, not original source and not intended to compile**.
- `disassembly/`: GNU objdump output for the 14 critical memory functions.
- [layout-experiment.json](layout-experiment.json): RV32 compiler/DWARF size
  comparison of the pinned reference before/after pointer-table compaction.
  This is not a modified decoder execution or ABI compatibility test.
- [g711-illustration.json](g711-illustration.json): mu-law/A-law round trips for
  all 65,536 signed 16-bit values. This demonstrates companding quantization,
  not the error of an SBR implementation using companded storage.

## Reproduce

Use a matching linked ESP32-C3 ELF, the pinned codec archive, Ghidra 12.0.4,
the C3 GNU toolchain and an IDF Python environment with pyelftools. Run from
the worktree root. Set these paths for the local installation:

```powershell
$ghidra = 'C:\Work\r36sx_disasm\ghidra_12.0.4_PUBLIC'
$env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-25.0.3.9-hotspot'
$toolbin = 'C:\Work\yoRadio\.idf\tools-v6.0.2\tools\riscv32-esp-elf\esp-15.2.0_20251204\riscv32-esp-elf\bin'
$python = 'C:\Work\yoRadio\.idf\tools-v6.0.2\python_env\idf6.0_py3.12_env\Scripts\python.exe'
$archive = 'C:\Work\yoRadio\.idf\esp-adf-libs\esp_audio_codec\lib\esp32c3\libesp_audio_codec.a'
$elf = 'idf/esp32c3-oled-native/build-constants-audit/yoradio_esp32c3_oled_native.elf'
$out = '.build/aac-decompile-repeat'
New-Item -ItemType Directory -Force $out | Out-Null
Get-FileHash $archive, $elf -Algorithm SHA256

& "$toolbin/riscv32-esp-elf-nm.exe" --defined-only -P $archive |
    ForEach-Object { if ($_ -match '^(\S+) [TtWw] [0-9a-f]+') { $Matches[1] } } |
    Sort-Object -Unique | Set-Content -Encoding ascii "$out/archive-functions.txt"

& "$ghidra/support/analyzeHeadless.bat" $out aac `
    -import $elf -processor RISCV:LE:32:default -cspec gcc `
    -max-cpu 2 -analysisTimeoutPerFile 300 `
    -scriptPath tools/codec_benchmark `
    -postScript DecompileAacMemory.java "$out/pseudocode" "@$out/archive-functions.txt"

& $python tools/codec_benchmark/sbr_memory_layout.py `
    --compiler "$toolbin/riscv32-esp-elf-g++.exe" --output "$out/reference"
& $python tools/codec_benchmark/aac_memory_layout_experiment.py `
    --reference "$out/reference/upstream" `
    --compiler "$toolbin/riscv32-esp-elf-g++.exe" --output "$out/layout"
& $python tools/codec_benchmark/g711_quantization_example.py `
    --output "$out/g711-illustration.json"

& "$toolbin/riscv32-esp-elf-objdump.exe" -d `
    --disassemble=PVMP4AudioDecoderInitLibrary $elf
```

The retained probe result is `55128 → 53240`, a **1,888-byte** reference payload
reduction. Inspect Ghidra's log and manifest; completion does not imply every
type/argument is correct. The import emits warnings for some unrelated DWARF
and instruction ranges; the PS allocator also has a type-propagation warning.
Ghidra's automatic language selection initially chose AndeStar; the retained
results were regenerated with explicit standard RV32. The export script rejects
other language IDs.

The build directory is ignored and its ELF is not a permanent artifact. For a
new build, record its hashes and regenerate the evidence rather than assuming
the old addresses still apply. The reference fetcher pins the Android revision
and requires network access. Never apply its structure offsets blindly to the
Espressif decoder; the report documents confirmed differences.
