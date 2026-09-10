# FIR ON raw candidate — 2026-09-10

Source3f72f25. Same CPU160/QIO40 profile and packets as FIR OFF; only
FIR-word enabled. Ten completed runs, exact PCM, unchanged static RAM/scratch.
SILK CPU median59.416→23.401%, Hybrid94.477→58.484%. CELT is not fixed.
Diagnostic raw-only image, not a production release. OTA preserved SPIFFS.

See [method and comparison](../../../docs/ESP8266_OPUS_FIR_WORD_BENCHMARK.md).
