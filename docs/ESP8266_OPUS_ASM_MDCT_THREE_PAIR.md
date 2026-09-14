# Opus ASM: shared-parity MDCT t0/t1/bitrev pairs

2026-09-14. ESP8266 LX106, CPU160/QIO40. Independent experiment after
[standalone bitrev](ESP8266_OPUS_ASM_MDCT_BITREV_PAIR.md), which was NOT accepted.
Control is accepted MDCT-half/tell-inline, not that rejected bitrev candidate.

- [x] Reschedule pre-rotation yr arithmetic to free a14/a15, no spills.
- [x] Cache t0/t1/bitrev words in a14/a15/a0, one shared parity branch.
- [x] Validate actual linked table alignment, bounds, mode and loop ABI.
- [x] Symbolic modular32 proof for450 pairs/all four transforms;16 numeric
  full transforms including PCM32 extrema, deterministic random, strides1/2
  and deliberately aliased input/output. No arithmetic rounding relaxed.
- [x] Preserve every other ELF byte, function/table address, RAM and stack.
- [ ] Complete10 control /10 candidate /10 repeated control physical runs.
- [ ] Save selection/maxima/RAM, restore ordinary radio and verify HTTP/WS.

## Exact transformation

In clt_mdct_backward_c, replace only [0x40247268,0x40247329):193 bytes.
Live instructions use160 bytes, followed by33 unreachable padding bytes.
All other ELF bytes, including original96-byte frame and FFT CALL0, unchanged.

For each pair of iterations: load aligned32-bit t0/t1/bitrev on the low half,
retain words in registers, take high halves on the following iteration.
One BBSI tests all three pointers' phase. The invariant -2*N4 stack value and
t0 address are needed only on the low half. Six table loads become three,
two stack reads of that invariant become one. Other PCM/stack reads and
all writes retain their sequence and values. No new array/stack slot.

yr uses a7 accumulator/a11 scratch, then yi uses the original a4/a5/a8/a2.
Reassociation is confined to modular32 ADD; each MULL, SRAI15 and SLLI1
term retains its own rounding/overflow semantics. Low unsigned16 products
are NOT changed to MUL16S. SAR unchanged. This is not reduced-precision PCM.

Original a0 is saved at sp+92; no loop call can destroy cached words.
At exit original instructions restore a15=yp from a9 and pass original
FFT arguments. FFT kills a0; a14 is overwritten before the following use.
Original epilogue restores a0/a12..a15. All tables immutable flash/L32I,
no unsafe16-bit flash/IRAM access introduced.

Actual standard MDCT N4=480/240/120/60, all even, all t0/t1/bitrev bases
word aligned. Proof checks linked mode48000_960_120 and its four FFT states.
No bitrate cap or packet-duration restriction is added. Not a general
arbitrary CUSTOM_MODES API: other builds keep the original C fallback.
Post-rotation/TDAC table accesses are unchanged in this experiment.

Per pair in the two-iteration proof:135 reachable instructions become106;
an intermediate high iteration has one extra back J in both variants.
Instruction counts are NOT cycle counts or predicted whole-decoder gain.

## Reproduction and evidence

Generator: tools/esp8266_opus_asm/mdct_three_pair.cjs, commented source
mdct_three_pair.s. Reporter: report_mdct_three_pair.cjs.
Tests: tests/esp8266-opus-mdct-three-pair.test.js (mutation guards included).

firmware/development/esp8266-opus-mdct-three-pair-{control,candidate}-v1/app.bin
are903216 B. Candidate SHA256:
9de8b4f8ea18ff9ec51eb71f699de12f68968e8309919fdb0f9f5e9955f7572a.
Control SHA256:
f74fb6f9b2dfd2bd4fd51ac63b772503dbe93b2917c2b012f5e4c15d223c3d97.
preflight.json, patches.s/elf, parent.elf.gz and sdkconfig saved beside image.

Fresh host tell-inline semantic parent11 scenarios exact (through320/510,
mixed/PLC/reset/OOM). Host does NOT execute new Xtensa ASM. New instructions
are checked by interpretation of actual linked disassembly plus physical
PCM hashes.12 related Node tests PASS/0skip before candidate deployment.

Raw runs use RAM-preloaded reproducible packets, no network audio or
PDM/output/function/stage profiling. CPU includes charged interrupts and
unchanged benchmark bookkeeping. Goal70% and live I2S qualification not yet
achieved. Default/ordinary firmware and C backend are unchanged.
