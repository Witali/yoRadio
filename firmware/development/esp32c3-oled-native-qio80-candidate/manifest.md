# esp32c3-oled-native-qio80-candidate

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
| `app.bin` | 1,392,688 | `0x1e0000` (verified app1 for this test) | `46fce1535fdcf13bfde61c1163c56c9b0b112b5dd95dc5c85896ded7a6abee3f` |
| `bootloader.bin` | 13,872 | `0x0` | `fafa1977197bf6fce71d339ede7699a281854c472611fc5a2255c453b5a284d7` |
| `sdkconfig` | 81,969 | Build configuration only | `99c03460b360d282a3caef37744ceaba03188245d75ceae7a61f7adf73293a19` |

Use the matching bootloader and app; image-header DIO is intentional even for QIO.
Verify the active OTA slot before any serial update. Preserve the partition table,
OTA selector, NVS and SPIFFS. No private board backup is included.

The [Quad experiment report](../../../docs/ESP32C3_FLASH_QUAD_20260930.md)
records the standalone results and validation boundaries. Full-radio candidates
require the separate acceptance report before promotion to the normal profile.
