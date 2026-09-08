# ESP8266 SPI radio: optional WebUI causal trace

## 2026-09-08

### Volume trace (`5c121bb`, retained diagnostic)

- 772128 bytes, SHA-256
  `DD16D9E55D20873908BB5D4E9739199A6E48CA41A549A2733099448E4C902BAF`.
- App0/hash verified. Adds fixed-category volume timing; no payload logging.
- Degraded-link run: 24 loads, 17 over500 ms, max21.232 s; 138 of224
  confirmations fail the200 ms/ack requirement. All16 audio starts pass.
- Stopped commands wait~0.9-1.8 s before TCP input; handlers~12-16 ms,
  input-to-handler~1 ms. Initial page shows6.381 s socket wait; no RAM errors.
- Later ICMP has29/33 timeouts. No automatic exclusions or network changes.
- Replaced on the board by the non-profiled build for further testing.

### Initial snapshot (`91889f4`)

- 772064 bytes, SHA-256
  `C3EEAD9E4AA8D46E125A9FA66BBF3277129E7CCF9A23866E7D5E79343C2A4241`.
- Matching shared script uploaded/hash verified. Opt-in snapshot after WS
  upgrade removes a client request; legacy/settings behavior unchanged.
- 66 host tests; 54 functional browser checks pass. Interleaved A/B: new
  p95 300.7/max384.6 ms; old p95 482.8/max508 ms, 30 loads each.
- Separate first run still has 556.5/1269.6 ms outliers. Stress 18 loads
  <=486.5 ms, but two of 168 confirmations take248.1/255.5 ms. Settings
  has one2605.4 ms outlier. No exclusions; latency goal remains open.

### TCP input trace (`14e1526`)

- 770688 bytes, SHA-256
  `B4F040752763A8DF6839943250795B9A9E33A184CFBEE85B44AA3408E996157A`.
- App0/hash verified. Read-only port-80 lwIP input hook in diagnostic builds;
  128-byte recent-connection table, no payload logging, no modified SDK.
- Fresh-boot/no-audio control: 40 loads, all stopped, 268.1-513.4 ms;
  one >500 ms, no JS or WS errors. Two ~210-230 ms command delays occurred
  before lwIP input; input-to-session was only 1.16-1.17 ms.
- This excludes audio decoding for those specific stalls. It does not alone
  distinguish RF loss from client/driver/TCP scheduling. No exclusions.
- Station 176/stopped, free heap 26096/min18804, stack headroom2272.

### UTF-8 repaired diagnostic (`fa1abc1`)

- 769952 bytes, SHA-256
  `3427ACBFAEC7732FC5DE3EF7DF86D7602BEFC4136D715B79BC09B118289F7DF8`.
- Same trace/wiring/profile; no partition or SPIFFS changes. Malformed ICY
  bytes no longer invalidate the whole WS text message; valid UTF-8 unchanged.
- 62 host checks pass. Corrected physical benchmark: 18 loads, maximum
  503.2 ms (3 exceed 500); all 168 confirmations <=77 ms; 12 audio starts
  pass. No JS or UTF-8 frame errors. Zero network exclusions.
- Station 176, volume 254, stopped. Free heap 25684/min8044, HTTP stack
  headroom 2268. The rare ~211 ms select wait is still being investigated.

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
