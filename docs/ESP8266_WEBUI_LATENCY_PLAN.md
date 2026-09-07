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
  Subsequent resets: SDK reasons 4 (ASSOC_EXPIRE), 6 (NOT_AUTHED),
  204 (HANDSHAKE_TIMEOUT), 205 (CONNECTION_FAIL), then DHCP around 20 s.
  RSSI at successful connections -68, -72 and -75 dBm, channel 10.
  The firmware now records initial RSSI/channel and numeric disconnect reason.
  These codes do not establish weak signal as the sole cause.
- [x] Add repeatable cold/warm browser timings and actual volume-button tests.
  `tools/test_esp8266_webui_latency.cjs --controls`; requires Playwright and
  installed Edge. JSON and screenshots go to the chosen `--output` directory.
- [ ] Record repeated baseline with stopped/playing radio and one/two tabs.
- [x] Remove measured HTTP transport and player bootstrap bottlenecks, preserving
  standard framing, common UI assets and bounded RAM (no whole-playlist buffer).
- [x] Replace two successive 250 ms player/status polls with state notifications
  and ordered station selection in the same HTTP poll; retain telemetry rate.
- [x] Test Play/Stop/Next/Prev/row clicks, AAC/MP3, mobile layout, settings readback
  and two concurrent subscribers. See `ESP8266_WEBUI_BUNDLE.md` and raw results.
- [ ] Apply equivalent shared-asset bootstrap acceleration to settings. Main
  player reaches 444–452 ms on a healthy run; settings still take 1.7–2.2 s.
- [ ] Extend page timing tests to reload while decoding and control updates
  during a concurrent load. Fix the audit's caught getsystem/radiolink exception.
- [ ] Isolate intermittent network stalls: one run had 50% ping loss even with
  RSSI near -61 dBm. A reset of the same image restored fast controls. A closer,
  unobstructed board placement was requested as an optional control experiment.
- [ ] Verify playback, settings, playlist updates and memory; retain regression
  tests and commit each independently validated change.
- [ ] Repeatedly meet 500/200 ms targets. Record failures, RSSI and maximum as
  well as median/p95; do not discard slow attempts or count only cached shells.

First retained improvements and raw measurements:
[2026-09-07 results](ESP8266_WEBUI_LATENCY_RESULTS_2026-09-07.md).
Full player is now about 0.89..0.92 s in the last four healthy-link samples;
volume confirmations 8..15 ms. Other controls and stressed cases remain open.

External radio DNS/connection/buffering time is a separate measurement, not a
guarantee of playback starting within 200 ms. Cold and warm results are separate.
Wi-Fi has no hard real-time bound; these targets require measured network health.

Private full-flash backup remains outside Git under
`.build/webui-diagnostic-20260907/private/` (contains Wi-Fi credentials).
