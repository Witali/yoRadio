# ESP8266 SPI radio: optional WebUI causal trace

## 2026-09-08

### Dispatch/input trace (`bf530f3`)

- 769696 bytes, SHA-256
  `4258A7118F9731CFA4D80E5FD7FBA0EE86E22AD78FB9291CA3192628282D3C89`.
- Flashed/verified app0, unchanged SPI radio wiring and saved files.
- Trace now starts before WS frame reads; records select wait, readiness-to-
  dispatch and parsed-command timestamps. Browser/board clock bounds, not
  assumed synchronized clocks. Conservative filtering retains other delays.
- 60 host checks passed. Physical trace uncovered invalid upstream ICY text
  passed into WS, causing browser UTF-8 errors and reconnects. Raw failed
  attempts retained; no network-wait exclusion. See `trace-dispatch-*`.

### Earlier getindex/send trace (`fa842ef`)

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
