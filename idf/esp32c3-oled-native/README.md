# Native ESP-IDF firmware for ESP32-C3 0.42-inch OLED

This is a separate Arduino-free firmware target for the compact ESP32-C3
SuperMini OLED / 01Space-style board. It uses ESP-IDF APIs directly and does
not include Arduino Core, Arduino libraries, Adafruit GFX, or the Arduino
yoRadio runtime.

A separate target directory is intentional. The CYD and C3 boards have
different CPU topology, display buses, controls, audio hardware and partition
layouts. Keeping independent `sdkconfig`, board code and images avoids making
the proven `esp32-cyd2usb-native` build depend on C3 conditionals. The native
network, WebUI and audio pipeline sources were carried over from that target.

## Hardware profile

- ESP32-C3, one RISC-V core at 160 MHz, 4 MiB flash;
- native USB Serial/JTAG console;
- SSD1306 72x40 OLED at I2C address `0x3c`, SDA GPIO5, SCL GPIO6;
- hardware two-line PCM-to-PDM stereo: left GPIO10, right GPIO3;
- active-low audio-level LED on GPIO8;
- active-low BOOT/radio button on GPIO9.

PDM hardware stays at 48 kHz with a 6.144 MHz carrier. Lower-rate decoded PCM
is linearly resampled with a shared exact phase and independent left/right
samples. The channels are never folded to mono. Use the two identical passive
filters and amplifier connection documented in
[`docs/ESP32-C3-0.42-OLED.md`](../../docs/ESP32-C3-0.42-OLED.md). Never connect
a speaker or headphones directly to either GPIO.

The OLED uses the controller-specific 28-column RAM offset and a reduced
default brightness. It displays the station, current song and IP address. The
shared WebUI `brightness` slider maps its 0..100 value to SSD1306 hardware
contrast and stores the selection in NVS. The GPIO8 PWM LED follows the
stronger channel peak and is configurable or removable under
`menuconfig -> yoRadio audio level LED`. One BOOT click pauses or resumes, two
clicks select the next station, and a hold selects the previous station.
Holding BOOT while resetting still enters the ROM downloader.

Software text scrolling is enabled for this board by default so every station
and track name follows the same timing and separator rules. The optional
`CONFIG_YORADIO_OLED_HW_SCROLL` experiment can be enabled in `menuconfig` for
A/B builds; eligible 10-to-15-glyph strings then use the SSD1306 scroll engine,
while longer strings continue to use software scrolling without truncation.

## Reproducible setup and build

This is the repository's default firmware target. From the repository root,
run:

```powershell
.\setup.ps1
.\build.ps1
```

The same scripts can be run directly from this directory:

```powershell
.\setup.ps1
.\build.ps1
```

`build.ps1` automatically invokes setup when dependencies are missing. Setup
downloads into the repository-local ignored `.idf` directory:

- portable CPython 3.12.10, verified by SHA-256;
- official ESP-IDF v6.0.2 and its pinned submodules;
- the ESP32-C3 RISC-V compiler, CMake, Ninja, esptool and IDF Python packages;
- official Espressif `esp_audio_codec` at commit
  `67b8d0e98f58c774b8652480893037273190e8dc`, including native ESP32-C3
  MP3, AAC, FLAC, Vorbis and Opus decoder libraries.

Application sources compile with `-O3`. The ESP-IDF component manager is
disabled, so builds cannot silently update dependencies.

Useful commands:

```powershell
.\build.ps1 size
.\build.ps1 size-components
.\build.ps1 -IdfArguments @('-p', 'COM7', 'app-flash')
.\build.ps1 -IdfArguments @('-p', 'COM7', 'monitor')
```

### Decoder selection

The native build exposes one compile-time choice for every codec that has an
alternative implementation in this repository:

| Codec | Implementations | Default |
|---|---|---|
| MP3 | Espressif, yoRadio Helix, yoRadio minimp3 | minimp3 |
| AAC | Espressif, yoRadio Helix AAC-LC | Espressif |
| FLAC | optimized yoRadio FLAC, Espressif | yoRadio |

The choices are under **yoRadio ESP32-C3 OLED** in `menuconfig`, and can also
be selected with the corresponding `CONFIG_YORADIO_*_DECODER_*` symbol in an
SDK defaults file. Only the chosen backend is registered and linked. Vorbis
and Opus keep their single Espressif implementation because the repository has
no independent alternative for them. The yoRadio backends compile directly
from the shared sources through a small ESP-IDF compatibility layer; Arduino
Core is not linked.

## Storage compatibility

The partition table matches Arduino-ESP32's 4 MiB `min_spiffs` layout:

- NVS at `0x9000`;
- OTA application slots at `0x10000` and `0x1f0000`;
- SPIFFS at `0x3d0000`, size 128 KiB;
- coredump partition at `0x3f0000`.

Flashing only `app-flash` preserves Wi-Fi settings, playlists and WebUI. Use
`spiffs-flash` only when the filesystem should be replaced explicitly.

Wi-Fi client credentials are read from `/data/wifi.csv` in the existing
tab-separated yoRadio format. If the file is absent or the connection fails,
the firmware starts an open `yoRadio-XXXXXX` access point on channel 1.

## Native HTTP server and WebUI

The firmware uses ESP-IDF's standard `esp_http_server` for the complete web
stack. It serves the shared yoRadio WebUI and gzip assets from SPIFFS, handles
multipart Wi-Fi and playlist uploads, exposes the native REST API, and runs
the built-in ESP-IDF WebSocket endpoint at `/ws`. No Arduino networking layer,
AsyncWebServer, AsyncTCP, or third-party WebSocket library is linked.

All static WebUI resources under `/www` are stored only as `.gz` files. A
request such as `/script.js` reads `/www/script.js.gz` and returns the compressed
bytes with `Content-Encoding: gzip`; decompression is performed by the browser.
Uncompressed WebUI uploads are rejected so they cannot shadow a compressed
asset. Mutable `/data/wifi.csv` and `/data/playlist.csv` remain plain text.

The repository playlist is included in the SPIFFS image as
`/data/playlist.csv`. The WebSocket compatibility adapter supports playback,
stop/toggle, previous/next station, volume and balance commands used by the
shared WebUI. It also publishes the current station, decoder state, RSSI and
free heap periodically. Equalizer controls remain disabled for this board.

In access-point mode, open `http://192.168.4.1/`. Saving Wi-Fi credentials in
the shared UI writes `/data/wifi.csv` and restarts the board. SSIDs and
passwords are stored exactly as entered; names beginning or ending with spaces
are therefore preserved rather than silently changed.

### Native REST API

The native service exposes:

- `GET /api/native/status`;
- `POST /api/native/reconnect`;
- `POST /api/native/play?codec=auto`, with a stream URL in the request body;
- `POST /api/native/stop`.

Codec selection may be `auto`, `mp3`, `aac`, `flac`, `ogg`, `vorbis` or
`opus`. These endpoints and the shared WebSocket protocol are served by the
same native ESP-IDF HTTP server.
