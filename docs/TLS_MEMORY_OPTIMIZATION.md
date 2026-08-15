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
- [x] Remove remaining temporary heap allocations from request construction
  and authentication before the TLS handshake.
- [ ] Measure whether public HTTPS playlist entries also work over plain HTTP;
  document safe replacements but never silently downgrade arbitrary URLs.
- [x] Produce a reproducible custom Arduino-ESP32/ESP-IDF library build with
  asymmetric TLS buffers: 16 KiB RX and 4 KiB TX. RX stays at the protocol-safe
  maximum because arbitrary radio servers may send full-size records.
- [x] Evaluate Espressif's dynamic TX/RX buffer mode and freeing TLS config data
  after the handshake. Prefer releasing an idle TX allocation over aliasing RX
  and TX memory; mbedTLS needs both directions concurrently during handshake.
  ESP-IDF 5.5.4 used by Arduino-ESP32 3.3.8 does not expose the old dynamic
  buffer Kconfig options, so this build uses the supported asymmetric lengths.
- [ ] If the custom core is reproducible, test certificate-heavy HTTPS hosts,
  redirects, chunked streams, 64/128/320 kbit/s MP3, and HTTP AAC.
- [x] Compare stopped/playing free heap and largest block against the baseline.
- [x] Keep a conservative fallback build using the stock 16+16 KiB TLS buffers.
  The custom SDK is opt-in through `-Esp32Sdk`; the Boards Manager installation
  and the normal build directory remain unchanged.

## 16 KiB RX / 4 KiB TX result (2026-08-15)

The DAC firmware was built with Arduino-ESP32 3.3.8 and the custom SDK, flashed
to COM8 without writing NVS or SPIFFS, hash-verified by esptool, and hard-reset.
`build.options.json` records the custom SDK path and the copied build
`sdkconfig` contains all three asymmetric-buffer settings.

Measurements below include the same active Telnet diagnostics as the baseline.
Ranges cover repeated visits during ten alternating station changes.

| State | Baseline free / largest | 16K RX + 4K TX free / largest | Change |
|---|---:|---:|---:|
| HTTPS MP3 64 kbit/s, station 574 | 6,576 / 2,932 | 19,484-19,520 / 12,276-14,324 | +12.9 KiB free |
| HTTPS MP3 320 kbit/s, station 591 | 7,888 / 1,588 | 20,712-27,632 / 13,812-15,348 | +12.5 KiB or more free |
| HTTP AAC 320 kbit/s, station 117 | 48,192 / 38,900 | 47,980-49,700 / 36,852 | approximately unchanged |
| Stopped after test | 74,980 / 40,948 | 76,148-76,152 / 55,284 | largest block +14.0 KiB |

All ten changes established their connection, initialized the expected decoder,
and reached `stream ready`. No decoder allocation failure, `not enough memory`,
watchdog leak, or unrecoverable host error was observed. The application image
is 1,587,520 bytes, below the 1,769,472-byte OTA slot.

## Rebuilding the custom SDK

The verified inputs were ESP32 Arduino Lib Builder `14a0af9`, Arduino-ESP32
3.3.8 (`b4f85baa`), and ESP-IDF 5.5.4 (`73550728`). Copy
`tools/tls-mbedtls-16k-rx-4k-tx.defconfig` to the builder as
`configs/defconfig.tls_16k_4k`, then build the ESP32 libraries:

```sh
./build.sh -s -t esp32 -b idf-libs qio 80m tls_16k_4k
```

Create an isolated SDK by overlaying only the configuration-dependent TLS
libraries on the stock 3.3.8 SDK:

```powershell
.\tools\New-TlsOptimizedEsp32Sdk.ps1 `
  -BuilderRoot <esp32-arduino-lib-builder> `
  -SourceSdk <Arduino15\packages\esp32\tools\esp32-libs\3.3.8> `
  -Destination .\.build\tls-16k-rx-4k-tx-sdk
```

Build and flash it without replacing the installed Arduino core or SPIFFS:

```powershell
.\.agents\skills\flash-reset-esp32\scripts\flash_yoradio.ps1 `
  -Port COM8 -AudioOutput DAC `
  -Esp32Sdk .\.build\tls-16k-rx-4k-tx-sdk
```

## Acceptance checks

1. Ten alternating station changes between HTTP AAC and at least two HTTPS MP3
   hosts without rebooting.
2. No `Decoder ... initialization failed`, `not enough memory`, watchdog leak,
   or unrecoverable host connection error.
3. Stopping playback returns decoder memory; a new diagnostic connection sees
   a largest free block of at least 50 KiB.
4. DAC fade-in/fade-out behavior remains unchanged.
5. Firmware image fits the 0x1B0000-byte application slot.
