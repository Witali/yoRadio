# ESP8266 native QIO40 SSO PDM 1.536 MHz

Validated development production-profile image for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-02
- Source commit: `cf9257e`
- Application offset: `0x10000`
- Application: `app.bin` (669,712 bytes)
- SHA-256: `D2E8BE94C262BF6E97661DD84CD701AD9DE5D34BCC9E69C490B8893B2326AAA2`
- CPU: 160 MHz; compiler release optimization
- Flash runtime: QIO 40 MHz (the SDK-compatible image header remains DIO)
- MP3: Helix 32-bit SSO
- AAC: Helix exact fixed-point
- Audio: mono I2S/SLC DMA on GPIO3, genuine PDM32 x1 at 1.538461 MHz
- DMA: two static ping-pong buffers of 512 32-bit words
- HTTP/WebSocket task stack: 5120 bytes
- Status LED: onboard active-low GPIO2; steady on Wi-Fi, 500-ms blink while playing

This build fixes truncated WebUI resources on the physical ESP8266 by copying
memory-mapped pages and scripts into a shared DRAM send buffer, pacing chunked
writes, retrying transient lwIP buffer exhaustion for up to 15 seconds, and
allowing a successful close-framed response to drain before socket cleanup.
Large per-handler stack arrays were replaced by a reusable static buffer.

It also reclaims the unused I2S WS pin after NoDAC DMA starts and uses the
onboard LED without another task or stack allocation.

All 282 repository tests pass. On the physical Wemos, the new image booted,
configured GPIO2 as an output and obtained 192.168.100.6 from Wi-Fi. A double
BOOT click selected Retro FM; the stream returned HTTP 200 and reported live
MP3 playback at 128 kbit/s. The root page, CSS, JavaScript, player/options fragments, logo, 36,086-byte playlist, and status
endpoint all returned HTTP 200. The WebSocket control test covered settings,
station selection, Play, Stop, Pause, Next, and Previous; only one persistent
WebSocket client is supported at a time.
