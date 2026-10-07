# ESP32-C3 stream format development firmware

- AAC: **Helix AAC core**.
- Deep Sleep clock: **enabled**.
- RTC clock: internal RC; no external 32.768 kHz crystal.
- Source: `7b5d257c5d4564f551ed45a8866128dde4e5e3be`.
- Image: `1,338,128` bytes; checksums in `manifest.json`.

This is an application-only ESP32-C3 OLED native image for the existing
WebUI Firmware update workflow. It does not contain an NVS or SPIFFS image.
For first installation, follow the [board guide](../../../idf/esp32c3-oled-native/README.md).

Built and checked without flashing the physical board. See the
[validation report](../../../docs/ESP32C3_STREAM_FORMAT_VALIDATION_20260930.md)
for emulator coverage and the remaining implicit SBR/PS transition limit.
