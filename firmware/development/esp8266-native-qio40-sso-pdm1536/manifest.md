# ESP8266 native QIO40 SSO PDM 1.536 MHz

Validated development production-profile image for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-02
- Source commit: `099a1c5`
- Application offset: `0x10000`
- Application: `app.bin` (669,248 bytes)
- SHA-256: `3F32B122BBA676BD4D3BB027C3A7C8002F4519A4536689C97AC9951376C80C2C`
- CPU: 160 MHz; compiler release optimization
- Flash runtime: QIO 40 MHz (the SDK-compatible image header remains DIO)
- MP3: Helix 32-bit SSO
- AAC: Helix exact fixed-point
- Audio: mono I2S/SLC DMA on GPIO3, genuine PDM32 x1 at 1.538461 MHz
- DMA: two static ping-pong buffers of 512 32-bit words
- HTTP/WebSocket task stack: 5120 bytes
- Status LED: unavailable with I2S-PDM; GPIO2 carries the fixed I2S WS signal

This build fixes truncated WebUI resources on the physical ESP8266 by copying
memory-mapped pages and scripts into a shared DRAM send buffer, pacing chunked
writes, retrying transient lwIP buffer exhaustion for up to 15 seconds, and
allowing a successful close-framed response to drain before socket cleanup.
Large per-handler stack arrays were replaced by a reusable static buffer.

The ESP8266 fixes I2S output to GPIO3 DATA, GPIO15 BCLK and GPIO2 WS. A physical
experiment confirmed that reclaiming GPIO2 after DMA starts makes the LED blink
but stops PDM audio. The production I2S-PDM profile therefore keeps both clock
pads assigned for the full transfer. GPIO2 status indication remains available
only in the legacy SPI-PDM profile; with I2S-PDM the onboard LED can appear
continuously lit because it averages the 48-kHz WS waveform.

All 282 repository tests pass. On the physical Wemos, the new image booted,
obtained 192.168.100.6 from Wi-Fi and started Retro FM. The stream returned HTTP
200 and reported live MP3 playback at 128 kbit/s. The root page, CSS, JavaScript,
player/options fragments, logo, 36,086-byte playlist, and status endpoint all
returned HTTP 200. The WebSocket control test covered settings, station
selection, Play, Stop, Pause, Next, and Previous; only one persistent WebSocket
client is supported at a time.
