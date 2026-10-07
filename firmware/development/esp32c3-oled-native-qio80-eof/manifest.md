# esp32c3-oled-native-qio80-eof

- Source: `69410cd5`; embedded version: `v0.9.693-1061-g69410cd5`.
- ESP-IDF v6.0.2; CPU 160 MHz, QIO 80 MHz; 4 MiB flash.
- Quiet production settings; no deep sleep; internal RTC; AAC Plus enabled.
- EOF status is published after the queued decoder output completes.

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `app.bin` | 1392912 | `0x1e0000` (verified app1 in the initial test) | `d5d226ccad1231f2a0c99f498a6bf826a6869f121f5cdf56508d6db82b04ce70` |
| `bootloader.bin` | 13872 | `0x0` | `fafa1977197bf6fce71d339ede7699a281854c472611fc5a2255c453b5a284d7` |
| `sdkconfig` | 81969 | Build configuration | `99c03460b360d282a3caef37744ceaba03188245d75ceae7a61f7adf73293a19` |

Use the matching bootloader to select the intended flash mode. Verify the active
app slot before a serial update; preserve NVS, SPIFFS and the OTA selector.
Image-header DIO is intentional for the QIO bootloader too.

[EOF behavior and validation](../../../docs/ESP32C3_EOF_STATUS.md).
This artifact does not by itself qualify QIO as the default or full-radio HE-AAC.
