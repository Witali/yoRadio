# ESP8266 native QIO 80 MHz development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: Zbit ZB25VQ32B, 4 MiB, QIO at 80 MHz
- JEDEC ID: `5E:4016`
- Audio: mono SPI-PDM on GPIO13/D7
- SDK: ESP8266 RTOS SDK v3.4

The ESP8266 ROM loads the bootloader through its DIO-compatible image header.
The QIO-configured bootloader then enables Quad I/O at 80 MHz before loading
the application. Flash all three images without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

SHA-256:

- `app.bin`: `0B354F2640D9B3D20767844D2A5AA94CDEE347661F2F6883019809A5BBA52007`
- `bootloader.bin`: `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin`: `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Physical validation on COM10:

- application completed two independent RTS cold-start sequences;
- CPU reported 160 MHz and the 511-station index loaded from SPIFFS;
- Wi-Fi connected and received `192.168.100.6`;
- WebUI root, status API and playlist returned HTTP 200;
- 20 consecutive status requests succeeded;
- eight consecutive 36,086-byte playlist reads from SPIFFS succeeded;
- the board was intentionally left running with QIO at 80 MHz.
