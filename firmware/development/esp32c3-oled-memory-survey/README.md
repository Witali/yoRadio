# ESP32-C3 RAM survey application

Unreleased diagnostic app, 2026-09-30. No deep sleep; USB logs and runtime CPU
statistics enabled. Adds boot/AAC allocation-phase snapshots and task stack
high-water marks. No allocator or codec algorithm changes.

[Exact image/configuration provenance](../../../tests/results/esp32c3-aac-memory-20260930/provenance.json)
and [findings](../../../docs/ESP32C3_AAC_MEMORY_20260930.md) are retained.
HE-AAC still runs out of SBR memory; this is not a fixed production release.
Install `app.bin` through WebUI application OTA, preserving NVS and SPIFFS.
