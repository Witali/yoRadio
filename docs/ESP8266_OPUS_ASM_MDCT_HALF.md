# Opus ASM: MDCT signed-half selection, frozen layout

2026-09-14, ESP8266 / LX106 160 MHz, QIO40. Independent candidate after
[unsuccessful duplicate-load replacement](ESP8266_OPUS_ASM_FROZEN_RELOADS.md).

- [x] Build five exact17-byte instruction replacements over the best tell-inline
  control. Three pre-rotation coefficient/bitrev reads, two TDAC window reads.
- [x] Keep all other ELF bytes, function/table addresses, RAM,96-byte MDCT stack,
  original aligned L32I accesses and register allocation unchanged.
- [x] Prove all32 input bits, both pointer parities, all registers and SAR.
- [ ] At least10 physical A/B/A runs, all attempts/peaks/memory retained.
- [ ] Archive results, accept only actual high-bitrate gain, restore normal radio.

Old sequence: mask=2; sign-extend low half; test address; optionally overwrite
with signed high half and jump to next instruction. New: mask=2; BBSI to high
half; otherwise low extension and jump past high path. The high path executes
3 instead of6 instructions, low5 instead of4. Alternating adjacent halfwords
average4 versus5; this is NOT a CPU-cycle or full decoder speed measurement.

No paired word-load optimization yet, no transform-size assumption, no new
buffer, no PCM approximation and no bitrate cap. No table bounds change.
Both17-byte slots use the original locations. Everything except the five
slots and image checksum/digest is byte-identical to the control app.

Generator: tools/esp8266_opus_asm/mdct_half.cjs. The source snapshot and C
fallback are untouched. Diagnostic candidate only, not default. Comments
in patches.s describe ABI and changes. A linker script fixes five standalone
sections at their original addresses; final app is repacked with SDK elf2image.

Artifacts: firmware/development/esp8266-opus-mdct-half-{control,candidate}-v1.
App903216 B, candidate SHA256
f74fb6f9b2dfd2bd4fd51ac63b772503dbe93b2917c2b012f5e4c15d223c3d97.
Control SHA2560129559856a9b339ec8428d903fc3e9bd3a4489bc127f1ed7a310d127d310811.

Goal remains raw decoder CPU192 <=70%, then >=20 seconds continuous I2S PDM
with working WebUI. No such result is claimed by static verification.
