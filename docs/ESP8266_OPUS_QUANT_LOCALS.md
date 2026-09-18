# Opus ASM: constant local scalar copies

Date: 2026-09-18. CPU160/runtime QIO40, raw Opus-only experiment.
Parent is accepted eBands-final, **not** the unaccepted quant-flags or packed
quant-decode images. Production defaults and original C fallback unchanged.

## Hypothesis

Replace23 L32I instructions reading proven local0/1 copies with three-byte
MOVI, without changing any instruction PC, width, register destination,
branch, arithmetic, call, frame or literal address. This removes23 static
DRAM read sites, not23 dynamically executed instructions. No speedup is
assumed: the previous18 ctx-only read experiment did not pass both gates.

The69 patched bytes are in the original9416-byte `quant_all_bands`, keeping
all3370 disassembled instructions and the384-byte call0 frame. No RAM,
scratch, callee-save or SAR change. Source comments identify each PC, local
slot and the value proven at that specific point. All18 ctx reads from the
previous experiment remain original L32I.

## Correctness contract

Slots SP124/132/140/192/220/240 are **not** globally immutable. For example,
SP132 contains0 at0x402521c5 and1 at0x40252a20. Other reads of SP192 remain
dynamic and are not replaced. The existing converged constant-propagation
analysis is observed without changing its CFG, transfer, call/alias/partial-
write invalidation or join rules; its original outputs must still match.
Only the23 pinned PCs with proven per-use values qualify.

The original native-caller/valid-object/private-frame contract is rechecked
against the accepted linked ELF and C sources, including indirect ROM calls
and address-taken checks. Linked proof requires every other instruction to
remain exact. ELF/app comparison allows only69 patch bytes and the required
application checksum. No bitrate or mode restriction is introduced.

The host model checks origins of the spilled flags and initial local values;
it is not a one-to-one execution of Xtensa stack accesses. Local lifetime and
per-PC substitutions are covered by the separate linked proof. All24 host
PCM/state/guard/reset/OOM/ASan/UBSan scenarios pass, including12..510kb/s,
short and120ms/48-frame packets, mixed modes and phase/VBR fixtures.

Tools: `quant_locals.cjs`, `quant_locals_proof.cjs`,
`check_bands.cjs quant-locals` and `report_quant_locals.cjs` under
`tools/esp8266_opus_asm/`. Negative regressions invalidate contracts, partial
local stores, initializer sources, instruction operands and destinations.

## Required physical gate

- [x] Fresh10A/10B/10A2,15s observation, retain every attempt and maximum.
- [x] Target PCM hashes/counts, scratch/RAM, both high-bitrate speed gates.
- [ ] Separate75% raw CPU target and later20s live I2S PDM/WebUI requirement.
- [x] Restore ordinary accepted ASM radio via native OTA, check HTTP/WS/playlist.

Artifacts: `firmware/development/esp8266-opus-quant-locals-{control,candidate}-v1/`.
Runs: `.build/opus-quant-locals-board-20260918/`. Native OTA only; no UART,
GPIO3 reset, Wi-Fi adapter changes, partition or SPIFFS writes.

## Physical result: not adopted

All 30 attempts completed with exact PCM hashes, sample/packet counts and
identical scratch high-water marks. Median raw task CPU percentages:

| Fixture, kb/s | A control | B local constants | A2 control |
| --- | ---: | ---: | ---: |
| mono 12 | 23.082958 | 23.090063 | 23.085771 |
| mono 24 | 53.905729 | 53.879854 | 53.886146 |
| stereo 64 | 61.196333 | 61.193167 | 61.205750 |
| stereo 128 | 70.364667 | 70.373354 | 70.374750 |
| stereo 192 | 77.868250 | 77.876125 | 77.881708 |

Both relative-speed gates fail. Against A, the minimum high-bitrate gain
is -0.012346% (a small slowdown). Against A2, the minimum gain is 0.001983%,
smaller than the 0.018590% loss at mono 12. These tiny differences do not
establish a meaningful speed change. Keep accepted eBands-final as baseline;
do not add this candidate or the previous quant-flags experiment to it.
The active 75% raw CPU target remains unmet, and this benchmark does not
qualify 20 seconds of continuous radio/I2S PDM/WebUI playback.

Evidence is deliberately unfiltered:

- Minimum free DRAM: A 904 B, B 896 B, A2 740 B. Lifetime free task stack:
  1660 B in every series. These are whole benchmark observations, not proof
  of a full-radio memory reserve or a per-decoder heap increase. Linked
  static RAM and the 384-byte function frame are unchanged.
- Maximum single-call wall time at 192 kb/s: 19977 / 28429 / 27993 us.
- B/run8 and A2/run5 contain diagnostic HTTP timeouts and CPU outliers
  of 90.003125% and 90.006125%. Both remain in medians, maxima and reports.
  Their presence in unchanged control too does not identify their cause.
- Task/wall accounting windows differ. Positive task-minus-wall excesses
  at mono 12 are retained: A/run7 149 us, B/run10 1099 us, A2/run7 413 us.
  No clamping or post-hoc subtraction is used.
- Scratch high-water reports are identical across all series: byte-area
  1808/2904/5488 B and word-area 14112/15600/15600 B for mono12/mono24/
  stereo respectively. The historical `scratch_words` counter is a byte
  size of the word-access arena, not a count of 32-bit words.

Local regression run: 42 passed, 0 failed, 0 skipped, including eight codec
ownership configurations with 100 mixed cycles each, injected allocation
failures, cancellation/reconnect cleanup and the linked ASM negative tests.
Logs from both pre-final and final test invocations are retained. The host
origin test now reads the saved correctness report instead of relying on
an ignored `.build` report. This does not replace the linked target proof.

Ordinary accepted heapreserve ASM radio was restored through native OTA:
HTTP 200/OK, slot 0x110000 -> 0x10000, app SHA256
`dfa1c0a298dde56f33d5bb88627b4c9aa643deca12d5329ce4a0398e6f60b273`.
HTTP status, WebSocket `getindex=1` and the unchanged 13016-byte playlist
responded. Final snapshot: stopped, no error, RSSI -47 dBm, combined free
heap 30328 B. This is not a browser-rendering, acoustic or endurance test.
As documented in the memory audit, the later detection-cancellation fix
is source-tested but not included in this restored image.

`comparison.json`, every raw JSON/log, OTA reports, initial/final snapshots
and local test logs are saved alongside the candidate firmware. Result
regressions independently recompute all medians, hashes, PCM counts,
selection and the current 75% target from the saved 30 attempts.
All three result regressions pass (0 failures, 0 skips).
