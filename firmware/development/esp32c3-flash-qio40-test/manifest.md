# esp32c3-flash-qio40-test

## Build

- Date: 2026-09-30; unreleased test build.
- Embedded version: `v0.9.693-1056-gf8a27e60-dirty`.
- Source: `f8a27e60` plus the flash diagnostic changes saved in `6c3da5e9`.
- ESP-IDF v6.0.2, ESP32-C3 160 MHz, QIO 40 MHz, 4 MiB embedded flash.
- Deep sleep disabled; internal RTC source.
- Purpose: Standalone physical flash/cache/AAC diagnostic; no radio, Wi-Fi, NVS writes, or deep sleep.

## Files

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `app.bin` | 376,464 | `0x1e0000` (verified app1 for this test) | `9fb41916dbfce4353592465ae5a41f903d3b5c08754eafcd42c1daae184ab455` |
| `bootloader.bin` | 19,392 | `0x0` | `26a93684dd138f64b32a6a370ecb8b5a423e4cb55e29ca53539aeea91e137e2f` |
| `sdkconfig` | 80,895 | Build configuration only | `39c71201e8b7840b0b910e9b23a31edbfec76dc431b3415a1561211c6d833115` |

Use the matching bootloader and app; image-header DIO is intentional even for QIO.
Verify the active OTA slot before any serial update. Preserve the partition table,
OTA selector, NVS and SPIFFS. No private board backup is included.

The [Quad experiment report](../../../docs/ESP32C3_FLASH_QUAD_20260930.md)
records the standalone results and validation boundaries. Full-radio candidates
require the separate acceptance report before promotion to the normal profile.
