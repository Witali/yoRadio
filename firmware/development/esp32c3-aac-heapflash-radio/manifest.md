# esp32c3-aac-heapflash-radio

- Source: `d77ea5b9fcf7a075676b65d181ffa185a2fde010`.
- Embedded version: `v0.9.693-1067-gd77ea5b9`.
- ESP-IDF 6.0.2; codec 2.6.2; ESP32-C3 160 MHz, DIO 80 MHz, no PSRAM/deep sleep.
- AAC/SBR memory experiment; see exact sdkconfig. Qualification recorded separately.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `app.bin` | 1540080 | `56a518980c678f646f1a7825f17943d3953800d15fca7a86fd714f144f5af9f9` |
| `bootloader.bin` | 18672 | `5f2943b0937afd4a3125bde948756972ae64cbe202327e0cc134687e501b6312` |
| `sdkconfig` | 82074 | `54c041389575f70edd06bb4a3bb9a4fd48df7fee97f62e411abb82ab4faa4bca` |

Application is intended for WebUI OTA. For serial recovery verify the active
app slot (app0: `0x10000`, app1: `0x1e0000`); bootloader offset is `0x0`.
Preserve NVS, SPIFFS and OTA selection. Trace/profiling images are diagnostic.

This image is retained for reproducibility, not a completed HE-AAC fix. Heap placement is experimental and is not enabled by the board defaults.
