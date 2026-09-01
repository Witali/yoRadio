# ESP8266 native QIO80 SSO PDM 1.536 MHz

Development production-profile image for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-01
- Application offset: `0x10000`
- Application: `app.bin` (668,576 bytes)
- SHA-256: `D980FD2A023A1F065BE352174D2FC1C32BDE275D2AE1A5784DFF2F1C5B965F79`
- CPU: 160 MHz; compiler release optimization
- Flash runtime: QIO 80 MHz (the SDK-compatible image header remains DIO)
- MP3: Helix 32-bit SSO
- AAC: Helix exact fixed-point
- Audio: mono I2S/SLC DMA on GPIO3, genuine PDM32 x1
- Nominal carrier: 1.536 MHz; divider result: 1.538461 MHz (+0.16%)
- DMA: two static ping-pong buffers of 512 32-bit words (4 KiB total)

The physical generated-PCM benchmark reached 100.2% realtime with zero
ping-pong underruns. DMA wait was 66.5% of wall time; FreeRTOS whole-system
counters reported 77.0% busy and 23.0% idle. Isolated 320-kbit/s RAM fixtures
used 28.12% CPU for MP3 SSO and 76.20% for AAC-LC. See
`docs/ESP8266_AUDIO_PROFILE.md` for the full method and limitations.
