# 2026-09-06 — I2S RCPDM32 output comparison

Diagnostic firmware, not ordinary radio. CPU160/QIO40, I2S RCPDM32 GPIO3,
2 x 512-word DMA, no Wi-Fi or decoder. Same deterministic PCM test as PDM32.
RC alpha=1/16; production modulation algorithm is unchanged.
Test volume=64, normalization=off, runtime only (NVS unchanged).

- Pack 48000 words: median 119216 us (2.116 times PDM32).
- Producer excluding DMA wait: 157903 us per nominal audio second.
- Two physical runs: no DMA underruns, partial handoffs or FIFO empty.
- RAM unchanged relative to PDM32. RCPDM does not replace the board default.

Flash app0 only at 0x10000. Restore ordinary radio after comparison.
No application UART RX commands: GPIO3 carries audio.

Results: [comparison](../../../docs/benchmarks/esp8266-output-compare-2026-09-06/README.md).
SHA256 and measured build details are in `manifest.json`.
