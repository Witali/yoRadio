# ESP8266 native libmad IRAM-workspace development artifact

- Built: 2026-09-01
- Source revision: `352733f`
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: 4 MiB, QIO at 80 MHz
- SDK: ESP8266 RTOS SDK v3.4
- Compiler: GCC 8.4, `-O3`
- Profile: `sdkconfig.libmad-mp3-only-qio80.defaults`
- MP3: ESP8266Audio libmad, external Layer III IRAM workspace
- AAC: disabled
- Physical validation: decoder RAM benchmark passed on the Wemos D1 mini;
  integrated radio/WebUI validation of this archived application is pending

Flash without erasing NVS or SPIFFS:

| File | Size | Offset | SHA-256 |
| --- | ---: | ---: | --- |
| `bootloader.bin` | 7,808 | `0x0000` | `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85` |
| `partitions.bin` | 3,072 | `0x8000` | `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF` |
| `app.bin` | 657,408 | `0x10000` | `09C1823BBF99EE352F5D5F127AD03EB2A8BD88EAC2B17FAD40D8F98F249661E9` |

Validation completed:

- MP3-only/QIO80 and full libmad+AAC/QIO80 Xtensa builds succeeded;
- all 261 repository tests passed;
- the external-workspace fixture decoded 18 retained 320-kbit/s MP3 frames
  to PCM byte-for-byte identical to the original libmad layout;
- Xtensa DWARF reports `mad_frame` reduced from 20,784 to 13,880 bytes;
- active MP3 workspace is expected to reserve 12,288 bytes IRAM and use
  20,388 bytes DRAM, freeing 6,904 bytes of byte-addressable DRAM compared
  with the previous MP3-only image;
- the fair full MP3+AAC hardware benchmark reserved 16,384 bytes IRAM and used
  22,180 bytes DRAM for libmad versus 14,756 bytes for Helix;
- libmad decoded 200 RAM-resident 320-kbit/s frames in 11,965 us average
  (2.005x realtime) versus Helix at 13,786 us (1.740x), while 50 lifecycle
  cycles returned heap from 96,868 to 96,868 bytes.
