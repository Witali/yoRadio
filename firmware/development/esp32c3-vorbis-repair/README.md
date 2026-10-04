# ESP32-C3 Vorbis initialization repair candidate

Application-only image, built 2026-10-04 from `codex/aac-storage18` after
`51667ff3`. Embedded build version was generated before the source commit.
See `manifest.json` for application/ELF/config/source identities.

Uses the tested PC19 receive-credit radio configuration with full-rate AAC,
SBR/PS and the Vorbis initialization repair enabled. Deep sleep is disabled;
USB diagnostic logging is enabled. No NVS or Wi-Fi configuration is included.

Build and linked callbacks verified. The isolated decoder passed its QEMU
lifecycle sweep. **This radio image has not been flashed or hardware-qualified.**

See [the results](../../../docs/ESP32C3_VORBIS_REPAIR_20261004.md) for reproduction,
scope and remaining plan steps. The incorporated Tremor code's BSD license is
retained in [COPYING](../../../idf/esp32c3-oled-native/main/vorbis_repair/COPYING).
