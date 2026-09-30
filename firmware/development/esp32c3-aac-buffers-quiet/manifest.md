# esp32c3-aac-buffers-quiet

- Source: `fb64725ce2e9250c24f6adf3998bc28ff2a7a4e5`.
- Embedded version: `v0.9.693-1068-gfb64725c`.
- ESP-IDF 6.0.2; codec 2.6.2; ESP32-C3 160 MHz, DIO 80 MHz, no PSRAM/deep sleep.
- AAC/SBR memory experiment; see exact sdkconfig. Qualification recorded separately.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `app.bin` | 1393120 | `d7640d4e80e230827b8365cf08fc67eac0a223b8f2f7f44cf8ff9a4eccbd2bfc` |
| `bootloader.bin` | 13200 | `e43e7cf8f3d8c0e81f2b187ca715775a3daef70beb1f3bdf75b74699501faee7` |
| `sdkconfig` | 82029 | `bd2b40271da86518ebee44bc256bb550a9e6570265fd98e368e9bad2001d11da` |

Application is intended for WebUI OTA. For serial recovery verify the active
app slot (app0: `0x10000`, app1: `0x1e0000`); bootloader offset is `0x0`.
Preserve NVS, SPIFFS and OTA selection. Trace/profiling images are diagnostic.

This image is retained for reproducibility, not a completed HE-AAC fix. AAC uses the 8 KiB PCM workspace and adaptive ADTS storage; full-radio SBR remains unresolved.
