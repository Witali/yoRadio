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
- [x] Record baseline with stopped/playing radio and one/two tabs; continue
  repetitions after each change. `--stress` now reloads during AAC320/MP3
  decoding and clicks real controls while the second tab is loading.
- [x] Remove measured HTTP transport and player bootstrap bottlenecks, preserving
  standard framing, common UI assets and bounded RAM (no whole-playlist buffer).
- [x] Replace two successive 250 ms player/status polls with state notifications
  and ordered station selection in the same HTTP poll; retain telemetry rate.
- [x] Test Play/Stop/Next/Prev/row clicks, AAC/MP3, mobile layout, settings readback
  and two concurrent subscribers. See `ESP8266_WEBUI_BUNDLE.md` and raw results.
- [x] Apply equivalent shared-asset bootstrap acceleration to settings.
  Correction: the old 1.7–2.2 s audit result included its deliberate 1.5 s
  sleep and was not a page-load measurement. The new observer requires live
  settings snapshots, DOM readback, capabilities, logo and Wi-Fi HTTP success.
  Actual baseline 531–534 ms; accelerated page 217–291 ms in these runs.
- [x] Extend page timing tests to reload while decoding and control updates
  during a concurrent load. Fix caught settings-link and station-selection
  messages when their target DOM is absent on the other page.
- [x] Remove repeated raw playlist parsing/transmission from the normal gzip
  request path. Optional `CONFIG_YORADIO_PLAYLIST_WEB_GZIP` defaults ON;
  build after upload, validate/reuse at boot, bounded identity fallback.
  36086 -> 12637 wire bytes; no whole-playlist RAM buffer. OFF excludes the
  encoder/cache objects. See `ESP8266_PLAYLIST_WEB_GZIP.md`.
- [x] Trace socket/flash/receive wall times, explicit TX waits, RAM errors,
  browser receive/handshake/initialization and independent ICMP latency.
  Keep raw statistics plus a separately explained processing sample; unknown
  causes must not be discarded. See `ESP8266_WEBUI_TRACE.md`.
- [x] Extend tracing before WS frame reads: separate select wait, readiness-to-
  dispatch, receive/parsing and response time; bound browser/board clocks.
- [x] Reproduce and fix malformed ICY bytes in WebSocket JSON. A raw F1 byte
  caused browser UTF-8 failures and repeated two-second reconnects. Preserve
  valid text, show '?' for invalid bytes; do not discard the status message.
  Actual C writer regression covers malformed/truncated UTF-8 and capacities.
- [x] Fix benchmark boundary cases: a minus click at zero is not an expected
  changed-value acknowledgement. Do not exercise controls on a failed page.
- [x] Remove the redundant initial getindex round trip for the opt-in native
  player. Preserve legacy/settings behavior and queue early snapshots safely.
  Same-image interleaved physical A/B and MP3/AAC/two-tab tests retained.
- [ ] Trace individual slow controls: two volume confirmations still took
  248-256 ms after the initial-snapshot improvement.
- [ ] Isolate intermittent network stalls: one run had 50% ping loss even with
  RSSI near -61 dBm. A reset of the same image restored fast controls. A closer,
  unobstructed board placement was requested as an optional control experiment.
- [ ] Verify playback, settings, playlist updates and memory; retain regression
  tests and commit each independently validated change.
- [ ] Repeatedly meet 500/200 ms targets. Record failures, RSSI and maximum as
  well as median/p95; do not discard slow attempts or count only cached shells.

First retained improvements and raw measurements:
[2026-09-07 results](ESP8266_WEBUI_LATENCY_RESULTS_2026-09-07.md).
That earlier stage reached 0.89..0.92 s. The subsequent shared bundle,
bounded direct reads and fixed-length HTTP response reached 444..452 ms in
five healthy-link loads, but the first attempt took 1097 ms. All 48 player
button confirmations in that batch were <=51.5 ms; two-tab volume updates
46..59 ms. See `ESP8266_WEBUI_BUNDLE.md`. Settings are now accelerated, but
the optional playlist cache improves normal loads to 249-416 ms in 17/18
exact-image attempts, but one takes 3440.5 ms. All 168 control confirmations
in that batch are <=158.9 ms. Later diagnostic runs still reproduce slower
loads and controls; do not declare completion or discard unknown causes.
Latest measurements: `ESP8266_WEBUI_LATENCY_RESULTS_2026-09-08.md`.

External radio DNS/connection/buffering time is a separate measurement, not a
guarantee of playback starting within 200 ms. Cold and warm results are separate.
Wi-Fi has no hard real-time bound; these targets require measured network health.

Private full-flash backup remains outside Git under
`.build/webui-diagnostic-20260907/private/` (contains Wi-Fi credentials).
