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
