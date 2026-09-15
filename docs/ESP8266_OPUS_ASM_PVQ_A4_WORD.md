# Opus ASM: word reads for the two remaining a4 PVQ probes

2026-09-15. Candidate over accepted pvq-byte-word84.01121% raw CPU192.
Physical speed not yet established; no change to the firmware default.

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

## Physical qualification still required

10 A /10 B /10 A at CPU160/runtime QIO40, same RAM-preloaded packets,
no physical output or function/stage profiler. Keep every attempt, error,
maximum and RAM minimum, including low-bitrate regressions. Compare both
fresh controls; restore ordinary radio via OTA afterwards. No UART/GPIO3.

The80% raw goal and20seconds continuous I2S PDM/WebUI are not established
by these local results. The accepted baseline remains pvq-byte-word until
the physical comparison completes.
