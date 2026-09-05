# ESP8266 native mono development build

- Built: 2026-09-05, source commit `236d4ad` (includes sync fix `effbd67`).
- Embedded version: `v0.9.693-420-g236d4ad-dirty`; unrelated Arduino changes
  in this workspace are not part of the native target.
- Target: Wemos D1 mini / ESP8266EX, CPU 160 MHz, 4 MiB QIO40 flash.
- SDK: ESP8266 RTOS SDK v3.4, GCC 8.4, O3.
- Profile: `esp8266/rtos-sdk-native/sdkconfig.defaults`, **Mono**, Helix MP3
  SSO + AAC, I2S-PDM32 on GPIO3, 2 x 512-word DMA buffers.
- Audio/stage/memory profiling, tone test and output benchmark: OFF.
- `app.bin`: 686944 bytes.
- SHA-256: `8EB0C0F3688770ABD2E73470F2F7C99426B539ACD195A2E268E29D9974825B25`.

## Changelog

- Add build-time Mono/Stereo selection. Compatible M/S MP3 skips side
  Huffman/dequantization, runs one IMDCT and one synthesis. Other modes keep
  a window-safe mono fallback; AAC/libmad downmix decoded PCM.
- Reduce MP3 callback PCM allocation from 2304 to 1152 bytes. No extra
  task, per-granule heap allocation, or change to DMA buffers.
- Correct MPEG2.5 sync detection; reject the reserved MPEG version.
- All **329 host tests pass**; actual Xtensa compilation passed for native
  Mono, Helix/AAC Stereo and experimental libmad/AAC Mono components.
- Static DRAM data+bss: 20840 bytes. IRAM vectors+text+bss: 27384 bytes;
  unchanged from the preceding DMA fix. Dynamic heap headroom and CPU speed
  of this build have **not** been measured on the physical board.
- [Implementation, fixtures and measured PCM results](../../../docs/ESP8266_MP3_MONO.md).

## Installation status and layout

**Not flashed or listening-tested.** The previously verified artifact in
`firmware/development/esp8266-native/` and the physical board are unchanged.
This is an application-only update for the existing 256-KiB SPIFFS / dual
960-KiB OTA-slot layout. Prefer application OTA to the inactive slot. For USB
flashing, resolve the selected boot slot first; do not erase NVS, SPIFFS or
OTA-selection data as part of an ordinary update. No credentials or private
filesystem image are included.
