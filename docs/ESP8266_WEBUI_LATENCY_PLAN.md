# ESP8266 WebUI latency goal

Target: complete usable player within 500 ms of navigation; server-confirmed
button response within 200 ms. Do not confuse an optimistic DOM update with
confirmation, or a connecting indicator with decoded audio starting.

- [x] Restore ordinary SPI-PDM radio on GPIO13/D7 after the isolated tone test.
- [x] Check RSSI and network latency without changing the computer's Wi-Fi.
  2026-09-07: RSSI -70 to -74 dBm, ping 15/15, 2-8 ms; 12 HTTP status
  requests 16-236 ms, TCP connect 3-9 ms. The earlier I2S session had lost
  pings and TCP connection timeouts even at -67 to -70 dBm. Signal strength
  alone does not establish the cause; the firmware and reset also changed.
- [x] Add repeatable cold/warm browser timings and actual volume-button tests.
  `tools/test_esp8266_webui_latency.cjs --controls`; requires Playwright and
  installed Edge. JSON and screenshots go to the chosen `--output` directory.
- [ ] Record repeated baseline with stopped/playing radio and one/two tabs.
- [ ] Remove measured HTTP transport and bootstrap bottlenecks, preserving
  standard framing, common UI assets and bounded RAM (no whole-playlist buffer).
- [ ] Verify playback, settings, playlist updates and memory; retain regression
  tests and commit each independently validated change.
- [ ] Repeatedly meet 500/200 ms targets. Record failures, RSSI and maximum as
  well as median/p95; do not discard slow attempts or count only cached shells.

External radio DNS/connection/buffering time is a separate measurement, not a
guarantee of playback starting within 200 ms. Cold and warm results are separate.
Wi-Fi has no hard real-time bound; these targets require measured network health.

Private full-flash backup remains outside Git under
`.build/webui-diagnostic-20260907/private/` (contains Wi-Fi credentials).
