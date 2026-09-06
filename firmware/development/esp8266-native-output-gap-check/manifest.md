# ESP8266 native isolated-output diagnostic image

- Date: 2026-09-05; not a radio/production image.
- Sources: 50f996b; CPU 160 MHz, QIO 40 MHz, -O3, I2S PDM32, 2 x 512 DMA words.
- AUDIO_PROFILE=OFF; AUDIO_OUTPUT_BENCHMARK=ON; TONE_TEST=OFF.
- app.bin: 125248 bytes.
- SHA256: 903E373DEAFB95229F1DAFCDC4F7E9A26294A965807D638BBD018CEC2AA2609D.
- Tested in app0 at 0x10000. Do not overwrite NVS/SPIFFS/otadata/partition table.
- Ordinary app restored after measurement; see docs/ESP8266_AUDIO_GAPS_2026-09-05.md.

## Changelog

Uses the existing generated-PCM benchmark with the current production output
configuration: Wi-Fi/codecs off, 2-second warmup and 10-second measurement.
Current saved normalization setting was off. No persistent settings are changed
by this isolated benchmark. Measured zero DMA underruns.
