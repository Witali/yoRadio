# ESP32-C3 GCC instruction audit: optimization follow-up

Recorded on 2026-10-08. Status: **planned**. Prioritize measured codec hot
loops, starting with FLAC Rice decoding and LPC reconstruction; see the
[hot-loop study](ESP32C3_FLAC_HOTLOOPS_20261008.md).

## Target capabilities and current observation

ESP32-C3 implements RV32IMC. It does not provide the standard Zbb `clz`, `ctz`
and `cpop` instructions. Those instructions belong to an optional RISC-V
extension, so another RISC-V processor may support them while C3 does not.
Sources: [Espressif datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.html),
[RISC-V bit-manipulation specification](https://docs.riscv.org/reference/isa/v20260120/unpriv/b-st-ext.html).

The existing `r9a97-flac-rice-bytewise` build uses
`-march=rv32imc_zicsr_zifencei -mtune=esp-base`. Its linked
`readRiceSignedInt(unsigned char)` calls `__clzsi2` at ROM address `0x4000079c`.
The pinned SDK's `components/esp_rom/esp32c3/ld/esp32c3.rom.libgcc.ld` resolves
that symbol. This is a software helper, not a hardware CLZ instruction. The
address is an observation for this build, never an address to hard-code.
Observed ELF SHA-256:
`a1bce686a8a5b1b629fa4778fb4bc6590b4fdc354c1696efaf1a09797ee159be`.

## Operations to inspect

| Operation | Candidate expression / generated code to inspect |
| --- | --- |
| Leading zero bits | Guarded `__builtin_clz`; actual helper calls, branches and loads |
| Leading one bits | Leading-zero count of a width-correct unsigned complement; handle all-ones input |
| Trailing zero bits / first set bit | Guarded `__builtin_ctz`, or `__builtin_ffs` with its different zero/index semantics |
| Total one bits | `__builtin_popcount`; distinct from counting a consecutive run of ones |
| Wide integer products | `mul`, `mulh`, `mulhu`, `mulhsu` from extension M; verify signedness and any remaining multiword helper calls |
| Byte swaps, rotates, masks and sign extension | Inspect emitted shifts/masks; do not assume optional bit-manipulation instructions exist on C3 |

GCC builtins express operations but do not guarantee one hardware instruction.
Traditional `__builtin_clz(0)` and `__builtin_ctz(0)` are undefined; preserve
explicit zero handling. See [GCC bit-operation builtins](https://gcc.gnu.org/onlinedocs/gcc/Bit-Operation-Builtins.html).

## Experiment checklist

- [ ] Capture the chip, SDK/toolchain revision, effective `-march`/`-mtune`,
  optimization flags, per-function pragmas and LTO state. Expand response files
  referenced by `compile_commands.json`. Only enable extensions supported by
  the actual chip; a compiler accepting `-march` is not proof of hardware support.
- [ ] Inspect both the object and **final linked ELF**, including inlined
  callers, ROM/library helpers, register spills and loop branches. Record
  instructions and code size before/after; a function name disappearing may
  mean it was inlined rather than removed.
- [ ] For C3 Rice decoding, compare the current ROM helper with a bounded
  inline shift/compare implementation and small nibble/byte lookup tables.
  Measure call overhead, flash/cache effects and table/code RAM cost. Treat
  each as a candidate, not an assumed improvement.
- [ ] Compare ordinary C/C++ and builtins first. Consider inline assembly only
  for a demonstrated compiler limitation, with explicit constraints/clobbers
  and a portable fallback. Do not enable Zbb to force unsupported instructions.
- [ ] Verify zero/all-ones inputs, each bit position, partial-byte widths,
  signed conversions, shift boundaries and truncated Rice codes. Require
  unchanged reader consumption/error state and exact FLAC PCM against the
  scalar reference; retain sanitizer checks.
- [ ] Benchmark real hot-loop inputs on C3, then whole-stream playback with
  Wi-Fi/TLS and output DMA active. Report cycles/time, linked code size and RAM
  separately. Accept only a measured benefit without audio or runtime regressions.

Useful read-only commands in the configured toolchain environment:

```text
riscv32-esp-elf-readelf -A app.elf
riscv32-esp-elf-objdump -d -C app.elf
riscv32-esp-elf-objdump -dr -C decoder.cpp.obj
riscv32-esp-elf-nm -S --size-sort -C app.elf
```

Use actual build paths in place of the illustrative filenames. ELF attributes
and disassembly describe generated code; the chip documentation determines
which instructions are legal. Repeat this audit after toolchain upgrades.
[GCC RISC-V target options](https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html).
