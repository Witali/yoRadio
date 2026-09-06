# 2026-09-06 — Exact AAC speed improvements

Ordinary native ESP8266 radio, source `851c7d2`. Diagnostic profiles OFF.

- Specialize bounded AAC window/overlap processing; retain 512-frame PCM.
- Decode short Huffman codes using a 3-KiB flash-only generated prefix table.
- Preserve exact PCM, overlap, clipping and mono downmix; AAC SSO stays OFF.
- Isolated 48-kHz/320-kbit/s AAC: 18945 -> 15140 us/frame (-20.09% time).
- No added DRAM/IRAM. Firmware grows 8304 bytes relative to the previous
  ordinary AAC-block build. Final host suite: 344 passed.
- Physical isolated I2S-PDM A/B tests: zero underruns/partial handoffs/FIFO
  empty for AAC and MP3. Timing excludes Wi-Fi; not a live-stream stress test.
- Reject the larger 12-KiB lookup (full-output underruns) and both bit-reader
  experiments (insufficient benefit, increased stack/code-layout regressions).

Flash app0 only at `0x10000`, preserve existing bootloader, OTA layout, NVS
and SPIFFS. GPIO3 carries audio: reset with RTS, never send UART commands.

See [optimization report](../../../docs/ESP8266_AAC_SPEED_OPTIMIZATION.md)
and `manifest.json` for hash, build settings and memory measurements.
