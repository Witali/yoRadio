# ESP8266 KaRadio Helix I2S-PDM

First compiled development image of the KaRadio-style producer/consumer
target for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-03
- Source base: `8db6399` plus the accompanying uncommitted target sources
- Application offset: `0x10000`
- Application: `app.bin` (605,680 bytes)
- Application SHA-256: `20090E9C9D37621C9C2B7DBA151DEA774749A0314D3B61ED7239785A10EBA090`
- Bootloader offset: `0x0`; file: `bootloader.bin`
- Partition table offset: `0x8000`; file: `partition-table.bin`
- CPU: 160 MHz; application compiled with `-O3`
- Flash runtime: QIO 40 MHz (the SDK-compatible image header remains DIO)
- Decoder: yoRadio Helix MP3 with the 32-bit SSO synthesis path
- AAC: disabled in this first RAM-conservative profile
- Audio: mono I2S/SLC-DMA PDM on GPIO3, PDM32 at nominal 1.536 MHz
- DMA: two static buffers of 512 32-bit words
- Stream pipeline: network priority 6, audio priority 5
- Compressed ring: 4,096 static bytes; startup threshold 3,072 bytes
- Network reads: up to 1,460 bytes directly into the writable ring region
- ELF IRAM text/BSS: 23,080 / 4,040 bytes
- ELF DRAM data/BSS: 1,640 / 24,352 bytes
- Flash text/rodata: 471,846 / 108,904 bytes
- HTTPS: disabled; HTTP/ICY, redirects and chunked transfer supported

The full SDK build completed successfully (613 Ninja steps). Twenty focused
Helix, PDM, memory-layout and KaRadio pipeline regression tests passed. This
image has not yet been flashed to the physical board, so playback stability,
runtime heap and worker stack high-water marks remain to be measured before it
is promoted from development.
