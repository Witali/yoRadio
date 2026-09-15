# Opus ASM: unconditional PVQ row-length census

2026-09-15. Control: accepted pvq-a4-word,82.83819% raw CPU192.
Host-only observation, not a new target implementation or timing result.

The linked quant_partition reads cache[0] at0x4024db47, L8UI a6,a2,0,
before the LM test. Count every entry, including LM==-1; the previous
upper-cost census alone would underestimate this load's frequency.

| Corpus | Reads | Audio seconds | Reads/second |
|---|---:|---:|---:|
|mono12|0|0.24|0|
|mono24|156|0.24|650|
|stereo64|846|0.24|3525|
|stereo128|1904|0.24|7933.33|
|stereo192|3026|0.24|12608.33|
|stereo320,2.5ms|3434|0.2425|14160.82|
|stereo320,5ms|4218|0.245|17216.33|
|stereo320,10ms|4518|0.25|18072|
|stereo320,20ms|4784|0.26|18400|
|stereo510|36940|1.22|30278.69|

All10 observed files preserve exact PCM, state/scratch sizes and arena
guards under ASan/UBSan. Every aligned word containing the requested byte
lies inside the complete392-byte static table. The observer returns the
original byte; its extra read is only instrumentation. No host timing is
interpreted as LX106 performance. Counts minus LM==-1 independently match
the previous upper-cost census for each identical fixture SHA256.

Evidence: [summary](benchmarks/esp8266-opus-pvq-row-word-profile-2026-09-15/summary.json),
profile.log, profile_pvq_row_word.cjs, pvq_row_probe.inc.c and three
esp8266-opus-pvq-row-profile regressions. Original fixtures remain unchanged.

Next: prove a2 preserved/a6 result/a0+a11 dead/SAR restored, static table
bounds and private encoder-only helper storage; then exact host/linked
tests and10 A/10 B/10 A on the board. No new RAM/table/stack or default change.
