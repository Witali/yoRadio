# Opus ASM: paired MDCT bitrev word reads

2026-09-14, LX106 CPU160/QIO40. Control is the accepted experimental
[MDCT half selector](ESP8266_OPUS_ASM_MDCT_HALF.md), not the older tell-inline alone.

- [x] Replace one24-byte pre-rotation block, preserving all other ELF bytes.
- [x] Keep a loaded32-bit bitrev word in a0 for two adjacent int16 entries.
- [x] Validate actual four immutable flash tables, alignment, bounds and mode.
- [x] Prove signed extraction for arbitrary word bits, scratch liveness and ABI.
- [ ] Minimum10 physical A/B/A, exact PCM, all maxima and free RAM retained.
- [ ] Archive decision and restore ordinary radio over OTA.

The unchanged96-byte prologue saves return address a0 at sp+92. No instruction
in the pre-rotation loop uses a0; the following FFT CALL0 overwrites it before
observing it, and function return restores the original address from sp+92.
This allows one register of temporary storage without another array/stack slot.
Removed temporary values a2/a5/a7 are overwritten before their next read.
All other live registers and SAR are unchanged. No memory writes are introduced.

First/low iteration: BBSI not taken, aligned L32I a0,a12,0; sign-extend low half.
Next/high iteration: reuse signed high half of a0, no second load. a12 advances
by2 in the unchanged loop. Per pair: two loads become one,14 instructions become8
inside this block. This is NOT a CPU-speed prediction. Four padding bytes are
unreachable; both paths explicitly branch to the original continuation address.

Actual standard Opus mode has bitrev counts480/240/120/60. All are word-aligned
immutable flash arrays; the public decoder creates the pinned48000/960 mode.
Generator rejects a different parent/table layout. No codec bitrate limit or
packet-duration restriction is added;320/510 kbps and PLC share the same tables.
This specialized diagnostic is not a general arbitrary custom-CELT-mode API.
Other architectures and custom configurations retain the original C fallback.
The last iteration performs no new read beyond the original table; post-rotation
in-place ordering and TDAC/window accesses are not modified in this experiment.

Generator: tools/esp8266_opus_asm/mdct_bitrev_pair.cjs. App903216 B,
candidate SHA2563095072ae7bed52ce2fb83b815122487e20403f5adbacd14116d91e363bf0274.
Saved under firmware/development/esp8266-opus-mdct-bitrev-pair-{control,candidate}-v1.
Default/C fallback/source snapshot unchanged. Goal70% remains unproven.
