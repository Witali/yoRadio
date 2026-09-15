# Opus ASM: word reads for the two remaining a4 PVQ probes

2026-09-15. Candidate over accepted pvq-byte-word84.01121% raw CPU192.
Physical gain confirmed by30 A/B/A; no change to the firmware default.

Pre-deployment127 related regressions PASS,0 failures/skips,134.70seconds.
The complete log is retained as preflight-tests.log beside the image.

Two L8UI a4,a4,0 sites become same-width CALL0:0x4024db52 before the split
decision and0x4024e1ad at the first binary-search probe. A25-byte/nine-op
leaf at0x4024de08 uses part of the first helper's unreachable zero padding.
It saves SAR in dead a11, aligns a4, reads one word, extracts the byte,
restores SAR and returns in a4. CALL0 changes dead a0; original caller return
remains at sp+108. No stack frame, stores, allocations, new tables or RAM.

All other instructions/addresses and table bytes remain unchanged, including
the first a10 helper and sixth-probe stub. Image size is still903216 bytes.
The candidate uses more live flash instructions inside existing padding;
same image size does not establish unchanged cache behavior or a speed gain.

## Evidence and verification

- [Host census](ESP8266_OPUS_PVQ_A4_WORD_PROFILE.md): at192,1765 first probes
  and2596 upper reads per0.24s,18170.83 selected loads per second of audio.
- Actual ELF mode pointers and complete392-byte bits/210-byte index tables
  verified against the original standard tables. Every valid row endpoint
  and every aligned word stays inside the complete bits storage.
- The9-op helper is an exact bijective a4/a10 renaming of the previously
  proved leaf: all32 word bits,4 phases, arbitrary SAR. Negative tests cover
  wrong registers, extraction, alignment, SAR, entry into padding and live
  a0/a11. Every other caller register remains unchanged.
- The actual linked search/calls execute378304 row/budget cases. Another
  79902 pre-split cases cover both branch outcomes, N thresholds, negative
  budgets and signed32 extremes. Caller/old-helper execution paths, logical
  byte-read order, q/cost and SAR match.458206 additional word reads checked.
  Instruction totals27368790 ->31492644 exclude old exception handling;
  they are not CPU measurements.
-24 host PCM/state/PLC/reset/OOM scenarios exact, including510kbps, phase
  variants and compound packets through120ms, under ASan/UBSan.

The initial local build was stopped by the verifier: its historical
branch-only disassembly walker did not enter the new CALL0-only leaf.
Added opt-in traversal of internal CALL0 targets, preserving continuations,
excluding external callees and deduplicating recursion. The default walker
is unchanged. Two new negative/behavior tests pass. The complete proof was
rerun successfully; the failed log is retained, not a target decode failure.

Recipes: pvq_a4_word.cjs, commented pvq_a4_word.s, pvq_a4_word_proof.cjs.
Control SHA256:a53e2684fbfbe7c52743c0fcb0ec50301b7d6106a4b055a8659d84ffe7817b05.
Candidate SHA256:fe34751b8dae0cbd87a58a1b767aa02a82b006aa8b452f66065446dbc9dbdae9.
Original C and GCC snapshots remain unchanged.

## Physical measurements

10 A /10 B /10 A at CPU160/runtime QIO40, same RAM-preloaded packets,
no physical output or function/stage profiler. Keep every attempt, error,
maximum and RAM minimum, including low-bitrate regressions. Compare both
fresh controls; restore ordinary radio via OTA afterwards. No UART/GPIO3.

All30 attempts completed with exact PCM. Median raw CPU, percent:

| kbps | A: byte-word | B: a4-word | A2: byte-word | Maximum call A/B/A2, us |
|---|---:|---:|---:|---|
|12|23.09273|23.09377|23.09846|8246 /7753 /7875|
|24|54.19171|54.16746|54.17313|19760 /14862 /14253|
|64|63.47258|63.41017|63.44331|22595 /18012 /16423|
|128|74.45779|73.76998|74.45352|29511 /20167 /20181|
|192|84.00988|82.83819|84.02250|31029 /21407 /23309|

Both high-bitrate gates PASS:192 relative time gain1.39470% /1.40952%,
128 gain0.92376% /0.91808%. Mono12 loss against A is0.00451%; against A2
no low-bitrate median is worse. Accepted as the experimental raw baseline,
82.83819%; another3.42618% reduction is needed to reach80%. Candidate192
range82.78900..82.94513%, mean82.85589%. No default/profile clock change.

Static RAM/IRAM/frame unchanged. Minimum free stack1660 B in all groups;
observed free DRAM minima544 /8028 /8352 B. At192:856 /9800 /9972 B.
Post-run raw free DRAM minima17600 /26300 /26192 B. These dynamic observations
are not new allocation sizes or proof of a memory saving by the candidate.

A/run3 had one HTTP observation timeout, decoded192 at96.92825% CPU, and
recorded minimum DRAM544 B (status allocator lifetime floor520 B). It
completed with exact PCM and is retained in every comparison. Its later
status read showed26572 B free. The cause of the low-memory/slow interval
is unknown; neither network starvation nor fragmentation is established.
Candidate and A2 have no observation errors. A2/run1 mono12 task>wall by254us
is retained as a timing-window discrepancy, without clamping or subtraction.

All maxima are retained. B19221.407ms is better than both controls but still
not a deadline guarantee for20ms frames; B24/64 maxima are worse than A2.
Source/proofs commit7f075c57; census9ddab73f. Full raw JSON/log/SHA/OTA and
independent comparisons are in
[comparison.json](../firmware/development/esp8266-opus-pvq-a4-word-candidate-v1/comparison.json).

Final129 related regressions PASS,0 failures/skips,143.00seconds. The results
test independently recomputes all30 attempts, medians/maxima/minima and
acceptance gates, rechecks linked proofs and validates ordinary restoration.
final-tests.log retained beside the image; not the entire repository suite.

## Ordinary restoration and remaining qualification

Ordinary live512-idle3s C-backend radio restored OTA to0x10000, SHA256
661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b.
CPU160/QIO40, I2S PDM32/GPIO3,2x512 DMA; benchmark OFF. Stopped station167,
unchanged playlist hash, empty error and WebSocket/getindex/playerwrap checked.
Root HTTP200:27249 gzip bytes in108.702ms, heap27628/min24748, RSSI-74dBm.
This measures the root document, not all browser resources; playback was
not started as part of restoration. No UART/reset or SPIFFS upload.

The80% raw goal and20seconds continuous I2S PDM/WebUI remain unproven.
