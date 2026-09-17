# PCM consumer using the app task — 2026-09-17

Ordinary radio with all18 accepted ASM stages, no extra consumer task/stack,
leased PCM2x960 mono, DMA2x128, LED OFF, RX14, TCP536/window2440/OOSEQ ON.
CPU160/QIO40, I2S PDM32 GPIO3. Input1024, scratch6144, reserve4096 unchanged.
OTA passed; exact image/loaded-byte proofs and configuration are retained.

First window includes startup and cannot qualify. The next steady Kultur24
window produced27.840s PCM/27.982s with196 underruns: improvement is not a
zero-gap success. Heap7156..8248B, output/app stack watermark1632B,
decoder stack1496B; no queue output error. More observations retained in
board/. Decoder wall time now includes waiting for leased PCM and is NOT
CPU utilization. This experimental mode is not the default.
