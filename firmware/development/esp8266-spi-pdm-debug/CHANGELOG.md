# ESP8266 temporary SPI-PDM debugging profile

## 2026-09-08 — settings bundle and playback-load regression tests

- Source `32d8978`; normal radio, SPI-PDM GPIO13/D7, CPU160/QIO40. Tone,
  codec benchmark and WebProfile are disabled. Shared script.js.gz updated;
  Wi-Fi, playlist, NVS and OTA layout preserved; app0 flashed at 0x10000.
- Shared settings bundle, null-DOM guards for system/selection messages,
  and bounded 1024-byte static-response scratch (+512 bytes RAM). No new
  worker stack or whole-playlist allocation; common Arduino/C3 assets remain
  the source for HTML/CSS/JS.
- `app.bin`: 759520 bytes, SHA-256
  `9ED938C2AD147FABBE4C341ED265D9C5C4765C8B218B73D13F00758D978CE3A8`.
- Exact image: all 54 functional browser checks and 52 host regressions pass;
  no JavaScript errors. Initial scroll to station 176 confirmed. Settings
  242–276 ms, acceptance plus readback 14.9–22.6 ms; stopped player 430–450 ms.
- Stress still fails the requested latency limits: AAC/MP3 page loads
  649–755 ms; three of 56 control confirmations exceed 200 ms (211, 230,
  291 ms). Four separately counted decoder starts succeed. Minimum heap
  after the full run 8804 bytes; HTTP stack headroom 2212 bytes. No claim of
  completing the 500/200 ms goal. Station 176 / volume 254 / stopped restored.
- Corrected earlier settings audit timings: its 1.7–2.2 s included an
  intentional 1.5 s test pause; the new dedicated test excludes that pause
  and waits for real saved settings in the DOM.
- Reports and remaining bottleneck:
  `docs/ESP8266_WEBUI_LATENCY_RESULTS_2026-09-08.md` and
  `tests/results/esp8266-webui-latency-20260908/`.

## 2026-09-08 — shared bootstrap and event-driven player status

- Source `9b9b5c6`; ordinary radio, SPI GPIO13/D7, CPU160/QIO40; WebProfile
  and isolated tone/codec benchmarks disabled. Board-default I2S is unchanged.
- Shared gzip player bootstrap (26847 bytes), runtime SPIFFS fingerprint and
  upload invalidation; no parallel HTML/JS implementation. Only script.js.gz
  was updated on SPIFFS; credentials and playlist were preserved.
- Fixed-length flash response with bounded aligned 1024-byte staging in the
  existing HTTP workspace; bounded 1087-byte playlist reads; state-change
  notifications and station-index update in the same HTTP poll. No new task
  or full-playlist RAM allocation.
- `app.bin`: 732896 bytes, SHA-256
  `18F3FC816DFD96135484C861350B0AC2CAAAE3C6BB055642B84CA7419ED1D65A`.
  Flashed app0 at 0x10000 only. No NVS/OTA/partition erase.
- Measured equivalent-source build: five player loads 444–452 ms, first-load
  outlier 1097 ms; all 48 player-button confirmations <=51.5 ms. Two-tab
  volume updates 46–59 ms. AAC320/MP3 and settings readback work; minimum
  measured heap 11272 bytes, HTTP stack headroom 2212 bytes.
- 49 host regression tests pass. Browser audit: 54 functional checks pass,
  plus one caught getsystem/radiolink exception (not yet resolved). Settings
  page still 1.7–2.2 seconds; network stalls remain under investigation.
  These limits mean the complete 500/200 ms goal is **not yet achieved**.
- Full results and remaining work: `docs/ESP8266_WEBUI_BUNDLE.md` and
  `docs/ESP8266_WEBUI_LATENCY_PLAN.md`. Original station 1, volume 254 and
  stopped state restored after tests.
- After flashing this exact saved image: cold 479.0 ms, warm 446.5 ms,
  all 16 button confirmations 8.0–53.9 ms; no browser errors, all 511 rows.
  RSSI -65/-69 dBm. Raw report: `retained-bundle-radio.json` under
  `tests/results/esp8266-webui-latency-20260907/`.

## 2026-09-08 (build 2026-09-07 UTC)

- Restored and tested ordinary SPI radio after the isolated 1 kHz test.
- Source `cae6aaf`: bounded playlist read-ahead, faster ASCII URL filter,
  no unconditional sleeps between static HTTP chunks, initial Wi-Fi RSSI and
  disconnect-reason logging. Optional WebProfile is **off** in this image.
- `app.bin`: 702832 bytes; SHA-256
  `682DC689A9C127C3664EA13A2ADB620906AF4CCA77F91E158E2B8150544E6E57`.
- Application-only app0 update; existing SPIFFS/Wi-Fi, station 1 and volume
  254 preserved. GPIO13/D7 remains the physical audio output.
- Complete player measured about 0.89..0.92 s in the profiled comparison;
  volume-button confirmations 8..15 ms; all 511 stations present. The 500 ms
  target is not yet met. Other controls and two-tab/playing tests remain open.
- After flashing this exact non-profiled image: cold 1.149 s (one slow script
  request), warm 0.843 s; volume acknowledgements 7.9..13.5 ms; no JS errors.
- See `docs/ESP8266_WEBUI_LATENCY_RESULTS_2026-09-07.md` for raw reports,
  network outliers and the 31 passing regression checks.

## 2026-09-07

- Wemos D1 mini: move the **audio filter input** from RX/GPIO3 to D7/GPIO13.
  GPIO14/D5 carries the SPI clock; do not connect it to the amplifier input.
  Retain the RC filter, AC coupling, common ground and high-impedance amplifier
  input. Never drive a low-impedance speaker directly from either GPIO.
- Normal native radio, Helix MP3 SSO/AAC, CPU 160 MHz, flash QIO 40 MHz.
  Uses existing asynchronous HSPI PDM8 at 384615 bit/s, 48 kHz PCM. I2S and
  RC-PDM are disabled. This is a temporary debugging trade-off, not a claim of
  audio quality equivalent to I2S PDM32.
- Board defaults remain I2S PDM32 on GPIO3. The overlay changes only audio
  selection; network, HTTP, storage and decoder defaults are inherited.
- `app.bin`: 702208 bytes, SHA-256
  `4F0BB139AC2FFC95300D4CED3E89C094DEA8F8036A6802537FAFFB51E32B0FFD`.
  Exact build configuration and source identity are in `sdkconfig` and
  `manifest.json` beside the image.
- Flash **only app0 at 0x10000**, after verifying the active OTA slot and taking
  a private backup. Do not write the build's initial OTA data, partition table,
  bootloader, NVS, PHY or SPIFFS. App0/app1 are 960 KiB, SPIFFS 256 KiB.

Build from repository root (does not flash):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/esp8266_audio_profile/build_spi_pdm_debug.ps1
```

## Before changing output

The board was reachable intermittently at 192.168.100.6, native radio stopped,
RSSI -67 to -70 dBm, free heap 22.7-24.3 KB, minimum 17356 bytes, HTTP stack
remaining 2340 bytes. The read-only Edge run loaded 511 stations and received
WebSocket updates, without JS/resource errors, but needed roughly 49 seconds.
The first HTML response alone took 23.46 seconds; script.js took 14.72 seconds.
Five of six later standalone TCP connections timed out at four seconds.
The router answered all comparison pings in less than 1 ms. These observations
localize delays to the device/network path, not a broken JS page or audio load;
they do not prove a hardware cause. UART passive capture was silent.

Full logs/screenshots and the credential-bearing flash backup are private,
under ignored `.build/webui-diagnostic-20260907/`, never included in Git.

At this earlier point the ordinary SPI radio image was built but **not flashed**: the user next
requested an isolated 1 kHz output test. The installed test is documented in
`../esp8266-spi-pdm-tone/CHANGELOG.md`. WebUI comparison after the output change
must wait until normal radio firmware is restored.
