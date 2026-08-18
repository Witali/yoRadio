# YoRadio 0.9.722 — DAC

## Build

- Date: 2026-08-16
- Source commit: `c948d83ea5ee6105c5e50e12373be51200838a16`
- Board: ESP32-2432S028 CYD2USB
- Audio output: ESP32 internal DAC
- Arduino core: Espressif ESP32 3.3.8
- Arduino CLI: 1.5.1
- FQBN: `esp32:esp32:esp32:FlashSize=4M,PartitionScheme=min_spiffs,PSRAM=disabled`
- TLS SDK: 16 KiB receive buffer, 4 KiB transmit buffer
- Application partition: `0x1B0000` bytes
- SPIFFS partition: 512 KiB at `0x370000`

The application contains the version string `0.9.722`. The build uses
1,597,168 bytes of its 1,769,472-byte OTA slot.

## Files

| File | Size | Flash offset | SHA-256 |
|---|---:|---:|---|
| `app.bin` | 1,597,168 | `0x10000` | `CDE224D5FDAF7695A42C8682A2AD63416E31C95A3EEC20D52CF26F2BCD9B7BF5` |
| `boot_app0.bin` | 8,192 | `0xE000` | `F94C5D786A7A8FAB06AC5D10E33BF37711A6697636DC037559EA19CC410A17F0` |
| `bootloader.bin` | 25,024 | `0x1000` | `1191EB3D913873C709C2FA100F829F4B824971000C0B8831B33F05F98BE3282A` |
| `full.bin` | 4,194,304 | `0x0` | `79B56980E1C3374D2A192F5AA37283E59B8D85D0236156462D1C8F4807A70EE2` |
| `partitions.bin` | 3,072 | `0x8000` | `295240EF93436F57E4520A00A89B2B844E28F17ADCCD346FBCD200AD767467A4` |

## Validation

- Flashed and hash-verified on COM8 at 460800 baud.
- NVS and SPIFFS were preserved.
- MP3 192 kbit/s started after 20,799/20,800 bytes of prebuffering.
- No stream-underflow warnings occurred during the 75-second playback test.
- Audio task ran on core 1 at priority 2 with 4,360 bytes of stack headroom.
- WebUI completed 20/20 concurrent requests with 21 ms median and 46 ms p95 latency.

## Installation

Use `app.bin` with the WebUI firmware updater for a normal update. This
preserves NVS and SPIFFS settings.

For serial installation while preserving settings, write only the component
images at their listed offsets. Do not erase the chip and do not write the
NVS region at `0x9000` or SPIFFS at `0x370000`.

`full.bin` is intended only for initial programming or recovery. Writing it at
`0x0` replaces the complete 4 MiB flash and erases all saved settings and
SPIFFS files.
