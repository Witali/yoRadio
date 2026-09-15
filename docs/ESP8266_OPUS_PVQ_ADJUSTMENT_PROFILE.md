# PVQ adjustment-loop byte access frequency

2026-09-15. Host-only census on exact halfword semantic model; no target
code change, timing claim or proof that an unobserved path is unreachable.
Observer wraps only pulses2bits after q--. It returns the original function
result, verifies static-table bounds and counts q=0 separately (no byte load).

| Corpus | Calls | Actual byte loads | q=0 | Loads/audio second |
|---|---:|---:|---:|---:|
|mono12|0|0|0|0|
|mono24|8|4|4|16.67|
|stereo64|6|6|0|25|
|stereo128|6|6|0|25|
|stereo192|10|10|0|41.67|
|320/2.5ms|0|0|0|0|
|320/5ms|0|0|0|0|
|320/10ms|2|2|0|8|
|320/20ms|0|0|0|0|
|510|0|0|0|0|

All10 files through510kbps have exact PCM, unchanged state/scratch/guards
under ASan/UBSan. The first five contain0.24s each; high-rate lengths differ
and are saved in summary.json. Original entropy/budget operations retained.

At192 this is about303 times less frequent than the signed index read
(12608.33/s). Therefore it is not the next high-value optimization alone.
No claim that its cycles or speedup are exactly303 times smaller: the
address/register paths differ. The path remains implemented for all inputs.

Reproduce:node tools/esp8266_opus_asm/profile_pvq_adjustment.cjs.
Raw evidence:docs/benchmarks/esp8266-opus-pvq-adjustment-profile-2026-09-15.
