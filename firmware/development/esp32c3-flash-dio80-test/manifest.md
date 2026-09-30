# esp32c3-flash-dio80-test

## Build

- Date: 2026-09-30; unreleased test build.
- Embedded version: `v0.9.693-1056-gf8a27e60-dirty`.
- Source: `f8a27e60` plus the flash diagnostic changes saved in `6c3da5e9`.
- ESP-IDF v6.0.2, ESP32-C3 160 MHz, DIO 80 MHz, 4 MiB embedded flash.
- Deep sleep disabled; internal RTC source.
- Purpose: Standalone physical flash/cache/AAC diagnostic; no radio, Wi-Fi, NVS writes, or deep sleep.

## Files

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `app.bin` | 376,464 | `0x1e0000` (verified app1 for this test) | `a25f18daa8603f2434094a5ce11a056161427a959e1000ead5f761380f4d3d75` |
| `bootloader.bin` | 18,608 | `0x0` | `71bd72f2182295a221e0bc9b2c96934cdff619f27d9d757355bfd5c444d0c49a` |
| `sdkconfig` | 80,895 | Build configuration only | `6b87a6e4923c78b6521ac68c61c80be673203ff7d3a4e4e11aff63ad1d8d5ca4` |

Use the matching bootloader and app; image-header DIO is intentional even for QIO.
Verify the active OTA slot before any serial update. Preserve the partition table,
OTA selector, NVS and SPIFFS. No private board backup is included.

The [Quad experiment report](../../../docs/ESP32C3_FLASH_QUAD_20260930.md)
records the standalone results and validation boundaries. Full-radio candidates
require the separate acceptance report before promotion to the normal profile.
