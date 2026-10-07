# esp32c3-oled-native-dio80-profile

## Build

- Date: 2026-09-30; unreleased test build.
- Embedded version: `v0.9.693-1057-g6c3da5e9`.
- Source: `6c3da5e9`.
- ESP-IDF v6.0.2, ESP32-C3 160 MHz, DIO 80 MHz, 4 MiB embedded flash.
- Deep sleep disabled; internal RTC source.
- Purpose: Matched DIO full-radio profiling control; deep sleep disabled.

## Files

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `app.bin` | 1,539,952 | `0x1e0000` (verified app1 for this test) | `f87574c0d63a7bce5846f17459a1c8f15ba2abb8547f8c24537e8028f8401dae` |
| `bootloader.bin` | 18,672 | `0x0` | `5f2943b0937afd4a3125bde948756972ae64cbe202327e0cc134687e501b6312` |
| `sdkconfig` | 82,150 | Build configuration only | `17c07d46a42de0033affa162b6b82d2c869e50db0d30528b3966b6b0e88cadd1` |

Use the matching bootloader and app; image-header DIO is intentional even for QIO.
Verify the active OTA slot before any serial update. Preserve the partition table,
OTA selector, NVS and SPIFFS. No private board backup is included.

The [Quad experiment report](../../../docs/ESP32C3_FLASH_QUAD_20260930.md)
records the standalone results and validation boundaries. Full-radio candidates
require the separate acceptance report before promotion to the normal profile.
