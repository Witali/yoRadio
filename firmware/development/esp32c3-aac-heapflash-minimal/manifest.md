# esp32c3-aac-heapflash-minimal

- Source: `fb64725ce2e9250c24f6adf3998bc28ff2a7a4e5`.
- Embedded version: `v0.9.693-1068-gfb64725c`.
- ESP-IDF 6.0.2; codec 2.6.2; ESP32-C3 160 MHz, DIO 80 MHz, no PSRAM/deep sleep.
- AAC/SBR memory experiment; see exact sdkconfig. Qualification recorded separately.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `app.bin` | 1528768 | `67539130ca5f0a566cedfd8c978fb0580d20d782c0d897f49af454d539abeda3` |
| `bootloader.bin` | 13200 | `c871c0ae52dc1670bcebed26ddaf9e8b1410554f8856fe36353dd595ecb2e55a` |
| `sdkconfig` | 81687 | `e38a97f06ebe39ba7ebc8bf4d81c5aed02b97b0c81aa54123507d8cbb2dd7580` |

Application is intended for WebUI OTA. For serial recovery verify the active
app slot (app0: `0x10000`, app1: `0x1e0000`); bootloader offset is `0x0`.
Preserve NVS, SPIFFS and OTA selection. Trace/profiling images are diagnostic.

This image is retained for reproducibility, not a completed HE-AAC fix. Heap placement is experimental and is not enabled by the board defaults.
