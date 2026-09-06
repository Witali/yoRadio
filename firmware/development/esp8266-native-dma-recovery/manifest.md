# Ordinary ESP8266 native DMA recovery — 2026-09-05

- Source: `aab3600`; unrelated Arduino working-tree edits are not in target.
- CPU 160 MHz, QIO40, SDK v3.4 / GCC 8.4 O3 (compact ISR uses Os).
- Mono Helix MP3 SSO/AAC, GPIO3 I2S-PDM32, 2 x 512-word capacity.
- `DMA_COMMITTED_PREFIX=ON`; trace/profile/benchmarks OFF.
- App: 687312 bytes.
- SHA-256: `3B7D1DCF590402C8E493F5A383358087C56359B0B7215A58E6463C34F99C9F15`.

Flashed app0 (`0x10000`) over COM8 and hash verified; bootloader, partition
table, NVS, SPIFFS and OTA selection not written. Restored station/volume.
Physical startup retains the 16-KiB IRAM arena. Static DRAM is 20848 bytes,
IRAM vectors/text/bss 27464. 338 host tests pass. Retro FM MP3 128 starts;
WebSocket status updates, but stream reconnects and startup HTTP delays
remain. New listening acceptance is pending; do not call this fully verified
continuous radio playback. [Results](../../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).
