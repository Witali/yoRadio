# ESP8266 native radio — AAC PCM blocks, 2026-09-06

- Application source: `9f991d6` (unrelated Arduino working-tree edits excluded).
- Ordinary radio, **not** the RAM benchmark. Trace/profile/benchmarks OFF.
- CPU 160 MHz, QIO40, Helix MP3 SSO/AAC-LC, mono GPIO3 I2S-PDM32.
- AAC block output ON, 512 frames / 1024 PCM bytes; DMA remains 2 x 512 words.
- Image: 690032 bytes.
- SHA-256: `ED44362C26A1438EAFA78EE6EBC7A828D741F12BA00E879D4F64392D9FCB6772`.
- App0 address: `0x10000`; no bootloader/partition/NVS/SPIFFS image included.

AAC saves 3072 DRAM bytes; exact PCM regression and physical RAM-to-DMA
tests pass. Decode-only calls cost about 6.1% more. Long-run streaming and
the earlier Wi-Fi/WebUI instability are not certified by this short benchmark.
See [results](../../../docs/ESP8266_AAC_PCM_BLOCKS.md).

App0 was flashed over COM8 and hash verified; RTS reset confirmed ordinary
startup and the retained 511-station index. Recovery AP was enabled before
late Wi-Fi association; HTTP at the previous IP timed out. No live-stream
or WebUI availability acceptance is claimed.
