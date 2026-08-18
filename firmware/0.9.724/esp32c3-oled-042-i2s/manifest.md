# YoRadio 0.9.724 — ESP32-C3 0.42 OLED / external I2S

## Build

- Date: 2026-08-16
- Source commit: `a083244f8b53e485cba0ebf0248e8aac8b701060`
- Board: 01Space-style ESP32-C3 with onboard 0.42-inch OLED
- Display: SSD1306, 72x40, I2C address `0x3c`, SDA GPIO5, SCL GPIO6
- Audio: external I2S, BCLK GPIO1, LRC/WS GPIO3, DIN GPIO10
- Arduino core: Espressif ESP32 3.3.8
- FQBN: `esp32:esp32:esp32c3:FlashSize=4M,PartitionScheme=min_spiffs,CDCOnBoot=cdc`
- Application partition: `0x1B0000` bytes
- SPIFFS partition: 512 KiB at `0x370000`

The application contains the version string `0.9.724`. The compiled program
uses 1,630,199 bytes (82%) of its 1,966,080-byte build limit. Static data uses
75,804 bytes (23%) of the 327,680-byte DRAM region reported by Arduino.

## Files

| File | Size | Flash offset | SHA-256 |
|---|---:|---:|---|
| `app.bin` | 1,630,352 | `0x10000` | `E993E011FD9B22172583EA4424CDA1342C8147863DB298310BFCDBCD10256F84` |
| `boot_app0.bin` | 8,192 | `0xE000` | `F94C5D786A7A8FAB06AC5D10E33BF37711A6697636DC037559EA19CC410A17F0` |
| `bootloader.bin` | 19,520 | `0x0` | `DA409642EA1619C16B4EF485219A91C3C2AE873CE3BAE37330C24100BD747439` |
| `factory.bin` | 4,128,768 | `0x0` | `ED210F2FDF4EB0DED57AA3E65DD6131E759897759C447119579A2335CE4217E0` |
| `partitions.bin` | 3,072 | `0x8000` | `295240EF93436F57E4520A00A89B2B844E28F17ADCCD346FBCD200AD767467A4` |
| `spiffs.bin` | 524,288 | `0x370000` | `2EDDC843280B2596E867CAC38B1E2626B531FBFE9E88B292BF20CBD881E829EB` |

## Validation

- Successfully compiled for the RISC-V ESP32-C3 target with Arduino-ESP32
  3.3.8.
- All 34 host regression tests passed, including four board-specific tests.
- The factory image was merged by esptool 5.2.0 with the current WebUI SPIFFS
  image.
- Hardware flashing and display/audio verification are pending connection of
  the new board; the existing COM8 CYD board was deliberately not overwritten.

## Installation

For initial programming, put the board into ROM download mode by holding BOOT,
pressing and releasing RST, and then releasing BOOT. Write `factory.bin` at
offset `0x0`. This image includes WebUI but clears NVS and SPIFFS settings.

For later firmware-only updates, use `app.bin` through WebUI or write it at
`0x10000`. Updating only `app.bin` preserves saved Wi-Fi and SPIFFS files.

`spiffs.bin` is provided for an explicit WebUI refresh at `0x370000`; writing
it replaces the files currently stored in SPIFFS.
