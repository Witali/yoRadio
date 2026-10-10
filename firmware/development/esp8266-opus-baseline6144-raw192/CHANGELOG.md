# Diagnostic Opus raw CPU baseline

2026-09-13, source c470f55, CPU160/QIO40, scratch6144, low-RAM OFF.
Own12/24/64/128/192kbps packets copied from flash to RAM before each measured
decode call. No audio HTTP/Ogg demux/normalizer/PDM output in the timing window.
Wi-Fi/WebUI/OTA remain available; task runtime includes charged ISR and probe
overhead, unlike wall time. This is a benchmark, not production firmware.
Exact inputs/configuration and source hashes are recorded in manifest.json.
