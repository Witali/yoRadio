# ESP8266 native development artifact

- Source revision: `3acd51d`
- Target: ESP8266EX, 4 MiB flash
- Framework: ESP8266 RTOS SDK v3.4
- Profile: development, diagnostic logging enabled, `-O3`, audio profiler disabled
- Features: HTTP/ICY radio streams, Helix MP3/AAC, WebUI-only display profile
- Application flash offset: `0x10000`
- File: `app.bin`
- Size: 670144 bytes
- SHA-256: `E8455F3EF7EF8F49F60E6E17F7E1E623221A01B91E40D23F37921D5041914B3D`

## Changes

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

- All 243 repository regression tests passed, including native C tests for URL,
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
- All 243 repository regression tests passed.