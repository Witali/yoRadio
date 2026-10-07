# esp32c3-oled-native-dio80-eof

- Source: `69410cd5`; embedded version: `v0.9.693-1061-g69410cd5`.
- ESP-IDF v6.0.2; CPU 160 MHz, DIO 80 MHz; 4 MiB flash.
- Quiet production settings; no deep sleep; internal RTC; AAC Plus enabled.
- EOF status is published after the queued decoder output completes.

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `app.bin` | 1392912 | `0x1e0000` (verified app1 in the initial test) | `abd5d0ed4aded1910cc1dcb2f11593fc2a858ec6b0f69bd52486dfef56ad4ed3` |
| `bootloader.bin` | 13200 | `0x0` | `d39d85b800e75ac7d01d7232b86c311d9cd7217eb71b17801d9c3daf93222459` |
| `sdkconfig` | 81969 | Build configuration | `cc532fb21983e616a32624a32160921b30fed776e63066d7277dce5a3317a4f2` |

Use the matching bootloader to select the intended flash mode. Verify the active
app slot before a serial update; preserve NVS, SPIFFS and the OTA selector.
Image-header DIO is intentional for the QIO bootloader too.

[EOF behavior and validation](../../../docs/ESP32C3_EOF_STATUS.md).
This artifact does not by itself qualify QIO as the default or full-radio HE-AAC.
