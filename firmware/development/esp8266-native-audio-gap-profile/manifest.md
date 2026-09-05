# ESP8266 native audio-gap diagnostic image

- Date: 2026-09-05; not a production default.
- Sources: 2468d51 plus the instrumentation committed as 50f996b.
- CPU 160 MHz, QIO 40 MHz, -O3, Helix MP3 SSO, ordinary I2S PDM32.
- Same production sdkconfig; AUDIO_PROFILE=ON, AUDIO_PROFILE_WINDOW_MS=30000.
- app.bin: 693856 bytes.
- SHA256: D9435D6F58C8F9BE804D00B42FD02322AB113EB8D53AC87132ACDC324100E9D1.
- Tested in app0 at 0x10000, existing 4-MiB OTA layout / SPIFFS 256 KiB.
- Never write this image over partition data, otadata, NVS or SPIFFS.
- Ordinary app restored after measurement; see docs/ESP8266_AUDIO_GAPS_2026-09-05.md.

## Changelog

Adds opt-in PCM gap and DMA late/incomplete-buffer counters, reporting every
30 seconds. Does not change decoder, PDM algorithm, buffer sizes or ownership.
