# Opus ASM: signed logN word-load

2026-09-15. Independent candidate over accepted pvq-index-half80.019979%
CPU192. Target build, exact host PCM and linked semantic proofs completed.
Physical A/B/A completed2026-09-17: rejected (see results below).
Live qualification is NOT completed. Default unchanged.

## Change and proof

Replace only `0x4024db91: l16si a4,a10,0` in quant_partition with a fixed J.
New helper at0x4024dcc4 branches on address bit1, performs one aligned L32I
and extracts the signed low/high halfword into a4. All other GPRs, including
a0/a10, and SAR are unchanged. No call, stack access, allocation or new table.

The helper has25 live bytes/nine static instructions, five executed on either
phase. It occupies42 bytes of originally encoder-only instructions. The
original predecessor SUB at0x4024dcc1 falls through: independently prove it
and the entire old slot dead under immutable encode=0, not merely the slot.
There are no original branch entries. The current parent has no entry;
only the new fixed J can reach the new helper. All outside bytes/addresses
are unchanged. The parent decoder-only contract and C fallback remain intact.

The logN object is21 signed16 values,42 bytes, at0x402d5a58. The mode's logN
pointer and values are authenticated from the actual ELF. Its last aligned
word includes two independently checked zero padding bytes. The host model
copies only two bytes at that last halfword, avoiding an out-of-object C read.
Only non-stereo compute_theta uses this host replacement, matching the
out-of-line quant_partition clone; stereo theta and other logN uses remain.

- [x] Actual assembler supports the complete sequence and exact slot widths.
- [x] Symbolic32-bit input, all65536 signed values/two phases, all21 real
  values/all64 SAR states:132416 linked numeric cases, unchanged registers.
- [x] Signed result, complete bounds, dead storage and outside ELF bytes.
- [x]24 host cases with ASan/UBSan: exact PCM/state/PLC/reset/OOM,320/510kbps,
  mixed/phase fixtures and120ms/48-frame compound packets.
- [x]4 focused positive/negative regressions; full174 related regressions
  PASS/0skip in465.90seconds. Both complete logs retained beside the image.
- [x] At least10 physical runs of control/candidate:10 A/10 B/10 A2.
- [x] Retain only measured high-bitrate gain without RAM growth; evaluate
  active80% threshold and additionally the requested78% next target.
- [ ] Qualify continuous I2S PDM>=20s and working WebUI separately.

132416 old visible L16SI instructions become794496 visible instructions;
the original SDK exception-handler work is outside that count. This is
not a claim that more visible instructions cost more or fewer cycles.
The motivation is avoiding SDK L16 emulation, not an unmeasured cycle model.

Image903216 B, static DRAM/IRAM and112-byte quant_partition frame unchanged.
Candidate SHA2562061c500bf801efd60e77286f5cbeb67cc3197cedcdfc373f929ebf314b8ceda.
Control SHA2560d76ec891f194e58e385339f1777e38c187b1bd0616a3c3bc8dfce91a033468e.
Two patch ranges45 bytes, no change of CPU160/QIO40 or production defaults.

## Reproduction and pending board work

Recipes/proofs/commented ASM:tools/esp8266_opus_asm/pvq_logn_word*.cjs/.s.
Artifacts:firmware/development/esp8266-opus-pvq-logn-word-{control,candidate}-v1.

```powershell
node tools/esp8266_opus_asm/check_bands.cjs pvq-logn-word
node tools/esp8266_opus_asm/pvq_logn_word.cjs
node --test tests/esp8266-opus-pvq-logn-word.test.js
```

Physical reports must go to `.build/opus-pvq-logn-word-board/before`,
`candidate`, `after`; explicit OTA reports ota-before/candidate/after.json.
Use the same RAM fixtures and run_raw_series.ps1 with Attempts10/IntervalMs15000.
The prepared report_pvq_logn_word.cjs rejects missing/incomplete series and
records both80% and78% gates; it has not been run without measurements.

Two HTTP status snapshots at19:17:05/19:19:39 UTC timed out. Read-only ping
reported destination unreachable; ARP for192.168.100.6 has no resolved MAC
and became Unreachable. This establishes unavailability from this computer,
not whether the board is powered off, disconnected or hung. Both failed
snapshots are retained beside the image. No OTA was sent; no serial command,
reset, network-adapter change, SPIFFS or NVS upload was performed.
Another fresh HTTP snapshot after all174 regressions also timed out and is
retained as board-final-unavailable.json. No physical test was silently skipped
and counted as passed: none has been performed for this candidate yet.

When the board returns, take a fresh initial snapshot before any OTA; do not
use an unavailable-status report as the restoration baseline. After trials,
restore the ordinary app and verify HTTP/WS/station/playlist. Never claim
this candidate improves speed or reaches the goal before those measurements.

## Physical results,2026-09-17: reject this helper

Board returned at192.168.100.6, initial RSSI-59dBm, stopped, free heap27628B.
All three app-only OTAs verified the alternate slot. CPU160MHz/QIO40, same
RAM packets and15s observation interval, no PCM output or function profiler.
All30 requested attempts completed and retained; exact PCM hashes at every
bitrate. The earlier unavailable observations above remain historical evidence.

| kbps | A CPU% | B CPU% | A2 CPU% |
| ---: | ---: | ---: | ---: |
| 12 | 23.099542 | 23.089521 | 23.092687 |
| 24 | 54.129333 | 54.114812 | 54.116229 |
| 64 | 62.624354 | 62.738271 | 62.659833 |
| 128 | 72.013813 | 72.095604 | 72.029958 |
| 192 | 80.041021 | 80.005042 | 80.047250 |

The192 improvement is only0.045/0.053% relative to the two controls.
At128 it is0.114/0.091% slower; at64 it is0.182/0.125% slower.
Both selection gates reject it. Even the raw80% threshold is NOT met:
80.005042 must not be rounded down to claim success.78% also remains unmet.
Do not combine this helper with the next candidate or change the default.

Static RAM/stack delta0, app903216B. Observed minimum DRAM A/B/A2:
4004/6668/8184B; minimum at192:9800/9800/9808B. These dynamic minima
include changing network state and are not evidence of an allocator saving.
Stack watermark1660B in every group. Maximum192 call21374/21599/22287us;
no HTTP observation failures. A2 mono12 run2/run7 had task-minus-wall
excess1816/1270us, retained unchanged because measurement windows differ.

Evidence: candidate artifact comparison.json, all30 run JSON/logs and three
OTA reports. `esp8266-opus-word-load-board.test.js` recomputes all results,
validates hashes/PCM/slots/CPU gates and rejects corrupted PCM or missing runs.
That test passes. The original signed-word proof was rerun before OTA.

The A2 control is also the initial control for the next exp2-table32 experiment;
it is one physical ten-run series, not twenty new measurements. No UART,
SPIFFS/NVS upload or PC network-setting change was made. Ordinary-app restoration
and full-path testing are recorded at the end of the overall board session.
