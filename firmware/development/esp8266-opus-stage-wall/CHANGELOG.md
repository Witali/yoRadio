# Opus live stage diagnostics, 2026-09-10

Source d155eaf, 884816-byte experimental OTA image. Fixed-point Opus,
WordASM/PDM32 IRAM/batch ON, ICDF OFF, normal post-frame pacing.
GPIO3 I2S PDM32, CPU160/QIO40, unchanged 2x512-word DMA buffers.
Adds64 bytes of diagnostic counters; no ISR/IRAM change. Production unchanged.
OTA to0x110000 succeeded. Continuity tests FAILED; not a release.

[Method, results and limits](../../../docs/ESP8266_OPUS_LIVE_STAGE_PROFILE.md).
Raw reports, including failed requests, are in results/.
