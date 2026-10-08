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

Agents optimizing this target should start with the
[ESP32-C3 optimization reference](../../docs/ESP32C3_OPTIMIZATION_REFERENCE.md)
for CPU/memory capabilities, cycle-counter usage, measurement limits and the
ESP-IDF 6.1 speed recommendations relevant to this board.

### RAM policy for Wi-Fi and AAC

The C3 defaults and `build-production.ps1` disable `CONFIG_ESP_WIFI_IRAM_OPT`
and `CONFIG_ESP_WIFI_RX_IRAM_OPT`. The production wrapper also updates an
existing sdkconfig, since ESP-IDF defaults alone do not replace saved choices.
Frequently used Wi-Fi routines then execute from cached flash, freeing about
19 KiB of internal RAM in the measured build. This resolved an AAC-LC allocation
failure in the full radio; 48 kHz stereo playback used about 35% total CPU in
the diagnostic LAN test. It trades peak Wi-Fi throughput and some cache-miss
latency for heap space. Connection-time and worst-case interrupt-latency A/B
measurements have not been performed.

These are supported SDK placement options, not a manual relocation of every
interrupt handler. The measured ELF keeps `wDev_ProcessFiq` in IRAM and `ppTask`
in ROM; ordinary Wi-Fi receive/transmit functions move to flash. Do not infer
that every networking callback remains cache-independent. See Espressif's
[RAM guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/performance/ram-usage.html)
and [interrupt allocation guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/system/intr_alloc.html).
Use `build.ps1` with a separate sdkconfig to compare Wi-Fi IRAM settings.

Fresh builds now select compact PC19 SBR storage, scoped low-QMF workspace and
the asymmetric owner. The requested SBR owner falls from 55,128 to 32,744 bytes;
the adapter includes the PC19 side metadata. Full SBR/PS arithmetic, output
rates/channels and the existing 16 KiB decoder stack are retained. Original
uncompacted builds can fail the larger allocation and output only the AAC core.
See the [compact profile evidence](../../docs/ESP32C3_AAC_PC19_NETWORK_20261004.md)
and [current SDK qualification](../../docs/ESP32C3_IDF_UPGRADE_20261007.md).

The default system RAM profile also uses the measured smaller BOOT, audio-output
and WebSocket-status stacks (8,192 fewer requested bytes), plus 6 static Wi-Fi RX
buffers and at most 16 dynamic RX and TX buffers each. This leaves room for the
contiguous SBR allocation: enabling compact AAC alone still failed with a
26,624-byte largest free block on the physical board. The shared decoder stack
and full TLS record sizes are unchanged. The heap allocator keeps its original
IRAM placement; the separate flash-allocator experiment is not enabled here.

Compact storage does not by itself qualify every public stream. The ESP-IDF
6.1 profiling tests still record HE allocation failures over HTTPS and network
allocation failures for some public HTTP streams. Controlled local HE/HEv2
playback passes at full rate; consult the current SDK report for the separate
load, sustained-playback and quiet-production outcomes. Dynamic TLS buffers
and the RTC TCP pool remain separate experiments, not board defaults.

The optional [minimum input / TLS reservation experiment](../../docs/ESP32C3_TLS_RESERVE_20261008.md)
reclaims only idle compressed-input slots and can reserve one full-record TLS
allocation in static DRAM. Both options are off by default. A contiguous TLS
slot does not guarantee enough memory for networking or every codec; consult
the report before enabling these overlays.

The optional [IRAM placement profiles](../../docs/ESP32C3_IRAM_REDUCTION_20261001.md)
compare a 3584-byte conservative capacity saving with a 23392-byte saving using
Flash Auto Suspend on the tested XMC-D chip. These use supported SDK placement
options and retain all Flash APIs. Read the measured qualification limits before
using the profiles; they are not applied by the production build wrapper.

The [Wi-Fi buffer balance follow-up](../../docs/ESP32C3_WIFI_BUFFER_BALANCE_20261001.md)
uses that headroom to test dynamic RX/TX limits of 16, retaining static RX=6
and the unchanged native AAC decoder. The earlier six-buffer FLAC throughput
failures and all subsequent qualification results remain recorded.
That follow-up also found an `Illegal instruction` panic during OTA with the
Auto Suspend placement profile. Keep that profile disabled pending diagnosis.

### Acceptance tests

The [testing guide](../../docs/ESP32C3_TESTING.md) lists missing coverage,
executable HTTP/HTTPS, codec-switching, CPU/heap and OTA tests, plus procedures
for physical audio, interrupt timing and power-cut recovery. Test outcomes are
recorded separately as PASS, FAIL or BLOCKED. The
[audio fixture server](../../tools/audio_test_server/README.md) is shared with
ESP8266, CYD and other HTTP players; it contains no C3 control commands.

### Connections and controls

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
After a single click, the OLED second row shows `playing` or `stopped` for two
seconds to confirm the resulting playback state. A successful double click
shows `next`, and a successful long press shows `prev` for the same interval.
Holding BOOT while resetting still enters the ROM downloader.

The shared WebUI screensaver controls also apply to this OLED. When the
stopped-radio screensaver is enabled, its saved timeout switches the display
to the selected `Clock` or `Blank` mode. Clock mode uses the full 72x40 screen
and a blinking colon. Pressing BOOT wakes the station screen immediately; the
configured single/double/long gesture is then handled normally.

Software text scrolling is enabled for this board by default so every station
and track name follows the same timing and separator rules. The optional
`CONFIG_YORADIO_OLED_HW_SCROLL` experiment can be enabled in `menuconfig` for
A/B builds; eligible 10-to-15-glyph strings then use the SSD1306 scroll engine,
while longer strings continue to use software scrolling without truncation.

### Optional deep-sleep clock

Build with `-DeepSleepClock` (also supported by the root and production build
scripts) to sleep while the stopped-radio screensaver displays the clock.
It is disabled without this switch. An RTC wake stub updates the colon every
500 ms and the digits on minute changes, without booting the application.
Wi-Fi, WebUI and USB are unavailable asleep. Hold BOOT for over 500 ms to
restore the station screen, release it, then press again to play.
Short clicks between timer wakes can be missed. A synchronized clock is
required; setup/AP, playing and Blank modes stay awake.
See [build instructions, limitations and tests](../../docs/ESP32C3_DEEP_SLEEP_CLOCK.md).

### Optional external RTC crystal

Use `-Rtc32kCrystal` in the root, native or production build script to select
an external passive 32.768 kHz crystal on GPIO0 (XTAL_32K_P) and GPIO1
(XTAL_32K_N). Combine it with `-DeepSleepClock` for the sleeping clock.
The switch selects 3000 calibration cycles and separate build/firmware paths.
Without it, the scripts select the internal RC source and 1024 cycles, including
when reusing an existing sdkconfig. ESP-IDF falls back to RC if the crystal
fails to start. Builds reject encoder or LED assignments to the crystal pins.
See [wiring, commands and validation](../../docs/ESP32C3_RTC_32K_CRYSTAL.md).

### Optional rotary encoder

An EC11/KY-040 encoder can be enabled with the supplied
`sdkconfig.encoder.defaults` overlay. Its default wiring is phase A/CLK to
GPIO0, phase B/DT to GPIO1, push switch/SW to GPIO4 and common to GND. Internal
pull-ups are enabled. Rotation changes volume with Arduino-compatible
acceleration and a short push toggles Play/Pause; the acceleration value is
stored in NVS and edited by the shared WebUI.

```powershell
.\build.ps1 -BuildDirectory build-encoder -Sdkconfig sdkconfig.encoder -SdkconfigDefaults @("sdkconfig.defaults","sdkconfig.encoder.defaults")
```

The standard `sdkconfig.defaults` keeps this optional hardware disabled.
Pin assignments, direction, transitions per detent, pull-ups and the push
switch can also be changed under **yoRadio ESP32-C3 OLED** in `menuconfig`.
See the [board wiring notes](../../docs/ESP32-C3-0.42-OLED.md#optional-rotary-encoder)
before connecting a module.

## Reproducible setup and build

For a clean Windows installation, start with the
[beginner's guide](../../docs/ESP32C3_BEGINNERS_GUIDE.md), including a
[prebuilt firmware route](../../docs/ESP32C3_BEGINNERS_GUIDE.md#prebuilt-firmware-no-compilation)
that needs no compiler or ESP-IDF installation.

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
- official ESP-IDF from the series in [idf-version.txt](idf-version.txt), at
  the exact commit in [idf-revision.txt](idf-revision.txt), with pinned submodules;
- the ESP32-C3 RISC-V compiler, CMake, Ninja, esptool and IDF Python packages;
- official Espressif `esp_audio_codec` at commit
  `67b8d0e98f58c774b8652480893037273190e8dc`, including native ESP32-C3
  MP3, AAC, FLAC, Vorbis and Opus decoder libraries.

Application sources compile with `-O3`. The ESP-IDF component manager is
disabled, so builds cannot silently update dependencies.

The current SDK pin is `release/v6.1` commit
`9a97f6c54ec638111ce55cd36581b3c192f15207`, checked on 2026-10-08.
It is newer than the `v6.1` release tag. Setup keeps this checkout in
`.idf/v6.1-9a97f6c54ec6`, alongside older SDKs, and build verifies its commit.
The toolchain lives in `.idf/tools-v6.1`; setup installs the versions required
by the pinned SDK. Updating the upstream branch does not silently move this pin.

Useful commands:

```powershell
.\build.ps1 size
.\build.ps1 size-components
.\build.ps1 -IdfArguments @('-p', 'COM7', 'app-flash')
.\build.ps1 -IdfArguments @('-p', 'COM7', 'monitor')
```

### Audio task priorities

By default, audio output runs at priority **8**, decoding at **7**, and stream
input at **5**. `CONFIG_YORADIO_OUTPUT_TASK_FIRST=y` applies to both ordinary
staged PCM output and the optional direct-DMA path. The output task waits when
PCM or a free DMA block is unavailable, allowing decoding and input to proceed.
This setting changes scheduling only; codec arithmetic, buffer sizes and
timeouts are unchanged.

For a comparison build, disable `YORADIO_OUTPUT_TASK_FIRST` in `menuconfig`
(output returns to priority 6). Existing `sdkconfig` files retain an explicit
disabled value; enable the option there or use a fresh build configuration.
See the [priority measurements](../../docs/ESP32C3_OUTPUT_PRIORITY_20261006.md)
for previous results and their limitations.

### Decoder selection

The native build exposes one compile-time choice for every codec that has an
alternative implementation in this repository:

| Codec | Implementations | Default |
|---|---|---|
| MP3 | Espressif, yoRadio Helix, yoRadio minimp3 | Espressif |
| AAC | Espressif with AAC Plus (SBR/PS), yoRadio Helix AAC core | Espressif + AAC Plus |
| FLAC | optimized yoRadio FLAC, Espressif | yoRadio |

The choices are under **yoRadio ESP32-C3 OLED** in `menuconfig`, and can also
be selected with the corresponding `CONFIG_YORADIO_*_DECODER_*` symbol in an
SDK defaults file. Only the chosen backend is registered and linked. Vorbis
and Opus keep their single Espressif implementation because the repository has
no independent alternative for them. The yoRadio backends compile directly
from the shared sources through a small ESP-IDF compatibility layer; Arduino
Core is not linked. Backend alternatives are compile-time diagnostics and are
not exposed as a WebUI setting.

### AAC and current stream parameters

Fresh builds enable `CONFIG_YORADIO_AAC_DECODER_ESPRESSIF=y` and
`CONFIG_YORADIO_AAC_PLUS=y`. This reconstructs the HE-AAC high-frequency band
and HE-AAC v2 stereo; HE-AAC is not capped at its 22.05/24 kHz core rate.
The emulator tests actual 44.1/48 kHz PCM. The compact configuration described
below is enabled in new board builds; recorded network/heap limitations remain
documented in the qualification reports.

An existing `sdkconfig` keeps its saved decoder and compact-storage choices.
Use a fresh build directory/sdkconfig to pick up all new defaults. The explicit
`sdkconfig.aac-pc19.defaults` overlay also documents the complete feature chain;
defaults files do not override choices in an existing sdkconfig. To change the
decoder manually, run
`./build.ps1 menuconfig` (PowerShell: `.\build.ps1 menuconfig`), select
**yoRadio codec backends → AAC decoder → Espressif**, then enable
**yoRadio ESP32-C3 OLED → Decode full HE-AAC SBR/PS with Espressif AAC**.
Rebuild with the same build directory, SDK configuration and Deep Sleep options.
Helix remains available as a smaller core-only alternative on C3.

OLED and WebUI use the current confirmed format, including decimal kHz and
mono/stereo. PCM rate/channels are tracked separately from source metadata;
Stop and station changes clear stale parameters. OLED retains a snapshot only
until its current scrolling line finishes. WebUI updates independently of bitrate.
`GET /api/status` also exposes `sample_rate`, `channels`, `bits_per_sample`,
`pcm_sample_rate`, `pcm_channels`, `format_is_pcm` and `channels_are_core`.

The Espressif public API exposes decoded PCM. The ADTS adapter additionally reads
the audited native core's SBR/PS flags to identify `HE-AAC` and `HE-AACv2`.
The private ABI is protected by compiler layout assertions and the pinned library
SHA-256. Source channels and PCM channels stay separate: HE-AAC mono can produce
two identical PCM channels without Parametric Stereo. It is displayed as
`HE-AAC 32 kHz mono`, with `pcm_channels=2`. Base/unknown profiles still report,
for example, `AAC PCM 44.1 kHz stereo`, without inventing an AAC object type.
See the [metadata regression results](../../docs/ESP32C3_AAC_METADATA_20261004.md).
With Helix, `HE-AAC 44.1 kHz core mono` means SBR was detected but PS stereo was
not confirmed; the actual PCM may still be 22.05 kHz mono.

ADTS rate/channel/profile changes recreate the Espressif decoder at the frame
boundary. The default late-SBR controller also handles SBR/PS activation with an
unchanged ADTS configuration and retains established extensions across gaps.
The unmodified control still has the historical Stop/Play requirement described
in the [original validation report](../../docs/ESP32C3_STREAM_FORMAT_VALIDATION_20260930.md).

The board defaults and `sdkconfig.aac-pc19.defaults` profile combine the
compact SBR owner with `CONFIG_YORADIO_AAC_HIGH_HISTORY_PC19` and
`CONFIG_YORADIO_AAC_LATE_SBR`. The first keeps 19-bit QMF mantissas with 144 bytes
of extra per-decoder metadata. The second repairs late activation and retains
SBR/PS through frames without extensions, preserving the AAC transform history.
Both options work in the network firmware; QEMU test options remain separate.
The shared implementation passed synthetic/recorded PCM tests within 3 LSB.
Keep the existing 16 KiB decoder stack and the pinned AAC archive. To build an
uncompacted reference, apply `sdkconfig.aac-native.defaults` after the board
defaults in a separate fresh configuration. It keeps AAC Plus enabled.
Before deployment, `tools/codec_benchmark/verify_aac_network_build.py` checks
the actual linked calls, type sizes, image/ELF match and absence of QEMU hooks.

Both native ESP-IDF profiles default to Espressif MP3. With the deterministic
320 kbit/s fixture, the 160 MHz C3 measured 27.9% decoder time for Espressif
(3.57x real-time headroom) and 30.2% for Helix, while scalar minimp3 required
407.9% of the available real-time CPU budget and starved the audio, BOOT-button
and WebSocket tasks.

### Network stream transports

The native player accepts continuous HTTP and HTTPS radio streams containing
MP3, AAC/AAC+, FLAC, Ogg Vorbis or Ogg Opus. HTTPS uses ESP-IDF's TLS 1.2
client, validates the server hostname and certificate against the full
Espressif root-CA bundle, supports standard and custom TLS ports, and follows
up to five HTTP redirects. TLS record buffers are allocated dynamically so a
second protected station can be opened after the PDM DMA and decoder have
already consumed RAM.

An invalid, expired or privately signed certificate is rejected. TLS 1.3-only
servers, HLS/DASH manifests (`.m3u8`/`.mpd`), RTSP, RTMP, MMS and WebSocket
audio are not stream transports in this target. Playlist entries must resolve
to the continuous encoded audio response itself; HTTPS does not by itself turn
an HLS manifest into a supported stream.

## Storage compatibility

The native 4 MiB partition table keeps dual OTA while reserving 256 KiB for
SPIFFS:

- NVS at `0x9000`;
- 1856 KiB OTA application slots at `0x10000` and `0x1e0000`;
- SPIFFS at `0x3b0000`, size 256 KiB;
- coredump partition at `0x3f0000`.

Changing from the former 128 KiB layout moves SPIFFS from `0x3d0000` to
`0x3b0000`. Back up `/data/wifi.csv` and `/data/playlist.csv` before the first
serial reflash, then write the new partition table and SPIFFS image together;
flashing the application alone cannot migrate the existing filesystem.

Use WebUI OTA for later application updates. For USB recovery after OTA,
follow [P6 in the beginner's guide](../../docs/ESP32C3_BEGINNERS_GUIDE.md#p6-update-an-existing-native-radio-preserve-settings-and-webui),
which also resets the boot selector: `app-flash` alone may leave the previous
`app1` selected. Use `spiffs-flash` only to explicitly replace the filesystem.

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
request such as `/style.css` reads `/www/style.css.gz` and returns compressed
bytes with `Content-Encoding: gzip`; decompression is performed by the browser.
The shared `script.js.gz` is embedded in the C3 application and takes precedence
over its SPIFFS copy, so application OTA also installs its compatible JavaScript.
The form, styles and remaining assets stay shared with Arduino/CYD and ESP8266.
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
- `POST /api/native/stop`;
- `GET /api/native/ota`: running version, ELF hash, slot and maximum image size;
- `POST /update`: the original Arduino multipart contract, `updatetarget=fw`
  or `firmware`, followed by one file named `update`; success is plain `OK`.

Codec selection may be `auto`, `mp3`, `aac`, `flac`, `ogg`, `vorbis` or
`opus`. These endpoints and the shared WebSocket protocol are served by the
same native ESP-IDF HTTP server.

### Application OTA

Use the shared **Update** page at `/update.html` with this target's `app.bin`.
The emergency form at `/emergency` uses the same upload endpoint. A first USB
application update is required for older native images without this handler.
See [browser and command-line steps](../../docs/ESP32C3_BEGINNERS_GUIDE.md#webui-ota-no-tools-required).

The receiver keeps a bounded workspace (512-byte multipart buffer, 4 KiB flash
buffer and 1 KiB receive buffer) and writes only the inactive 1,900,544-byte app
slot. It checks chip ID and project name before erasing, rejects oversized,
duplicate or incomplete uploads, verifies the image with ESP-IDF, checks its
exact on-flash length, and selects the new slot only after successful completion.
Failures abort the OTA handle. Receive deadlines are 10 seconds without data
and 180 seconds overall. NVS, SPIFFS and the running app are not written.

Playback stops without changing saved Smart Start or station settings. The
Update page refreshes the idle timer while awake; the upload holds a deep-sleep
activity lease through validation and restart. Wake a sleeping radio with BOOT.
Raw SPIFFS OTA is unavailable; use Board's file importer. The existing bootloader
and partition layout stay unchanged. Automatic first-boot rollback/self-test is
not enabled; a bootable but malfunctioning application may need USB recovery.
