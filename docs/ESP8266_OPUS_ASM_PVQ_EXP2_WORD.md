# Opus ASM: signed exp2_table8 word-load

2026-09-15. Second independent candidate over accepted pvq-index-half
80.019979% CPU192, not over the unmeasured logN candidate. This is an
experiment, not a production/default change or evidence of reaching78%.

2026-09-17: physical30 A/B/A completed. Helper rejected:80.328125% CPU192,
slower than both controls. The independent direct exp2-table32 is preferable.

## Change and proof

Replace only `0x4024dc76: l16si a3,a3,0` in quant_partition with a fixed J.
The25-byte helper at0x4024dcf8 tests address bit1, performs one aligned L32I
and sign-extends the selected halfword in a3. Every other GPR, including
a0/a10, and SAR remain unchanged. No call, new stack slot, allocation or table.
Both phases execute five helper instructions, with nine static instructions.

The old25-byte slot is decoder-inaccessible encoder code. Independently
prove the falling-through ADD at0x4024dcf6 also dead under immutable encode=0.
Check original incoming branches and the current parent for helper entries.
All other linked instructions and addresses must stay identical. The chosen
slot does not overlap the earlier logN helper at0x4024dcc4..0x4024dcee;
combining both remains a separate experiment, not an assumed additive gain.

exp2_table8 is eight signed16 values/16bytes at0x402d74d8. Authenticate its
literal pointer at0x40211a9c and every actual value from the parent ELF.
Every aligned word stays inside the table; unlike logN, no padding is needed.
The host model replaces only non-stereo compute_qn, matching quant_partition;
stereo theta and other inlined clones remain unchanged. C fallback preserved.

- [x] Source storage and predecessor proven dead; separate helper slots.
- [x]24 host cases, exact PCM/state/PLC/reset/OOM through510kbps, phase/mixed
  fixtures and120ms/48-frame compound packets; ASan/UBSan enabled.
- [x] Complete linked-image proof:131072 signed cases/two address phases plus
  eight real entries/all64 SAR states,131584 cases total. Other registers,
  SAR,112-byte frame and all outside ELF bytes are unchanged.
- [x] Four focused positive/negative tests PASS in110.99s; complete related
  suite178 tests PASS/0fail/0skip in487.12s. Full logs retained with the image.
- [x] At least10 physical control/candidate runs:10 A/10 B/10 A2.
- [x] Record medians, maxima, all failures and free RAM/stack; accept only a
  measured high-bitrate gain without increased RAM. Check80% and78% separately.
- [ ] Qualify I2S PDM>=20s and WebUI separately before any production promotion.

The intended mechanism is avoiding the SDK narrow-load exception handler,
not reducing visible instruction count. Both phases add five visible
instructions relative to one L16SI; neither number is a cycle estimate.
Host correctness does not measure LX106 execution speed or cache misses.

Image903216bytes, static DRAM/IRAM and stack unchanged. Two patch ranges,
28bytes total. Candidate SHA256:
`7108b97e9afb067689911c1817b6f9ebbc8fce97588a82bfd1a7f292708377e1`.
Control SHA256:
`0d76ec891f194e58e385339f1777e38c187b1bd0616a3c3bc8dfce91a033468e`.
CPU160MHz/runtimeQIO40 and production defaults remain unchanged.

## Reproduction and board status

Sources: `tools/esp8266_opus_asm/pvq_exp2_word.cjs`,
`pvq_exp2_word_proof.cjs`, commented `pvq_exp2_word.s`.
Artifacts: `firmware/development/esp8266-opus-pvq-exp2-word-{control,candidate}-v1`.

```powershell
node tools/esp8266_opus_asm/check_bands.cjs pvq-exp2-word
node tools/esp8266_opus_asm/pvq_exp2_word.cjs
node --test tests/esp8266-opus-pvq-exp2-word.test.js
```

Physical reports go to `.build/opus-pvq-exp2-word-board/before`, `candidate`,
`after`, with explicit ota-before/candidate/after.json. Use the established
RAM fixtures and run_raw_series.ps1 Attempts10/IntervalMs15000. The prepared
report_pvq_exp2_word.cjs rejects missing/incomplete series and records both
the active80% gate and the requested78% next target. No synthetic timing data.

Initial and repeated HTTP status requests to192.168.100.6 timed out. This
shows unavailability from this computer, not its cause. No OTA, UART, reset,
network-adapter changes or SPIFFS/NVS upload was performed. When reachable,
take a fresh snapshot before OTA; never use a failed snapshot as a restoration
baseline. After trials restore the ordinary app and verify HTTP/WS/playlist.

After all178 regressions, another fresh HTTP status snapshot also timed out.
All three failed observations are retained beside the image as
board-initial/recheck/final-unavailable.json. The ARP entry was Unreachable
with no resolved MAC. No physical test was counted as passed or replaced by
host timing. Physical speed, runtime free heap/stack and live output remain
unmeasured for this candidate; no production promotion has occurred.

## Physical results2026-09-17: rejected

The unavailability paragraphs above are historical. All30 raw attempts and
three app-only OTA operations completed; all PCM hashes match the fixtures.
Control A reuses the actual last10 control runs from exp2-table32. Across
logN/table32/exp2-helper there are70 unique physical runs, not90; the two
shared boundaries are checked by the evidence regression test.

| kbps | A CPU% | B CPU% | A2 CPU% |
| ---: | ---: | ---: | ---: |
| 12 | 23.098063 | 23.084354 | 23.087812 |
| 24 | 54.128083 | 54.123771 | 54.111813 |
| 64 | 62.623646 | 62.944292 | 62.608833 |
| 128 | 72.011875 | 72.398792 | 72.033083 |
| 192 | 80.044312 | 80.328125 | 80.059792 |

Relative slowdown at192:0.355/0.335%; at128:0.537/0.508%.
Both selection checks reject the helper; neither80% nor78% raw gate passes.
Choose the independently measured direct table32 (79.626521% CPU192),
not this helper. Do not combine alternatives that replace the same load.

Static RAM/stack delta0, app903216B. Observed minimum DRAM A/B/A2:
3628/7668/8164B; at192:9800/9624/9800B. Stack watermark1660B in all groups.
Maximum192 calls20402/20457/20785us. No HTTP observation errors.
Candidate mono12 run2 task>wall by468us is preserved, not subtracted.

All30 run JSON/logs, OTA reports and comparison.json are next to app.bin.
Fresh local related tests:18 PASS/0skip (118.99s). The board evidence test
additionally recomputes all three experiments and checks shared controls.
This completes the independent helper comparison, not live playback QA.
