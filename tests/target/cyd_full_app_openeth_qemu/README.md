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

The [startup results](../../results/cyd-full-app-openeth-20261111/README.md)
and [RX backoff results](../../results/cyd-openeth-rx-backoff-20261111/README.md)
cover the diagnostic profiles. Production Wi-Fi, the five-second watchdog and
physical audio require their own evidence.
