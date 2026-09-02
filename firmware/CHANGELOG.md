# Firmware changelog

Every released build is recorded here. Existing release directories and
entries are retained; changes are published under a new firmware version.

## Development — 2026-09-02

### ESP8266 production firmware and WebUI refresh

- Rebuilt and flashed the QIO80/160-MHz Helix SSO production profile with
  1.536-MHz I2S/SLC DMA PDM output.
- Updated the physical board to the current shared compressed WebUI while
  preserving `wifi.csv`, `playlist.csv`, and `playlist.idx`; all 11 HTTP
  resources returned `200`, including the 511-station filtered playlist.
- Added Web API regression coverage for Play, Stop, Toggle, Next, Previous,
  current-station publication, player state, bitrate, and RSSI. All 278
  repository tests pass.
- The live API run also exposed a separate audio issue: the selected stream
  can remain stopped and eventually make the board unreachable. The archived
  image records the exact firmware used to reproduce that problem.

## Development — 2026-09-01

### ESP8266 I2S-PDM 1.536-MHz carrier

- Set the default I2S/SLC PDM carrier to nominally 1.536 MHz. The ESP8266
  divider produces 1.538461 MHz (+0.16%) and production uses genuine PDM32 x1;
  genuine PDM128 at 6.144 MHz remains an experimental build option.
- Two static 512-word DMA buffers implement true ping-pong buffering. They
  occupy 4,096 bytes and each covers about 10.67 ms. A direct FreeRTOS task
  notification blocks once per returned buffer, replacing 2-ms polling
  without dynamic allocation.
- Added a 456-byte IRAM, branchless, fully unrolled PDM32 packer. On the
  physical Wemos D1 mini it generated 100.2% realtime PCM with zero ping-pong
  underruns and reduced producer non-wait time from 33.5% to 9.1% (3.66x).
  Genuine PDM128 at 6.144 MHz reached only 64.4% realtime and remains rejected.
- Isolated 320-kbit/s RAM fixtures measured Helix MP3 SSO at 28.12% CPU and
  Helix AAC-LC at 76.20% CPU. The production binary is archived under
  [`development/esp8266-native-qio80-sso-pdm1536/`](development/esp8266-native-qio80-sso-pdm1536/).

### ESP8266 MP3 SSO with 384-kHz SPI-PDM

- Added a separate MP3 SSO + SPI-PDM8 profile while retaining 16-bit,
  769.231-kHz SPI-PDM as the normal default.
- The new HSPI configuration outputs eight PDM bits per 48-kHz PCM sample at
  384.615 kHz. It halves conversion work and transfer interrupts, doubles the
  12-block queue coverage to about 16 ms, and trades this for higher one-bit
  quantization noise.
- Built the complete QIO80/160-MHz radio and WebUI image, verified the final
  SDK configuration, and passed all 267 repository tests. The build is
  archived for physical testing under
  [`development/esp8266-native-qio80-sso-pdm8/`](development/esp8266-native-qio80-sso-pdm8/).

### ESP8266 isolated audio-output profiles

- Added a deterministic generated-PCM benchmark that exercises the real audio
  driver without Wi-Fi, HTTP, flash reads, or a decoder.
- Removed the producer-side 64-byte SPI-PDM copy by filling a reserved static
  queue slot directly. On the physical Wemos D1 mini this reduced output
  compute by 6.07% and total CPU busy time by 1.2 percentage points with no
  heap cost.
- Saved one QIO80 configuration for both stream profiling and generated-PCM
  output testing. SPI-PDM remains the default; the same benchmark compiles
  with fixed I2S/SLC DMA for a future GPIO3/15/2 hardware comparison.
- Refreshed and flashed the ordinary QIO80 radio/WebUI image after testing;
  WebUI returned HTTP 200 at `192.168.100.6`.

### ESP8266 Helix 32-bit SSO MP3 synthesis

- Added an optional reduced-precision Helix polyphase path that maps the hot
  synthesis loop to native LX106 32-bit multiply/accumulate operations without
  adding decoder buffers. The exact 64-bit path remains available at build
  time.
- The retained 320-kbit/s stereo fixture kept all frames and samples, measured
  48.50 dB PCM SNR against exact Helix, and had a maximum error of 34 signed
  16-bit PCM levels.
- On the physical 160-MHz Wemos D1 mini, average MP3 frame time fell from
  13,705 to 6,414 us (53.20%); isolated throughput rose from 1.751x to 3.741x
  realtime with unchanged codec DRAM and free heap.
- Built and flashed the complete radio/WebUI QIO80 image. It connected at
  `192.168.100.6`, served WebUI/status/playlist over HTTP 200, and started an
  MP3 128-kbit/s stereo station through WebSocket control.
- Archived the development image and exact hashes under
  [`development/esp8266-native-qio80-sso/`](development/esp8266-native-qio80-sso/).

### ESP8266 experimental libmad IRAM frame workspace

- Moved the 4,608-byte Layer III spectral workspace and 2,304-byte reorder
  workspace from `mad_frame` DRAM into the shared aligned 32-bit IRAM arena.
  The byte-addressed stream reservoir, frame header, subband samples, and
  overlap state remain in DRAM.
- Reduced the Xtensa `mad_frame` layout from 20,784 to 13,880 bytes, freeing
  6,904 bytes of 8-bit DRAM. The MP3-only profile now reserves 12 KiB IRAM,
  of which the decoder uses 11,152 bytes.
- Verified byte-identical PCM between the original and external-workspace
  layouts, passed all 261 repository tests, and built both MP3-only and full
  libmad+AAC QIO80 images.
- On the physical 160-MHz Wemos D1 mini, the new libmad decoded the retained
  320-kbit/s RAM frame in 11,965 us average (2.005x realtime), versus Helix at
  13,786 us (1.740x). libmad is 13.21% faster by frame time, but uses 7,424
  bytes more DRAM and adds 50,384 bytes of flash. The ordinary validated Helix
  radio image was restored after the benchmark and obtained `192.168.100.6`.
- Archived the test image under
  [`development/esp8266-native-libmad-iram/`](development/esp8266-native-libmad-iram/)
  without replacing the previously hardware-validated libmad image.

### ESP8266 experimental libmad MP3 backend

- Follow-up: made libmad follow the common codec-arena lifetime. `mad_stream`,
  `mad_frame` and `mad_synth` now have symmetric allocation/free paths; input,
  PCM and decoder state are created only after stream detection and released
  on Stop/error.
- Added exact DRAM/IRAM accounting, post-allocation reserve checks and a
  50-create/50-switch physical stress test; heap returned from 96,868 to 96,868
  bytes with no leak.
- Added the tested MP3-only QIO80 profile. Its 5-KB IRAM arena covers the
  measured 4,236-byte `mad_synth`, and its 2,304-byte PCM buffer lets real
  128-kbit/s MP3, ICY metadata, WebUI HTTP 200 and Stop coexist on the Wemos.
- Replaced the previous reset-loop development `app.bin` with the working
  MP3-only image. The combined libmad+AAC profile remains build-only because
  AAC's 16-KB word arena leaves insufficient contiguous heap for libmad.

- Added a pinned ESP8266Audio `libmad-8266` backend selected by
  `CONFIG_YORADIO_MP3_DECODER_LIBMAD`; Helix remains the production default.
- The deterministic 320-kbit/s fixture produced the same frame/sample count
  as Helix, with 49.41 dB SNR and a maximum difference of 99 PCM levels.
- Built both Helix and libmad QIO80 radio profiles and passed all 256 repository
  tests. On the physical 160-MHz Wemos D1 mini, libmad decoded the 320-kbit/s
  MP3 RAM fixture at 1.859x realtime versus 1.679x for Helix: 10.72% higher
  throughput and 9.69% lower average frame time.
- The full libmad radio image is not usable yet: allocating its 33,336-byte
  workspace before Wi-Fi makes `network_service_start()` fail and causes a
  repeatable reset loop. Helix remains the production default; the working
  QIO80 Helix image was restored after the test.
- Archived the experimental application and recovery binaries under
  [`development/esp8266-native-libmad/`](development/esp8266-native-libmad/).

### ESP8266 native persistent WebUI server

- Changed static WebUI delivery to standard HTTP/1.1 persistence: every
  response is explicitly framed and the browser reuses one keep-alive
  connection instead of reopening TCP for each asset.
- Serialized the ESP8266-only asset loader while retaining the common YoRadio
  HTML, JavaScript and CSS sources used by the other firmware targets.
- Increased the bounded server capacity to four active Web sessions and a
  three-connection listen backlog, with short idle expiry and LRU recovery.
- Backported the standard WebSocket connection-state query and stopped stale,
  reused file descriptors from closing an unrelated HTTP request.
- Flashed the QIO 80 MHz image on the physical Wemos D1 mini. With WebSocket
  open, nine page resources reused one HTTP socket; live playlist-row Play,
  Stop, Toggle, Next and Previous scenarios passed, along with 42 focused
  regressions.
- Replaced the checked development application and recorded its exact hash in
  [`development/esp8266-native-qio80/`](development/esp8266-native-qio80/).

### ESP8266 native QIO 80 MHz experiment

- Added a separate `sdkconfig.qio80.defaults` profile while retaining QIO
  40 MHz as the normal default.
- Identified the physical 4 MiB flash by JEDEC ID `5E:4016` as a Zbit
  ZB25VQ32B, whose Quad I/O read specification covers 80 MHz at 3.3 V.
- Flashed a physical Wemos D1 mini without erasing NVS or SPIFFS and verified
  two starts, Wi-Fi, WebUI/API access and repeated playlist reads.
- Archived the checked binaries and hashes in
  [`development/esp8266-native-qio80/`](development/esp8266-native-qio80/).

## Development — 2026-08-31

### ESP8266 native WebUI station selection

- Fixed clicks on the full station row and verified that the emitted `play=N`
  command selects and starts the requested station on a physical Wemos D1 mini.
- Kept the repository playlist shared, but made the ESP8266 index and WebUI list
  contain only its supported plain-HTTP MP3/AAC streams: 511 entries, no HTTPS
  and no Ogg/Opus/FLAC/HLS/WAV entries.
- Embedded the current shared `script.js.gz` in application flash, so this WebUI
  fix is delivered without overwriting SPIFFS, `wifi.csv` or the stored playlist.
- Built and flashed source revision `3acd51d`; all 243 regression tests and the
  live Play/Stop/Next/Previous/playlist-click scenarios passed. The checked
  artifact and SHA-256 manifest are in
  [`development/esp8266-native/`](development/esp8266-native/).
### ESP8266 native HTTP stack stabilization

- Corrected HTTP authority, redirect and chunked-transfer parsing for the
  low-memory radio client and added native protocol tests.
- Made ESP HTTP Server writes bounded and nonblocking, explicitly closed short
  static/API sessions and capped TCP PCB allocation to prevent heap exhaustion.
- Fixed mobile WebUI startup by excluding cache-busting query parameters from
  static SPIFFS filenames; all versioned page resources now return HTTP 200.
- Flashed and tested the physical Wemos D1 mini: 12 concurrent requests, three
  53,808-byte playlist transfers, follow-up HTTP and ping all succeeded.
- Played a real HTTP AAC stream on a non-default port and verified WebSocket
  Play/Pause/Next/Previous/Stop synchronization.
- Built source revision `ceb6440`; all 240 regression tests passed. The checked
  artifact and SHA-256 manifest are in
  [`development/esp8266-native/`](development/esp8266-native/).

## Development — 2026-08-30

### ESP8266 native asynchronous WebUI image

- Backported the standard ESP HTTP Server asynchronous request API and moved
  SPIFFS/static WebUI responses to one low-memory worker.
- Kept the primary HTTP task available for WebSocket and status traffic while
  static files are being read and transmitted.
- Protected asynchronous sockets from receive polling and LRU eviction until
  their worker completes the request.
- Built source revision `eed1ac0` with `-O3` and archived the application at
  [`development/esp8266-native/`](development/esp8266-native/).
- Flashed a physical ESP8266EX and concurrently loaded the WebUI shell, six
  compressed assets and the 53,808-byte playlist. Every request returned 200,
  while the same WebSocket delivered 46 ping replies.
- Confirmed 36,032 bytes of free heap after DHCP with no reset, stack fault or
  allocation error; all 218 repository tests passed.
## Development — 2026-08-29

### Native ESP-IDF ESP32-C3 OLED production and development images

- Merged `codex/esp32c3-overclock-profile` through source revision `eef49d1`.
- Rebuilt and archived separate production and development artifact sets. Each
  set includes an OTA/WebUI `app.bin`, a 4 MiB recovery `full.bin`, bootloader,
  partition table, initial OTA selector and a SHA-256 manifest:
  - [`development/esp32c3-oled-native-production/`](development/esp32c3-oled-native-production/)
  - [`development/esp32c3-oled-native-development/`](development/esp32c3-oled-native-development/)
- The production application leaves 31% of the smallest app partition free;
  the development application with diagnostic logging leaves 24% free.
- Recovery images deliberately exclude user SPIFFS content. Flashing
  `full.bin` at `0x0` erases the complete flash; normal OTA updates use
  `app.bin` and preserve settings.
- Fixed SNTP server-name lifetime: lwIP now receives pointers backed by
  persistent storage rather than a deleted startup task stack.
- Moved reconnect-triggered SNTP control and synchronization reporting to a
  FreeRTOS task at priority 1. The lwIP callback only posts a constant-time
  task notification.
- Confirmed an SNTP response on a physical ESP32-C3 at 8.237 seconds while a
  320 kbit/s MP3 stream was already decoding, with no underrun, reconnect or
  audio interruption.
- Exercised MP3, AAC and Ogg streams near 320 kbit/s. Decoder load remained
  about 25–28% for MP3, 21% for AAC and 33–34% for Ogg, leaving at least a
  roughly 3x real-time decoding margin.
- Verified Wi-Fi client mode, HTTPS certificate validation, WebUI status,
  SSD1306 initialization, stereo PDM output, playlist restoration and 55 host
  regression tests.
- Recorded the exact build identity, flash offsets, sizes and SHA-256 values in
  the accompanying manifests for both profiles.

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
