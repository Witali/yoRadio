# ESP8266 KaRadio Helix I2S-PDM

First compiled development image of the KaRadio-style producer/consumer
target for a 4 MiB Wemos D1 mini / ESP-12E.

- Built: 2026-09-03
- Source base: `ca5b52e` plus the physical-test memory correction
- Application offset: `0x10000`
- Application: `app.bin` (605,680 bytes)
- Application SHA-256: `406CE1D5678DBC769A3309CE5AE0CA223A3BCC56C7A9BE81F8CD5672862F4A74`
- Bootloader offset: `0x0`; file: `bootloader.bin`
- Partition table offset: `0x8000`; file: `partition-table.bin`
- CPU: 160 MHz; application compiled with `-O3`
- Flash runtime: QIO 40 MHz (the SDK-compatible image header remains DIO)
- Decoder: yoRadio Helix MP3 with the 32-bit SSO synthesis path
- Decoder memory: 11,472 bytes DRAM + 16,384 bytes IRAM on the physical board
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

The image was flashed to physical ESP8266EX `48:3f:da:18:f0:35` on COM8; the
bootloader verified it and SPIFFS retained 511 indexed HTTP stations. Client
Wi-Fi connected to the configured router at `192.168.100.6`; HTTP returned
`200 OK`, WebSocket commands selected stations, and ROCK FM was identified as
MP3 128 kbit/s, 44.1 kHz stereo with `playing` status. Twenty-one focused
Helix, PDM, memory-layout and KaRadio pipeline regression tests passed.

Physical testing also exposed an unresolved limitation: after several seconds
of active Helix + I2S-PDM playback, the TCP/IP/WebUI path stops accepting new
connections. A 2-KiB compressed-ring experiment returned another 2 KiB to the
heap but did not remove the failure, so the production 4-KiB jitter buffer was
restored. The board is left in the tested stopped state with WebUI reachable;
this development image must not yet be promoted as playback-stable.
