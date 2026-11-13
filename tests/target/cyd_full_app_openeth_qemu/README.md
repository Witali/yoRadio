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

For the continuous DAC DMA experiment, use the C3 TCP window of 8640 bytes
and receive mailbox of 8 entries. Add `'-D','CYD_OPENETH_DAC_START_ORDER=ON'`
for the start-order control and `'-D','CYD_OPENETH_DAC_BOUND_STOP_WAIT=ON'`
for the combined candidate. Both switches select a build-local copy of the
pinned SDK's synchronous DAC driver. The candidate publishes DMA state before
start and waits at most the caller's timeout for a previous transfer to stop.
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

The [startup results](../../results/cyd-full-app-openeth-20261111/README.md)
and [RX backoff results](../../results/cyd-openeth-rx-backoff-20261111/README.md)
cover the diagnostic profiles. Production Wi-Fi, the five-second watchdog and
physical audio require their own evidence.
