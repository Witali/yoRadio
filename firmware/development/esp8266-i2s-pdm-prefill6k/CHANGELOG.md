# ESP8266 native — I2S PDM, 6-KiB compressed input

## 2026-09-09 — prefill and per-frame refill

- Source: `a2edf76b5ed6669aaf62e75612552eca87b79a89`.
- App: 760768 bytes, SHA-256
  `37CA790E0FA59C01AC800427E632861D68BC5F9FAA15D6636727146A80C08AF6`.
- Compressed input grows from 1536 to 6144 bytes (+4608 bytes dynamic DRAM).
  Reuses the decoder input; no additional FIFO or task/stack.
- Startup/reconnect attempts to fill the entire input for at most 1000 ms.
  Playback refills nonblocking before each compressed frame; no wait for a
  full buffer once playing. Stop/station changes cancel the prefill.
- Incremental ICY filtering covers split metadata and the initial HTTP body.
  Network EOF/timeout drains complete queued frames before reconnecting.
  Playing is published only after successful PCM output.
- Output and decoders unchanged: mono Helix MP3 SSO + AAC, standard I2S PDM32
  on RX/GPIO3, nominal 1.536 MHz, two 512-word DMA buffers. CPU160, QIO40.
- Production ERROR logs; all tone tests, benchmarks and tracing disabled.
  App fits the existing 960-KiB OTA slot; no partition/SPIFFS changes.
- Host verification: 236/236 ESP8266 tests pass, no skips. Actual Helix
  MP3/AAC PCM and frame formats match legacy draining exactly at input sizes
  1536/4096/6144 and read chunks 1/73/1024 bytes.
- Built and saved only, **not flashed**. Runtime free heap, WebUI load and
  continuous physical audio still require on-board tests; this is not a
  claim that the earlier DMA underruns or Wi-Fi dropouts are fixed.
- Install through native WebUI OTA; do not send UART application commands or
  automatically fall back to serial while the audio circuit is on RX.

Build:
`tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-i2s-pdm-prefill6k`

[Design and test results](../../../../docs/ESP8266_INPUT_PREFILL_2026-09-09.md).

## 2026-09-09 — physical OTA validation (same binary)

- Native `/update` accepted the app; active slot changed from 0x10000 to
  0x110000. No SPIFFS/NVS/partition image uploaded, no serial reset/TX commands.
- Free heap after boot: 23956 bytes. MP3 128 playback failed continuity and
  stalled API requests; cumulative SDK minimum reached 4612 bytes, then 1024
  after another station attempt. These are allocator minima, not largest blocks.
- Stopped-player two-tab WebUI smoke passed: 263/273 ms initial readiness;
  ten volume actions acknowledged in both tabs in 22–71 ms; volume restored.
- This is **not a stability-qualified production image**. No successful
  20-second continuous PCM run; AAC/high-bitrate hardware checks remain open.
  See the linked document and saved board reports for evidence and caveats.
