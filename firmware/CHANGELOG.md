# Firmware changelog

Every released build is recorded here. Existing release directories and
entries are retained; changes are published under a new firmware version.

## 0.9.724 — 2026-08-16

### ESP32-C3 0.42-inch OLED target

- Added an opt-in profile for the 01Space-style ESP32-C3 board with the
  onboard 72x40 SSD1306 OLED.
- Added a native 72x40 display driver with the panel-specific initialization
  sequence and 28-column controller offset instead of treating it as a
  cropped 128x64 display.
- Added a compact player, playlist and access-point layout for the 72x40
  visible area.
- Configured the onboard OLED on GPIO5/GPIO6 and the BOOT button on GPIO9.
- Adapted all explicitly pinned work to the ESP32-C3's single core.
- Configured external I2S audio on GPIO1 (BCLK), GPIO3 (LRC/WS) and GPIO10
  (DIN); ESP32-C3 has no internal analogue DAC.
- Added a reproducible build script and regression tests for the board
  profile, task placement, audio wiring and OLED geometry.

## 0.9.723 — 2026-08-16

### DAC startup

- Deferred installation and routing of the internal DAC until Arduino `setup()`
  is running, avoiding peripheral writes from the global audio constructor.
- Started the zero-filled I2S DMA path at DAC code 0 and ramped the analogue
  bias to its code-128 midpoint over 100 ms before any media can play.
- Kept midpoint samples queued before and after the first decoded frame changes
  the I2S sample rate.
- Preserved midpoint silence while stopped, connecting, buffering or recovering
  from a decoder error; the existing 100 ms media fade-in/fade-out remains in
  place above this hardware-bias sequence.
- Added regression tests for initialization order, ramp endpoints, clock-change
  protection and unsigned DAC silence.

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
