# ESP8266 native QIO 80 MHz development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: Zbit ZB25VQ32B, 4 MiB, QIO at 80 MHz
- JEDEC ID: `5E:4016`
- Audio: mono SPI-PDM on GPIO13/D7
- SDK: ESP8266 RTOS SDK v3.4
- Source: `esp8266/rtos-sdk-native` from the source tree committed with this manifest
- Profile: development, `-O3`, Helix MP3/AAC, shared ESP HTTP Server task

The ESP8266 ROM loads the bootloader through its DIO-compatible image header.
The QIO-configured bootloader then enables Quad I/O at 80 MHz before loading
the application. Flash all three images without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

SHA-256:

- `app.bin` (670,848 bytes): `1CF122A5266A871707FE8A48A5C44262732065E983EEB569345324C1EBA937E8`
- `bootloader.bin`: `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin`: `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Physical validation on COM10:

- Helix MP3/AAC fixed-point multiplication no longer calls the ROM
  `__muldi3` helper in the decode hot path;
- the optimized decoders produced PCM identical to the retained 64-bit
  reference for the checked-in 320-kbit/s MP3 and AAC golden fixtures;
- safe MP3 divisions by 3, 5, 6, 18, and 36 use an exact Q32 reciprocal
  multiply with quotient correction; reciprocal OFF/ON averaged 14,653/14,284
  us per RAM-resident 320-kbit/s frame, a 2.52% speedup;
- disassembly confirmed that the ordinary MP3 frame path no longer calls the
  ROM integer divide helper; only one-time free-format bitrate detection keeps
  a variable division;
- GCC 8.4 disassembly and physical RAM benchmarks rejected loop unrolling in
  the MP3 polyphase kernel: the original, manual x2, and manual x4 functions
  use 1,730/2,763/4,699 bytes and average 14,284/15,092/15,669 us per frame;
  the production source therefore keeps the compact original loop;
- decode-only MP3 320 kbit/s reached 74.1% realtime with a 32.9 ms worst
  decoder call, versus 53.8% before the fixed-point optimization;
- decode-only AAC 320 kbit/s reached 99.2% realtime with a 21.4 ms worst
  decoder call, versus 80.8% before the fixed-point optimization;
- application completed two independent RTS cold-start sequences;
- the reciprocal-enabled production image booted after flashing on COM10;
- CPU reported 160 MHz and the 511-station index loaded from SPIFFS;
- Wi-Fi connected and received `192.168.100.6`;
- WebUI root, `/api/native/status`, and `/data/playlist.csv` returned HTTP 200;
- 20 consecutive status requests succeeded;
- eight consecutive 36,086-byte playlist reads from SPIFFS succeeded;
- with WebSocket `/ws` open, the HTML shell, variables, four shared assets,
  player fragment, logo and 36,086-byte playlist all returned HTTP 200 over
  one reused HTTP/1.1 connection, with valid Content-Length or chunked framing;
- live WebUI commands verified the full settings response, playlist-row Play,
  Stop, Toggle, Next and Previous state updates on the physical board;
- 42 focused HTTP, WebSocket and shared-WebUI regression tests passed;
- the board was intentionally left running with QIO at 80 MHz.
