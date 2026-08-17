# Minimal ESP-IDF firmware for ESP32-2432S028 CYD2USB

This profile builds yoRadio with the current stable ESP-IDF 6.0.2 for the
dual-USB CYD board: original dual-core ESP32, ST7789 display, XPT2046 touch and
internal DAC or PDM output on GPIO26. Arduino is retained as an ESP-IDF
component while CMake compiles only the yoRadio modules and libraries required
by this board.

The profile keeps Wi-Fi station/AP fallback, HTTP/HTTPS streams, TLS, SPIFFS,
WebUI, OTA web updates, ST7789, touch, MP3/AAC/FLAC and DAC/PDM output. It
excludes MQTT, IRremote, VS1053, alternate displays, Nextion, GT911, Bluetooth/BLE,
Ethernet, PPP, IPv6, Zigbee, Matter, RainMaker, Insights and Arduino OTA.

ESP-IDF 6 removed the legacy built-in-DAC I2S driver. The default `continuous`
backend therefore writes DAC audio through the supported `dac_continuous` API.
It keeps a dedicated 8-bit PCM queue and a continuously supplied DMA ring.
Brief decoder/network gaps are filled with the `0x80` midpoint, so the
converter never holds an arbitrary last sample and resumes with a DC step.

For comparison and fallback, the profile also has a `legacy` backend. Setup
pins the official ESP-IDF v5.5.4 tree and CMake compiles its original
`components/driver/deprecated/i2s_legacy.c` inside the IDF 6 application. A
small DAC-only compatibility wrapper supplies renamed SDK definitions; RX/ADC
and external digital I2S are deliberately unsupported by this backend.

The third `pdm` backend uses the ESP-IDF 6 `i2s_pdm` API and the ESP32 hardware
PCM-to-PDM converter. Its one-bit stream is routed to GPIO26, with mono mixing,
DMA buffering and bias ramps already handled by YoRadio's PDM output path.

### Confirmed PDM clock fix

ESP-IDF 6.0.2 calculates the PCM-to-PDM bit clock after reducing the `fp/fs`
ratio to an integer. With Espressif's fixed-carrier DAC profile this changes
the requested 6.144 MHz carrier to 5.6448 MHz for a 44.1 kHz stream, while a
48 kHz stream still receives 6.144 MHz. On this board the mismatch produced
clearly audible extra noise on stereo 44.1 kHz stations (for example,
Sputnik), although stereo 48 kHz stations such as Vesti FM remained clean.

The PDM build replaces only that calculation in a build-local copy of
`i2s_pdm.c`: multiplication is performed in 64 bits before division by `fs`.
It keeps the carrier at 6.144 MHz for both 44.1 and 48 kHz while retaining the
sample-rate-dependent `fp/fs` converter settings. Listening tests confirmed
that this fix eliminated the extra station-dependent PDM noise. The pinned
ESP-IDF checkout is not modified, and CMake deliberately stops with an error
if a future SDK changes the original expression and the workaround needs to
be reviewed.

## Reproducible setup

Run from this directory:

```powershell
.\setup.ps1
```

The script downloads everything into the repository-local, ignored `.idf`
directory and does not require an existing Python or ESP-IDF installation:

- official portable CPython 3.12.10, verified by SHA-256;
- official ESP-IDF v6.0.2 and its pinned submodules;
- official ESP-IDF v5.5.4 source for the optional legacy DAC backend;
- official Arduino-ESP32 4.0.0-alpha1, the first release line supporting IDF 6;
- Adafruit BusIO 1.17.4;
- Adafruit GFX 1.12.6;
- Adafruit ST7735/ST7789 1.11.0;
- XPT2046 Touchscreen v1.4;
- the ESP32 Xtensa compiler, CMake, Ninja, esptool and IDF Python packages.

Existing checkouts must match their exact pinned tags. Re-running setup is
safe and only validates/reuses installed dependencies. Use
`.\setup.ps1 -SkipToolchain` to validate source dependencies without invoking
the ESP-IDF tool installer.

## Build

```powershell
.\build.ps1
.\build.ps1 size
.\build.ps1 size-components

# Build and inspect the optional ESP-IDF 5.5.4 legacy I2S/DAC backend.
.\build.ps1 -BuildDirectory build-legacy -AudioBackend legacy
.\build.ps1 size -BuildDirectory build-legacy -AudioBackend legacy

# Build the hardware I2S PDM/sigma-delta output on GPIO26.
.\build.ps1 -BuildDirectory build-pdm -AudioBackend pdm
.\build.ps1 size -BuildDirectory build-pdm -AudioBackend pdm
```

`build.ps1` calls setup automatically when a required dependency is missing.
Generated images are stored in `build/`; `build/flasher_args.json` is the
authority for offsets. The tested application image occupies about 1.12 MiB
of each 1.69 MiB OTA slot. `continuous` remains the default; the serial boot
log identifies the backend compiled into the image. The former `-DacBackend`
parameter remains an alias for `-AudioBackend`.

## Flash without erasing settings

The partition layout matches the CYD2USB profile: NVS at `0x9000`, OTA apps at
`0x10000` and `0x1c0000`, and SPIFFS at `0x370000`. A routine app update must
write only `build/yoradio_cyd2usb_minimal.bin` at `0x10000`. Do not write
`build/spiffs.bin` unless replacing the WebUI and saved Wi-Fi/playlist data is
explicitly intended.

The first test was performed on COM8 at 460800 baud. Esptool verified the
written image hash, and serial monitoring confirmed stable AP-mode operation
without reset loops, watchdog warnings or DAC driver errors.

## Current limitation

Arduino-ESP32 4.0.0-alpha1 conditionally removes its complete TLS client when
all PSK modes are disabled, even for certificate and insecure clients. The
minimal configuration therefore enables the smallest PSK exchange mode to
retain HTTPS radio support. This can be removed after the upstream Arduino
IDF-6 component no longer has that compile-time dependency.
