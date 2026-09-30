# esp32c3-aac-heapflash-minimal-usb

- Source: `fb64725ce2e9250c24f6adf3998bc28ff2a7a4e5`.
- Embedded version: `v0.9.693-1068-gfb64725c-dirty`.
- ESP-IDF 6.0.2; codec 2.6.2; ESP32-C3 160 MHz, DIO 80 MHz, no PSRAM/deep sleep.
- AAC/SBR memory experiment; see exact sdkconfig. Qualification recorded separately.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `app.bin` | 1530224 | `f01d35cffdfb4eb10b8227794f99f978371a3948c87d8133ba86325fe3b98f80` |
| `bootloader.bin` | 13296 | `b1ff556ab400ce1cdcebb56ca825eea0b644e6f4f07ed3cd036808c1ba89f749` |
| `sdkconfig` | 81707 | `04d86367b2b0168fe829b605cb0b01e765752b75c5255bf94af5ed8238e0811e` |

Application is intended for WebUI OTA. For serial recovery verify the active
app slot (app0: `0x10000`, app1: `0x1e0000`); bootloader offset is `0x0`.
Preserve NVS, SPIFFS and OTA selection. Trace/profiling images are diagnostic.

The dirty version suffix comes from documentation/test-runner edits; firmware
sources under `idf/` and `yoRadio/` match the recorded source commit.

This image is retained for reproducibility, not a completed HE-AAC fix. Heap placement is experimental and is not enabled by the board defaults.
