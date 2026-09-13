# Experimental Opus ASM flash placement: +128 bytes

2026-09-13; source `556989f3`. Not production default, not live-qualified.
Best tell-inline parent; 128 unreachable bytes before quant_partition,
unchanged instructions/arithmetic/stack/PCM model. App: 903360 bytes; final
growth also includes linker layout/relaxation, not just the 128-byte prefix.
Exact SHA/profile are in manifest.json. CPU160/QIO40; raw packets in RAM,
no PDM or function/stage profiling during benchmark. C fallback unchanged.
OTA only. This is independent of layout32, not combined with it.

Host parent PCM/PLC/reset/OOM PASS; 49 regression tests PASS. Linked hot
instruction graphs/counts exact; static RAM unchanged. Ten physical candidate
runs, ten best controls before and ten after: CPU192 median 90.101042% versus
88.118854/88.122729%. Candidate rejected; no PCM/observation errors. Full lower
bitrate, maximum latency, heap/stack and all attempts in comparison.json.
The two layout candidates share the same control series (40 unique runs total).
Ordinary radio restored through OTA; snapshot stopped/error empty, RSSI -59,
free heap27448. WebUI HTTP200 in0.097054s is a smoke check, not a full UI/live
qualification. The 70% CPU192/continuous I2S PDM goal is not achieved.
