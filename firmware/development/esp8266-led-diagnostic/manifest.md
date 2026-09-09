# esp8266-led-diagnostic

Separate diagnostic companion. HTTP log access is authorized only for this profile; not production.

- Source: 82edaf25f03e9f73567248768884d593dff974b9
- Built UTC: 09/09/2026 16:42:03
- app.bin: 765840 bytes
- SHA-256: E09CE877727F25E9DC389143A7725BA1BFE25FE42C4F14098DAEAC229A5C1B65
- LED enabled: True; refresh: 10 Hz; maximum brightness: 32 / 255.
- Web audio pause: short. SPIFFS log: True; HTTP log: True.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, compressed input 4096 B.
- I2S PDM32 DATA GPIO3/RX, 1.538461 MHz, two 512-word DMA buffers; LED GPIO2.
- App-only OTA selects the inactive 960-KiB slot. No SPIFFS/NVS/partition replacement.

See [measured results and remaining limitations](../../../docs/ESP8266_LED_REGRESSION_2026-09-09.md).
Control images are not proof of glitch-free playback. Full configuration is in sdkconfig.
