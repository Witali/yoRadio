# yoRadio native ESP-IDF firmware

This is a separate firmware for the ESP32-2432S028 CYD2USB board. It uses
ESP-IDF APIs directly and deliberately does not include Arduino Core,
Arduino libraries, Adafruit GFX, or the Arduino yoRadio runtime.

The native port keeps the existing 4 MiB partition layout, so flashing only
the application image does not erase NVS or the SPIFFS web UI. The SPIFFS
image target is generated from `yoRadio/data` for explicit WebUI updates.

## Build

```powershell
.\setup.ps1
.\build.ps1
```

To reuse a previously installed dependency cache:

```powershell
.\build.ps1 -DependencyRoot C:\path\to\.idf
```

To flash only the application and preserve Wi-Fi/SPIFFS:

```powershell
.\build.ps1 -IdfArguments @('-p', 'COM8', 'app-flash')
```

To install or restore the WebUI explicitly:

```powershell
.\build.ps1 -IdfArguments @('-p', 'COM8', 'spiffs-flash')
```

The display driver is a native ESP-IDF ST7789/SPI-DMA port taken from the
HLV-codec CYD firmware and kept locally in `main/cyd_display.*`.

