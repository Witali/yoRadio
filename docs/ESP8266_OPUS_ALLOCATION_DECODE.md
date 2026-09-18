# Decoder-only allocation ASM — 2026-09-18

Experimental variant over accepted eBands-final; **rejected, not promoted**. The goal
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

- [x] Fresh10 A /10 B /10 A2 at CPU160/runtime QIO40, 15-s observation.
- [x] Exact target PCM, all attempts/outliers/maxima/low-DRAM observations.
- [x] Both high-bitrate gates checked: FAIL; <=75% raw CPU192 also FAIL.
- [x] Restore ordinary heapreserve ASM radio and verify HTTP/WS/playlist.
- Not applicable: rejected candidate is not relocated into the full radio.
  The accepted baseline still needs >=20s continuous I2S/WebUI qualification.

Artifacts are under `firmware/development/esp8266-opus-allocation-decode-`
`{control,candidate}-v1`. No UART, partitions, SPIFFS or PC Wi-Fi changes.

```text
node tools/esp8266_opus_asm/allocation_decode.cjs
node tools/esp8266_opus_asm/check_bands.cjs allocation-decode
node --test tests/esp8266-opus-allocation-decode.test.js
node tools/esp8266_opus_asm/report_allocation_decode.cjs
node --test tests/esp8266-opus-allocation-decode-results.test.js
```

## Physical result: no promotion

All 30 attempts completed with exact PCM hashes, sample and packet counts.
These are RAM-packet raw decoder measurements: network audio, PDM and
function/stage profiling are disabled; Wi-Fi/WebUI and timing bookkeeping
remain enabled. They do not establish live-radio CPU or continuity.

| Source stream | A CPU budget | B CPU budget | A2 CPU budget |
| --- | ---: | ---: | ---: |
| Mono 12 kb/s | 23.086083% | 23.098979% | 23.093521% |
| Mono 24 kb/s | 53.888750% | 53.866563% | 53.892938% |
| Stereo 64 kb/s | 61.181292% | 61.163687% | 61.208646% |
| Stereo 128 kb/s | 70.376938% | 70.352396% | 70.381438% |
| Stereo 192 kb/s | 77.861000% | 77.851250% | 77.869417% |

The 192-kb/s relative gains are only 0.012522% and 0.023330%, smaller than
the 12-kb/s relative losses of 0.055860% and 0.023636%. Both selection gates fail.
The first 192-kb/s difference is 0.009750 CPU percentage points, equivalent to
about 1.95 us per 20-ms frame. This small median change inside overlapping
timing ranges is not evidence of a reliably faster full player. Removing
unexecuted encoder code mostly changes instruction layout/cache behavior;
it does not remove 67 executed instructions from each decoded frame.

Keep eBands-final. Its accepted historical 192-kb/s reference remains 77.880896%;
the new candidate's 77.851250% does not achieve the current 75% target.
The original C fallback, default backend and ordinary radio are unchanged
by this experiment. The retained instruction proof and smaller live body
may be reused in a separately measured combination, not silently promoted.

### Maxima, memory and observation failures

| Measurement | A | B | A2 |
| --- | ---: | ---: | ---: |
| Maximum 192-kb/s decode wall call | 19.972 ms | 20.678 ms | 28.140 ms |
| Maximum 128-kb/s decode wall call | 22.097 ms | 21.658 ms | 27.978 ms |
| Minimum free DRAM | 900 B | 896 B | 1048 B |
| Minimum lifetime free task stack | 1660 B | 1660 B | 1660 B |
| Maximum 192-kb/s raw CPU budget | 77.903417% | 77.942625% | 90.011750% |

No attempts were removed or replaced. A2/run9 has a polling timeout and
the 90.011750% outlier; it subsequently finished successfully and remains
in every statistic. A/run1 and run4 mono12 have task_us exceeding wall_us
by 3718 and 106 us. Those windows measure different work; the excess is
retained rather than clamped or subtracted. The low DRAM observations also
remain; a successful raw decoder run is not full-radio memory safety.

The combined preflight/lifecycle/reconnect run passed 30/30 with zero skips.
Three result regressions passed: authenticate all 30 saved raw JSON files,
recompute medians/maxima/selection decisions, and verify ordinary-radio
OTA restoration plus the recorded WebUI responses.
Raw reports, confirmed OTA slots, manifests and logs are archived with
the candidate under firmware/development, not only in an ignored build.

## Restore and remaining work

After explicitly checking benchmark state 3/error 0, restored ordinary
`esp8266-opus-live-asm-heapreserve-20260918` via OTA, HTTP200/OK and slot
0x110000 -> 0x10000. SHA256:
`dfa1c0a298dde56f33d5bb88627b4c9aa643deca12d5329ce4a0398e6f60b273`.
It carries the accepted 18-stage ASM chain plus the non-memory reconnect
retention and actual-DRAM reserve corrections, not this rejected patch.

HTTP status/audio, WebSocket getindex and playlist were checked. The board
is stopped without an error, RSSI -49 dBm, combined free heap 30328 B.
Playlist wire size 13016 B, SHA256
`79b401c4d433e39ab1134a9d0776f62eea888eedffaa79c3a35851ae2fac5185`.
No UART access, reset, PC Wi-Fi change or shutdown was used. This was an
API check, not a visual browser or acoustic/continuous-audio test.

The [memory report](ESP8266_OPUS_MEMORY_RECONNECT_2026-09-18.md) remains
the authority for full-radio fragmentation: retained network allocations,
the post-Stop DRAM difference and live underruns still require investigation.
