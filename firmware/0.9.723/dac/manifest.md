# YoRadio 0.9.723 — DAC

## Build

- Date: 2026-08-16
- Source commit: `68cdfa4c6cdedff2b1caa733b59545d92ddad62a`
- Board: ESP32-2432S028 CYD2USB
- Audio output: ESP32 internal DAC
- Arduino core: Espressif ESP32 3.3.8
- Arduino CLI: 1.5.1
- FQBN: `esp32:esp32:esp32:FlashSize=4M,PartitionScheme=min_spiffs,PSRAM=disabled`
- TLS SDK: 16 KiB receive buffer, 4 KiB transmit buffer
- Application partition: `0x1B0000` bytes
- SPIFFS partition: 512 KiB at `0x370000`

The application contains the version string `0.9.723`. The build uses
1,597,872 bytes of its 1,769,472-byte OTA slot.

## Files

| File | Size | Flash offset | SHA-256 |
|---|---:|---:|---|
| `app.bin` | 1,597,872 | `0x10000` | `22FEEB1ABB79EAF66EA3E36B3030242C0C8DBD0502AE8CAEB628268AD3082F13` |
| `boot_app0.bin` | 8,192 | `0xE000` | `F94C5D786A7A8FAB06AC5D10E33BF37711A6697636DC037559EA19CC410A17F0` |
| `bootloader.bin` | 25,024 | `0x1000` | `1191EB3D913873C709C2FA100F829F4B824971000C0B8831B33F05F98BE3282A` |
| `full.bin` | 4,194,304 | `0x0` | `42322762FABF61E84833418E4FF51E02BBB8AB6D9DEB29328508C1E7DB4C30C0` |
| `partitions.bin` | 3,072 | `0x8000` | `295240EF93436F57E4520A00A89B2B844E28F17ADCCD346FBCD200AD767467A4` |

## Validation

- Flashed and hash-verified on COM8 at 460800 baud.
- NVS and SPIFFS were preserved.
- The binary was checked for its embedded `0.9.723` version string.
- All 30 host regression tests passed, including six DAC sequencing tests.
- The PDM variant also compiled successfully after the shared startup change.
- Three DAC stop/start cycles connected to Vesti FM in 36–45 ms and reached
  MP3 stereo, 48 kHz, 16-bit playback without I2S, decoder or memory errors.
- Each start waited for 20,385–20,799 of 20,800 input-buffer bytes before the
  first decoded frame; the audio-task stack retained 4,360 bytes of headroom.

## Installation

Use `app.bin` with the WebUI firmware updater for a normal update. This
preserves NVS and SPIFFS settings.

For serial installation while preserving settings, write only the component
images at their listed offsets. Do not erase the chip and do not write the
NVS region at `0x9000` or SPIFFS at `0x370000`.

`full.bin` is intended only for initial programming or recovery. Writing it at
`0x0` replaces the complete 4 MiB flash and erases all saved settings and
SPIFFS files.
