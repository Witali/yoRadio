# esp32c3-flash-qio80-test

## Build

- Date: 2026-09-30; unreleased test build.
- Embedded version: `v0.9.693-1056-gf8a27e60-dirty`.
- Source: `f8a27e60` plus the flash diagnostic changes saved in `6c3da5e9`.
- ESP-IDF v6.0.2, ESP32-C3 160 MHz, QIO 80 MHz, 4 MiB embedded flash.
- Deep sleep disabled; internal RTC source.
- Purpose: Standalone physical flash/cache/AAC diagnostic; no radio, Wi-Fi, NVS writes, or deep sleep.

## Files

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `app.bin` | 376,464 | `0x1e0000` (verified app1 for this test) | `0395a9d1697961d87c5f7bb554521253cb18eb4bd1b60de80b6163cfc7eaec5e` |
| `bootloader.bin` | 19,392 | `0x0` | `68820f159d93c31857db01e6333535369be3f452b2f3e03a55c4e00c5d109ef9` |
| `sdkconfig` | 80,895 | Build configuration only | `1bf8b7cbc0fa9de0af5f7a219fe9d1d7163c8c082752c16cc6ed4dbcc17bdb88` |

Use the matching bootloader and app; image-header DIO is intentional even for QIO.
Verify the active OTA slot before any serial update. Preserve the partition table,
OTA selector, NVS and SPIFFS. No private board backup is included.

The [Quad experiment report](../../../docs/ESP32C3_FLASH_QUAD_20260930.md)
records the standalone results and validation boundaries. Full-radio candidates
require the separate acceptance report before promotion to the normal profile.
