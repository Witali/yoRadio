# ESP32-C3 OLED native production development image

## Build

- Date: 2026-08-29
- Embedded source revision: `d595dac`
- ESP-IDF: 6.0.2
- Target: ESP32-C3, RISC-V, single core at 160 MHz
- Board: 01Space-style ESP32-C3 with onboard 0.42-inch SSD1306 OLED
- Profile: production, `-O3`, application and bootloader logs disabled
- Display: SSD1306, 72x40, I2C address `0x3c`, SDA GPIO5, SCL GPIO6
- Audio: stereo PDM, left GPIO10, right GPIO3, 48 kHz output
- Application partition: 0x1d0000 bytes
- SPIFFS: 256 KiB at `0x3b0000`

## File

| File | Size | Flash offset | SHA-256 |
|---|---:|---:|---|
| `app.bin` | 1,303,824 | `0x10000` | `D3B519173DDEF7B24E1042D04DCB65B64AB4D8E9BA1E7F5990EA336A8B80A34D` |

This is an application-only update. Writing it at `0x10000`, or uploading it
through WebUI OTA, preserves NVS, saved settings, Wi-Fi configuration,
playlist and SPIFFS WebUI files.

## Validation

- Flashed and hash-verified through the native USB Serial/JTAG adapter on a
  physical ESP32-C3 revision 0.4.
- Restored Wi-Fi client mode, the saved playlist and Radio Mayak playback.
- Received `SNTP synchronized` 8.237 seconds after reset while Radio Mayak was
  already decoding a 320 kbit/s MP3 stream; no underrun or pause followed.
- Radio Mayak MP3: 317–324 kbit/s measured, 27.7–28.1% decode time, 3.54–3.60x
  real-time margin.
- Radio Record HQ MP3: 319–321 kbit/s measured, 25–26% decode time, 3.8–3.9x
  real-time margin.
- Radio Caprice AAC: 317–324 kbit/s measured, about 21% decode time, about
  4.7x real-time margin.
- Laza Radio Ogg Vorbis: 320–329 kbit/s measured, 33–34% decode time, about
  3.0x real-time margin.
- Production WebUI remained reachable and reported active MP3 48 kHz stereo
  playback after the final control interval.
- 55 native ESP32-C3 clock, SNTP, WebUI and settings regression tests passed.
