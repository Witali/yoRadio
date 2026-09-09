# esp8266-led-production

Installed production; UART errors only, no SPIFFS logging or HTTP log route.

- Source: 82edaf25f03e9f73567248768884d593dff974b9
- Built UTC: 09/09/2026 16:41:54
- app.bin: 763248 bytes
- SHA-256: 3A06BB31AC4F31F311FFB57E825FE36956F23549037EAC383697F54D9DAF8235
- LED enabled: True; refresh: 10 Hz; maximum brightness: 32 / 255.
- Web audio pause: short. SPIFFS log: False; HTTP log: False.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, compressed input 4096 B.
- I2S PDM32 DATA GPIO3/RX, 1.538461 MHz, two 512-word DMA buffers; LED GPIO2.
- App-only OTA selects the inactive 960-KiB slot. No SPIFFS/NVS/partition replacement.

See [measured results and remaining limitations](../../../docs/ESP8266_LED_REGRESSION_2026-09-09.md).
Control images are not proof of glitch-free playback. Full configuration is in sdkconfig.

Installed by app-only OTA on 2026-09-09; app1 0x110000 confirmed. Station 501
(Дорожное радио) left playing. Final 22.465-s sample: PCM/time 98.91%,
RAM >=8432 B, no long PCM stall, but 253 DMA underrun events remain. WebUI
HTTP/WS respond; occasional multi-second HTTP body transfers are unresolved.
