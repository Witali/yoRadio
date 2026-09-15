# Opus ASM: remaining endpoint byte-load census

2026-09-15. Host observer on accepted row-word82.00615% CPU192, not target timing.
Counts the original endpoint reads, not the final duplicate already removed.
Upper cache[hi] is read for every search; lower cache[lo] only when lo!=0.

|Corpus|Lower|Upper|Audio seconds|Total reads/second|
|---|---:|---:|---:|---:|
|mono12|0|0|0.24|0|
|mono24|57|102|0.24|662.50|
|stereo64|508|675|0.24|4929.17|
|stereo128|1074|1204|0.24|9491.67|
|stereo192|1647|1765|0.24|14216.67|
|stereo320,2.5ms|1924|2784|0.2425|19414.43|
|stereo320,5ms|2459|2942|0.245|22044.90|
|stereo320,10ms|2560|2784|0.25|21376|
|stereo320,20ms|2485|2665|0.26|19807.69|
|stereo510|19250|19751|1.22|31968.03|

All10 files preserve exact PCM, state/scratch and arena guards under ASan/UBSan.
Every aligned word containing the byte is within the392-byte static table.
Upper count agrees with the independent first-search census at identical fixture
SHA256. These are semantic host counts, not measured LX106 instruction frequency
or time; target inlining/layout and call overhead require physical comparison.

[Full results](benchmarks/esp8266-opus-pvq-endpoint-word-profile-2026-09-15/summary.json).
Recipe profile_pvq_endpoint_word.cjs, observer pvq_endpoint_probe.inc.c and three
esp8266-opus-pvq-endpoint-profile regressions. No target/default/RAM change yet.
Next: upper read via the existing a10 word helper; lower read via a fixed-return
jump fragment using dead a0 for SAR. Prove live registers, control flow, static
bounds and recursive return correctness before host/physical qualification.
