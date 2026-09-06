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
- AAC: disabled to preserve the ESP8266 heap reserve
- Profile: `sdkconfig.libmad-mp3-only-qio80.defaults`, experimental

Flash without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

SHA-256:

- `app.bin` (657,696 bytes): `A9523A52CFC19FCBFB1AE069B62BF297C5858A6BB4F5C5C7DCC12293B8306B2E`
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
- application size is 50,384 bytes larger than the matching Helix image;
- physical 160-MHz/QIO80 MP3 RAM benchmark: 12,904 us average, 12,925 us
  maximum, 1.859x realtime and 67,888 bytes free heap;
- matching Helix benchmark: 14,289 us average, 14,313 us maximum, 1.679x
  realtime and 81,416 bytes free heap;
- libmad improves isolated MP3 throughput by 10.72%, with 9.69% lower average
  frame time;
- 50 decoder create/destroy cycles and 50 MP3/AAC switches returned heap from
  96,868 to 96,868 bytes (delta 0);
- the MP3-only profile reserves 5,120 bytes of IRAM and uses 27,292 bytes of
  DRAM while libmad is active;
- physical boot, DHCP at `192.168.100.6`, WebUI HTTP 200, live ICY metadata,
  MP3 128-kbit/s playback and WebUI Stop all passed.

This archived application replaces the earlier reset-loop image and is usable
as the experimental MP3-only libmad firmware. The combined libmad+AAC profile
still exceeds the practical heap budget after reserving AAC's 16-KB word arena;
use this MP3-only profile or the normal Helix production profile.
