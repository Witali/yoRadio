# Opus ASM: signed logN word-load

2026-09-15. Independent candidate over accepted pvq-index-half80.019979%
CPU192. Target build, exact host PCM and linked semantic proofs completed.
Physical A/B/A and live qualification are NOT completed. Default unchanged.

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
- [ ] At least10 physical runs of control/candidate, preferably10 A/10 B/10 A2.
- [ ] Retain only measured high-bitrate gain without RAM growth; evaluate
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
