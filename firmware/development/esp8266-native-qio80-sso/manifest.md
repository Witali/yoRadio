# ESP8266 native QIO 80 MHz Helix SSO development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: Zbit ZB25VQ32B, 4 MiB, QIO at 80 MHz
- Audio: mono SPI-PDM on GPIO13/D7
- SDK: ESP8266 RTOS SDK v3.4, GCC 8.4, `-O3`
- Source: `esp8266/rtos-sdk-native`
- Profile: `sdkconfig.helix-sso-qio80.defaults`
- Decoder: Helix MP3/AAC with `CONFIG_YORADIO_HELIX_MP3_SSO=y`

This is a complete radio/WebUI image, not the RAM-only codec benchmark. The
32-bit SSO MP3 synthesis reuses the existing Helix state and coefficient table;
it does not allocate another decoder buffer. The exact 64-bit synthesis path
remains selectable by building without `CONFIG_YORADIO_HELIX_MP3_SSO`.

Flash all three images without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

SHA-256:

- `app.bin` (672,192 bytes): `C8325972B332E01C8DA5DF69CA06366B6A180EB8FE5759BB07AF8DFAFD21C113`
- `bootloader.bin` (7,808 bytes): `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin` (3,072 bytes): `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Validation:

- The deterministic 320-kbit/s stereo fixture retained all 18 frames and
  41,472 samples. SSO PCM measured 48.50 dB SNR against exact Helix with a
  maximum absolute error of 34 signed 16-bit PCM levels.
- On the physical 160-MHz Wemos D1 mini, exact/SSO average frame times were
  13,705/6,414 us, or 1.751x/3.741x realtime. SSO cut frame time by 53.20%
  without changing the 14,756-byte codec DRAM use or 81,280-byte free heap in
  the isolated benchmark.
- Fifty decoder create/destroy and MP3/AAC switching cycles returned heap from
  96,108 to 96,108 bytes in both builds.
- The full image was flashed on COM8, mounted the existing SPIFFS, indexed 511
  stations, connected to Wi-Fi as `192.168.100.6`, and initialized SPI-PDM.
- WebUI root, native status, and the 36,086-byte playlist returned HTTP 200.
  A WebSocket `play=502` command started the saved station and reported
  `MP3 128 kbps 44 kHz stereo` with player state `playing`.
- All 262 repository tests passed. The SSO profile remains a development
  variant while additional live bitrate/channel/block-type coverage is run.
