# Decoder-only allocation ASM — 2026-09-18

Experimental variant over accepted eBands-final; **not promoted**. The goal
remains <=75% CPU at 192 kb/s plus continuous I2S/WebUI. Smaller code alone
does not establish either result.

## Change and contract

`clt_compute_allocation` receives `encode=prev=signalBandwidth=0` from the
single native CELT caller. The original C implementation and saved GCC ASM
are unchanged. A separate frozen-layout overlay removes 67 encoder-only
instructions and three constant branches, preserving all audio-dependent
branches, integer arithmetic, load/store widths and external references.

The conditional [earlier audit](ESP8266_OPUS_ALLOCATION_DECODE_AUDIT.md) is
extended as follows:

- Backward CFG reaching definitions establish callerSP+80 as the local
  base at this call, not an assumed decoder-state pointer. The scalar
  output addresses are callerSP+236, +232 and +180. They cannot overlap
  the outgoing encode/prev/bandwidth arguments at +40/+44/+48.
- Three output arrays trace to bounded scratch allocations, separate from
  the task stack. A valid entropy decoder object is external or the
  caller's private `_dec`. Pinned source does not modify or take the address
  of the by-value encode parameter. This is the valid native C decoder
  object contract, not a promise about arbitrary invalid pointers or RAM
  corruption.
- The accepted ELF has one direct call into the function and no raw address
  references to its range in allocated PROGBITS, scanning every byte
  alignment. Pinned C sources contain only definition and decoder call.
  All three indirect calls resolve to ROM `__udivsi3` at 0x4000e21c, as
  specified by the SDK ROM linker file. No arbitrary callback is used.
- An independent check compares all 930 retained assembled instructions,
  branch destinations, literal/call addresses and operands with the
  projected original. Negative mutations must be rejected.

The valid bitrate/mode domain is not narrowed. The optimization relies on
decode versus encode, not a 192-kb/s test ceiling. PLC and invalid-packet/OOM
handling retain the same bounded decoder behavior.

## Preflight

Original function span2564 B; new live code2345 B with219 B unreachable
padding to retain every other address. The192-B frame, static RAM and
application size903216 B are unchanged. This is not a219-B app saving.

Candidate SHA256:
`3afa449c417903c91126c35940955a4fba0fe5ba30d294db6af6159cccca57fe`.

Seven regressions pass. The host semantic model gives exact PCM/state in
24 ASan/UBSan cases: 12..510 kb/s, SILK/hybrid/CELT, mixed/reset/PLC/OOM,
2.5..20-ms frames, VBR/packed frames and120-ms compound packets. This
validates the C semantic mirror, not physical LX106 execution or speed.

## Physical gate

- [ ] Fresh10 A /10 B /10 A2 at CPU160/runtime QIO40, 15-s observation.
- [ ] Exact target PCM, all attempts/outliers/maxima/low-DRAM observations.
- [ ] Both high-bitrate gates; separately check <=75% raw CPU192.
- [ ] Restore ordinary heapreserve ASM radio and verify HTTP/WS/playlist.
- [ ] If accepted, relocate into full radio and qualify >=20s I2S/WebUI.

Artifacts are under `firmware/development/esp8266-opus-allocation-decode-`
`{control,candidate}-v1`. No UART, partitions, SPIFFS or PC Wi-Fi changes.

```text
node tools/esp8266_opus_asm/allocation_decode.cjs
node tools/esp8266_opus_asm/check_bands.cjs allocation-decode
node --test tests/esp8266-opus-allocation-decode.test.js
```
