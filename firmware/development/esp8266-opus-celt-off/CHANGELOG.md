# CELT A4: historical control before through192 test selection

2026-09-10, sourcea256ea8. App912320B, CPU160/QIO40. Raw benchmark only,
FIR/ICDF/word ON, CELT decoder-only OFF, selected-stage profiler OFF.
Application-only OTA passed; no SPIFFS/NVS/partition/USB changes.

All10 attempts completed; each contains five own tone/noise fixtures,
120measured packets/2.4s decoded audio per fixture after warmup. Poll30s,
5s rest between runs. No network audio or PDM; Wi-Fi/WebUI remain enabled.
Task CPU includes charged ISR/instrumentation, not other tasks.

|Input|Median task CPU|Minimum free DRAM|Minimum free task stack|
|---|---:|---:|---:|
|SILK12|24.457%|4484B|1660B|
|Hybrid24|58.632%|4484B|1660B|
|CELT64|71.305%|4484B|1660B|
|CELT128|93.745%|4768B|1660B|
|CELT510|168.990%|9784B|1660B|

`attempt1..10.json/log`, identical successful `run1..10.json`, `summary.json`
retain every result, including the lower-memory ninth attempt. No failures.
This is **not a completed optimization A/B**. The user then selected tests
through192kbps, without a runtime bitrate restriction. The candidate legacy
image was OTA-booted but never benchmarked. New matched OFF/ON measurements
use the separate through192 corpus; do not mix these populations.
