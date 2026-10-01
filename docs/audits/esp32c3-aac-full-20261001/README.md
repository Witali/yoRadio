# Complete inventory and decompilation of the shipped AAC decoder

Exported **186 of 186 functions** from **144 AAC decoder archive members**,
including local functions, unreferenced Huffman/prediction helpers and the five
optimized filter cores located separately in the archive. All exports completed.
`ps_allocate_decoder` retains a Ghidra type-propagation warning.

The selection includes all AAC-specific executable code present in the pinned
Espressif archive, rather than only the earlier direct-call closure. The earlier
audit also included generic SDK registration/allocation helpers; these are
external dependencies here. AAC encoding and other codecs are out of scope.
Four configuration objects contain no symbols/code in this vendor build; source
features compiled out of the library cannot be recovered by decompilation.

## Evidence

- `inventory.json`: every member and hash, function size/address/binding, 116+
  data/table symbols, and the explicit external SDK/ROM dependencies.
- `pseudocode/manifest.json` and 186 adjacent `.c` files: complete export,
  direct calls, addresses and warnings. **This is inferred pseudocode, not
  original source or a compilable replacement.** Prototypes and field meanings
  still need verification against machine code and paired PCM tests.
- `provenance.json`: exact file and binary hashes.
- `headless-full.log`: Ghidra 12.0.4 analysis/export completion.

The analysis ELF links every selected object without garbage collection at
`0x43000000`, with relaxation disabled. Only external dependencies receive
addresses from the production ELF. AAC definitions and their relocations belong
to the newly linked text, so formerly discarded functions can be analyzed too.
**This ELF imports external addresses without their code and must never run or
be flashed.** It stays in the ignored `.build` directory.

The inventory pins the original decoder archive SHA-256 to
`311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.
Every AAC external reference is resolved either to another selected member or
an explicitly listed general SDK/ROM function. The preparer rejects missing or
ambiguous definitions and inventory changes.

## Reproduce

From the worktree root with the installed tools:

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& $python tools/codec_benchmark/prepare_full_aac_decompile.py `
  --archive C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec/lib/esp32c3/libesp_audio_codec.a `
  --firmware idf/esp32c3-oled-native/build-constants-audit/yoradio_esp32c3_oled_native.elf `
  --tool-prefix C:/Work/yoRadio/.idf/tools-v6.0.2/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf- `
  --output .build/aac-full-repeat
$env:JAVA_HOME = 'C:/Program Files/Eclipse Adoptium/jdk-25.0.3.9-hotspot'
& 'C:/Work/r36sx_disasm/ghidra_12.0.4_PUBLIC/support/analyzeHeadless.bat' `
  .build/aac-full-repeat aac-full `
  -import .build/aac-full-repeat/aac-full.elf -processor RISCV:LE:32:default -cspec gcc `
  -max-cpu 2 -analysisTimeoutPerFile 300 -scriptPath tools/codec_benchmark `
  -postScript DecompileAacMemory.java .build/aac-full-repeat/pseudocode inventory:.build/aac-full-repeat/functions.txt
& $python tests/test-aac-full-decompile.py
```

Use a fresh output folder or Ghidra's explicit `-overwrite` when repeating an
import. A different firmware ELF can provide external addresses, but its hash
and the newly linked ELF hash must be recorded. See the
[RAM execution plan](../../ESP32C3_HE_AAC_RAM_EXECUTION_20261001.md) for modifications
and validation; decompilation completion alone does not qualify a RAM layout.
