# ESP8266 native QIO40 SSO PDM 1.536 MHz

Validated development production-profile image for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-02
- Source commit: `fb802df`
- Application offset: `0x10000`
- Application: `app.bin` (669,248 bytes)
- SHA-256: `FB212FEB807290AC3068C2E0725BE41A4B0F08C895EB2F9103D8ABA4B6DB2E56`
- CPU: 160 MHz; compiler release optimization
- Flash runtime: QIO 40 MHz (the SDK-compatible image header remains DIO)
- MP3: Helix 32-bit SSO
- AAC: Helix exact fixed-point
- Audio: mono I2S/SLC DMA on GPIO3, genuine PDM32 x1 at 1.538461 MHz
- DMA: two static ping-pong buffers of 512 32-bit words
- HTTP/WebSocket task stack: 5120 bytes
- Diagnostic trace: disabled in this binary
- Benchmark and tone-test profiles: disabled
- Status LED: unavailable with I2S-PDM; GPIO2 carries the fixed I2S WS signal

The tracked `esp8266/rtos-sdk-native/sdkconfig.defaults` is the canonical
configuration. It explicitly disables libmad and all alternative output modes,
preventing an experimental backend from leaking into production through a stale
build cache.

All 284 repository tests pass. On the physical Wemos, a trace build made from
the same profile opened station 510 (Retro FM) over HTTP/ICY, selected MP3 from
the stream, decoded non-silent 44.1-kHz stereo PCM, preserved a non-silent
normalized/mono signal, and copied changing PDM32 words into the physical SLC
DMA ring. WebUI advanced from stopped to playing and reported MP3 128 kbit/s,
44 kHz stereo. The final archived binary was rebuilt with every trace and
benchmark option OFF.
