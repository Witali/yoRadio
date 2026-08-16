# YoRadio 0.9.721 — DAC

## Build

- Date: 2026-08-16
- Source commit: `6719863205bd239534036d2cc2fb822c34264522`
- Board: ESP32-2432S028 CYD2USB
- Audio output: ESP32 internal DAC
- Arduino core: Espressif ESP32 3.3.8
- Arduino CLI: 1.5.1
- FQBN: `esp32:esp32:esp32:FlashSize=4M,PartitionScheme=min_spiffs,PSRAM=disabled`
- TLS SDK: 16 KiB receive buffer, 4 KiB transmit buffer
- Application partition: `0x1B0000` bytes
- SPIFFS partition: 512 KiB at `0x370000`

The application contains the version string `0.9.721`. The build uses
1,595,376 bytes of its 1,769,472-byte OTA slot.

## Files

| File | Size | Flash offset | SHA-256 |
|---|---:|---:|---|
| `app.bin` | 1,595,376 | `0x10000` | `7760EBA29982CBE50AC03080B0EA9CD031D89898FC47FCDAED9D82A5FBCCF6E7` |
| `boot_app0.bin` | 8,192 | `0xE000` | `F94C5D786A7A8FAB06AC5D10E33BF37711A6697636DC037559EA19CC410A17F0` |
| `bootloader.bin` | 25,024 | `0x1000` | `1191EB3D913873C709C2FA100F829F4B824971000C0B8831B33F05F98BE3282A` |
| `full.bin` | 4,194,304 | `0x0` | `3D6CE5868DFC1C2FF7F3C5FF6DCDF0E0AC8BC9F8C86354ABCD57731C9779E2C5` |
| `partitions.bin` | 3,072 | `0x8000` | `295240EF93436F57E4520A00A89B2B844E28F17ADCCD346FBCD200AD767467A4` |

## Installation

Use `app.bin` with the WebUI firmware updater for a normal update. This
preserves NVS and SPIFFS settings.

For serial installation while preserving settings, write only the component
images at their listed offsets. Do not erase the chip and do not write the
NVS region at `0x9000` or SPIFFS at `0x370000`.

`full.bin` is intended only for initial programming or recovery. Writing it at
`0x0` replaces the complete 4 MiB flash and erases all saved settings and
SPIFFS files.
