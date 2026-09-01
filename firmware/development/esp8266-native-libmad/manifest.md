# ESP8266 native experimental libmad development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: 4 MiB, QIO at 80 MHz
- Audio: mono SPI-PDM on GPIO13/D7
- SDK: ESP8266 RTOS SDK v3.4
- Compiler: GCC 8.4, `-O3`
- Source: `esp8266/rtos-sdk-native`
- MP3: ESP8266Audio libmad, upstream commit
  `10d929ac01436dfe8856e0a06fd9ec35a848c6e2`
- AAC: yoRadio Helix
- Profile: `sdkconfig.libmad-qio80.defaults`, experimental

Flash without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

SHA-256:

- `app.bin` (721,232 bytes): `BBF092841F4098E43119A47625940D9DEBD3FA164FED097D094CBDDA02A77DA7`
- `bootloader.bin` (7,808 bytes): `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin` (3,072 bytes): `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Validation completed:

- full Helix-default and libmad QIO80 radio builds succeeded;
- the libmad RAM-benchmark image built successfully;
- golden MP3: 18 frames, 41,472 signed samples, 82,944 PCM bytes,
  48 kHz stereo;
- PCM versus current Helix: 49.41 dB SNR, maximum absolute error 99 levels;
- all 256 repository tests passed;
- static DRAM: 15,984 bytes; reported decoder workspace: 33,336 bytes;
- application size is 50,384 bytes larger than the matching Helix image.

Physical validation is not claimed for this artifact: no serial port was
enumerated when the benchmark was ready. Flash it only as an experimental
image and record RAM-frame realtime ratio, maximum frame time, free heap, and
live radio stability before considering a default change.
