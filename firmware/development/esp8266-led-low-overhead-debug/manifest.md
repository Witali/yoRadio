# esp8266-led-low-overhead-debug

Historical control image for the LED regression experiment; not the recommended daily firmware.

- Source: 432849282338fdd54baaa58352f735fea9341df3
- Built UTC: 09/09/2026 16:14:20
- app.bin: 765824 bytes
- SHA-256: E1ADFB8D6D891CA4366BAE111DFDA1B5EFAC644A37C91585299656A703AB1401
- LED enabled: True; refresh: 10 Hz; maximum brightness: 255 / 255.
- Web audio pause: short. SPIFFS log: True; HTTP log: True.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, compressed input 4096 B.
- I2S PDM32 DATA GPIO3/RX, 1.538461 MHz, two 512-word DMA buffers; LED GPIO2.
- App-only OTA selects the inactive 960-KiB slot. No SPIFFS/NVS/partition replacement.

See [measured results and remaining limitations](../../../docs/ESP8266_LED_REGRESSION_2026-09-09.md).
Control images are not proof of glitch-free playback. Full configuration is in sdkconfig.
