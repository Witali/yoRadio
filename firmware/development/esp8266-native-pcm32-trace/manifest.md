# ESP8266 native PCM32 / direct DMA diagnostic build

- Built and tested: 2026-09-05; source commit `6bd547b`.
- Same tracked ordinary profile as `../esp8266-native-pcm32/`, with only
  `YORADIO_ESP8266_AUDIO_TRACE=ON`. Benchmark/profiling/tone probes OFF.
- Wemos D1 mini, CPU 160 MHz, 4 MiB QIO40, RTOS SDK v3.4 / GCC 8.4 O3.
- Mono, Helix MP3 SSO + AAC, GPIO3 I2S-PDM32, two 512-word DMA buffers.
- `app.bin`: **689792 bytes**.
- SHA-256: `C249F9374D62FB8CD8C103BC5422CA2439A6E4D227F23D39E13A1A214D26506D`.

Flashed app0 only with hash verification. The bounded trace prints an initial
snapshot and then nonzero decoder/processed PCM and non-neutral committed
DMA-PDM. It runs outside the ISR and is not suitable for CPU timing.
Retro FM MP3 128 kbit/s: 32-frame mono PCM min=-3/max=17, FNV `e24d7993`,
identical after processing at volume 254 / balance 0. DMA-PDM fingerprints
change and include `5555555a`, confirming that the output is not all neutral.
Actual MP3 workspace: DRAM 8440, IRAM 16384. Final trace snapshot: free heap
15504, lifetime minimum 10988, web stack headroom 2328. ICY/feed continued.

The ordinary image was subsequently restored and started; this diagnostic
is not left installed. Nonzero DMA data is not an electrical GPIO
measurement or a confirmed listening result. Wi-Fi/HTTP startup retries
were observed. No credentials or private filesystem image is included.

[Detailed results and filtered trace](../../../docs/ESP8266_PCM32_DIRECT_DMA.md).
