# esp8266-led-low-overhead-off

Historical control image for the LED regression experiment; not the recommended daily firmware.

- Source: 432849282338fdd54baaa58352f735fea9341df3
- Built UTC: 09/09/2026 16:15:58
- app.bin: 761872 bytes
- SHA-256: 2F0C9D2BB07844D9412788301959AD91CA2455BD24A4225060D220D8F4AAFBBC
- LED enabled: False; refresh: 0 Hz; maximum brightness: 0 / 255.
- Web audio pause: short. SPIFFS log: False; HTTP log: False.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, compressed input 4096 B.
- I2S PDM32 DATA GPIO3/RX, 1.538461 MHz, two 512-word DMA buffers; LED GPIO2.
- App-only OTA selects the inactive 960-KiB slot. No SPIFFS/NVS/partition replacement.

See [measured results and remaining limitations](../../../docs/ESP8266_LED_REGRESSION_2026-09-09.md).
Control images are not proof of glitch-free playback. Full configuration is in sdkconfig.
