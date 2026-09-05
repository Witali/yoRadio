# ESP8266 native development artifact

- Built: 2026-09-05
- Source revision: `a08cf8b` (native sources unchanged; unrelated Arduino changes excluded)
- Target: ESP8266EX, 4 MiB flash
- Framework: ESP8266 RTOS SDK v3.4
- Profile: development, diagnostic logging enabled, `-O3`, audio profiler disabled
- Features: HTTP/ICY radio streams, Helix MP3/AAC, WebUI-only display profile
- Application flash offset: `0x10000`
- File: `app.bin`
- Size: 670448 bytes
- SHA-256: `F1D1B954843295A4D9433133EEE7F601B6172EA9F5ABEA253BDB93345FA93E3A`

## Changes

- Rebuilt the current native firmware and flashed the physical Wemos D1 mini.
  Refreshed stale shared WebUI assets in SPIFFS at 0x100000 after a full backup,
  preserving Wi-Fi, playlist and index. The private SPIFFS image is not tracked.
  Application behaviour is unchanged; the build identity reflects the revision.
- Removed the dedicated 2048-byte input task. BOOT and encoder ISRs now queue
  compact events and wake the existing 3072-byte application task with a task
  notification; debounce and click recognition run when that task wakes.
- Added a compact locked playback-state accessor so button toggling no longer
  places a complete 484-byte station-state snapshot on the application stack.
- Replaced the 320-byte station/title status copies with compact hashes while
  retaining every WebUI field and immediate metadata-change notification.
- Formats escaped WebSocket JSON directly into its bounded output buffer and
  reduced the HTTP server task stack from 5120 to 4096 bytes.
- Added an RFC 9112-compatible low-memory HTTP stream parser: correct authority/port
  handling, relative redirects, chunked transfer decoding and bounded socket I/O.
- Made HTTP Server sends nonblocking and deadline-bounded, with correct transient
  errno handling matching the Espressif transport conventions.
- Closed short static/API sessions explicitly, limited the accept backlog and
  bounded active TCP PCBs so connection bursts cannot exhaust the ESP8266 heap.
- Reduced TCP MSS/window memory while preserving enough throughput for radio.
- Fixed Next/Previous so the search starts after, rather than at, the current
  HTTP station.
- Stripped cache-busting query parameters before static SPIFFS lookup so mobile
  browsers can load every versioned CSS, JavaScript and HTML resource.

- Fixed clicks on the full playlist row, not just its nested text, and embedded the
  current shared `script.js.gz` in application flash for safe WebUI updates.
- Built an ESP8266-only station index and WebUI response containing only plain
  HTTP MP3/AAC-compatible entries; HTTPS, Ogg, Opus, FLAC, HLS and WAV are hidden.

## Validation

- Current physical/browser audit: [2026-09-05 report](../../../docs/ESP8266_WEBUI_AUDIT_2026-09-05.md).
  Main player, MP3/AAC, live status and supported settings work, but the full
  shared WebUI is NOT yet implemented. Missing Wi-Fi/upload/update handlers,
  ignored settings, initial playlist scrolling and multi-tab problems remain.
- One-client page load 2.45-3.49 s; volume 53-108 ms; pause/resume/selection
  typically 0.3-0.9 s. Concurrent clients can cause large delays and reconnects.
- Repository regression suite: 301/301 passed. This does not supersede the
  failing live-browser capability checks documented in the audit.

## Historical validation (earlier builds; not a full-WebUI claim)

- On the physical board, free heap after DHCP increased from 21,160 to 23,300
  bytes (+2,140), accounting for the removed stack and task control block.
  The firmware booted at 160 MHz, rejoined Wi-Fi and logged that BOOT input is
  owned by the application task. DTR on this USB-UART adapter does not drive
  GPIO0 independently, so the three physical button gestures still require a
  manual press test.
- The complete repository suite passed: 301 tests, including assertions that
  no input task or input-stack allocation remains and that both button and
  encoder ISRs notify the application task.
- Static DRAM fell from 20,536 to 20,216 bytes; together with the 1,024-byte
  stack reduction this releases 1,344 bytes of runtime RAM. The physical board
  reported 21,160 bytes free after DHCP versus 19,816 before this change.
- All 301 repository tests passed. A physical `getindex` WebSocket exchange
  returned valid station, metadata, volume, RSSI, buffer, bitrate, format,
  uppercase and playback fields followed by the current station index.
- Rebuilt from the tracked canonical `sdkconfig.defaults`, flashed to COM8 and
  verified by the flash tool without erasing NVS or SPIFFS.
- UART startup showed 160 MHz, 89,852 bytes of free heap early in boot and
  19,816 bytes after DHCP; the 16,384-byte IRAM codec arena, 511-station index
  and SPIFFS usage of 92,368 / 2,884,241 bytes were reported correctly.
- The board rejoined the configured router at `192.168.100.6`; `/` and
  `/api/native/status` returned HTTP 200, with station, RSSI and `/ws` status.
- All repository regression tests passed, including native C tests for URL,
  redirect, header-token and fragmented chunked-body handling.
- The physical Wemos D1 mini joined Wi-Fi at `192.168.100.6`. Root HTML, gzip
  JavaScript, the 53,808-byte playlist and native status all returned HTTP 200.
- Twelve concurrent HTTP requests completed successfully; afterwards ping was
  3/3 with 0% loss and the full playlist was served again.
- A real non-default-port HTTP stream with a query played as AAC at 61 kbit/s.
- All versioned mobile WebUI resources returned HTTP 200, including settings,
  player, CSS, JavaScript and the playlist.
- WebSocket Play, Pause, Next, Previous and Stop status scenarios all passed.
- Live WebSocket checks returned system, display, timezone and control settings.
- The physical playlist contains 511 supported entries, 0 HTTPS entries and 0
  explicitly unsupported codec/container entries.
- Direct `play=2` (the exact command sent by a row click) selected Radio Caprice —
  Opera and reached actual playback; all Play/Stop/Next/Previous checks passed.
- All repository regression tests passed.
