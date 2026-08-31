# ESP8266 native development artifact

- Source revision: `ceb6440`
- Target: ESP8266EX, 4 MiB flash
- Framework: ESP8266 RTOS SDK v3.4
- Profile: development, diagnostic logging enabled, `-O3`, audio profiler disabled
- Features: HTTP/ICY radio streams, Helix MP3/AAC, WebUI-only display profile
- Application flash offset: `0x10000`
- File: `app.bin`
- Size: 659696 bytes
- SHA-256: `03A2E4F0A3A1A5FB757EB4A7FD4D5902AE1312CA9A303F59797619EDB7C866A7`

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

## Validation

- All 240 repository regression tests passed, including native C tests for URL,
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
