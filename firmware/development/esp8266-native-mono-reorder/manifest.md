# ESP8266 native mono + shared reorder development build

- Built: 2026-09-05, source commit `f3138f2`.
- Embedded version: `v0.9.693-422-gf3138f2-dirty`. Unrelated Arduino
  working-tree changes are excluded from this native target.
- Target: Wemos D1 mini / ESP8266EX, CPU 160 MHz, 4 MiB QIO40 flash.
- SDK: ESP8266 RTOS SDK v3.4, GCC 8.4, O3.
- Profile: ordinary `sdkconfig.defaults`, Mono, Helix MP3 SSO + AAC,
  I2S-PDM32 on GPIO3, two 512-word DMA buffers.
- `YORADIO_ESP8266_MP3_SHARED_REORDER=ON`; profiling/benchmark/tone probes OFF.
- `app.bin`: **686848 bytes**.
- SHA-256: `65D3515B9B54F0F7BA50724011754627C3A0EDD1AF5F83ECEB4FF87F6F6007C7`.

## Changelog

- Reuse 792 bytes of idle channel-0 IMDCT output as MP3 short-block reorder
  scratch; remove the separate DRAM allocation and retain one memory owner.
- Both mono M/S and stereo/fallback use the shared scratch. PCM is byte-for-
  byte identical to the separate-buffer reference in the A/B tests.
- 331 host tests pass, including allocation-failure cleanup, scratch canaries,
  reset and 50 AAC/MP3 allocation cycles. Ordinary Xtensa firmware builds.
- Static DRAM remains 20840 bytes; IRAM vectors/text/bss remains 27384 bytes.
  Dynamic allocation saving is 792 bytes plus unmeasured allocator overhead.
- Flash text and application image are 96 bytes smaller than the preceding
  mono build. No input-buffer, stack, DMA or WebUI configuration change.
- [Details and results](../../../docs/ESP8266_MP3_REORDER_REUSE.md).

## Hardware / installation status

Flashed on 2026-09-05 to the physical Wemos D1 mini (COM8), application only
at `0x10000`, with esptool hash verification. The preceding app0 was backed
up locally. Bootloader, partition table, NVS, SPIFFS and OTA selection were
not written. Wi-Fi, station 498, volume 254 and the 511-station index restored.

WebUI `/` returned HTTP 200. A short WebSocket play/stop smoke test started
ROCK FM MP3 128 kbit/s, received 11 frames, and restored the stopped state.
The first stream-open attempt failed with -4; the retry returned HTTP 200.
MP3 workspace reported DRAM 9528 bytes, IRAM 16384 bytes. One playing
snapshot showed free heap 12532 bytes and minimum heap 10572 bytes; these
are short-run observations, not a worst-case memory/performance guarantee.
CPU timing, prolonged RF-load stability, AAC playback and listening remain
untested for this build. No credentials or private filesystem included.
