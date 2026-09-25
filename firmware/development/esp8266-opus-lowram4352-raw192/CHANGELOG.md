# Diagnostic low-RAM Opus raw CPU candidate

2026-09-13, source c470f55, CPU160/QIO40, scratch4352, low-RAM ON.
SILK lending, compact autocorrelation, word-safe SILK PLC IRAM; otherwise
matched to esp8266-opus-baseline6144-raw192, including its12/24/64/128/192kbps
own packet corpus. No audio network/demux/normalizer/PDM in decode timings.
Wi-Fi/WebUI/OTA remain available; this is not a production radio image.
Exact inputs/configuration and source hashes are recorded in manifest.json.
