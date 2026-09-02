# ESP8266 native QIO40 SSO PDM 1.536 MHz

Validated development production-profile image for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-02
- Source commit: `d2bc15c`
- Application offset: `0x10000`
- Application: `app.bin` (669,248 bytes)
- SHA-256: `6745B919DDE7D5F8F363139A89AE74514AD8A0FF7752D60637D4C08E43803273`
- CPU: 160 MHz; compiler release optimization
- Flash runtime: QIO 40 MHz (the SDK-compatible image header remains DIO)
- MP3: Helix 32-bit SSO
- AAC: Helix exact fixed-point
- Audio: mono I2S/SLC DMA on GPIO3, genuine PDM32 x1 at 1.538461 MHz
- DMA: two static ping-pong buffers of 512 32-bit words
- HTTP/WebSocket task stack: 5120 bytes

This build fixes truncated WebUI resources on the physical ESP8266 by copying
memory-mapped pages and scripts into a shared DRAM send buffer, pacing chunked
writes, retrying transient lwIP buffer exhaustion for up to 15 seconds, and
allowing a successful close-framed response to drain before socket cleanup.
Large per-handler stack arrays were replaced by a reusable static buffer.

All 280 repository tests pass. On the physical Wemos, the root page, CSS,
JavaScript, player/options fragments, logo, 36,086-byte playlist, and status
endpoint all returned HTTP 200. The WebSocket control test covered settings,
station selection, Play, Stop, Pause, Next, and Previous; only one persistent
WebSocket client is supported at a time.
