# Branchless eBands pair: tested and rejected — 2026-09-18

Candidate `esp8266-opus-ebands-src-candidate-v2` is based on the accepted
`eBands-final-candidate-v2`, not the rejected quant/u16 experiments.
It replaces only the existing36-byte leaf at0x4024dd48; its caller at
0x40248418 and all other instructions/addresses remain unchanged.

The leaf loads `align(p)` and `align(p+2)`, sets SAR with `SSA8L`, then
uses `SRC` to extract the exact signed16 pair. Both accesses remain inside
the44-byte table, including the last pair. Other GPRs are unchanged;
the only caller overwrites SAR with `SSL a4` before using it.
The ISA semantics were checked against the
[Cadence Xtensa ISA summary, SRC/SSA8L](https://www.cadence.com/content/dam/cadence-www/global/en_US/documents/tools/silicon-solutions/compute-ip/isa-summary.pdf).

Preflight passed132416 numeric cases plus independent symbolic bit proofs,
all21 table pairs/all64 initial SAR values and negative ABI/bounds tests.
Six regression tests passed. The host semantic mirror passed24 exact PCM,
state/reset/OOM/PLC cases, including510kbps and120ms packets.
No new RAM, stack or image bytes:903216B, candidate SHA256
`95584ccfcf27e3d20807dce204b02a925497273900a01a1f32de4065169fc697`.

This is **not an accepted speed improvement**. It executes12 instructions
and two loads per pair, versus6/9 instructions and1/2 loads in the accepted
leaf. Fewer branches do not prove fewer cycles. Initial hardware testing
was deferred for the user's full-radio fragmentation investigation; the
complete physical A/B/A test below was performed afterwards.

## All 30 physical measurements

Ten new independent attempts each for accepted control A, SRC candidate B
and repeated control A2. CPU160/runtime QIO40; identical RAM packet corpus
12/24/64/128/192 kb/s and 15-s observation interval. No network audio,
normalization, PDM output or function/stage profiler inside this benchmark.
The Wi-Fi/WebUI service stays enabled; task time includes charged ISR and
timing bookkeeping. No attempt or outlier was omitted.

| Source stream | A CPU budget | B CPU budget | A2 CPU budget |
| --- | ---: | ---: | ---: |
| Mono 12 kb/s | 23.085083% | 23.090375% | 23.092333% |
| Mono 24 kb/s | 53.884396% | 53.902646% | 53.870104% |
| Stereo 64 kb/s | 61.201250% | 61.202354% | 61.212188% |
| Stereo 128 kb/s | 70.353646% | 70.378500% | 70.363833% |
| Stereo 192 kb/s | 77.878917% | 77.872167% | 77.863833% |

The apparent initial 192-kb/s gain is only 0.008667%; compared with A2,
B is slower. Both comparisons lose at 128 kb/s (0.035327% and 0.020844%).
Both high-bitrate selection gates fail. Keep accepted eBands-final and
do not add SRC to the live chain. The current 75% goal is not met.

All target PCM hashes/sample/packet totals match the selected fixtures.
Maximum 192-kb/s decode wall calls A/B/A2: 19.930/19.813/20.314 ms;
maximum 128 calls: 21.644/21.654/21.181 ms. These maxima are not averages
and are not continuous-audio qualification.

Minimum free DRAM A/B/A2: 5324/1580/900 B; minimum free task stack1660 B
in all three. Static RAM, scratch and stack frame sizes are unchanged.
These low dynamic reserves remain in the reports, not filtered away.
There were no HTTP observation errors. B/run10 mono12 has task_us greater
than wall_us by1216 us; the accounting windows differ, so that observation
is retained without clamping or subtracting an estimated overhead.

The six preflight regressions were rerun before OTA. The saved C semantic
mirror runs on the little-endian host; it is not a replacement for target
instruction execution. Its comment's endian-neutral wording must not be
used as a portability claim. The ordinary C backend is unchanged.

Reproduction: `report_ebands_src.cjs` verifies the artifact pair, all inherited
semantic proofs, confirmed OTA slots and every recorded attempt, then
archives the three sets and calculates both speed gates. Independent result
tests recompute the statistics from all30 SHA-authenticated raw JSON files.
Both result regressions passed. A final combined run passed27/27 tests
(zero skipped), including codec allocation/free, reconnect and the separate
conditional-allocation audit. This does not replace physical live playback.

## Board restoration

After benchmark state3/error0 was explicitly verified, the normal
`esp8266-opus-live-asm-heapreserve-20260918` image was restored by OTA:
SHA `dfa1c0a298dde56f33d5bb88627b4c9aa643deca12d5329ce4a0398e6f60b273`,
running slot0x10000, HTTP200/OK. That image retains the accepted18-stage
ASM chain and the reconnect/actual-DRAM fixes, not this SRC experiment.
HTTP status, WebSocket getindex and playlist were checked; board stopped,
RSSI-47 dBm, combined free heap30328 B. No new audio-continuity or visual
browser qualification is claimed. UART and PC Wi-Fi were not used.

Two preflight issues were corrected before any OTA: the test normalizer
initially expected `RET` instead of `RET.N`; the first host model modified
the adjacent allocation-vector search instead of the init loop. A regression
reproduced the latter and now pins exactly the three source uses sharing
the changed pair. v2 fixes model metadata, with unchanged candidate bytes.
Failure and final test logs are retained with the v2 artifact.

Reproduce:

```text
node tools/esp8266_opus_asm/ebands_src.cjs
node tools/esp8266_opus_asm/check_bands.cjs ebands-src
node --test tests/esp8266-opus-ebands-src.test.js
node tools/esp8266_opus_asm/report_ebands_src.cjs
node --test tests/esp8266-opus-ebands-src-results.test.js
```

The ordinary C fallback and production defaults are unchanged. The accepted
CPU192 reference remains77.880896%;75% and20s live qualification are pending.
