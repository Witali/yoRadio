# ESP8266 native network-reader experiment

- Built: 2026-09-05; compile-checked only, NOT flashed or accepted as default.
- Sources: 79fd2c4 plus the zero-copy stream-probe change recorded with this image.
- CPU 160 MHz, QIO 40 MHz, GCC 8.4, -O3; ordinary I2S PDM32.
- Helix MP3 SSO and AAC enabled; 4-KiB compressed ring, 2560-byte network stack.
- YORADIO_ESP8266_KARADIO_PIPELINE=ON; AUDIO_PROFILE and OUTPUT_BENCHMARK=OFF.
- app.bin: 689664 bytes.
- SHA256: 65353587BEEEDD094A1FA95463B55D70CE034E2AF2C75BE47F1D8D541CAB0A5E.
- Existing 4-MiB OTA layout / 256-KiB SPIFFS; application image only.
- The board remains on the previously verified ordinary native app; local
  default build cache has been returned to KARADIO_PIPELINE=OFF.

## Changelog

Remove the 1024-byte stream-detection copy and inspect the already published
ring prefix before the first decoder read. ELF still contains a 4096-byte
compressed ring and 512-byte producer URL, but no s_karadio_probe.

This reduces the producer variant's static DRAM by 1024 bytes. It does not
reduce native's single-task default (which never included the probe), increase
the ring, or establish sufficient RAM headroom for full AAC + WebUI operation.
See docs/ESP8266_AUDIO_MEMORY_TODO.md for remaining acceptance work.
