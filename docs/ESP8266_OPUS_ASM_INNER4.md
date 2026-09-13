# Opus ASM: inner product unroll4

2026-09-14. Candidate `bands-inner4-asm`, parent `bands-tell-inline-asm`.
Status: implemented as an opt-in experiment; physical acceptance pending.

## Scope and exactness

Only the inlined `celt_inner_prod(X,X,N)` energy loop in
`renormalise_vector` changes. No global compiler unrolling or pitch/PLC
changes. For N >= 8, process complete groups of four, then the original
scalar loop for the remaining 0..3 elements. N <= 0 keeps the original
guard. N 1..7 retains the scalar loop, with one additional threshold branch.

The bulk loop executes 14 instructions for four elements instead of 20.
There are four entry instructions and one tail check. These are instruction
counts, **not an LX106 cycle prediction or an end-to-end speed measurement**.
Paired signed 16-bit loads preserve access widths; nothing reads past N.
Every multiply and accumulation has exactly the original order and low
32 bits, including wraparound. No reassociation, saturation or approximation.

`a4` and `a7` are extra dead caller-saved temporaries. The original live
registers, input memory and SAR are unchanged at the join. Stack remains
32 bytes; no new buffer/table/heap/static RAM. The object function grows
181 -> 233 bytes; linker/image sizes still require separate verification.

## Checklist

- [x] Separate ASM overlay on the best tell-inline parent; C default unchanged.
- [x] Comments describing entry/join registers, tail and fixed-point semantics.
- [x] Actual-instruction tests: 6162 cases, lengths 1..1024/1536/2047/2048,
      extreme int16 inputs, wraparound, 2-byte alignment and read bounds.
- [x] Host ASan/UBSan exact PCM through 192, 320 (2.5/5/10/20 ms) and
      510 kbit/s; PLC/reset/OOM and arena/scratch guards.
- [x] Linked disassembly, same build settings and static RAM/stack.
      Function +52 bytes; app 903216 -> 903280 bytes (+64 including alignment).
      IRAM text 22900, IRAM BSS 4044, vectors 128, DRAM data 1652 and BSS
      18752 bytes remain identical. Flash text +52, flash rodata +4 bytes.
- [ ] At least 10 physical A / 10 B / 10 A; retain all failures/outliers.
- [ ] Record CPU, maxima and free RAM; apply the high-bitrate acceptance rule.
- [ ] Restore ordinary I2S PDM radio via OTA; verify WebUI/playlist/status.

Speed tests use RAM-resident packets with network audio, PDM and detailed
profiling off. They do not qualify continuous live playback. A successful
candidate needs >=20 seconds of I2S PDM plus WebUI before production adoption.
192 kbit/s is a measurement target, not a decoder bitrate limit.

Reproduction:

```text
node tools/esp8266_opus_asm/inner4.cjs <xtensa-lx106-elf-gcc.exe>
node --test tests/esp8266-opus-inner4-asm.test.js
node tools/esp8266_opus_asm/check_bands.cjs inner4
```
