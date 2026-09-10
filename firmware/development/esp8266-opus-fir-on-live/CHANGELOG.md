# FIR ON live diagnostic — 2026-09-10

Source3f72f25, app884848B, CPU160/QIO40; Opus fixed-point, WordASM,
ICDF-word and FIR-word enabled. I2S PDM32 GPIO3, two512-word DMA buffers.
No raw benchmark task/fixtures or FreeRTOS runtime stats. Diagnostic stream
and wall-stage endpoints available; default board profile unchanged.

Installed through OTA into app1/0x110000. SPIFFS/Wi-Fi/playlist preserved.
DLF Opus24 via HTTP redirects was rejected by the existing20ms packet bound.
The supported56kbps Opus stream produced PCM, but the second health snapshot
timed out: uninterrupted playback was **not** confirmed. Both reports retained.
Explicit stop succeeded; playing=false, free_heap27324B, RSSI−59dBm.
This image remains installed, stopped. Not a continuous-audio qualification.

See [complete results](../../../docs/ESP8266_OPUS_FIR_WORD_BENCHMARK.md).
