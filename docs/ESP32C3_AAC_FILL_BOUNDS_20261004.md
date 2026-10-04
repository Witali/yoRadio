# Bounded AAC fill element parsing

The ESP32-C3 AAC path now validates FIL lengths before copying SBR data or
skipping ordinary fill bytes. Both native entry points use the checked parser
in plain and compact builds. Correct FIL data remains byte-identical to the
pinned library, with no new heap allocations or persistent RAM.

## Defect and repair

The original `getfill` and `get_sbr_bitstream` advance `used_bits` according to
the advertised count without first verifying that those bytes exist. The SBR
copy loop then subtracts the byte cursor from an unsigned input length. After
crossing the end, that subtraction can wrap and permit reads beyond the declared
frame. Some original reads also use a two-byte load when one byte remains.

A direct test against the actual RISC-V library reproduces the cursor defect:
a count header in a declared 16-bit input leaves both original cursors at 2164
bits. The SBR copy reads padding beyond that declared input. This test deliberately
provides a larger backing buffer so the reproduction itself stays in allocated
storage; it is not a test of exploitability. The repaired functions reject the
span and leave the cursor at the exact 16-bit end.

The new implementation:

- Checks the count field, optional escape byte and complete payload against
  both `available_bits` and `input_length` before accessing the payload.
- Preserves `count = 15 + escape - 1`, including escape zero and the maximum
  269-byte count. This agrees with the pinned FAAD `fill_element` implementation
  and the actual native-library comparison.
- Uses byte loads and reads a second byte only when the requested bits cross
  its boundary. A valid element needs no readable padding in this helper.
- Preserves SBR and SBR-CRC types, the first low-half-byte payload convention,
  every copied byte, the element identifier, and the already-filled-slot behavior.
- Publishes no partial SBR element on invalid input. An invalid span moves the
  cursor to the byte end, allowing the audited controller's existing input-error
  path to handle it without unsigned remaining-length underflow.

The shared private ABI uses named fields in `aac_fill_parser.h`. All accessed
fields are cross-checked against the extended decoder view by the RV32 compiler.
The existing archive SHA-256 gate applies to these hooks as well.

Reference: pinned [FAAD syntax source](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/syntax.c),
and the repository's audited `getfill`, `get_sbr_bitstream` and
`PVMP4AudioDecodeFrame` exports under
`docs/audits/esp32c3-aac-core-symbolic-20261001/pseudocode/`.

## Verification

| Check | Result |
| --- | --- |
| Direct comparison with native FIL functions | 69,376 valid cases per QEMU build, all exact |
| Matrix | All 271 count encodings, 8 alignments, 16 extension types, 2 slot states |
| Host ASan and UBSan without input padding | 69,376 valid, 343,475 truncated and 4 invalid-state cases pass |
| Plain AAC QEMU build | Parser comparison, metadata and normal format/smoke checks pass |
| PC19 QEMU build | Parser, metadata, faults, recovery, transitions and pointer checks pass |
| Subsequent captured PCM versus previous PC19 | 865,280 channel samples, zero differences |
| Guest instructions for the same 12 SBR-gap phases | 252,439,833 → 252,445,844, +0.002381% |
| Instrumented library allocations and frees | 696 / 696; previous fault run was 700 / 700 |
| Decoder task minimum free stack | 2,844 bytes of 16,384 |
| Added parser persistent RAM | `.data = 0`, `.bss = 0`; no allocator calls |
| Physical integration image | Builds and contains calls to both checked wrappers |

The instruction count is from the emulator, not physical CPU time. Fewer
allocations reflect rejecting malformed FIL before unnecessary SBR allocation;
this is not a reduction in the memory needed by valid HE-AAC playback.

The first plain build failed to link because its vendor archive was scanned
after `libmain`. Explicit undefined-symbol linker options now retain both wrapper
objects. The failed build log is preserved. Disassembly of the physical image
confirms `compact5_PVMP4AudioDecodeFrame` calls `__wrap_get_sbr_bitstream` and
`__wrap_getfill`; merely finding wrapper symbols in the ELF was not the only check.

## Build artifact and remaining work

The physical integration image is saved at
`firmware/development/esp32c3-aac-fill-network/app.bin`, with hashes in its manifest.
It uses the existing PC18 storage and network diagnostics, DIO 80 MHz, with deep
sleep disabled. It has not been flashed or physically qualified. PC19 and the
late-SBR experiment remain gated separately; this repair does not promote them.

This closes the identified FIL-helper boundary defect. Other native bit readers,
Huffman decoding, malformed syntax beyond FIL, transport truncation, same-decoder
recovery, physical playback/CPU/OTA and all-codec acceptance remain open. The
full-radio goal is not complete.

## Reproduction

[Retained evidence](../tests/results/esp32c3-aac-fill-20261004/) includes configs,
source snapshots, sanitizer results, diagnostics, PCM and image fingerprints.

```powershell
python tests/run-aac-fill-parser.py
python tests/test-aac-fill-parser.py --compiler PATH/TO/riscv32-esp-elf-gcc.exe
python tools/codec_benchmark/run_aac_fill.py `
  --build idf/esp32c3-oled-native/build-qemu-aac-fill-pc19 `
  --dependency-root C:/Work/yoRadio/.idf --output .build/aac-fill/recheck `
  --qemu PATH/TO/qemu-system-riscv32 --bios PATH/TO/qemu/bios --wsl
```

For the plain build, add `--plain` and select its recorded build directory.
Omit `--wsl` when using a native Windows QEMU executable.
