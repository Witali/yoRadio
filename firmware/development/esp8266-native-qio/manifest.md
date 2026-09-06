# ESP8266 native QIO development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: 4 MiB, QIO at 40 MHz
- Audio: mono SPI-PDM on GPIO13/D7
- SDK: ESP8266 RTOS SDK v3.4

The ESP8266 boot ROM loads the bootloader in DIO mode. The QIO-configured
bootloader then enables Quad I/O before loading the application. Flash all
three images without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

Physical validation on COM10:

- ESP8266EX and 4 MiB flash detected, JEDEC ID `5E:4016`;
- application booted repeatedly after RTS reset;
- CPU reported 160 MHz;
- SPIFFS and the 511-station index loaded;
- Wi-Fi connected and received `192.168.100.6`;
- WebUI root returned HTTP 200.
