# ESP8266 SPI radio: optional WebUI causal trace

## 2026-09-08

- Source `fa842ef`, 769504 bytes, SHA-256
  `514E0D61CE3A67353C9B3B7DE5F019F66A98C92743537EAA329A3DA7EE437F03`.
- Flashed app0 at 0x10000, hash verified. Radio, not a tone generator.
  CPU160/QIO40, SPI-PDM GPIO13/D7, playlist gzip ON, WebProfile ON.
  Wi-Fi, full playlist, station/volume and partition layout preserved.
- Response IDs, bounded SPIFFS read and socket timing counters, EAGAIN versus
  memory errors, bounded sleep budget versus late rescheduling, `getindex`,
  and slow/failed async WebSocket sends. No added task or per-request heap.
- 59 host regressions pass. Exact image: two browser rounds, 12 loads,
  7 above 500 ms (maximum 1348.1 ms); 112 confirmed controls, one at 256 ms.
  No JS/test exception. Initial-state processing 14.4-26.6 ms, no TX retry
  or memory error; no slow async-send records in this particular batch.
- All raw delays retained: no network-wait exclusion was justified.
  Diagnostic output can itself affect timing. This is not a production
  latency claim or a completed 500/200 ms goal.
- Final board: station 176 / volume 254 / stopped, no error. Free heap
  25996 bytes; observed minimum 7532, HTTP stack headroom 2228 bytes.
- Rebuild with `tools/esp8266_audio_profile/build_spi_pdm_debug.ps1 -WebProfile`.
  Non-profiled radio remains in `../esp8266-spi-pdm-debug/`.
  See `docs/ESP8266_WEBUI_TRACE.md` and `trace-index-*` raw results.
