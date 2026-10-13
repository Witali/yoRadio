# Production profile

Build the quiet maximum-performance ESP32-C3 OLED image with:

```powershell
.\build-production.ps1
```

Flash only the application while preserving NVS, playlists and WebUI files:

```powershell
.\build-production.ps1 -IdfArguments @('-p', 'COM9', 'app-flash')
```

The profile uses `sdkconfig.defaults` plus
`sdkconfig.production.defaults`. It keeps the normal O3 optimization and
compiles out application and ESP-IDF logs, disables bootloader logs and the
application console, and silently reboots on panic. The USB Serial/JTAG ROM
bootloader remains available for reflashing. Its short reset banner is emitted
by mask ROM and cannot be removed by an application build.

Use the regular `build.ps1` profile when serial diagnostics are needed.

## Reproduce the measured ESP-IDF 6.1 radio candidate

```powershell
.\build-production.ps1 -TestedRadioProfile
```

This adds `sdkconfig.radio-tested.defaults`: QIO 80 MHz, fractional 48 kHz
output, the measured TLS/input memory policy, one-second prefill, and release
of the completed HTTP request buffer. It uses the SDK revision pinned in this
project. The decoder profiles and precision stay unchanged.

The switch uses a separate `build-production-radio-tested` directory by default
and saves its image to `firmware/development/esp32c3-oled-native-production-radio-tested/app.bin`.
An explicitly selected existing configuration receives these profile settings
too; unrelated settings remain. The `-DeepSleepClock` and `-Rtc32kCrystal`
switches still select their respective variants.

“Tested” identifies the measured configuration, not complete production
qualification. See the [results and remaining checks](../../docs/ESP32C3_HTTP_REQUEST_BUFFER.md).
The ordinary production command retains its existing configuration policy.
