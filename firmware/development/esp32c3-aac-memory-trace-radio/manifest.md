# esp32c3-aac-memory-trace-radio

- Source: `8740af78b6e71ab0f53aff1f6027c168a112db17`.
- Embedded version: `v0.9.693-1064-g8740af78`.
- ESP-IDF 6.0.2; codec 2.6.2; ESP32-C3 160 MHz, DIO 80 MHz, no PSRAM/deep sleep.
- AAC/SBR memory experiment; see exact sdkconfig. Qualification recorded separately.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `app.bin` | 1541984 | `1948d2c32563a837ab037f4035803faba503f69ee765022743588a8cb0ef4563` |
| `bootloader.bin` | 18672 | `5f2943b0937afd4a3125bde948756972ae64cbe202327e0cc134687e501b6312` |
| `sdkconfig` | 82187 | `67ebc22e21c3c7f3473e262591390a0d6e668cb1a7378d7ef97317ff14b2f211` |

Application is intended for WebUI OTA. For serial recovery verify the active
app slot (app0: `0x10000`, app1: `0x1e0000`); bootloader offset is `0x0`.
Preserve NVS, SPIFFS and OTA selection. Trace/profiling images are diagnostic.
