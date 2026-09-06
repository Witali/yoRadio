# ESP8266 native development artifact

- Built: 2026-09-05
- Native source: includes DMA fix 4ad22fb (built before commit; embedded version tag 795000a-dirty). Unrelated Arduino working-tree changes excluded.
- Target: Wemos D1 mini / ESP8266EX, 4 MiB flash, CPU 160 MHz
- SDK: ESP8266 RTOS SDK v3.4, GCC 8.4, -O3
- Profile: diagnostic logging enabled; Helix MP3 SSO + AAC; display disabled
- Output: I2S PDM on GPIO3, nominal 1.536 MHz, two DMA buffers of 512 words
- Flash: QIO 40 MHz (the SDK's boot image header is DIO; SDK enables QIO)
- app.bin: 688656 bytes
- SHA-256: BD2AE0F650AF5B041001B68DEB5EC6E5A3B1028CE87D27B3E10AF1AF5F40CC9A

## Changelog: 2026-09-05 I2S DMA ownership

- Submit only fully filled buffers; finite descriptors prevent DMA from
  revisiting producer-owned storage. Keep two 512-word payload buffers.
- Replace missing audio with 0xAAAAAAAA (50% density PDM audio zero), never
  repeat stale audio or clear a partially filled producer buffer.
- Stop switches to neutral PDM at EOF without modifying active DMA memory.
- Preserve the 16-KiB codec IRAM arena; static DRAM is 8 bytes smaller.
- 331 regression tests passed; isolated physical test: 941 EOFs, zero
  underruns/FIFO-empty observations, 65-ms partial-buffer delay PASS.
- Flashed app0 at 0x10000 and verified the write hash. Normal radio restored,
  Wi-Fi connected; MP3 128 starts. AAC 320 still ended/reconnected during the
  final test, so uninterrupted AAC playback is not claimed. Settings/SPIFFS
  unchanged; restored station 498, volume 254, playback stopped.
- See [DMA fix and limitations](../../../docs/ESP8266_I2S_DMA_OWNERSHIP.md).

## Flash layout — changed; read before using USB flashing

| Image/partition | Address | Size |
| --- | --- | --- |
| bootloader.bin | 0x0 | image size |
| partition-table.bin | 0x8000 | image size |
| NVS, preserved | 0x9000 | 24 KiB |
| PHY, preserved | 0xf000 | 4 KiB |
| app0 | 0x10000 | 960 KiB |
| OTA selection data | 0x100000 | 8 KiB |
| app1 | 0x110000 | 960 KiB |
| SPIFFS | 0x3c0000 | 256 KiB |

ota-data-initial.bin is for first migration only. Do not write it during an
ordinary update. Prefer POST /update through WebUI: it writes the inactive
application slot and preserves NVS/SPIFFS.

The old 3 MiB SPIFFS started at 0x100000. Never flash that old SPIFFS image
using this partition table. Back up and migrate files first, as described in
[the layout guide](../../../docs/ESP8266_OTA_LAYOUT.md).

No Wi-Fi credentials or private SPIFFS image are included in this artifact.

## Changelog: 2026-09-05 WebUI/OTA repair

- Migrated the physical board to 256 KiB SPIFFS and two 960 KiB application
  slots after a complete private flash backup; preserved NVS, Wi-Fi and playlist.
- Added streaming multipart file uploads, Wi-Fi readback/save, Board maintenance,
  native application OTA and an embedded emergency firmware-upload page.
- Kept the shared Arduino/C3/CYD HTML/CSS/JavaScript. Native capabilities hide
  unsupported hardware/settings and disable raw SPIFFS OTA.
- Added two bounded WebSocket subscribers and single-task ownership of the
  shared JSON buffer; corrected connecting/error/format states and throttled VBR.
- Persisted supported settings and applied SNTP/timezone updates at runtime.
- Fixed initial playlist scroll; unchanged CSV uploads no longer trigger a
  list refresh. Failed index replacement rolls back to the previous CSV.
- Batched HTTP framing and playlist data without extra data buffers; applied
  one response-wide send deadline instead of renewing it for every write.
- Raised the TCP PCB limit from 6 to 10 to include the HTTP listener, backlog,
  radio and draining connections. HTTP sessions remain limited to four,
  including two WebSockets. HTTP task stack is 5120 bytes.
- Bootstrap retries failed CSS/JS downloads up to three times sequentially;
  after exhaustion it displays a reload message instead of an endless spinner.

## Verification and remaining limitations

- 322 local regression tests passed, including executable native C tests for
  HTTP framing, streaming multipart and playlist transaction rollback.
- Physical OTA went app0 -> app1 -> app0 in 19.562 / 23.594 seconds on the
  earlier OTA-enabled candidate; both boot addresses were verified.
- On candidate 4c44b75 (before the bootstrap-only change): invalid OTA rejection, identical playlist import, gzip
  WebUI upload, Wi-Fi upload/reboot and byte-exact readback passed.
- HTTP GET retries were necessary. Intermittent incomplete/slow HTTP transfers
  remain unresolved; this is not a claim of full WebUI stability.
- Final browser bootstrap passed: 511 rows, initial scroll, page load 18.195 s,
  four status reads 29/37/37/30 ms. The test restored station 500, volume 160,
  playback stopped. Two-tab stability still requires further acceptance.
- Detailed results and outstanding acceptance checks:
  [repair report](../../../docs/ESP8266_WEBUI_REPAIR_RESULTS_2026-09-05.md),
  [checklist](../../../docs/ESP8266_WEBUI_REPAIR_TODO.md).

Earlier builds and measurements remain available in Git history.
