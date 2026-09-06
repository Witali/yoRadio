# ESP8266 native PCM32 / direct DMA development build

- Built and flashed: 2026-09-05; source commit `6bd547b`.
- Target: Wemos D1 mini / ESP8266EX, CPU 160 MHz, 4 MiB QIO40 flash.
- SDK: ESP8266 RTOS SDK v3.4, Xtensa GCC 8.4, O3.
- Profile: tracked `sdkconfig.defaults`, Mono, Helix MP3 SSO + AAC,
  GPIO3 I2S-PDM32 at nominal 1.536 MHz (actual 1.538461 MHz), 2 x 512 words.
- Shared MP3 reorder ON; audio trace/profiling/benchmark/tone probes OFF.
- `app.bin`: **687232 bytes**.
- SHA-256: `4F4D732668DD9AC38A5F4534593290D1C2D1C6E20B5FC30065D02B7504F5796C`.
- Unrelated Arduino working-tree edits are excluded from this native target.

## Changes and verification

Helix MP3 produces 32 frames per callback; mono PCM is 64 bytes rather than
1152. PDM conversion writes directly into a producer-owned DMA span without
the intermediate 64-word array/copy. The fixed two-buffer ownership protocol
and task stack sizes are unchanged. Signed balance clamping fixes neutral
balance muting; mono bypasses balance for restored and runtime settings.

337 host tests pass; focused direct-DMA tests pass after the final reset
check. ELF static DRAM is 20848 bytes and IRAM vectors/text/bss is 27384.
Physical MP3 workspace is 8440 DRAM / 16384 IRAM. GCC function-local
output-write stack frame falls from 352 to 80 bytes; this does not measure
whole-task stack usage or imply returned heap space.

Flashed only app0 at `0x10000` over COM8, esptool hash verified, then reset.
No bootloader, partition-table, NVS, SPIFFS or OTA-selection writes. Station
510, volume 254 and 511 playlist entries restored. WebSocket play started
Retro FM MP3 128 kbit/s; WebUI `/` returned HTTP 200 in 0.192 s. A playing
snapshot showed heap 14040, lifetime minimum 7192, web stack headroom 2328.
Stream EOF/reconnects and one failed open attempt were observed; these are
not declared fixed. Board left playing for a user listening check, which is
not yet confirmed. No matched hardware CPU benchmark or long-run claim.

Diagnostic PCM-to-DMA proof and retained logs:
[PCM32 / direct DMA results](../../../docs/ESP8266_PCM32_DIRECT_DMA.md).
