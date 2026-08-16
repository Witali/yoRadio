# Firmware changelog

Every released build is recorded here. Existing release directories and
entries are retained; changes are published under a new firmware version.

## 0.9.722 — 2026-08-16

### Runtime scheduling

- Moved stream decoding, normalization and PCM output into a dedicated
  `AudioTask` on core 1 at priority 2.
- Kept AsyncTCP/WebUI and display work on core 0, leaving the lower-priority
  Arduino loop on core 1 for controls, OTA and service work.
- Added periodic audio-task timing and stack high-water telemetry when Audio
  Info is enabled.
- Reserved the audio-task stack statically so task creation cannot fragment the
  runtime heap used by network and codec buffers.
- Reused the dedicated audio task for bounded host connections, eliminating the
  transient 6 KiB connection-task allocation and its low-memory failure mode.
- Sized the unified static audio/connection stack to 8 KiB, preserving TLS
  stack headroom while using less peak RAM than the previous two-task path.
- Routed cross-core audio diagnostics through a static non-blocking queue so
  only the service loop writes Telnet sockets, preventing TCP-state races and
  keeping network writes out of the audio hot path.
- Raised web-stream startup prebuffering from 80% to 95% after hardware tests
  detected a near-empty buffer during the first second of MP3 playback.

## 0.9.721 — 2026-08-16

Initial archived build for the ESP32-2432S028 CYD2USB board.

### Audio

- Added internal DAC and I2S PDM/sigma-delta output support.
- Added selectable Helix/minimp3 decoding and made minimp3 the default.
- Added a shared codec arena and decoder cleanup to reduce heap fragmentation.
- Added 100 ms fade-out/fade-in when changing sources.
- Kept the internal DAC at its zero midpoint during stream gaps.
- Added adaptive normalization with configurable maximum boost, target dBFS
  and time constant.
- Optimized normalization with Q12 and a 32-bit soft limiter.
- Added 80% startup prebuffering and a 14-block default input buffer.
- Added independent adaptive left/right VU meters.

### Network and memory

- Added saved Wi-Fi retry attempts before access-point fallback.
- Reduced TLS transmit memory while retaining a 16 KiB receive buffer.
- Fixed decoder and TLS cleanup when changing stations.

### Display and WebUI

- Added Cyrillic and common UTF-8 character normalization.
- Increased display SPI frequency to 80 MHz.
- Added normalization and MP3 decoder controls to WebUI.
- Added content-derived WebUI cache revisions.
- Added confirmations and tests for destructive SPIFFS/settings operations.

### Board integration

- Added touch-to-reconnect from access-point mode.
- Preserved NVS and SPIFFS during normal firmware flashing.
