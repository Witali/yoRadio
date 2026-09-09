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
