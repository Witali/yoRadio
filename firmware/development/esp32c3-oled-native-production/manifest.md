# ESP32-C3 OLED native production artifact set

## Build

- Date: 2026-09-30; unreleased development build.
- Embedded version: `v0.9.693-1061-g69410cd5`.
- Source: `69410cd5`; EOF status follows queued decoder output.
- ESP-IDF 6.0.2, codec package 2.6.2; ESP32-C3, 160 MHz, DIO80, 4 MiB flash.
- Production logs/profiling disabled; deep sleep disabled; internal RTC source.
- OLED SSD1306 72x40, SDA GPIO5/SCL GPIO6; stereo PDM GPIO10/GPIO3, 48 kHz.
- Both Wi-Fi IRAM speed options disabled to free about 19 KiB of internal RAM.
- Exact configuration and ELF identity: [DIO test artifact](../esp32c3-oled-native-dio80-eof/manifest.json).

## Files

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | ---: | --- |
| `app.bin` | 1392912 | `0x10000` | `abd5d0ed4aded1910cc1dcb2f11593fc2a858ec6b0f69bd52486dfef56ad4ed3` |
| `full.bin` | 4194304 | `0x0` | `022bc7e7caf5bd0bb0a7ae4315e5b4579643bd16a18d203ec68abf9b0811691d` |
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

## Validation and known limitations

See the [EOF status report](../../../docs/ESP32C3_EOF_STATUS.md) for host,
reference-decoder and physical-board results for this exact application.
The archived full image has matching embedded application bytes and erased
NVS/SPIFFS regions; it was not flashed over the user's settings.

Full-rate HE-AAC/HE-AAC v2 remain blocked by a 55,128-byte SBR allocation
in the complete radio. The codec currently falls back to the core. Passing
EOF checks does not qualify that fallback as full-rate HE-AAC playback.
DIO 80 MHz remains the default; the [full QIO acceptance gate](../../../docs/ESP32C3_QIO80_ACCEPTANCE_20260930.md)
did not pass. Worst-case interrupt latency remains unmeasured.
