# ESP32-C3 live-radio diagnostic image

Unreleased 2026-09-30 test application; deep sleep disabled. Enables USB logs,
FreeRTOS runtime statistics and failed-allocation diagnostics. Both optional
Wi-Fi IRAM speed settings are disabled. This is a profiling image, not the
quiet production variant.

[Provenance and hashes](../../../tests/results/esp32c3-radio-hardware-20260930/provenance.json)
identify the exact tested app and saved configuration. Use WebUI OTA to install
`app.bin` while preserving settings. No bootloader, NVS or SPIFFS is included.

The LC 48 kHz stereo test passed. HE/v2 fell back to their cores after an SBR
allocation failure and did not pass full-rate validation. See the
[hardware report](../../../docs/ESP32C3_CACHE_HARDWARE_20260930.md) and
[reproduction instructions](../../../tools/codec_benchmark/cache/HARDWARE.md).
