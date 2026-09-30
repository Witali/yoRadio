# esp32c3-oled-native-qio80-profile

## Build

- Date: 2026-09-30; unreleased test build.
- Embedded version: `v0.9.693-1057-g6c3da5e9`.
- Source: `6c3da5e9`.
- ESP-IDF v6.0.2, ESP32-C3 160 MHz, QIO 80 MHz, 4 MiB embedded flash.
- Deep sleep disabled; internal RTC source.
- Purpose: Full-radio QIO acceptance candidate; deep sleep disabled.

## Files

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `app.bin` | 1,539,952 | `0x1e0000` (verified app1 for this test) | `fc06c46106ae420d2d34bb41ebfbcfdbca574dd9b082c2fb310e937cb007e29d` |
| `bootloader.bin` | 19,456 | `0x0` | `fd89576c0cd8b3a36378202548484ae27b99a9d587925d7eb5748890f295d818` |
| `sdkconfig` | 82,150 | Build configuration only | `81428452861721b710a486783720df7a2497a148bee6e0daa43e3b31c3231e13` |

Use the matching bootloader and app; image-header DIO is intentional even for QIO.
Verify the active OTA slot before any serial update. Preserve the partition table,
OTA selector, NVS and SPIFFS. No private board backup is included.

The [Quad experiment report](../../../docs/ESP32C3_FLASH_QUAD_20260930.md)
records the standalone results and validation boundaries. Full-radio candidates
require the separate acceptance report before promotion to the normal profile.
