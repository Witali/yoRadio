# Raw Opus control for detailed profiler, 2026-09-13

Source e550ded3, CPU160/QIO40, GCC-ASM, same raw fixtures/options as
functions-192-v2 with function profiling OFF.902992B. Ten device trials
retained; all five PCM hashes exact. Not an ordinary-radio release.

192kbps median CPU budget92.876%, maximum105.613%. Attempt6 contains an
HTTP observation timeout and a low-memory outlier (minimum sampled DRAM
884B, lifetime heap minimum860B after the run). It is NOT discarded. The
decoder completed with exact PCM and memory recovered after the run, but
this does not qualify realtime stability or prove the cause of the pressure.
No network audio, demux, normalization or PDM is included in this benchmark.
