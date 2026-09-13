# Experimental Opus ASM flash placement: +32 bytes

2026-09-13; source `556989f3`. Not production default, not live-qualified.
Best tell-inline parent; 32 unreachable bytes before quant_partition, unchanged
instructions/arithmetic/stack/PCM model. App: 903248 bytes. Exact SHA/profile
are in manifest.json. CPU160/QIO40; raw packets in RAM, no audio output during
benchmark, no function/stage profiling. C fallback unchanged. OTA only.

Host parent PCM/PLC/reset/OOM PASS; 49 regression tests PASS. Final linked hot
instruction graphs/counts exact; static RAM unchanged. Ten physical candidate
runs, ten best controls before and ten after: CPU192 median 91.600354% versus
88.118854/88.122729%. No PCM/observation errors; candidate rejected. Full lower
bitrate, maximum latency, heap/stack and all attempts in comparison.json.
The two layout candidates share the same control series (40 unique runs total).
Ordinary radio restored through OTA; see the layout128 artifact for restore
and WebUI HTTP200 evidence. The 70% CPU192/live-audio goal is not achieved.
