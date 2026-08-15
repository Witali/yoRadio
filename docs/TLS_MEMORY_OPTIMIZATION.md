# TLS memory optimization TODO

Target: ESP32-D0WD-V3 without PSRAM, Arduino-ESP32 3.3.8, internal DAC build.

The goal is to keep HTTPS radio reliable without taking memory away from
non-TLS codecs. A change is accepted only after switching repeatedly between
HTTP AAC and HTTPS MP3 on the physical board without decoder allocation or
host connection failures. NVS and SPIFFS must remain untouched.

## Baseline (2026-08-15)

Measurements include an active Telnet diagnostic client, which itself lowers
the available heap. After closing Telnet, the stopped player reported 76,164
bytes free and a 59,380-byte largest block.

| State | Free heap | Largest block | Notes |
|---|---:|---:|---|
| Stopped, before test | 88,476 | 86,004 | Telnet connected |
| HTTP AAC, station 117 | 48,192 | 38,900 | Playing |
| HTTPS MP3, station 574 | 6,576 | 2,932 | Playing, Telnet connected |
| HTTPS MP3, station 591 | 7,888 | 1,588 | Playing, Telnet connected |
| Stopped after test | 74,980 | 40,948 | Before closing Telnet |
| Stopped, new Telnet session | 76,164 | 59,380 | Network allocations coalesced |

Arduino-ESP32 3.3.8 ships a prebuilt mbedTLS configuration with symmetric
16 KiB input and output record buffers. Its `WiFiClientSecure` API does not
provide `setBufferSizes()`, so sketch-only macro overrides are rejected: they
would make the sketch and precompiled mbedTLS library ABI-incompatible.

## Work list

- [x] Free the previous decoder and TLS session before allocating URL parser
  buffers.
- [x] Remove heap-owned connection task parameters and release pre-reserved
  minimp3 memory after failed TLS handshakes.
- [x] Add a second host connection attempt and increase the HTTPS watchdog
  window from 2.7 to 5 seconds.
- [x] Make MP3 cleanup free both Helix and minimp3 regardless of the currently
  selected backend.
- [ ] Remove remaining temporary heap allocations from request construction
  and authentication before the TLS handshake.
- [ ] Measure whether public HTTPS playlist entries also work over plain HTTP;
  document safe replacements but never silently downgrade arbitrary URLs.
- [ ] Determine whether a custom Arduino-ESP32/ESP-IDF build with asymmetric
  8 KiB RX and 2 KiB TX mbedTLS buffers is reproducible in this repository.
- [ ] If the custom core is reproducible, test certificate-heavy HTTPS hosts,
  redirects, chunked streams, 64/128/320 kbit/s MP3, and HTTP AAC.
- [ ] Compare stopped/playing free heap and largest block against the baseline.
- [ ] Keep a conservative fallback build using the stock 16+16 KiB TLS buffers.

## Acceptance checks

1. Ten alternating station changes between HTTP AAC and at least two HTTPS MP3
   hosts without rebooting.
2. No `Decoder ... initialization failed`, `not enough memory`, watchdog leak,
   or unrecoverable host connection error.
3. Stopping playback returns decoder memory; a new diagnostic connection sees
   a largest free block of at least 50 KiB.
4. DAC fade-in/fade-out behavior remains unchanged.
5. Firmware image fits the 0x1B0000-byte application slot.

