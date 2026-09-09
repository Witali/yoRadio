# yoRadio ESP8266 native

## Volume control

The player slider and WebSocket `volume=N` use **0..100 inclusive** (step 1).
`volp`, `volm` and encoder steps use percentage points; the configured step
remains 1..10 (default 2). Zero is mute; 100 is the former full-scale 254.
The initial/default volume 160 is displayed as 63. Percent refers to the
linear gain control, not a calibrated acoustic loudness percentage.

PCM gain and the version-1 NVS blob retain 0..254 units. Existing settings
are not rewritten during boot, and all 101 new values round-trip exactly.
There are no new audio buffers, tasks or per-sample conversions.

Deploy the updated shared `yoRadio/data/www/script.js.gz` **before** the new
app (or update both together). The new script works with old firmware too;
it opts into percent only when `volumeMax=100` is advertised. An old script
with a new app can send legacy 0..254 commands, which the new API clamps to
100; do not operate that mismatched combination. Reload all open WebUI tabs.
For application-only OTA, the old SPIFFS asset does not update automatically.
The compressed built-in player/settings bundles include the capability too.

Other chips and Arduino WebRadio are unchanged. KaRadio ESP8266 reuses this
controller/WebUI and inherits the scale when rebuilt (not separately tested).
See the
[synchronization plan](../../docs/VOLUME_0_100_SYNC_PLAN.md).

This target uses the official Espressif `ESP8266_RTOS_SDK v3.4` and follows
the ESP-IDF-style component/CMake layout. It is deliberately HTTP-only. The
normal profile uses the yoRadio Helix MP3 and AAC decoders; an experimental
ESP8266Audio `libmad-8266` MP3 backend can be selected at compile time with
`CONFIG_YORADIO_MP3_DECODER_LIBMAD` while AAC remains on Helix.

AAC-LC defaults to 512-frame PCM callbacks: 1024 bytes of mono PCM instead
of a 4096-byte stereo frame. Set `YORADIO_ESP8266_AAC_BLOCK_OUTPUT=OFF` for
the retained full-frame A/B path. `YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES`
accepts 32/64/128/256/512; the physical PDM32 test selected 512 for continuity.
See [AAC memory and timing results](../../docs/ESP8266_AAC_PCM_BLOCKS.md).

The default profile targets a 4 MiB ESP-12E/NodeMCU/Wemos-class module at
160 MHz and uses the external flash in QIO mode at 40 MHz. The bootloader is
initially written in DIO as required by ESP8266 RTOS SDK, then enables Quad I/O
during startup. Use DIO for modules whose flash chip does not support QIO.
The optional `sdkconfig.qio80.defaults` profile selects QIO at 80 MHz for
modules with a suitably rated flash chip. Use it instead of
`sdkconfig.defaults`; it is kept separate from the default profile because
signal integrity still depends on the particular module PCB.
For a reproducible Wemos QIO80 libmad experiment, use
`sdkconfig.libmad-qio80.defaults`. The ordinary defaults continue to select
`CONFIG_YORADIO_MP3_DECODER_HELIX`.
The `sdkconfig.helix-sso-qio80.defaults` profile keeps Helix but enables its
experimental reduced-precision 32-bit polyphase synthesis. It allocates no
additional decoder buffers and is intended for PCM-quality and physical speed
comparison before the optimization is considered for production.
The `sdkconfig.helix-sso-qio80-pdm8.defaults` profile retains the legacy
8-bit SPI-PDM selection for comparative tests. The default backend is now
continuous I2S/SLC DMA on GPIO3 with a nominal 1.536-MHz carrier; legacy HSPI
output remains selectable with `CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM`.
The matching `sdkconfig.audio-profile-qio80-pdm8.defaults` profile also
enables FreeRTOS runtime counters. Build it with
`YORADIO_ESP8266_AUDIO_PROFILE` and
`YORADIO_ESP8266_HELIX_STAGE_PROFILE` to measure network, frame scan,
decoder internals, normalization, PDM conversion, SPI wait, CPU idle, and heap
on a physical board.
The matching `sdkconfig.aac-sso-qio80.defaults` profile keeps exact MP3 and
enables the experimental three-partial-product AAC fixed-point path for
isolated PCM, disassembly, and physical timing comparison.
The `sdkconfig.libmad-mp3-only-qio80.defaults` experiment also disables AAC;
this reduces stereo PCM storage from 4096 to 2304 bytes and the fixed IRAM word
arena from 16 KiB to 12 KiB. The arena stores the 4236-byte `mad_synth`, the
4608-byte Layer III spectral workspace, and the 2304-byte reorder workspace.
The Xtensa build uses 11152 bytes of that arena and reduces `mad_frame` in
8-bit DRAM from 20784 to 13880 bytes. It is not a full-feature replacement
profile.
Audio defaults to mono I2S-PDM on fixed DATA GPIO3/RX. Two explicitly owned
SLC-DMA buffers clock one 32-bit word per 48-kHz PCM sample. Production
computes 32 genuine delta-sigma decisions per sample, giving a nominal
1.536-MHz carrier. The ESP8266 integer divider produces 1.538461 MHz (+0.16%).

## Canonical production configuration

For an error-log-only production build on Windows, with all tone, decoder,
memory and WebUI profiling modes disabled, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools/esp8266_audio_profile/build_i2s_pdm_production.ps1
```

This uses a separate build directory, validates I2S PDM32/mono/Helix/QIO40
selections, and saves the app, configuration and manifest under
`firmware/development/esp8266-i2s-pdm-production/`. It does not flash.
DATA is GPIO3/RX (not the temporary SPI debug output GPIO13/D7); do not send
UART application commands while I2S owns RX.

Optional HTTP/audio arbitration: `-WebAudioPause short` prioritizes the HTTP
task without releasing the decoder; `-WebAudioPause long` cooperatively
releases the decoder/stream during static-page loading and reconnects after
the last request. Default: `off`. This is a build-time policy, independent of
debug logging; see [pause modes and limitations](../../docs/ESP8266_WEB_AUDIO_PAUSE.md).

Experimental low-level RC-PDM feedback, interpolation and dither are documented
in [RC-PDM Feedback](../../docs/ESP8266_RCPDM_FEEDBACK.md). This is opt-in via
`CONFIG_YORADIO_RCPDM_FEEDBACK`; the production PDM32 default is unchanged.

The audio producer converts PCM directly into a reserved, producer-owned
DMA span; EOF may take a committed prefix only after all producer loans are
released. The two 512-word-capacity buffers remain; playing underruns retry
with 64 neutral words and stop uses 512. See [DMA recovery](../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).
Balance is ignored for mono PCM,
including restored settings and runtime updates; volume/normalization still
apply. See [PCM32, direct DMA and physical trace](../../docs/ESP8266_PCM32_DIRECT_DMA.md).

An independent experimental **I2S RCPDM** output is available with
`sdkconfig.i2s-rcpdm.defaults` / `CONFIG_YORADIO_AUDIO_OUTPUT_I2S_RCPDM`.
It predicts an RC filter with alpha=1/16 and emits exactly 32 bits per 48-kHz
output PCM sample through the existing GPIO3 DMA backend. It does not replace
the default delta-sigma I2S PDM. See [RCPDM configuration and filter](../../docs/ESP8266_I2S_RCPDM.md).
For the algorithms, Simple variants, output bitrates, quality trade-offs and
measured CPU cost, see the [RC-PDM versus PDM overview](../../docs/RC_PDM_OVERVIEW.md).

The tracked `sdkconfig.defaults` is the authoritative default for this board.
It explicitly selects QIO 40 MHz flash, a 160 MHz CPU, Helix MP3 SSO, Helix
AAC, mono decoded PCM, I2S-PDM on GPIO3, genuine PDM32 at nominal 1.536 MHz, and the static
2 x 512-word SLC-DMA ping-pong buffers. The 3072-byte main task also owns the button and
encoder gesture state machine, awakened directly by their ISRs, so there is no
separate input-task stack. The HTTP/WebSocket task uses 5120 bytes. libmad,
AAC SSO, legacy SPI-PDM, standard I2S PCM,
and PDM128 are explicitly disabled. This explicit selection prevents a stale
experimental choice from being inherited by a fresh build.

The compressed decoder input now defaults to 4096 bytes
(`CONFIG_YORADIO_STREAM_INPUT_BYTES`). Startup tries to fill the whole buffer
for up to 1000 ms (`CONFIG_YORADIO_STREAM_PREFILL_MS`); playback refills from
nonblocking TCP before each compressed frame. No second FIFO or task is added.
This frees 2048 DRAM bytes compared with the previous 6144-byte default.
See [prefill behavior, RAM budget and test limits](../../docs/ESP8266_INPUT_PREFILL_2026-09-09.md).
Larger values remain build-time options and need hardware stress testing.

Configure every ordinary or diagnostic build with the tracked defaults path,
for example:

```sh
cmake -S esp8266/rtos-sdk-native -B .build/esp8266-production \
  -G Ninja \
  -DSDKCONFIG_DEFAULTS="$PWD/esp8266/rtos-sdk-native/sdkconfig.defaults"
ninja -C .build/esp8266-production
```

The project forces the generated `sdkconfig` into that build directory. An
ignored `esp8266/rtos-sdk-native/sdkconfig` left by an experiment is therefore
never an input to a new build and cannot replace Helix with libmad. Explicit
`-DSDKCONFIG=...` is still supported for controlled experiments.

Use a fresh build directory when changing profiles. A diagnostic audio trace
may add `-DYORADIO_ESP8266_AUDIO_TRACE=ON`, but must keep the same
`SDKCONFIG_DEFAULTS`; that option only adds bounded logging and must not change
the codec, flash, clock, or output selections. See
[`docs/ESP8266_AUDIO_PATH.md`](../../docs/ESP8266_AUDIO_PATH.md) for the traced
signal path and physical verification.

A genuine PDM128 mode at nominally 6.144 MHz
is compile-time selectable but remains experimental because it cannot run in
realtime on the physical Wemos D1 mini. The NoDAC path keeps I2S clocks internal:
it routes only DATA GPIO3 to the audio filter, not BCLK GPIO15 or WS GPIO2.
The GPIO2 audio-level LED is available with NoDAC I2S and SPI-PDM; standard
external-DAC I2S still owns GPIO2 as WS and disables the LED. Connect GPIO3 through the
documented low-pass/AC-coupling chain and then to a high-impedance amplifier
input. The default now selects build-time `CONFIG_YORADIO_AUDIO_MONO`:
compatible Helix MP3 M/S frames skip the side channel and use one
IMDCT/synthesis. Select `CONFIG_YORADIO_AUDIO_STEREO` or the complete
`sdkconfig.stereo.defaults` profile to retain stereo decoding and independent
L/R balance. The one-pin PDM backend itself remains mono in either case.
See [mono/stereo behavior and tests](../../docs/ESP8266_MP3_MONO.md).
The ESP-12F/Wemos GPIO2 LED follows the post-volume mono PCM peak, with fast
attack and slow release; stopped audio is dark. `CONFIG_YORADIO_STATUS_LED`
enables it by default; set `n` (or build with `-NoAudioLevelLed`) to compile
out its state and peak processing. `CONFIG_YORADIO_STATUS_LED_UPDATE_HZ=10`
updates every 100 ms; select `20` for 50 ms. Every fourth frame in a bounded
snapshot is measured inside the gain loop. Hardware sigma-delta supplies pulses,
without software PWM interrupts. See [LED details and tests](../../docs/ESP8266_AUDIO_LEVEL_LED.md).
The PDM profile uses a small local output-only backend instead of the RTOS SDK
I2S driver. Peripheral/companion-link setup follows ESP8266Audio's Arduino
backend, but output descriptors now terminate rather than forming an unguarded
ring. The producer owns one buffer until all 512 words are ready; EOF submits
the next complete buffer and wakes the producer. I2S/FIFO are not reset between
blocks. On underrun, only the completed DMA buffer is replaced by audio zero
(`0xAAAAAAAA`, alternating 1/0), never a partial producer block or stale audio.
Both 2048-byte buffers and descriptors remain static. Initialization waits
for the first EOF and fails explicitly if DMA does not start. See
[DMA ownership fix and physical tests](../../docs/ESP8266_I2S_DMA_OWNERSHIP.md).
The board default profile uses QIO at 40 MHz. A physical Wemos D1 mini with
verified bootloader, partition table, and application bytes intermittently
stopped immediately after the ROM loader at QIO80; the same code boots and
serves the WebUI at QIO40. The named `qio80` profiles remain available for
explicit experiments on modules whose flash and PCB are stable at 80 MHz.
ESP8266 RTOS SDK intentionally
stores DIO in the boot image header so the ROM can load it on every supported
flash chip; `CONFIG_SPI_FLASH_MODE=0x0` makes early SDK initialization enable
QIO before the application executes. Do not override the boot header to QIO.
The same default profile selects the measured faster 32-bit Helix MP3 SSO
synthesis path and the genuine PDM32 x1 I2S backend.

The production codec layout reserves one physically verified contiguous
16384-byte IRAM arena. Helix MP3 splits IMDCT output by channel: one channel
fits the arena and the remaining word workspaces use DRAM. On the physical
board the previous stereo MP3 workspace reported 11472 bytes DRAM and 16384
bytes IRAM. Helix now emits 32 frames per synchronous callback, requiring
only 64 bytes of mono PCM (128 stereo), instead of a 576-frame granule.
The current mono/shared-reorder workspace measures 8440 bytes DRAM and
16384 bytes IRAM. Fallback transform storage and the IRAM reservation remain
unchanged; AAC and libmad keep their own existing PCM layouts.
Helix now also reuses the idle IMDCT output for short-block reorder scratch,
removing another 792-byte DRAM allocation. The CMake option
`YORADIO_ESP8266_MP3_SHARED_REORDER` defaults to `ON`; `OFF` restores separate
storage for A/B measurement. See [lifetime contract and tests](../../docs/ESP8266_MP3_REORDER_REUSE.md).
Larger single or secondary IRAM allocations are not a default: the SDK heap
regions rejected them even when the ELF map showed enough aggregate bytes.

GPIO3 is also UART0 RX. The application intentionally never reads UART input
and routes the pin to I2S while running; UART0 TX logging on GPIO1 remains
available. The onboard 470-ohm series resistor limits contention with CH340
TXD; do not send UART data from the host while audio is playing.

Legacy mono HSPI-PDM on GPIO13/D7 can be selected with
`CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM`; GPIO14/D5 is then an unused SPI clock.
Standard stereo PCM for an external I2S DAC remains available through
`CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PCM` and uses DATA GPIO3, BCLK GPIO15 and
LRCLK GPIO2. The optional SSD1306 bus is SDA GPIO4/SCL GPIO5.

ESP8266 RTOS SDK enforces 2440 bytes as the minimum TCP send buffer, so the
canonical profile keeps both send buffer and receive window at 2440 bytes for
high-bitrate radio. RAM is bounded in the WebUI itself: static responses use one
512-byte scratch buffer, the persistent status buffer is 1088 bytes, and
volatile RSSI/buffer telemetry is sampled every two
seconds instead of enqueueing a full status frame on every fluctuation.

The network layout intentionally matches the ESP32-C3 OLED native target:
WebUI HTTP resources use the standard port 80 and the persistent WebSocket is
the `/ws` route on that same server and port. Static gzip responses close their
short-lived sockets after transfer; there is no second WebUI or WebSocket port.

The HTTP/WebSocket task currently requires a **4096-byte stack**. The older
status formatter overflowed that size because it held multiple escaped copies
of station and ICY strings. The bounded direct JSON writer removed those
temporaries; a physical Wemos D1 mini then completed the full WebSocket status
exchange and playlist-backed WebUI requests with 4096 bytes. Do not reduce it
further without a new on-device high-water and full Web API test.

The project is under active implementation; use the repository setup/build
scripts once they are added rather than invoking a globally installed SDK.

## Experimental Ogg Opus

`CONFIG_YORADIO_OGG_OPUS` (default OFF, mono output only) adds vendored
fixed-point libopus without Arduino. The build helper accepts `-EnableOpus`
with a fresh `-Variant`; this is not a device-qualified production profile.
It supports mono/stereo mapping-0 streams at 48-kHz mono output, packets up to
20 ms / 1536 bytes, bounded shared IRAM/scratch and incremental Ogg parsing.
MP3/AAC retain their existing settings. See [limits, memory reuse, tests and
remaining qualification](../../docs/ESP8266_OPUS_NATIVE.md).

## Optional local SPIFFS logging

Optional local diagnostic logging: build with `-Diagnostic -SpiffsLog` using
`tools/esp8266_audio_profile/build_i2s_pdm_production.ps1`, or configure
`-DYORADIO_ESP8266_DIAGNOSTIC=ON -DYORADIO_ESP8266_SPIFFS_LOG=ON`.
Production has neither SPIFFS logging nor log HTTP routes. Diagnostic-only
`-DYORADIO_ESP8266_SPIFFS_LOG_HTTP=ON` enables read-only `/api/native/log`
and `/api/native/log/previous` downloads. Default OFF; two bounded 8 KiB SPIFFS
files, a 512-byte RAM queue, deferred app-task writes, no new task/stack.
UART output is preserved. HTTP reading additionally requires `-SpiffsLogHttp`;
USB flash extraction with the native SPIFFS format remains available.
Flash writes can disturb audio.
See [configuration, limits and USB extraction](../../docs/ESP8266_SPIFFS_LOGGING.md).

## OTA-first updates with audio connected to RX

For the connected Wemos D1 mini, use OTA for subsequent application updates:
the audio circuit is connected to UART RX/GPIO3. Do not automatically fall
back to serial flashing/reset if Wi-Fi or HTTP is unavailable. Serial recovery
requires a separate user decision. Passive GPIO1/TX log capture must not send
UART bytes or assert the reset/boot control lines.

The native firmware already provides `POST /update` on HTTP port 80. Its
multipart fields, in order, are `updatetarget=fw` and `update=<app.bin>`.
Upload only an ESP8266 RTOS SDK native application image, not an Arduino
image, merged flash image, bootloader, partition table or SPIFFS image.
The two app slots are 960 KiB each at `0x10000` and `0x110000`; the production
artifact is `firmware/development/esp8266-i2s-pdm-production/app.bin`.

Before an update, verify stable HTTP access and read `/api/native/status`,
including `app_address`. Retain the application binary and its manifest under
`firmware/`. The OTA handler stops playback, writes the inactive slot, and
selects it only after complete reception and successful SDK image validation.
A successful request returns HTTP 200 with `OK`, then schedules a restart.
This updates neither the partition table nor NVS/SPIFFS contents; stopping
playback can, however, persist the normal stopped/smart-start setting.

After restart, verify HTTP access, the expected new `app_address`, settings,
playlist, WebUI and playback. A lost upload response is ambiguous: first
inspect the running slot instead of blindly retrying the POST. Do not claim
an OTA update succeeded from the upload request alone, and do not assume
automatic rollback if a validated image fails during application startup.

The existing `tools/test_esp8266_maintenance.py` exercises both OTA slots but
also uploads Wi-Fi, playlist and WebUI files; it is a separately authorized
maintenance test, not the routine app-only updater.
