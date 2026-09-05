# ESP8266 native memory profile (diagnostic, not the default firmware)

- Built: 2026-09-05; native source: `6160747` (built immediately before commit).
- Wemos D1 mini / ESP8266EX, CPU 160 MHz, QIO 40 MHz, RTOS SDK v3.4, GCC 8.4, O3.
- Normal Helix MP3 SSO + AAC, GPIO3 I2S PDM32, 2 x 512-word DMA ring.
- `YORADIO_ESP8266_MEMORY_PROFILE=ON`; audio stage profiling, isolated output/
  codec benchmarks, KaRadio producer and heap tracing are OFF.
- `app.bin`: 689488 bytes.
- SHA-256: `01CFD5F57E26B441BDF3A2336CFE66D9A930C8BFE0ECB3AC89A9BF67B5B6AFC8`.

## Changelog

Adds opt-in UART measurements of DRAM free/lifetime minimum/largest block,
sampled low-water windows, separate free IRAM and app/audio/httpd/idle stack
margins. No additional task, speculative allocations, buffer resizing or
FreeRTOS trace arrays. The final profile has 24 bytes of explicit static state;
alignment makes the DRAM heap-region difference from ordinary firmware 32 bytes.

The exploratory image used for the first MP3/two-tab run was 689536 bytes,
SHA-256 `FC0DC32636F0C6DC7344B6D9DB47D2544D6A731CEB6119C2EAE0B4EF7A640DE9`.
It also reported a `scan_us` field from a non-monotonic SDK time reading;
that field was removed from this final image. Discard that timing column in
the exploratory log; its heap and stack counters remain usable.

Flash only the active app slot (0x10000 on the tested board). Preserve NVS,
SPIFFS, partitions and OTA selection data. Never use this diagnostic file as a
SPIFFS image. Restore the ordinary `../esp8266-native/app.bin` after testing.
Its expected SHA-256 is
`76E47B98D18CCC7C259FCFDDE7A627D1266C6A6D17A408E103F4C9BD3BABAE59`.

Workload and interpretation: `tools/esp8266_memory_profile/README.md`.
Results are recorded separately in `docs/ESP8266_MEMORY_HEADROOM_2026-09-05.md`.
