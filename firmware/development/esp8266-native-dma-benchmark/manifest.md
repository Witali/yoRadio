# ESP8266 I2S DMA ownership benchmark (development)

2026-09-05. Wemos D1 mini, CPU 160 MHz, QIO 40 MHz, GPIO3 I2S PDM32,
nominal 1.536 MHz; two 512-word buffers (4096 bytes).

- app.bin: 126032 bytes
- SHA-256: F9DF36479B43E2A990254932FF67DBA9FDBA8F63F84D16EF3E1923C5F15C8224
- Physical final run: 941 EOFs, no underrun/FIFO-empty events, stalled producer PASS.
- Driver source: 4ad22fb, built before commit with embedded 795000a-dirty tag.

Build: `YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK=ON`, audio/memory profiles and
tone-test OFF. Same DMA driver as ordinary radio; Wi-Fi and codecs disabled.
Generated 48 kHz stereo PCM: 2 s warmup, 10 s measurement, then a 65 ms
deliberately stalled partial-buffer test. Settings read, not persisted.

Changelog: finite descriptors and explicit FILLING/READY/DMA ownership;
neutral PDM on underrun; EOF/FIFO counters and byte-exact partial-buffer check.

Flash **app0 only at 0x10000** on the existing 256 KiB SPIFFS / dual-OTA layout.
Do not rewrite bootloader, partition table, NVS, otadata, or SPIFFS.
This is a test image, not the normal radio firmware.
