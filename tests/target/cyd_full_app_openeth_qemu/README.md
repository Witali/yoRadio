# CYD application startup and load over QEMU OpenETH

The diagnostic CMake hook links the production CYD application and replaces
its `network_service_start` call with ESP-IDF OpenETH and an IPv4 event. The
production startup task then initializes the audio tasks, radio control and
WebUI. The application also initializes ST7789 and its normal SPI DMA buffers.
QEMU exposes HTTP on a loopback port. With `--tls-material`, the guest can
reach one local TLS station through a restricted guest forwarding rule.
[Espressif's classic ESP32 QEMU Ethernet documentation](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/esp32/README.md#ethernet-support)

The SDK 6.0.2 Python environment supplies `cryptography` for the optional TLS
profile. Start from a built CYD vendor PDM `sdkconfig`. Set the four paths in
the example to the existing dependencies, production configuration, QEMU
executable and ROM directory.

```powershell
$deps = 'C:/Work/yoRadio/.idf'
$baseConfig = 'path/to/built/vendor-pdm/sdkconfig'
$qemu = '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
$rom = 'C:/Work/QEMU-ESP32/pc-bios'
$py = "$deps/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe"
$target = 'tests/target/cyd_full_app_openeth_qemu'
& $py -B "$target/prepare-profile.py" --sdkconfig $baseConfig --output .build/openeth-profile --tls-diagnostics
$profile = (Resolve-Path .build/openeth-profile).Path
$hook = (Resolve-Path "$target/attach.cmake").Path.Replace('\','/')
& ./idf/esp32-cyd2usb-native/build.ps1 -DependencyRoot $deps -BuildDirectory "$profile/build" -Sdkconfig "$profile/sdkconfig" -IdfArguments @('-D','IDF_TOOLCHAIN=gcc','-D',"CMAKE_PROJECT_yoradio_cyd2usb_native_INCLUDE=$hook",'build')
& $py -B "$target/prepare.py" --build "$profile/build" --spiffsgen "$deps/v6.0.2/components/spiffs/spiffsgen.py" --output .build/openeth-fixture
& $py -B tests/run-cyd-full-app-openeth.py --build .build/openeth-fixture --qemu $qemu --rom $rom --output .build/openeth-idle
& $py -B tests/run-cyd-full-app-openeth.py --build .build/openeth-fixture --qemu $qemu --rom $rom --tls-material $profile --output .build/openeth-load
```

Use fresh output directories for each run. The TLS profile adds telemetry, a
30-second task watchdog and a one-day local CA. Keep the generated key in the
ignored profile directory. The fixture copies tracked WebUI assets and stages a
one-station TSV playlist and its index into a separate SPIFFS image. The boot
control serves the exact gzip JavaScript asset and reports the actual guest's
heap and stack samples. The load case selects station 1 through the WebUI API
and requires progress in the audio driver's byte counter across a WebUI read.

For the OpenETH receive-memory experiment, add `'-D','CYD_OPENETH_RX_BACKOFF=ON'`
to `-IdfArguments` before `'build'`. Use a new build directory with the same
TLS profile and station fixture. The hook replaces the pinned SDK's OpenETH
MAC source inside that build. It checks for a ready descriptor before
allocating and waits one tick before retrying a failed allocation. The report
records the UART pressure markers and any health samples returned during
playback, including samples with nonzero failure counters.

For the [TLS buffer comparison](../../results/cyd-openeth-tls-dynamic-20261111/README.md),
make a second copy of the TLS diagnostic `sdkconfig` in a fresh build directory.
Replace `# CONFIG_MBEDTLS_DYNAMIC_BUFFER is not set` with
`CONFIG_MBEDTLS_DYNAMIC_BUFFER=y` and reuse the first profile's CA and TLS
station. Build both configurations with the RX overlay. Keep the TLS record
limits at 16384/4096 bytes and leave dynamic certificate/configuration cleanup
disabled. Compare both generated `config/sdkconfig.json` files before running.

Add `--through-eof` to the TLS run to check the complete Opus file with the
Ogg timeline enabled. The runner requires the full TLS response, the original
generation's EOF, the exact output count, and another exact WebUI asset read
after EOF. PDM uses the driver byte count.

For continuous and legacy DAC, select the corresponding CYD audio backend in
the isolated `sdkconfig` and add `'-D','CYD_OPENETH_PCM_PROBE=ON'` to the build
arguments. The probe counts only decoded PCM accepted by the actual output
function and requires 528,000 stereo frames at the ordered flush. Priming and
idle writes are outside the probe. QEMU runs the continuous DAC model at
48 kHz and the legacy model at its supported ceiling of 96 kHz. The legacy
driver still requests its normal x16 rate, so its host deadline is 360 seconds.

The continuous DAC build automatically applies the DMA start and wait fix.
To reproduce the full-record comparison, use the C3 TCP window of 8640 bytes
and receive mailbox of 8 entries with the dynamic TLS and OpenETH settings
above. The historical start-order and combined diagnostics are reproducible
at `eb3b096ec`.
Run `tests/run-cyd-dac-write-test.py --sdk <pinned-sdk> --output <fresh-directory>`
for the early completion, timeout, and recovery cases under ASan/UBSan.
[DAC DMA results](../../results/cyd-openeth-dac-wait-20261113/README.md).

Add `--full-tls-records` with `--through-eof` to verify TLS 1.2 AES-GCM record
lengths on the local HTTPS server. The Opus fixture uses 43 full 16,384-byte
body writes and an 1807-byte tail. The CPython/OpenSSL message callback records
only outgoing encrypted record lengths. The runner checks each length.
To compare the reserved RX buffer, enable `CONFIG_YORADIO_TLS_STATIC_RX_RESERVE`
in a fresh copy of the static-buffer diagnostic config. Reuse the CA and
station fixture and keep the same OpenETH RX overlay across the three builds.
[Full-record results](../../results/cyd-openeth-full-records-20261111/README.md).
For PDM with static RX, use the [QEMU I2S DMA fix and tested profile](../../results/cyd-pdm-static-rx-20261113/README.md)
for the complete run, including the WebUI request after EOF.

## TLS reconnect and OTA during playback

Build the static RX profile with `'-D','CYD_OPENETH_TLS_RX_PROBE=ON'` and
`'-D','CYD_OPENETH_PCM_PROBE=ON'`. The RX probe reports each acquisition
and return of the buffer in the application's BSS. The PCM probe confirms
that real audio reaches the output in each TLS session.

This test opens a fresh host TCP connection for every guest connection and
keeps QEMU user networking restricted. With a Windows build that uses
`subprojects/slirp-win32`, apply the
[loopback forwarding patch](qemu-slirp-loopback.patch) to the QEMU source
tree and rebuild with the same I2S DMA start fix. The Windows SLIRP command
backend otherwise passes a Winsock handle to GLib as a file descriptor.
The patch adds `cmd:tcp-loopback:<port>` for a fixed loopback destination.
On POSIX hosts, the runner uses [QEMU's per-connection guestfwd command](https://www.qemu.org/docs/master/system/invocation.html)
with the Python loopback relay.

```powershell
& $py -B tests/run-cyd-full-app-openeth.py --build .build/openeth-fixture --qemu $qemu --rom $rom --tls-material $profile --output .build/openeth-ota-lifecycle --radio-ota-lifecycle
```

The controller checks Stop/Play, a truncated image that fails verification
and resumes playback, then a same-image update started during playback.
After the software reset it checks the running `app1` slot, ELF hash,
WebUI asset and fresh TLS playback. All writes are to the QEMU snapshot.
The controller also checks the original flash file digest after QEMU exits.

## Input reclaim under allocator pressure

Use the PDM stereo Opus profile with static TLS RX and
`CONFIG_YORADIO_TLS_INPUT_RECLAIM=y`. Enable the RX probe, PCM probe and
PCM MD5 in both builds. First run the ordinary profile through EOF with
`--full-tls-records` and capture the single `CYD_OPENETH_PCM_MD5` from its
UART log. Then build with `'-D','CYD_OPENETH_RECLAIM_PROBE=ON'`, stage
its flash fixture and repeat the same command with
`--expect-input-reclaim <control PCM MD5>`.

After the first decoded write, the probe checks for an idle slot between
reads and makes one Mbed TLS allocation under real internal heap pressure.
The production stream task performs the request, which keeps the slot
available to reclaim while the probe measures and allocates. The
controller requires one recorded allocation failure of the measured size,
a successful retry through bounded idle-slot release, a live static RX loan, byte-identical
PCM and working WebUI through EOF.
[Probe](input_pressure.c)

## Radio TLS and HTTPS WebUI under pressure

Build the reclaim profile above with
`'-D','CYD_OPENETH_TLS_OVERLAP_PROBE=ON'`. Prepare the disposable WebUI
identity using the ESP-IDF 6.0.2 NVS generator.

```powershell
& $py -B "$target/prepare-https.py" --nvsgen "$deps/v6.0.2/components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py" --output .build/openeth-https
```

Add `--web-https-fixture .build/openeth-https` to the full-record
input-reclaim run. The controller holds one verified TLS 1.2/P-256
connection to the production WebUI. It requires one heap RX buffer at
the allocator retry, a live static radio RX loan, working API requests
while PCM advances, and the exact static asset at EOF. The static route
closes its connection after the asset. The test waits for the heap RX
release before exiting.

Use `--short-opus-pages` for the paired run with eight original Opus
packets per page. The packet bytes, headers and final granule are
preserved. The original page layout is the default.

For the early Opus decoder open test, keep the original page layout and use
PDM with the same TLS options above. Build the control with
`CONFIG_YORADIO_OGG_OPUS_RAW` disabled and the replay with it enabled. Add
`'-D','CYD_OPENETH_OPUS_HEAP_PROBE=ON'` to each build. The successful
packet-level run logs a stereo decoder open after OpusTags and checks the
full radio response, exact output, and the same verified HTTPS connection
through EOF. [Results](../../results/cyd-ogg-large-pages-20261117/README.md)

## Other playback fixtures

For Helix MP3, use `--codec mp3 --through-eof` with the PCM and PCM MD5
probes and `CONFIG_YORADIO_MP3_DECODER_HELIX=y`. Compare builds with
`CONFIG_YORADIO_AUDIO_MONO` enabled and disabled. The fixture repeats a
48 kHz stereo MP3 segment containing M/S frames. The controller checks
stereo source metadata, the configured PCM channel count, the exact frame count
at EOF and a subsequent WebUI asset request. It records the MD5 of decoded
PCM accepted by the backend.

On ESP-IDF 6.0.2 with PDM, both Helix builds consumed all 193,536 MP3 bytes
and delivered 580,608 PCM frames through EOF. Status reported two source
channels in both builds, with one PCM channel in the mono build and two in
the stereo build. The WebUI served the exact JavaScript asset after EOF in
both runs with zero allocation failures. The
[Helix host regressions](../../esp8266-helix-golden.test.js) check the
skipped M/S work, fallback modes and overlap state.

For a matched FLAC comparison, use two copies of the same TLS diagnostic
configuration and local CA. Select `CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF`
in the first and `CONFIG_YORADIO_FLAC_DECODER_CUSTOM` in the second. Use
continuous DAC, the DMA fix, dynamic TLS buffers, TCP 8640/8 and OpenETH RX
backoff in both builds. Add `'-D','CYD_OPENETH_PCM_PROBE=ON'` and
`'-D','CYD_OPENETH_PCM_MD5=ON'` to each build. Run each fixture with
`--codec flac --through-eof --full-tls-records`. The runner verifies the
lossless PCM16 frame count and MD5 against FLAC STREAMINFO at the output
task's ordered flush. The probe hashes the decoded samples accepted by the
backend, before volume processing and conversion to DAC samples.
[FLAC STREAMINFO specification](https://www.rfc-editor.org/rfc/rfc9639.html#section-8.2).

To reproduce the [custom FLAC production watchdog matrix](../../results/cyd-flac-openeth-20261116/README.md#matched-full-application-results-on-all-three-outputs),
set `CONFIG_ESP_TASK_WDT_TIMEOUT_S=5` in the TLS diagnostic profile. Use
one build per output selection and enable both PCM probe options for each
build, including PDM. The runner checks the exact `/script.js` with a
25-second socket I/O timeout, independent of the guest watchdog.

For [Opus Family 1](../../results/cyd-opus-family1-openeth-20261116/README.md),
disable `CONFIG_YORADIO_AUDIO_STEREO_ONLY` for multichannel playback and
add `'-D','CYD_OPENETH_PCM_PROBE=ON'` and
`'-D','CYD_OPENETH_PCM_CHANNEL_METRICS=ON'` to the diagnostic build. Use
`'-D','CYD_OPENETH_OPUS_HEAP_PROBE=ON'` to record available internal memory
and the largest matching block before and after each Espressif decoder open.
Generate a local fixture with FFmpeg and ffprobe available on PATH.

```powershell
& $py -B "$target/prepare-opus-family1.py" --output .build/family1-120 --packet-ms 120
& $py -B tests/run-cyd-full-app-openeth.py --build .build/openeth-fixture --qemu $qemu --rom $rom --tls-material $profile --output .build/openeth-family1-120 --opus-family1 .build/family1-120/fixture.json --through-eof --full-tls-records
```

The fixture defaults to eight channels and a 1,000 ms Ogg muxer page target.
Use `--packet-ms 20`, `--channels 4` or `--channels 6`, and
`--ogg-page-ms 200` to vary one property per comparison. The runner checks
the exact post-trim frame count, then compares energy and zero crossings in
each Vorbis-order channel against the libopus decode. It also requires
progress during a WebUI read and an exact asset read after EOF.

With the default stereo-only build, run the same `--opus-family1` fixture
with `--expect-channel-limit` in place of the EOF and full-record options.
The runner checks the channel-limit status, absence of decoder opens and PCM
writes, and the exact WebUI asset after rejection. Enable the Opus heap probe
to observe every raw decoder open.

To compare two builds of the ST7789 status display, use `check-tft.py`
with the same OpenETH boot profile. It waits for the full network-client
frame in QEMU and compares the dimensions and every RGB pixel. The PPM
frames are saved under the supplied ignored output directory.

```powershell
& $py -B "$target/check-tft.py" --baseline .build/openeth-before --build .build/openeth-after --qemu $qemu --rom $rom --output .build/tft-comparison
```

The [startup results](../../results/cyd-full-app-openeth-20261111/README.md)
and [RX backoff results](../../results/cyd-openeth-rx-backoff-20261111/README.md)
cover the earlier diagnostic profiles. Production Wi-Fi and physical audio
require hardware evidence.
