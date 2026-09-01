# ESP8266 native QIO80 SSO PDM 1.536 MHz

Development production-profile image for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-01
- Application offset: `0x10000`
- Application: `app.bin` (668,592 bytes)
- SHA-256: `30C8666F5F22B844C4EB01B30347DC278DB719D0ED52A3A3FE2E9095099A2975`
- CPU: 160 MHz; compiler release optimization
- Flash runtime: QIO 80 MHz (the SDK-compatible image header remains DIO)
- MP3: Helix 32-bit SSO
- AAC: Helix exact fixed-point
- Audio: mono I2S/SLC DMA on GPIO3, genuine PDM32 x1
- Nominal carrier: 1.536 MHz; divider result: 1.538461 MHz (+0.16%)
- DMA: two static ping-pong buffers of 512 32-bit words (4 KiB total)
- PDM packer: branchless PDM32, fully unrolled in 456 bytes of IRAM
- DMA wait: one direct task notification per returned 512-word buffer

The physical generated-PCM benchmark reached 100.2% realtime with zero
ping-pong underruns. DMA wait was 90.4% of wall time and producer non-wait time
fell from 33.5% to 9.1% (3.66x). Isolated 320-kbit/s RAM fixtures used 28.12%
CPU for MP3 SSO and 76.20% for AAC-LC. See
`docs/ESP8266_AUDIO_PROFILE.md` for the full method and limitations.
