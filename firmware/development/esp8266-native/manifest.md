# ESP8266 native development artifact

- Source revision: `8d26dbd`
- Target: ESP8266EX, 4 MiB flash
- Framework: ESP8266 RTOS SDK v3.4
- Profile: development, diagnostic logging enabled, `-O3`, audio profiler disabled
- Features: HTTP radio streams, Helix MP3/AAC, WebUI-only display profile
- Application flash offset: `0x10000`
- File: `app.bin`
- Size: 655776 bytes
- SHA-256: `DC4FCE7E6B93928B7E2C7B6723222289977F48F1B94A9D1B4E8E33BC3FAE5163`

## Changes

- Replaced synchronous SPI-PDM transactions with a bounded 12-block queue
  drained by the HSPI transfer-complete interrupt.
- The audio task now sleeps on a FreeRTOS notification only while the queue is
  full; it no longer spins while every 512-bit PDM block is transmitted.
- Increased the board-specific input stack to 3072 bytes after physical BOOT
  tests exposed stack overflows while reading the SPIFFS playlist.
- Added reproducible MP3/AAC profiling URLs and optional static IPv4 settings
  to the opt-in diagnostic profile; they are absent from this normal image.

## Validation

- Clean normal firmware build completed successfully with AAC enabled and the
  profiling option disabled; all 231 repository regression tests passed.
- The physical Wemos D1 mini joined Wi-Fi by DHCP at 192.168.100.6; WebUI
  root and /api/native/status both returned HTTP 200.
- A simulated short BOOT press selected station 1 and opened its ICY stream;
  live status reported playback, AAC, 67 kbit/s and current RSSI.
- Reproducible local AAC 320, AAC 64 and MP3 128 streams all exercised the
  interrupt-driven output without watchdog resets or SPI queue timeouts.
- On AAC 320, SPI queue wait averaged about 22% of wall time as blocked task
  time, while gain/mix/PDM computation averaged about 13%.
