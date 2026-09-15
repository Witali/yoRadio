# Opus ASM: phase-specialized signed index word extraction

2026-09-15. Independent experiment on accepted index-word80.08060% CPU192.
Host24 exact PCM scenarios, linked packaging and30 physical A/B/A complete.
Current goal80% and20second continuous I2S/WebUI remain unqualified.

## Hypothesis and ABI

The index table contains int16, so the pointer has only two phases modulo4.
Test address bit1 with BBCI. For the upper half subtract2, load the aligned
word and arithmetic-shift16. For the lower half load, shift-left16 then
arithmetic-shift16. No variable shift, SAR save/restore or a0 scratch.
Each path executes five helper instructions versus ten in index-word v2.
This is an instruction count, NOT a measured timing advantage.

The helper occupies25 live bytes in the parent's proven29-byte slot.
Restore the original instruction order: the load redirect at0x4024db22
returns to0x4024db25; original return store stays at0x4024db36/sp+108.
Three patch ranges35 bytes, no new table, RAM, stack or allocations.
Original C fallback and GCC snapshots are retained unchanged.

The plan initially suggested rebuilding independently on endpoint-word.
Instead this reproducible overlay uses the now accepted immutable index-word
image as its direct control, restoring the same original load/store order.
Thus the board comparison measures improvement over80.08060%, not merely
over the older80.99456%. It never overwrites the previous candidate.

Preview confirmed BBCI support. ADDI.N does not encode-2, so use ordinary
ADDI (three bytes). Initial preview failure is retained, no failed app flashed.
A host registration edit exceeded Windows command length; the partial edit
was fixed with narrow patches and the failed host invocation was retained.

## Required validation

- [x] Host PCM/state/PLC/reset/OOM exact in24 cases, including320/510kbps,
  phase fixtures and120ms/48-frame compound packets, under ASan/UBSan.
- [x] Independently verify linked signed extraction for all65536 values,
  two phases and105 real indices; preserve all original GPRs/SAR/stack.
- [x] Authenticate parent's occupied helper, original dead-storage proof,
  last-word padding and complete table bounds; freeze all outside bytes.
- [x] Run positive and negative regressions; unchanged static RAM/frame.
- [x] Physical10 A/10 B/10 A at160MHz/QIO40, RAM packets/no output/profiling.
  Preserve all attempts, errors, maxima, RAM and lower-rate regressions.
- [x] Restore ordinary radio through OTA and verify station/playlist/HTTP/WS.
- [ ] Accept only measured speed without RAM growth, then qualify real audio.

Recipes:tools/esp8266_opus_asm/pvq_index_half.cjs and commented .s;
proof:pvq_index_half_proof.cjs. No default profile change.

Linked proof:131072 signed cases+6720 actual-table/SAR cases,137792 word
loads. Prefix instructions2618048->1929088:exactly five fewer per case,
excluding old exception costs. Three patch ranges/35 bytes; all outside
bytes/addresses,903216-byte image and static RAM/IRAM/frame unchanged.
Candidate SHA2560d76ec891f194e58e385339f1777e38c187b1bd0616a3c3bc8dfce91a033468e.
Control SHA25642f3b445aa7515c69cdcc1f563f9f177f7ed16b75bbabd4eb62358f0bbff5391.
Full160 related preflight regressions PASS/0skip,258.95seconds, log retained.

## Physical result

All30 runs retained; raw packets in RAM, no audio output/network input or
function/stage profiling, CPU160/QIO40 unchanged. Exact fixture PCM hashes.

| kbps | A CPU% | B CPU% | A2 CPU% | Maximum call A/B/A2, us |
|---|---:|---:|---:|---:|
|12 mono|23.09496|23.08627|23.08671|8861 /7827 /7297|
|24 mono|54.13296|54.12010|54.11319|19704 /14283 /14272|
|64 stereo|62.68185|62.62602|62.62654|23467 /16062 /16569|
|128 stereo|72.06458|72.00285|72.02125|28924 /17979 /18255|
|192 stereo|80.05594|80.01998|80.04450|29877 /20371 /22845|

Relative192 gain0.04492/0.03063%;128 gain0.08566/0.02554%.
The repeated-control mono24 slowdown0.01278% is smaller than both high-rate
gains:both acceptance gates pass. This is a small experimental gain, not a
robust guarantee that each run is faster. Default unchanged.80.01998>80;
another0.02497% relative reduction is needed for the raw target alone.

Min sampled DRAM A/B/A2:1044 /8020 /8176 B;192-only1532 /9800 /9624 B.
Post-run minima18276 /26016 /26124 B; all free stack minima1660 B.
Static DRAM/IRAM/frame unchanged by linked proof. A/run3 and4 had HTTP
observation timeouts and CPU19292.35/92.32%; both are retained, not filtered.
The next runs recovered without a reset. These observations do not prove a
leak or attribute the slowdown to network or decoder instructions.
B/run2 mono12 task553230us>wall552951us by279us retained, no subtraction of
the52us empty estimate. No decoder errors; B/A2 have no observation errors.

The20.371ms maximum B call still leaves a deadline question for live DMA;
average raw CPU is not proof of uninterrupted I2S or usable WebUI.
Raw evidence and comparison.json are saved beside the candidate image.

Ordinary C radio restored OTA to0x10000. HTTP/WS, stopped station167 and
playlist hash unchanged. Root HTTP200/27249 gzip bytes/103.15ms;
free heap27628 B,min24748 B,RSSI-61dBm. This is root transfer only, not a
full browser latency or20second live qualification of the ASM candidate.
Final165 related regressions PASS/0skip in346.60seconds, including physical
report, restoration and adjustment census. Full final-tests.log retained.
Two separate Git attribute regressions also PASS:hashed JSON stays LF on
Windows checkout, while raw logs retain their original bytes.
