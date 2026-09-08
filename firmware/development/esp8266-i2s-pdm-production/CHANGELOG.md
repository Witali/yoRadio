# ESP8266 production: I2S PDM32

## 2026-09-08 — Wi-Fi RX A/B campaign return to production

- Source `43e558a`, app 760080 bytes, SHA-256
  `45D5A1A7A7FFFA937F3DBCCA2FB6DD824AF2E0A46BFC455532F068416D757227`.
- OTA HTTP 200, 760402 multipart bytes in 18.238 s; confirmed boot from
  app0 0x10000 after app1 0x110000, followed by client Wi-Fi and HTTP status.
  No bootloader, partition, SPIFFS, playlist or credential writes.
- Includes correct temporary recv-error classification for multipart uploads;
  ten delayed identical-logo uploads passed on hardware before this build.
- Bounded socket-readiness waiting remains opt-in. Production still uses
  wait=0, idle timeout=1000 ms, read limit=1024, one scheduler yield.
  No new RAM buffers, no decoder/PDM algorithm changes. Full radio A/B did
  not justify promoting the receive-only CPU improvement as a default.
- All diagnostic sweeps and profiling disabled; ERROR logging retained.
  Build now verifies stream defaults and records HTTP/audio source hashes.
- Two real Edge pages loaded in 397/317 ms while stopped, ten volume actions
  reached both subscribers in 33–55 ms; Play/Stop/Next/Prev status checks passed.
  230 host tests pass. Physical audio continuity is not implied by these checks;
  DMA underruns remain an open issue documented in the campaign report.
- Details: `docs/ESP8266_WIFI_RX_OPTIMIZATION_2026-09-08.md`.
- Five-minute MP3 128 test: PCM/wall 0.9752, 6559 underrun events; continuity
  failed despite 279 successful health responses. AAC ~65 stopped with
  CONNECTION ERROR around second 124; RSSI reached -92 dBm and 12 health
  requests timed out. Software Stop/Reboot restored client connectivity.
- A page load during MP3 failed with ERR_CONTENT_LENGTH_MISMATCH. After
  Stop, two-page/ten-command smoke passed again. These failures are retained;
  this build is not declared a fix for audio continuity or loaded WebUI.

## 2026-09-08

- User stopped the latency investigation and requested ordinary production
  radio with I2S PDM instead of the temporary SPI debug output.
- Source `fd34463`, app758432 bytes, SHA-256
  `8F3DC79EF7D8C11945F64BAB9CAB5D9A2EA237CD7691CB8F6C814F651DA39B01`.
- Flashed app0 at0x10000 on COM8, hardware flash hash verified. NVS, Wi-Fi,
  full playlist, SPIFFS, bootloader and partition table were not overwritten.
- Standard delta-sigma PDM32 on GPIO3/RX, nominal1.536 MHz
  (integer divider1.538461 MHz), mono48 kHz PCM, two512-word SLC-DMA buffers.
  CPU160 MHz, QIO40, Helix MP3 SSO and Helix AAC. No SPI/RCPDM/PCM transport.
- Tone, codec/output benchmark, audio/memory/WebUI tracing are disabled.
  Application log level ERROR; normal error reporting remains enabled.
- Includes latest shared WebUI initial-snapshot and compact-volume fixes.
  No renewed latency optimization or extended benchmark was requested.
- Build: `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1`.
  Connect the filtered amplifier input to RX/GPIO3, not D7/GPIO13.
  UART was used only for ROM flashing/reset and passive TX log capture.
- Short boot check: firmware runs, but the SDK reports repeated Wi-Fi
  association/disconnection attempts. Two HTTP status attempts timed out;
  network readiness and audible radio were not confirmed. No further Wi-Fi
  debugging or settings changes were performed, per the user's stop request.
  Precompiled SDK Wi-Fi code can still emit its own state messages despite
  the application ERROR log threshold.
