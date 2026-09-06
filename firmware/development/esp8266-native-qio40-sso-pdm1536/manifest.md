# ESP8266 native QIO40 SSO PDM 1.536 MHz

Validated development production-profile image for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-02
- Source commit: `99d15cc`
- Application offset: `0x10000`
- Application: `app.bin` (670,000 bytes)
- SHA-256: `92CB090C923DA36E58499AE2E6E438CEEC98D2C48D8544958D7E0AA2BD844E9F`
- CPU: 160 MHz; compiler release optimization
- Flash runtime: QIO 40 MHz (the SDK-compatible image header remains DIO)
- MP3: Helix 32-bit SSO
- AAC: Helix exact fixed-point
- Audio: mono I2S/SLC DMA on GPIO3, genuine PDM32 x1 at 1.538461 MHz
- DMA: two static ping-pong buffers of 512 32-bit words
- Task stacks: main 3072 bytes, input 2048 bytes, HTTP/WebSocket 5120 bytes
- Active MP3 workspace: 11,472 bytes DRAM and 16,384 bytes IRAM
- Diagnostic trace: disabled in this binary
- Benchmark and tone-test profiles: disabled
- Status LED: unavailable with I2S-PDM; GPIO2 carries the fixed I2S WS signal

The tracked `esp8266/rtos-sdk-native/sdkconfig.defaults` is the canonical
configuration. It explicitly disables libmad and all alternative output modes,
preventing an experimental backend from leaking into production through a stale
build cache.

All 290 repository tests pass. On the physical Wemos, station 510 (Retro FM)
played as MP3 128 kbit/s while 32 WebSocket status frames arrived during a
60-second run. After the closing socket timeout drained, the standard Web API
again returned HTTP 200 with `playing=true`, `codec=MP3`, and `bitrate=128`.
The archived binary has diagnostic trace, benchmark, and tone-test options OFF.
