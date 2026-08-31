# ESP8266 native development artifact

- Source revision: `085f24d`
- Target: ESP8266EX, 4 MiB flash
- Framework: ESP8266 RTOS SDK v3.4
- Profile: development, diagnostic logging enabled, `-O3`, audio profiler disabled
- Features: HTTP radio streams, Helix MP3/AAC, WebUI-only display profile
- Application flash offset: `0x10000`
- File: `app.bin`
- Size: 655808 bytes
- SHA-256: `C1A7B52D3FBC3EA3697BA977D7F24DD7F67A54BA8C4CA39B9289C4E72E802F1C`

## Changes

- Enabled the Helix AAC decoder by default.
- Reserved a complete 2048-sample stereo PCM frame in AAC-enabled builds;
  MP3-only builds retain the smaller 1152-sample granule buffer.
- Added a one-tick scheduler pause after each successfully processed input
  chunk so the idle task can feed the watchdog during continuous streams.
- Retained the opt-in audio stage profiler outside this normal firmware image.

## Validation

- Clean normal firmware build completed successfully with AAC enabled and the
  profiling option disabled.
- All 225 repository regression tests passed.
- AAC 60-77 kbit/s, 22 kHz mono decoded on the physical ESP8266 for four
  consecutive five-second windows without a watchdog reset.
- AAC 320 kbit/s, 44 kHz stereo decoded without the former PCM-buffer overflow;
  measured throughput remained about 37% of real time, so high-rate AAC is not
  yet suitable for uninterrupted playback with synchronous SPI-PDM output.
- Switching from AAC 320 kbit/s to AAC 64 kbit/s completed without reallocating
  the outer codec workspace or corrupting the PCM buffer.
