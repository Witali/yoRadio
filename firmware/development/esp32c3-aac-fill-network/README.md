# ESP32-C3 bounded FIL integration build

`app.bin` includes bounded AAC FIL parsing and the native AAC metadata fixes.
It is a replaceable development build for the ESP32-C3 OLED board, with network
heap diagnostics, DIO 80 MHz and deep sleep disabled.

The build retains the existing PC18 storage configuration. It does not promote
the PC19/late-SBR experiment and is not qualified against all production gates.
It has not been installed or tested on the physical board in this checkpoint.

Image and ELF fingerprints are in `manifest.json`. Configurations, tests and
limitations are documented in
[the parser report](../../../docs/ESP32C3_AAC_FILL_BOUNDS_20261004.md).
