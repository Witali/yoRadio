# App PCM / input2KiB / DMA256 — 2026-09-17

Only DMA capacity changes from apppcm2k:128 to256 words per buffer,
adding1024B static DRAM. PCM remains2x960 mono and no extra task/stack.
All18 accepted ASM stages, CPU160/QIO40, I2S PDM32 GPIO3, LED OFF,
RX14, TCP536/window2440/OOSEQ ON. Scratch6144 and reserve4096 unchanged.

OTA passed. **Kultur24:0/10 qualified**, five incomplete measurement
windows. Scratch stage8 failures had10768..11732B total free but largest
blocks4200..5160B, below the required6144B. Stage10 failures had2812..3868B
free against the unchanged4096B reserve. Boot minimum2636B was observed.
Intervals with no PCM after init failure count neutral output, not an
active-audio dropout rate. All ten results are retained under board/.

NOT selected as default or a successful buffer increase. The next image
returns to DMA128 and measures background-service delay before further
changes. No acoustic qualification or claim of normal playback.
