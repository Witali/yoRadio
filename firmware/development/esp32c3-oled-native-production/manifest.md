# ESP32-C3 OLED native production artifact set

## Build

- Date: 2026-09-30; unreleased development build.
- Embedded version: `v0.9.693-1049-g3903c058-dirty`.
- Source: `3903c058` plus the Wi-Fi flash-placement settings and diagnostic
  allocation hook (compiled out in production). See the
  [measurement provenance](../../../tests/results/esp32c3-radio-hardware-20260930/provenance.json)
  for ELF, configuration and source hashes.
- ESP-IDF 6.0.2, codec package 2.6.2; ESP32-C3, 160 MHz, DIO80, 4 MiB flash.
- Production logs/profiling disabled; deep sleep disabled; internal RTC source.
- OLED SSD1306 72x40, SDA GPIO5/SCL GPIO6; stereo PDM GPIO10/GPIO3, 48 kHz.
- Both Wi-Fi IRAM speed options disabled to free about 19 KiB of internal RAM.

## Files

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | ---: | --- |
| `app.bin` | 1392688 | `0x10000` | `4374ece3e0613d96003a9635c28be21964994d81a11857e785e016403e704c6c` |
| `full.bin` | 4194304 | `0x0` | `0813a12430420e8fe8802068c3632f922aa4fc4fd389a0feba59c3ce9f0ff7dc` |
| `bootloader.bin` | 13200 | `0x0` | `d39d85b800e75ac7d01d7232b86c311d9cd7217eb71b17801d9c3daf93222459` |
| `partitions.bin` | 3072 | `0x8000` | `f26d55c34a06f24ed917555cc4608a87f7c2300a6a71e20153d6dd43816e2f18` |
| `boot_app0.bin` | 8192 | `0xe000` | `7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f` |

Use `app.bin` through WebUI OTA for a normal update preserving NVS, credentials,
playlists and SPIFFS. A direct serial write must target the active app slot;
`0x10000` is app0, and app1 is at `0x1e0000`.

`full.bin` is a clean 4 MiB recovery image with the same application at app0,
bootloader, partition table and initial OTA selector. NVS and SPIFFS regions
are erased (`0xff`); no board backup or saved user configuration is included.
Flashing the full image replaces all saved settings and SPIFFS contents.

## Validation and known limitation

- Production build and partition-size check passed.
- Installed through WebUI OTA; a 25-second LAN test confirmed AAC-LC 48 kHz
  stereo, then a reboot resumed the user's original station.
- Image size, embedded app bytes and erased NVS/SPIFFS regions checked.
- Full-rate HE-AAC/HE-AAC v2 remain blocked by a 55,128-byte SBR allocation
  in the complete radio. The codec currently falls back to the core. See the
  [hardware report](../../../docs/ESP32C3_CACHE_HARDWARE_20260930.md).
- Connection-time and worst-case interrupt-latency A/B tests are still pending.
