# Opus ASM: three loads instead of four in FFT radix-5

2026-09-14, CPU 160 MHz / QIO40. Parent: accepted
[MDCT post-rotation pairs](ESP8266_OPUS_ASM_MDCT_POST_PAIR.md).

- [x] Locate the exact GCC ASM/linked instruction group.
- [x] Preserve the eight-byte range with three loads and no executed padding.
- [x] Prove exact registers and ordered reads for arbitrary memory values.
- [x] Verify no interior or indirect branch, no new RAM/frame or changed ABI.
- [ ] Complete 10 A /10 B /10 A2 physical raw runs and evaluate both speed gates.
- [ ] Save every attempt, maxima/RAM, decision, and restore ordinary radio OTA.

## Change

In the saved GCC kiss_fft.c.s, label .L54 implements `scratch[0] = *Fout0`
inside the radix-5 loop. It reads the same task-private sp+32 pointer twice:

```asm
# Original: 2+2+2+2 bytes.
l32i.n a2, a1, 32
l32i.n a3, a1, 32
l32i.n a2, a2, 0
l32i.n a3, a3, 4

# Candidate: 3+2+3 bytes.
l32i   a3, a1, 32
l32i.n a2, a3, 0
l32i   a3, a3, 4
```

Only [0x40254126,0x4025412e) changes. There is no NOP, new branch, literal,
array or spill. Other ELF bytes and instruction/table addresses stay fixed.
After the group, a2/a3 have the same complex r/i values; all other registers,
SAR and memory are unchanged. The two data loads stay in the same order.
The removed operation is a duplicate private-stack read, not MMIO or shared
input. The symbolic proof covers arbitrary word values and possible data
aliasing. No bitrate/mode or numerical-precision restriction is added.

This differs from the rejected frozen-reloads experiment: that retained four
instructions by replacing one L32I with MOV. Here the whole group has three
instructions. Narrow/wide encoding preserves layout, but the shorter sequence
alone does not prove lower cycle count, especially with load dependencies.
The existing C_MUL_TABLE already reads twiddle r/i as one packed word; that
earlier optimization is unchanged and is not credited as a new improvement.

## Evidence and reproduction

`node tools/esp8266_opus_asm/fft_load3.cjs` generates both images and verifies
actual linked opcodes, unchanged memory/addresses and image checksums.
Commented code: fft_load3.s. Report: report_fft_load3.cjs. Tests:
tests/esp8266-opus-fft-load3.test.js, including negative mutation guards.
10 pre-deployment related tests PASS; no source C or saved GCC ASM changes.

Artifacts: firmware/development/esp8266-opus-fft-load3-{control,candidate}-v1.
Both app.bin images are 903216 B. Candidate SHA256:
081444a69f1f32fb407bbe39f06ae9175980e6fbefbbab124e1628f78bb682e0.
Control SHA256:
5e5525a242f5145db2aa5888ea76bd8f4515e3f7910333ec5f7d12cedaced7d4.
No production/default change. Physical performance is not yet accepted;
70% CPU192 and continuous I2S PDM/WebUI remain unproven.
