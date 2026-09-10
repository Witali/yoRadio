# Opus input2048 diagnostic candidate, 2026-09-10

Source5147be3, app885520B. Same configuration as input1k-clock except Opus
input2048B. Fixed scratch6144B, minimum4096B post-init reserve, PCM and
2x512-word GPIO3 I2S PDM32 DMA unchanged. This requires1024B more dynamically
allocated DRAM; static sizes alone do not establish safe heap headroom.

Built and archived for A/B; no qualification is implied by compilation.
Do not promote before repeated physical continuity/heap measurements.
Builder changes remain diagnostic-only; production input stays1024B.
Host lifecycle tests include2048 input with allocation-failure and cleanup
coverage. They cannot prove free contiguous memory on the physical device.
