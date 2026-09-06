# 2026-09-06 — I2S PDM32 output comparison

Diagnostic firmware, not ordinary radio. CPU160/QIO40, I2S PDM32 GPIO3,
2 x 512-word DMA, no Wi-Fi or decoder. Generates deterministic PCM and
measures the production packer before DMA plus 10 seconds of physical output.
Test volume=64, normalization=off, runtime only (NVS unchanged).

- Pack 48000 words: median 56337 us.
- Producer excluding DMA wait: 96458 us per nominal audio second.
- Two physical runs: no DMA underruns, partial handoffs or FIFO empty.
- Diagnostic timestamps read atomically across the SDK's CCOUNT reset.

Flash app0 only at 0x10000. Restore ordinary radio after comparison.
No application UART RX commands: GPIO3 carries audio.

Results: [comparison](../../../docs/benchmarks/esp8266-output-compare-2026-09-06/README.md).
SHA256 and measured build details are in `manifest.json`.
