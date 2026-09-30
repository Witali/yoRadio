# esp32c3-aac-buffers-radio

- Source: `d77ea5b9fcf7a075676b65d181ffa185a2fde010`.
- Embedded version: `v0.9.693-1067-gd77ea5b9`.
- ESP-IDF 6.0.2; codec 2.6.2; ESP32-C3 160 MHz, DIO 80 MHz, no PSRAM/deep sleep.
- AAC/SBR memory experiment; see exact sdkconfig. Qualification recorded separately.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `app.bin` | 1542208 | `4675bbc4e73f41b55606129ca9fa763e17f52504c70707e5ae76506c491883d9` |
| `bootloader.bin` | 18672 | `5f2943b0937afd4a3125bde948756972ae64cbe202327e0cc134687e501b6312` |
| `sdkconfig` | 82187 | `67ebc22e21c3c7f3473e262591390a0d6e668cb1a7378d7ef97317ff14b2f211` |

Application is intended for WebUI OTA. For serial recovery verify the active
app slot (app0: `0x10000`, app1: `0x1e0000`); bootloader offset is `0x0`.
Preserve NVS, SPIFFS and OTA selection. Trace/profiling images are diagnostic.

This image is retained for reproducibility, not a completed HE-AAC fix. AAC uses the 8 KiB PCM workspace and adaptive ADTS storage; full-radio SBR remains unresolved.
